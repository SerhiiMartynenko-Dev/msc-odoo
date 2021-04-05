# -*- coding: utf-8 -*-


from odoo import models, fields


class MSCProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(default='product')


class MSCProductProduct(models.Model):
    _inherit = 'product.product'

    size_value = fields.Char(compute='_compute_size_value')

    #
    #
    #
    def _compute_size_value(self):
        for record in self:
            size = ''

            if record.product_template_attribute_value_ids:
                for av in record.product_template_attribute_value_ids:
                    if av.name and ('size' in av.attribute_id.name.lower() or 'размер' in av.attribute_id.name.lower() or 'розмір' in av.attribute_id.name.lower()):
                        size = av.name
                        break

            record.size_value = size

    #
    #
    #
    def action_print_label(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/report/pdf/%s/%s' % (
                self.env.ref('msc.action_product_label_report').report_name,
                ','.join([str(i) for i in self.ids]),
            )
        }

