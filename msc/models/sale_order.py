# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(digits='Decimal Precision for Discount Percentage for Sales Order')
    discount_price = fields.Monetary(string="Discount Price",
                                     compute='_compute_discount_price',
                                     readonly=False)

    #
    #
    #
    @api.onchange('discount_price', 'price_unit')
    def _onchange_discount_price(self):
        for record in self:
            if not record._context.get('skip_discount_price_recompute'):
                if record.price_unit:
                    record.discount = (1 - (record.discount_price or 0.0) / record.price_unit) * 100.0

    @api.onchange('discount', 'price_unit')
    @api.depends('discount', 'price_unit')
    def _compute_discount_price(self):
        self = self.with_context(skip_discount_price_recompute=True)
        for record in self:
            record.discount_price = record.price_unit * (1 - (record.discount or 0.0) / 100.0)

