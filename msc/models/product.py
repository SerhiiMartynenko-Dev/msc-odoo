# -*- coding: utf-8 -*-


from odoo import models, fields


class MSCProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(default='product')

