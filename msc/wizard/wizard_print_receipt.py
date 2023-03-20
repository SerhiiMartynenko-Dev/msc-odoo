from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_round, float_compare


class MSCPrintReceiptWizard(models.TransientModel):
    _name = 'msc.wizard.print_receipt'
    _description = "MSC Print receipt wizard"

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        ondelete='cascade',
        required=True,
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        ondelete='restrict',
        required=True,
    )
    amount = fields.Monetary(
        string="Amount",
        required=True,
        readonly=True,
    )
    amount_with_commission = fields.Monetary(
        string="Amount to pay",
        required=True,
        readonly=True,
    )

    @api.model
    def create_and_show(self, sale_order):
        if not sale_order or sale_order.state == 'cancel' or not sale_order.amount_total:
            return None

        if len(sale_order.invoice_ids) > 1:
            raise UserError(_("More than one invoice already created for this order"))

        if sale_order.invoice_ids and sale_order.invoice_ids[0].payment_state in ('in_payment', 'paid'):
            return sale_order.invoice_ids[0].action_print_receipt()

        # check settings
        sale_team = self.env.company and self.env.company.msc_default_sale_team_id
        if not sale_team:
            raise UserError(_("Default sales team not defined in the settings!"))
        if not sale_team.fiscal_journal_id:
            raise UserError(_("Fiscal operations journal not defined for sales team!"))

        # prepare wizard values
        uah = self.env.ref('base.UAH')
        values = {
            'sale_order_id': sale_order.id,
            'currency_id': uah.id,
        }

        # compute UAH amount with transfer commission (be each position)
        currency = sale_order.currency_id
        def _to_uah(value):
            if currency != uah:
                return currency.compute(value, uah)
            return value

        transfer_commission = 0.0
        if sale_team.fiscal_journal_id.bank_account_id:
            transfer_commission = sale_team.fiscal_journal_id.bank_account_id.transfer_commission or 0.0

        amount_with_commission = 0.0
        for line in sale_order.order_line:
            amount_with_commission += float_round(float_round(_to_uah(line.price_total / line.product_uom_qty) / (1 - transfer_commission), precision_rounding=uah.rounding)  * line.product_uom_qty, precision_rounding=uah.rounding)

        values.update({
            'amount': _to_uah(sale_order.amount_total),
            'amount_with_commission': amount_with_commission,
        })

        # create and show wizard
        wizard = self.create(values)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Print Receipt"),
            'res_model': wizard._name,
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'edit',
            }
        }

    def action_payment_received(self):
        self.ensure_one()

        invoice = self.sale_order_id._msc_get_invoice()

        if invoice:
            if invoice.payment_state in ('in_payment', 'paid'):
                raise UserError(_("Invoice already paid or in payment"))

            # check settings
            sale_team = self.env.company and self.env.company.msc_default_sale_team_id
            if not sale_team:
                raise UserError(_("Default sales team not defined in the settings!"))
            if not sale_team.fiscal_journal_id:
                raise UserError(_("Fiscal operations journal not defined for sales team!"))
            if not sale_team.fiscal_checkbox_cashier_id:
                raise UserError(_("Cashier not defined for sales team!"))
            if not sale_team.fiscal_checkbox_cash_register_id:
                raise UserError(_("Cash register not defined for sales team!"))

            values = {
                'journal_id': sale_team.fiscal_journal_id.id,
                'currency_id': self.currency_id.id,
                'amount': self.amount_with_commission,
                'kw_checkbox_is_register_receipt': True,
                'kw_checkbox_cashier_id': sale_team.fiscal_checkbox_cashier_id.id,
                'kw_checkbox_cash_register_id': sale_team.fiscal_checkbox_cash_register_id.id,
            }

            if float_compare(self.amount, self.amount_with_commission, precision_rounding=self.currency_id.rounding) != 0:
                if not sale_team.fiscal_journal_id.bank_account_id or not sale_team.fiscal_journal_id.bank_account_id.transfer_commission_account_id:
                    raise UserError(_("Account for transfer commission not defined!"))

                values.update({
                    'payment_difference_handling': 'reconcile',
                    'writeoff_account_id': sale_team.fiscal_journal_id.bank_account_id.transfer_commission_account_id.id,
                    'writeoff_label': _("Transfer commission"),
                })

            self.env['account.payment.register'].with_context(
                active_model='account.move',
                active_id=invoice.id,
                active_ids=invoice.ids,
            ).create(values)._create_payments()

            action = invoice.action_print_receipt()
            return {
                'type': 'ir.actions.act_multi',
                'actions': [
                    {'type': 'ir.actions.act_window_close'},
                    action,
                ]
            }

    def action_payment_rejected(self):
        self.ensure_one()

        # just close wizard
        self.unlink()

