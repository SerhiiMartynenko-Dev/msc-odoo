# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    msc_color_attribute = fields.Many2one(related='company_id.msc_color_attribute', readonly=False)

    msc_default_sale_team_id = fields.Many2one(
        related='company_id.msc_default_sale_team_id',
        readonly=False,
    )
