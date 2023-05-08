# -*- coding: utf-8 -*-


from odoo import api, models, fields, _
from odoo.exceptions import UserError


class MSCSaleOrder(models.Model):
    _inherit = 'sale.order'

    total_units = fields.Float(string="Total Units", digits='Product Unit of Measure', compute='_compute_total_units')
    amount_stock_cost = fields.Monetary(string="Total Stock Cost", compute='_compute_amount_stock_cost')
    margin = fields.Monetary(copy=False)
    margin_percent = fields.Float(copy=False)

    invoice_paid = fields.Boolean(
        compute='_compute_invoice_paid',
    )

    #
    #
    #
    @api.onchange('order_line')
    @api.depends('order_line.product_uom_qty')
    def _compute_total_units(self):
        for record in self:
            record.total_units = sum(record.order_line.mapped('product_uom_qty'))

    @api.onchange('order_line')
    @api.depends('order_line.stock_cost', 'order_line.product_uom_qty')
    def _compute_amount_stock_cost(self):
        for record in self:
            record.amount_stock_cost = sum([r.stock_cost * r.product_uom_qty for r in record.order_line])

    def _compute_invoice_paid(self):
        for record in self:
            record.invoice_paid = record.invoice_ids and all([r.payment_state in ('paid', 'in_payment') for r in record.invoice_ids])

    #
    #
    #
    def action_set_discount(self):
        self.ensure_one()
        return self.env['msc.wizard.order_set_discount'].create_and_show(self)

    def action_print_receipt_regular_customer(self):
        # check settings
        sale_team = self.env.company and self.env.company.msc_default_sale_team_id
        if not sale_team:
            raise UserError(_("Default sales team not defined in the settings!"))

        if not sale_team.nonfiscal_journal_id:
            raise UserError(_("Non-Fiscal operations journal not defined for sales team!"))

        # prepare invoice
        self._msc_get_invoice()

        # just create payment
        model_payment_register = self.env['account.payment.register']
        if not self.user_has_groups('account.group_account_invoice'):
            model_payment_register = model_payment_register.sudo()

        for invoice in self.invoice_ids:
            if invoice.payment_state not in ('in_payment', 'paid'):
                model_payment_register.with_context(
                    active_model='account.move',
                    active_id=invoice.id,
                    active_ids=invoice.ids
                ).create({
                    'journal_id': sale_team.nonfiscal_journal_id.id,
                })._create_payments()

        # show receipt
        return self.invoice_ids[0].action_print_receipt()

    def action_print_receipt(self):
        return self.env['msc.wizard.print_receipt'].create_and_show(sale_order=self)

    #
    #
    #
    def _msc_get_invoice(self):
        self.ensure_one()
        if self.state == 'cancel':
            return

        self = self.sudo()
        if self.state in ('draft', 'sent'):
            self.action_confirm()

        if self.picking_ids:
            for picking in self.picking_ids:
                if picking.state in ('draft', 'waiting', 'assigned'):
                    for move in picking.move_lines:
                        if move.quantity_done != move.product_uom_qty:
                            move.quantity_done = move.product_uom_qty
                    picking.button_validate()

        if not self.invoice_ids:
            context = {
                'active_model': 'sale.order',
                'active_ids': [self.id],
                'active_id': self.id,
            }
            self.env['sale.advance.payment.inv'].with_context(context).create({}).create_invoices()
            self.refresh()

        for invoice in self.invoice_ids:
            if invoice.state == 'draft':
                invoice.action_post()

        return self.invoice_ids[0]


class MSCSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(digits='Decimal Precision for Discount Percentage for Sales Order')
    discount_price = fields.Monetary(string="Discount Price",
                                     compute='_compute_discount_price',
                                     readonly=False)

    purchase_price = fields.Float(copy=False)
    stock_cost = fields.Monetary(related='product_id.stock_cost', store=True, copy=False)
    margin = fields.Monetary(copy=False)
    margin_percent = fields.Float(copy=False)

    #
    #
    #
    @api.onchange('discount_price', 'price_unit')
    def _onchange_discount_price(self):
        for record in self:
            if not record._context.get('skip_discount_price_recompute'):
                if record.price_unit:
                    record.discount = (1 - (record.discount_price or 0.0) / record.price_unit) * 100.0

    @api.onchange('discount', 'price_unit')
    @api.depends('discount', 'price_unit')
    def _compute_discount_price(self):
        self = self.with_context(skip_discount_price_recompute=True)
        for record in self:
            record.discount_price = record.price_unit * (1 - (record.discount or 0.0) / 100.0)

    @api.depends('stock_cost', 'product_id.stock_cost', 'product_id.standard_price')
    def _compute_purchase_price(self):
        for record in self:
            record.purchase_price = record.stock_cost or record.product_id.standard_price

    #
    #
    #
    def get_sale_order_line_multiline_description_sale(self, product):
        name = ''

        if product:
            name = product.name
            if product.default_code:
                name = '[%s] %s' % (product.default_code, name)

            color_value = product.color_value
            size_value = product.size_value

            if color_value or size_value:
                if color_value and size_value:
                    name += ' (%s, %s)' % (color_value, size_value)
                else:
                    name += ' (%s)' % (color_value or size_value)

        return name


