# -*- coding: utf-8 -*-


from odoo import api, models, fields, _


class MSCPrintProductLabelWizard(models.TransientModel):
    _name = 'msc.wizard.print_product_label'
    _description = "MSC print product label wizard"

    source_id = fields.Many2one(comodel_name='purchase.order', ondelete='cascade', required=True)

    mode = fields.Selection(selection=[
        ('all', "For all products"),
        ('select', "Select products"),
    ], string="Pint labels mode", required=True, default='all')

    #
    #
    #
    @api.model
    def create_and_show(self, source_id):
        # check wizard params
        assert source_id, "Source is required"
        if isinstance(source_id, models.Model):
            source_id = source_id.id

        wizard = self.create({
            'source_id': source_id,
        })

        # open wizard instance
        return {
            'type': 'ir.actions.act_window',
            'name': _("Print labels for products"),
            'res_model': wizard._name,
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'form_view_initial_mode': 'edit',
            }
        }

    def action_print(self):
        self.ensure_one()

        products = self.source_id.mapped('order_line.product_id')
        action = None
        if self.mode == 'all':
            action = products.action_print_label()
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': _("Products"),
                'res_model': products._name,
                'domain': [('id', 'in', products.ids)],
                'view_mode': 'tree,form',
            }

        return action

