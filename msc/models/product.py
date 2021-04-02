# -*- coding: utf-8 -*-


from odoo import models, fields


class MSCProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(default='product')


class MSCProductProduct(models.Model):
    _inherit = 'product.product'

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

