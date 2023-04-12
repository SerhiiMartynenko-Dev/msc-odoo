import base64
import logging

from ast import literal_eval
import requests
from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    kw_checkbox_organization_id = fields.Many2one(
        comodel_name='kw.checkbox.organization', )
    kw_checkbox_receipt_id = fields.Many2one(
        comodel_name='kw.checkbox.receipt', string='Receipt', )
    checkbox_check = fields.Char(
        related='kw_checkbox_receipt_id.name', )
    checkbox_qr = fields.Binary(
        compute='_compute_checkbox_qr', )
    is_offline = fields.Boolean(
        default=False)

    def _compute_checkbox_qr(self):
        for obj in self:
            if obj.kw_checkbox_receipt_id:
                obj.checkbox_qr = base64.b64encode(
                    requests.get(obj.kw_checkbox_receipt_id.qr_url).content)
            else:
                obj.checkbox_qr = False

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        receipt = self.env['kw.checkbox.receipt'].browse(
            ui_order.get('kw_checkbox_receipt_id'))
        if receipt:
            res.update({'checkbox_check_ids': [receipt.id],
                        'checkbox_check': receipt.name,
                        'checkbox_qr': receipt.qr_url, })
        return res

    def get_order_goods(self):
        self.ensure_one()
        goods = {'goods': [], 'discounts': [], 'payments': []}
        cash_payment = self.payment_ids.filtered(
            lambda x: x.payment_method_id.is_cash_count)
        bank_payment = self.payment_ids.filtered(
            lambda x: not x.payment_method_id.is_cash_count)
        if cash_payment:
            goods['payments'].append({
                "type": "CASH",
                "value": round(sum([x.amount for x in cash_payment]) * 100),
                "label": 'Готівка',
            })
        if bank_payment:
            goods['payments'].append({
                "type": "CASHLESS",
                "value": round(sum([x.amount for x in bank_payment]) * 100),
                "label": 'Безготівковий розрахунок',
            })
        for line in self.lines:
            if not line.qty:
                continue
            uktzed = \
                'UKTZED {}'.format(
                    line.product_id.product_tmpl_id.kw_checkbox_uktzed) if \
                line.product_id.product_tmpl_id.kw_checkbox_uktzed else ''
            goods['goods'].append({
                'quantity': line.qty * 1000, 'good': {
                    'code': line.product_id.id,
                    'name': line.product_id.name,
                    'tax': line.product_id.taxes_id.mapped(
                        'kw_checkbox_tax_ids').mapped('symbol'),
                    'uktzed': uktzed,
                    'price': (line.price_subtotal_incl / line.qty * 100)}
            })
        return goods

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super(PosOrder, self).create_from_ui(orders)
        for order_id in res:
            order = self.browse(order_id['id'])
            ps = self.env["pos.payment"].search(
                [('pos_order_id', '=', order.id)], limit=1)
            j = False
            if not ps or not ps.payment_method_id or \
                    not ps.payment_method_id.kw_checkbox_is_register_receipt:
                continue
            category = ps.payment_method_id.kw_checkbox_product_category_id
            for checkbox_category in order.config_id.kw_checkbox_category_ids:
                if checkbox_category.kw_checkbox_product_category_id \
                        == category:
                    j = checkbox_category
                    break
            if not j:
                continue
            if not order.kw_checkbox_organization_compare(
                    j.kw_checkbox_organization_id):
                raise ValueError(_(
                    'You cant register payment throw this method'))
            if not order.kw_checkbox_organization_id:
                order.kw_checkbox_organization_id = \
                    j.kw_checkbox_organization_id.id
            goods = order.get_order_goods()
            shift = order.session_id.kw_checkbox_get_shift(
                j.kw_checkbox_organization_id)
            if shift:
                receipt = self.env['kw.checkbox.receipt'].sell(
                    payload=goods, cashier_id=shift.cashier_id,
                    cash_register_id=shift.cash_register_id, )
                receipt.wait_receipt_done()
                receipt.update_info()
                order.kw_checkbox_receipt_id = receipt.id
            else:
                order.is_offline = True
        return res

    def kw_checkbox_organization_compare(self, organization_id):
        self.ensure_one()
        if not self.lines:
            return True
        if not self.kw_checkbox_organization_id:
            return True
        if not organization_id:
            return True
        if organization_id.id == self.kw_checkbox_organization_id.id:
            return True
        return False

    def checkbox_refund(self):
        self.ensure_one()
        res_val = self.kw_checkbox_receipt_id.res_val
        if res_val:
            cashier_id = self.kw_checkbox_receipt_id.cashier_id
            cash_register_id = self.kw_checkbox_receipt_id.cash_register_id
            checkbox = cashier_id.get_checkbox()
            checkbox.license_key = cash_register_id.license_key
            d = literal_eval(res_val)
            for obj in d.get('goods'):
                obj['is_return'] = True
            res2 = checkbox.shift()
            res2 = checkbox.receipts_sell(d)
            kw_checkbox_receipt_id = self.env['kw.checkbox.receipt'].create({
                'status': res2['status'],
                'cb_id': res2['id'],
                'type': res2['type'],
                'transaction_cb_id': res2['transaction']['id'],
                'shift_cb_id': res2['shift']['id'],
                'cashier_id': cashier_id.id,
                'cash_register_id': cash_register_id.id,
                'cashier_cb_id': cashier_id.cb_id,
                'res_val': res2,
                'cash_register_cb_id': cash_register_id.cb_id
            })
            kw_checkbox_receipt_id.wait_receipt_done()
            kw_checkbox_receipt_id.update_info()
            self.kw_checkbox_receipt_id = kw_checkbox_receipt_id.id

    def checkbox_sell_offline(self):
        _logger.info('checkbox_sell_offline')
        self.ensure_one()
        if self.kw_checkbox_organization_id:
            cash_register_id = self.env['kw.checkbox.cash.register'].search([
                ('organization_id', '=',
                 self.kw_checkbox_organization_id.id)], limit=1)
            cashier_id = self.env['kw.checkbox.cashier'].search([
                ('organization_id', '=',
                 self.kw_checkbox_organization_id.id)], limit=1)
            goods = self.get_order_goods()
            offline_code = self.env['kw.checkbox.offline.code'].search([
                ('cash_register_id', '=', cash_register_id.id)], limit=1)
            if offline_code:
                goods['fiscal_code'] = offline_code.fiscal_code
                goods['fiscal_date'] = \
                    offline_code.datetime_created_at.strftime(
                        "%Y-%m-%d %H:%M:%S")
                receipt = self.env['kw.checkbox.receipt'].sell_offline(
                    payload=goods, cashier_id=cashier_id,
                    cash_register_id=cash_register_id, )
                receipt.wait_receipt_done()
                receipt.update_info()
                self.kw_checkbox_receipt_id = receipt.id
                offline_code.sudo().active = False

    def checkbox_check_and_sell_offline(self):
        self.ensure_one()
        if self.kw_checkbox_organization_id:
            cash_register_id = self.env['kw.checkbox.cash.register'].search([
                ('organization_id', '=',
                 self.kw_checkbox_organization_id.id)], limit=1)
            if not cash_register_id.ping_tax_service():
                raise exceptions.ValidationError(_(
                    "You should use offline mode, because CheckBox"
                    " signature turned off"))
            self.checkbox_sell_offline()
