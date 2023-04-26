import logging

from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    kw_checkbox_is_register_receipt = fields.Boolean(
        default=False, string='Register CheckBox receipt')
    kw_checkbox_is_journal_register_receipt = fields.Boolean(
        related='journal_id.kw_checkbox_is_register_receipt')
    kw_checkbox_receipt_id = fields.Many2one(
        comodel_name='kw.checkbox.receipt', string='Receipt', )
    kw_checkbox_invoice_id = fields.Many2one(
        comodel_name='account.move', string='Invoice', )
    kw_checkbox_cashier_id = fields.Many2one(
        comodel_name='kw.checkbox.cashier', string='Cashier', )
    kw_checkbox_cashier_ids = fields.Many2many(
        comodel_name='kw.checkbox.cashier',
        compute='_compute_kw_checkbox_cashier_ids', )
    kw_checkbox_cash_register_id = fields.Many2one(
        comodel_name='kw.checkbox.cash.register', string='Cash register', )
    kw_checkbox_cash_register_ids = fields.Many2many(
        comodel_name='kw.checkbox.cash.register',
        compute='_compute_kw_checkbox_cash_register_ids', )

    @api.model
    def default_get(self, vals):
        res = super().default_get(vals)
        active_id = self.env.context.get('active_id')
        res['kw_checkbox_invoice_id'] = active_id
        return res

    @api.depends('journal_id')
    def _compute_kw_checkbox_cashier_ids(self):
        for obj in self:
            ids = self.env.user.kw_checkbox_cashier_ids
            obj.kw_checkbox_cashier_ids = [(6, 0, ids.ids)]
            if len(ids) == 1:
                obj.kw_checkbox_cashier_id = ids[0].id

    @api.depends('journal_id')
    def _compute_kw_checkbox_cash_register_ids(self):
        for obj in self:
            ids = self.env['kw.checkbox.cash.register'].search([])
            obj.kw_checkbox_cash_register_ids = [(6, 0, ids.ids)]
            if len(ids) == 1:
                obj.kw_checkbox_cash_register_id = ids[0].id

    @api.constrains(
        'kw_checkbox_is_register_receipt', 'kw_checkbox_cashier_id',
        'kw_checkbox_cash_register_id', )
    def constrains_checkbox_fields(self):
        for obj in self:
            if obj.kw_checkbox_is_register_receipt and not \
                    obj.journal_id.kw_checkbox_is_register_receipt:
                raise exceptions.ValidationError(
                    _('This journal payment cant be registered as checkbox '
                      'receipt'))

    def _create_payment_vals_from_wizard(self):
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'kw_checkbox_is_register_receipt':
                self.kw_checkbox_is_register_receipt,
            'kw_checkbox_cashier_id': self.kw_checkbox_cashier_id.id,
            'kw_checkbox_invoice_id': self.kw_checkbox_invoice_id.id,
            'kw_checkbox_cash_register_id':
                self.kw_checkbox_cash_register_id.id
        }

        if not self.currency_id.is_zero(self.payment_difference) \
                and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        return payment_vals

    def _create_payment_vals_from_batch(self, batch_result):
        batch_values = self._get_wizard_values_from_batch(batch_result)
        return {
            'date': self.payment_date,
            'amount': batch_values['source_amount_currency'],
            'payment_type': batch_values['payment_type'],
            'partner_type': batch_values['partner_type'],
            'ref': self._get_batch_communication(batch_result),
            'journal_id': self.journal_id.id,
            'currency_id': batch_values['source_currency_id'],
            'partner_id': batch_values['partner_id'],
            'partner_bank_id': batch_result['key_values']['partner_bank_id'],
            'payment_method_id': self.payment_method_id.id,
            'destination_account_id': batch_result['lines'][0].account_id.id,
            'kw_checkbox_is_register_receipt':
                self.kw_checkbox_is_register_receipt,
            'kw_checkbox_cashier_id': self.kw_checkbox_cashier_id.id,
            'kw_checkbox_invoice_id': self.kw_checkbox_invoice_id.id,
            'kw_checkbox_cash_register_id':
                self.kw_checkbox_cash_register_id.id
        }
