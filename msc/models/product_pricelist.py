# -*- coding: utf-8 -*-


import ast

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class MSCPricelist(models.Model):
    _inherit = 'product.pricelist'

    #
    #
    #
    def action_add_item(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Add Price List Item"),
            'res_model': 'product.pricelist.item',
            'view_mode': 'form',
            'view_id': self.env.ref('msc.product_pricelist_item_form_view').id,
            'target': 'new',
            'context': {
                'msc_product_domain': True,
                'form_view_initial_mode': 'edit',
                'default_pricelist_id': self.id,
                'default_applied_on': '0_product_variant',
            }
        }


class MSCPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    product_domain = fields.Char(string="Product Domain")

    #
    #
    #
    @api.model
    def create(self, values):
        if self._context.get('msc_product_domain'):
            domain = values.get('product_domain')
            if not domain or domain == '[]':
                raise ValidationError(_("Product domain value not defined"))

            domain = ast.literal_eval(domain)

            products = self.env['product.product'].search(domain)
            if not products:
                raise ValidationError(_("No any products found for specified domain"))

            for product in products:
                items = self.browse()

                new_values = dict(values)
                new_values['applied_on'] = '0_product_variant'
                new_values['product_id'] = product.id

                items += super().create(new_values)

            return items[0]

        return super().create(values)

    #
    #
    #
    def action_save(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

