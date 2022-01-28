

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class CheckboxAccountJournal(models.Model):
    _inherit = 'account.journal'

    kw_checkbox_is_register_receipt = fields.Boolean(
        default=False, string='Register Checkbox receipt')
    kw_checkbox_organization_id = fields.Many2one(
        comodel_name='kw.checkbox.organization', string='Organization', )
