from odoo import api, models, fields


class InventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    cost_method = fields.Selection(related='product_id.categ_id.property_cost_method')
    stock_valuation_cost = fields.Monetary(string="Total Amount", compute='_compute_stock_valuation_cost')
    currency_id = fields.Many2one(related='inventory_id.company_id.currency_id')

    def _compute_stock_valuation_cost(self):
        model_valuation = self.env['stock.valuation.layer'].sudo()
        for record in self:
            record.stock_valuation_cost = sum(model_valuation.search([('product_id', '=', record.product_id.id)]).mapped('value'))

    def action_revaluation(self):
        self.ensure_one()
        return self.product_id.action_revaluation()

