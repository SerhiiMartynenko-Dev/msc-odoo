# -*- coding: utf-8 -*-


from odoo import models, fields


class MSCStockLandedCostLine(models.Model):
    _inherit = 'stock.landed.cost.lines'

    split_method = fields.Selection(default='by_current_cost_price')

