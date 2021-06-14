# -*- coding: utf-8 -*-


from odoo import api, models, fields


class MSCSaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_stock_cost = fields.Monetary(string="Stock Cost", compute='_compute_amount_stock_cost')

    #
    #
    #
    @api.onchange('order_line')
    @api.depends('order_line.stock_cost')
    def _compute_amount_stock_cost(self):
        for record in self:
            record.amount_stock_cost = sum(record.order_line.mapped('stock_cost'))

    #
    #
    #
    def action_set_discount(self):
        self.ensure_one()
        return self.env['msc.wizard.order_set_discount'].create_and_show(self)

    def action_print_receipt(self):
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
            if invoice.payment_state not in ('in_payment', 'paid'):
                self.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=invoice.ids
                ).create({})._create_payments()

        return self.invoice_ids[0].action_print_receipt()


class MSCSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(digits='Decimal Precision for Discount Percentage for Sales Order')
    discount_price = fields.Monetary(string="Discount Price",
                                     compute='_compute_discount_price',
                                     readonly=False)

    stock_cost = fields.Monetary(related='product_id.stock_cost', store=True)

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

    @api.depends('product_id.stock_cost')
    def _compute_purchase_price(self):
        for record in self:
            record.purchase_price = record.stock_cost or record.product_id.standard_price

