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


class MSCPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    #
    #
    #
    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()

        name = product_lang.name
        if product_lang.default_code:
            name = '[%s] %s' % (product_lang.default_code, name)

        color_value = product_lang.color_value
        size_value = product_lang.size_value

        if color_value or size_value:
            if color_value and size_value:
                name += ' (%s, %s)' % (color_value, size_value)
            else:
                name += ' (%s)' % (color_value or size_value)

        return name


