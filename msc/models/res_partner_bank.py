from odoo import api, models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    transfer_commission = fields.Float(
        string="Transfer commission",
        default=0.0,
    )
    transfer_commission_account_id = fields.Many2one(
        comodel_name='account.account',
        ondelete='restrict',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        string="Commission account",
    )

