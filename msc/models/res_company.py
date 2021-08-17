# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCResCompany(models.Model):
    _inherit = 'res.company'

    msc_color_attribute = fields.Many2one(comodel_name='product.attribute', ondelete='set null')

