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
        goods = super().get_payment_goods()

        uah = self.env.ref('base.UAH')
        transfer_commission = (
            self.journal_id and
            self.journal_id.bank_account_id and
            self.journal_id.bank_account_id.transfer_commission
            or 0.0
        )

        def _to_uah(value):
            if self.kw_checkbox_invoice_id.currency_id != uah:
                value = float_round(self.kw_checkbox_invoice_id.currency_id.compute(value / 100.0, uah), precision_rounding=uah.rounding)
            value = float_round(value / (1 - transfer_commission), precision_rounding=uah.rounding)
            return float_round(value * 100.0, precision_digits=0)

        if self.kw_checkbox_invoice_id.currency_id != uah:
            for item in goods['goods']:
                item['good']['price'] = _to_uah(item['good']['price'])
            for item in goods['discounts']:
                item['value'] = _to_uah(item['value'])

        return goods
