# -*- coding: utf-8 -*-


from odoo import api, models, fields


def _ean13_checksum(ean):
    """ Code copy from barcode module

    :param ean:
    :return:
    """
    code = list(ean)
    if len(code) != 12:
        return -1

    oddsum = evensum = total = 0
    for i in range(len(code)):
        if i % 2 == 0:
            evensum += int(code[i])
        else:
            oddsum += int(code[i])
    total = oddsum * 3 + evensum
    return int((10 - total % 10) % 10)


class MSCProductTemplate(models.Model):
    _inherit = 'product.template'

    type = fields.Selection(default='product')

    stock_cost = fields.Monetary(string="Stock Cost", compute='_compute_stock_cost')

    #
    #
    #
    def _compute_stock_cost(self):
        model_move = self.env['stock.move'].sudo()
        model_valuation = self.env['stock.valuation.layer'].sudo()

        for record in self:
            # find last incoming move
            move = model_move.search([
                ('location_id.usage', '=', 'supplier'),
                ('product_id.product_tmpl_id', '=', record.id),
                ('state', '=', 'done'),
            ], order='sequence desc, id desc', limit=1)

            if move:
                valuations = model_valuation.search([('stock_move_id', '=', move.id)])
                amount = sum(valuations.mapped('value'))
                quantity = sum(valuations.mapped('quantity'))
                record.stock_cost = (amount or 0) / (quantity or 1)

            else:
                record.stock_cost = 0


class MSCProductProduct(models.Model):
    _inherit = 'product.product'

    barcode = fields.Char(readonly=True)
    size_value = fields.Char(compute='_compute_size_value')

    stock_cost = fields.Monetary(string="Stock Cost", compute='_compute_stock_cost')

    #
    #
    #
    def _compute_size_value(self):
        for record in self:
            size = ''

            if record.product_template_attribute_value_ids:
                for av in record.product_template_attribute_value_ids:
                    if av.name and ('size' in av.attribute_id.name.lower() or 'размер' in av.attribute_id.name.lower() or 'розмір' in av.attribute_id.name.lower()):
                        size = av.name
                        break

            record.size_value = size

    def _compute_stock_cost(self):
        model_move = self.env['stock.move'].sudo()
        model_valuation = self.env['stock.valuation.layer'].sudo()

        for record in self:
            # find last incoming move
            move = model_move.search([
                ('location_id.usage', '=', 'supplier'),
                ('product_id', '=', record.id),
                ('state', '=', 'done'),
            ], order='sequence desc, id desc', limit=1)

            if move:
                valuations = model_valuation.search([('stock_move_id', '=', move.id)])
                amount = sum(valuations.mapped('value'))
                quantity = sum(valuations.mapped('quantity'))
                record.stock_cost = (amount or 0) / (quantity or 1)

            else:
                record.stock_cost = 0


    #
    #
    #
    @api.model
    def create(self, values):
        new_record = super().create(values)

        # create unique barcode
        new_record.with_context(set_barcode=True).barcode = new_record._create_barcode()

        return new_record

    def write(self, values):
        values = values or {}
        if not self._context.get('set_barcode') and 'barcode' in values:
            values.pop('barcode')

        return super().write(values)

    def _create_barcode(self):
        self.ensure_one()
        code = '27%010d' % self.id
        return '%s%s' % (code, _ean13_checksum(code))

    #
    #
    #
    def action_print_label(self):
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': '/report/pdf/%s/%s' % (
                self.env.ref('msc.action_product_label_report').report_name,
                ','.join([str(i) for i in self.ids]),
            )
        }

