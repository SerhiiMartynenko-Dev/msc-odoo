from odoo import api, models, fields


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    def _default_fiscal_journal_id(self):
        return self.env['account.journal'].search([('kw_checkbox_is_register_receipt', '=', True)], limit=1)

    def _default_fiscal_checkbox_cashier_id(self):
        return self.env['kw.checkbox.cashier'].search([], limit=1)

    def _default_fiscal_checkbox_cash_register_id(self):
        return self.env['kw.checkbox.cash.register'].search([], limit=1)

    nonfiscal_journal_id = fields.Many2one(
        comodel_name='account.journal',
        domain="[('kw_checkbox_is_register_receipt', '=', False)]",
        string="Non fiscal operations journal",
    )
    fiscal_journal_id = fields.Many2one(
        comodel_name='account.journal',
        domain="[('kw_checkbox_is_register_receipt', '=', True)]",
        default=lambda self: self._default_fiscal_journal_id(),
        string="Fiscal operations journal",
    )
    fiscal_checkbox_cashier_id = fields.Many2one(
        comodel_name='kw.checkbox.cashier',
        ondelete='restrict',
        default=lambda self: self._default_fiscal_checkbox_cashier_id(),
        string="Cashier",
    )
    fiscal_checkbox_cash_register_id = fields.Many2one(
        comodel_name='kw.checkbox.cash.register',
        ondelete='restrict',
        default=lambda self: self._default_fiscal_checkbox_cash_register_id(),
        string="Cash register",
    )

