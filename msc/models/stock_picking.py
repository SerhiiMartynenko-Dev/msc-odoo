# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCStockPicking(models.Model):
    _inherit = 'stock.picking'

    total_demand = fields.Float(string="Total Demand", digits='Product Unit of Measure', compute='_compute_totals')
    total_done = fields.Float(string="Total Done", digits='Product Unit of Measure', compute='_compute_totals')

    #
    #
    #
    def _compute_totals(self):
        for record in self:
            record.total_demand = sum(record.move_lines.mapped('product_uom_qty'))
            record.total_done = sum(record.move_lines.mapped('quantity_done'))
