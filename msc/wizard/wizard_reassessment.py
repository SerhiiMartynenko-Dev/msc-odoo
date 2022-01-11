# -*- coding: utf-8 -*-


import ast

from odoo import api, models, fields, tools, _
from odoo.exceptions import ValidationError, UserError


class MSCReassessmentWizard(models.TransientModel):
    _name = 'msc.wizard.reassessment'
    _description = "MSC reassessment wizard"

    product_domain = fields.Char(string="Product Domain", required=True)

    mode = fields.Selection(selection=[
        ('percent', "Percent")
    ], required=True, default='percent', string="Mode")
    value = fields.Float(string="Value", required=True, default=100)

    #
    #
    #
    @api.onchange('mode')
    def _onchange_mode(self):
        for record in self:
            if record.mode == 'percent':
                record.value = 100

    #
    #
    #
    @api.model
    def create_and_show(self):
        if self.env.user.has_group('msc.group_msc_sale_user'):
            raise UserError(_("Not allowed"))

        return {
            'type': 'ir.actions.act_window',
            'name': _("Reassessment"),
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'edit',
            }
        }

    def action_confirm(self):
        self.ensure_one()

        domain = self.product_domain
        if not domain:
            raise ValidationError(_("Product domain value not defined"))

        domain = ast.literal_eval(domain)

        products = self.env['product.product'].search(domain)
        if not products:
            raise ValidationError(_("No any products found for specified domain"))

        product_templates = products.mapped('product_tmpl_id')
        for product_template in product_templates:
            # @TODO
            if self.mode == 'percent':
                product_template.list_price = tools.float_round(product_template.list_price * self.value / 100.0, precision_digits=0)

        # remove wizard
        self.unlink()

