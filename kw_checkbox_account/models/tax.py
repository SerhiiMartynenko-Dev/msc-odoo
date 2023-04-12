import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class CheckboxTax(models.Model):
    _inherit = 'kw.checkbox.tax'

    account_tax_id = fields.Many2many(
        comodel_name='account.tax', )
