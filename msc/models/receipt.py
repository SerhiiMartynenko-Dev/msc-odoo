from odoo import api, models, fields

from odoo.addons.kw_checkbox.models.checkbox import CheckBoxApi


class CheckboxReceipts(models.Model):
    _inherit = 'kw.checkbox.receipt'

    png_url = fields.Char(compute='_compute_url', string="PNG url")

    @api.depends('name', 'fiscal_date', 'cb_id')
    def _compute_url(self):
        super()._compute_url()
        checkbox = CheckBoxApi(test_mode=self.company_id.kw_checkbox_mode != 'prod')

        for record in self:
            record.png_url = checkbox.get_url('/receipts/%s/png?paper_width=%s' % (record.cb_id, self.env.company.msc_receipt_width))

