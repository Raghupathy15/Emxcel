# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    no_of_spare_part_qty = fields.Integer("Auto Generate Number of Quantity")
    auto_generate_qty_check = fields.Boolean("Auto Generate Quantity Check")

    @api.multi
    def auto_generate_inventory(self):
        for rec in self:
            if rec.filter != 'product' or rec.product_id.tracking != 'serial':
                raise UserError(
                    _("You must select Inventory of One product only and product tracking should be By Unique Serial Number."))
            if rec.auto_generate_qty_check:
                raise UserError(_("Already auto sequence is generated."))

            product_sequence = self.env['stock.production.lot'].search([('product_id', '=', rec.product_id.id)],
                                                                       order='id desc', limit=1)
            if product_sequence:
                product_sequence_number = product_sequence.product_sequence+1
            else:
                product_sequence_number = 0
            for x in range(rec.no_of_spare_part_qty):
                lot_stock_id = self.env['stock.production.lot'].create(
                    {'name': str(rec.product_id.part_number) + '-' + str(rec.product_id.remark) + '-' + str(
                        product_sequence_number + x + 1),
                     'product_id': rec.product_id.id})
                self.env['stock.inventory.line'].create({
                    'product_id': rec.product_id.id,
                    'inventory_id': rec.id,
                    'prod_lot_id': lot_stock_id.id,
                    'product_qty': 1.0,
                    'location_id': rec.location_id.id,
                })
            rec.auto_generate_qty_check = True
