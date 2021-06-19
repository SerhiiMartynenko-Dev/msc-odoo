# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_units = fields.Float(string="Total Units", digits='Product Unit of Measure', compute='_compute_total_units')

    #
    #
    #
    @api.onchange('order_line')
    @api.depends('order_line.product_uom_qty')
    def _compute_total_units(self):
        for record in self:
            record.total_units = sum(record.order_line.mapped('product_uom_qty'))

    #
    #
    #
    def action_print_label_wizard(self):
        self.ensure_one()
        return self.env['msc.wizard.print_product_label'].create_and_show(self)

