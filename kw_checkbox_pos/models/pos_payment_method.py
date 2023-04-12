import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    kw_checkbox_is_register_receipt = fields.Boolean(
        default=False, string='Register Checkbox receipt')
    kw_checkbox_product_category_id = fields.Many2one(
        comodel_name='kw.checkbox.product.category',
        default=lambda self: self.env['kw.checkbox.product.category'].search(
            [('name', '=', 'Default Category')]),
        string='Product Category', required=True, )
