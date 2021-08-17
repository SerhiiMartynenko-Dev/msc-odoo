# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    msc_color_attribute = fields.Many2one(related='company_id.msc_color_attribute', readonly=False)

