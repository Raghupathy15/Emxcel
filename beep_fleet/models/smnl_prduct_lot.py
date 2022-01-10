# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    product_sequence = fields.Integer("Product Sequence")

    @api.model
    def create(self, vals):
        product = self.env['product.product'].browse(vals['product_id'])
        if product.is_spare_part and product.tracking == 'serial':
            if not vals.get('product_sequence') or vals['product_sequence'] == 0:
                product_sequence = self.search([('product_id', '=', vals['product_id'])], order='id desc', limit=1)
                if product_sequence:
                    product_sequence_number = product_sequence.product_sequence+1
                else:
                    product_sequence_number = 0
                vals['product_sequence'] = product_sequence_number
        return super(StockProductionLot, self).create(vals)
