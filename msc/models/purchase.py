# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    #
    #
    #
    def action_print_label_wizard(self):
        self.ensure_one()
        return self.env['msc.wizard.print_product_label'].create_and_show(self)

