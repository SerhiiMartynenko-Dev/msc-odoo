# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


#
#
#
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_tag_ids = fields.Many2many(comodel_name='product.tag',
                                       relation='product_template_product_tag_rel',
                                       column1='product_id', column2='tag_id',
                                       string="Tags")

    @api.model
    def create(self, values):
        new_record = super().create(values)

        if new_record.product_tag_ids:
            product_tag_ids = set(new_record.product_tag_ids.ids)

            for variant in new_record.product_variant_ids:
                if not variant.product_tag_ids or product_tag_ids != set(variant.product_tag_ids.ids):
                    variant.write({
                        'product_tag_ids': [(6, 0, new_record.product_tag_ids.ids)]
                    })

        return new_record


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_tag_ids = fields.Many2many(comodel_name='product.tag',
                                       relation='product_product_product_tag_rel',
                                       column1='product_id', column2='tag_id',
                                       string="Tags")

    @api.model
    def create(self, values):
        new_record = super().create(values)

        if new_record.product_tmpl_id.product_tag_ids:
            new_record.write({
                'product_tag_ids': [(6, 0, new_record.product_tmpl_id.product_tag_ids.ids)]
            })

        return new_record


#
#
#
class ProductTag(models.Model):
    _name = 'product.tag'
    _description = "Product Tag"
    _order = 'name, id'

    name = fields.Char(string="Name", required=True, index=True, translate=True)
    active = fields.Boolean(string="Active", default=True)

