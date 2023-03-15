import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class CheckboxReceipts(models.Model):
    _inherit = 'kw.checkbox.receipt'

    invoice_id = fields.Many2one(
        comodel_name='account.move', )
    payment_id = fields.Many2one(
        comodel_name='account.payment', )
