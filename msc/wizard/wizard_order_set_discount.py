# -*- coding: utf-8 -*-


from odoo import api, models, fields, _


class MSCSaleOrderSetDiscountWizard(models.TransientModel):
    _name = 'msc.wizard.order_set_discount'
    _description = "MSC set discount on sale order wizard"

    order_id = fields.Many2one(comodel_name='sale.order', ondelete='cascade', required=True)

    discount = fields.Float(string="Discount", default=0)

    #
    #
    #
    @api.model
    def create_and_show(self, order_id):
        if isinstance(order_id, models.Model):
            order_id = order_id.id

        wizard = self.create({
            'order_id': order_id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _("Set sale order discount"),
            'res_model': wizard._name,
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'dialog_size': 'small',
                'form_view_initial_mode': 'edit',
            }
        }

    def action_confirm(self):
        self.ensure_one()

        self.order_id.order_line.write({
            'discount': self.discount * 100.0,
        })

        # remove wizard
        self.unlink()

