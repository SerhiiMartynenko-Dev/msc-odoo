# -*- coding: utf-8 -*-


from odoo import api, models, fields, _
from odoo.exceptions import UserError


class MSCAccountMove(models.Model):
    _inherit = 'account.move'

    date_paid = fields.Datetime(string="Paid Date", compute='_compute_date_paid')

    #
    #
    #
    @api.depends('payment_state')
    def _compute_date_paid(self):
        for record in self:
            date_paid = None
            if record.payment_state == 'paid':
                payment_info = record._get_reconciled_invoices_partials()
                if payment_info and len(payment_info[0]) > 2:
                    payment_info = payment_info[0][2]
                    if payment_info and payment_info.payment_id:
                        date_paid = payment_info.payment_id.create_date

            record.date_paid = date_paid

    #
    #
    #
    def action_print_receipt(self):
        self.ensure_one()
        if self.move_type != 'out_invoice' or self.payment_state != 'paid':
            raise UserError(_("Receipt not paid yet"))
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/report/pdf/%s/%s' % (
                self.env.ref('msc.report_product_label').report_name,
                self.id,
            )
        }

