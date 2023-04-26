import logging

from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    kw_checkbox_is_register_receipt = fields.Boolean(
        default=False, string='Register CheckBox receipt')
    kw_checkbox_is_journal_register_receipt = fields.Boolean(
        related='journal_id.kw_checkbox_is_register_receipt')
    kw_checkbox_receipt_id = fields.Many2one(
        comodel_name='kw.checkbox.receipt',
        string='Receipt', )
    kw_checkbox_invoice_id = fields.Many2one(
        comodel_name='account.move', string='Invoice', )
    kw_checkbox_cashier_id = fields.Many2one(
        comodel_name='kw.checkbox.cashier',
        string='Cashier', )
    kw_checkbox_cashier_ids = fields.Many2many(
        comodel_name='kw.checkbox.cashier',
        compute='_compute_kw_checkbox_cashier_ids', )
    kw_checkbox_cash_register_id = fields.Many2one(
        comodel_name='kw.checkbox.cash.register',
        string='Cash register', )
    kw_checkbox_cash_register_ids = fields.Many2many(
        comodel_name='kw.checkbox.cash.register',
        compute='_compute_kw_checkbox_cash_register_ids', )

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

    @api.model
    def default_get(self, field_list):
        rec = super(AccountPayment, self).default_get(field_list)
        invoice_defaults = self.new(
            {'reconciled_invoice_ids': rec.get('reconciled_invoice_ids')}
        ).reconciled_invoice_ids
        if invoice_defaults:
            rec['kw_checkbox_invoice_id'] = invoice_defaults[0].id
        return rec

    def get_payment_goods(self):
        self.ensure_one()
        goods = {'goods': [], 'discounts': [], 'payments': []}
        if self.journal_id.type == 'cash':
            goods['payments'].append({
                "type": "CASH",
                "value": round(self.amount * 100),
                "label": 'Готівка',
            })
        else:
            goods['payments'].append({
                "type": "CASHLESS",
                "value": round(self.amount * 100),
                "label": 'Безготівковий розрахунок',
            })

        for line in self.kw_checkbox_invoice_id.invoice_line_ids:
            sum_tax = round(sum([
                tax.compute_all(line.price_unit)['total_included']
                for tax in line.tax_ids]) * 100) or line.price_unit * 100
            if line.price_unit < 0:
                goods['discounts'].append({
                    "type": "DISCOUNT",
                    "mode": "VALUE",
                    "value": 0 - sum_tax,
                    'tax_codes': line.tax_ids.mapped(
                        'kw_checkbox_tax_ids').mapped('code'),

                })
            if not line.quantity or line.price_unit < 0:
                continue
            uktzed = line.product_id.product_tmpl_id.kw_checkbox_uktzed
            uktzed = 'UKTZED {}'.format(uktzed) if uktzed else ''
            goods['goods'].append({
                'quantity': line.quantity * 1000,
                'is_return': line.move_id.move_type == 'out_refund',
                'good': {
                    'code': line.product_id.id, 'name': line.product_id.name,
                    'excise_barcodes':
                        [x.name for x in line.kw_checkbox_excise_barcode_ids],
                    'tax': line.tax_ids.mapped(
                        'kw_checkbox_tax_ids').mapped('code'),
                    'uktzed': uktzed, 'price': sum_tax, }, })
        return goods

    def action_post(self):
        # _logger.info('post kw_checkbox_is_register_receipt')
        for obj in self:
            if not obj.kw_checkbox_is_register_receipt:
                continue
            checkbox = obj.kw_checkbox_cashier_id.get_checkbox()
            if not checkbox:
                continue
            if obj.amount != obj.kw_checkbox_invoice_id.amount_total:
                raise exceptions.UserError(
                    _('Checkbox: Payment amount can not be different than '
                      'total amount'))
            goods = obj.get_payment_goods()
            receipt = self.env['kw.checkbox.receipt'].sell(
                cashier_id=obj.kw_checkbox_cashier_id,
                cash_register_id=obj.kw_checkbox_cash_register_id,
                payload=goods, )
            receipt.invoice_id = obj.kw_checkbox_invoice_id.id
            receipt.payment_id = obj.id
            receipt.wait_receipt_done(obj.kw_checkbox_cashier_id.access_token)
            receipt.update_info()
        return super(AccountPayment, self).action_post()
