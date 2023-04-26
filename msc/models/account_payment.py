from odoo import models
from odoo.tools import float_round

from odoo.addons.kw_checkbox_invoice_to_receipt.models.account_payment import AccountPayment as KWAccountPayment


class MSCAccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        """ Override to switch off amount value check

        :return:
        """
        for obj in self:
            if not obj.kw_checkbox_is_register_receipt:
                continue

            checkbox = obj.kw_checkbox_cashier_id.get_checkbox()
            if not checkbox:
                continue

            # if obj.amount != obj.kw_checkbox_invoice_id.amount_total:
            #     raise exceptions.UserError(
            #         _('Checkbox: Payment amount can not be different than '
            #           'total amount'))

            goods = obj.get_payment_goods()
            receipt = self.env['kw.checkbox.receipt'].sell(
                cashier_id=obj.kw_checkbox_cashier_id,
                cash_register_id=obj.kw_checkbox_cash_register_id,
                payload=goods, )
            receipt.invoice_id = obj.kw_checkbox_invoice_id.id
            receipt.payment_id = obj.id
            receipt.wait_receipt_done(obj.kw_checkbox_cashier_id.access_token)
            receipt.update_info()

        return super(KWAccountPayment, self).action_post()

    def get_payment_goods(self):
        self.ensure_one()

        uah = self.env.ref('base.UAH')
        currency = self.kw_checkbox_invoice_id.currency_id
        transfer_commission = (
            self.journal_id and
            self.journal_id.bank_account_id and
            self.journal_id.bank_account_id.transfer_commission
            or 0.0
        )

        data = {'goods': []}

        for line in self.kw_checkbox_invoice_id.invoice_line_ids:
            if not line.quantity:
                continue

            uktzed = line.product_id.product_tmpl_id.kw_checkbox_uktzed
            uktzed = 'UKTZED {}'.format(uktzed) if uktzed else ''

            price = float_round(line.price_subtotal / line.quantity, precision_rounding=currency.rounding)
            if currency != uah:
                price = float_round(currency.compute(price, uah), precision_rounding=uah.rounding)
            price = float_round(price / (1 - transfer_commission), precision_rounding=uah.rounding)
            price = float_round(price * 100.0, precision_digits=0)

            data['goods'].append({
                'quantity': line.quantity * 1000,
                'is_return': line.move_id.move_type == 'out_refund',
                'good': {
                    'code': line.product_id.id,
                    'name': line.product_id.name,
                    'excise_barcodes': [x.name for x in line.kw_checkbox_excise_barcode_ids],
                    'tax': line.tax_ids.mapped('kw_checkbox_tax_ids').mapped('code'),
                    'uktzed': uktzed,
                    'price': price,
                },
            })

        if self.journal_id.type == 'cash':
            data['payments'] = [{
                'type': 'CASH',
                'value': float_round(self.amount * 100, precision_digits=0),
                'label': 'Готівка',
            }]
        else:
            data['payments'] = [{
                'type': 'CASHLESS',
                'value': float_round(self.amount * 100, precision_digits=0),
                'label': 'Безготівковий розрахунок',
            }]

        return data


        def _to_uah(value):
            if self.kw_checkbox_invoice_id.currency_id != uah:
                value = float_round(self.kw_checkbox_invoice_id.currency_id.compute(value / 100.0, uah), precision_rounding=uah.rounding)
            value = float_round(value / (1 - transfer_commission), precision_rounding=uah.rounding)
            return float_round(value * 100.0, precision_digits=0)

        if self.kw_checkbox_invoice_id.currency_id != uah:
            for item in data['goods']:
                item['good']['price'] = _to_uah(item['good']['price'])
            for item in data['discounts']:
                item['value'] = _to_uah(item['value'])

        return data
