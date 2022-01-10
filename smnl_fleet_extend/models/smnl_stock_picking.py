# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.date_done:
                for stock_move in rec.move_ids_without_package:
                    if stock_move.product_id.is_fleet:
                        for move_line in stock_move.move_line_ids:
                            if not move_line.fleet_id and move_line.qty_done == 1:
                                if stock_move.purchase_line_id.price_total != 0 and stock_move.purchase_line_id.product_qty != 0:
                                    purchase_price = stock_move.purchase_line_id.price_total / stock_move.purchase_line_id.product_qty
                                else:
                                    purchase_price = 0
                                fleet = self.env['fleet.vehicle'].create({'purchase_id': rec.purchase_id.id or False,
                                                                          'purchase_line_id': stock_move.created_purchase_line_id.id,
                                                                          'vin_sn': move_line.lot_name,
                                                                          'purchase_shop': rec.partner_id.id or False,
                                                                          'model_id': move_line.product_id.fleet_model_id.id,
                                                                          'product_id': move_line.product_id.id,
                                                                          'image_medium': move_line.product_id.image_medium,
                                                                          'purchase_date': fields.Date.today(),
                                                                          'bill_number': rec.origin,
                                                                          'purchase_price': purchase_price,
                                                                          'warranty_expiry_date': stock_move.purchase_line_id.warranty_expiry_date,
                                                                          'stock_move_id': stock_move.id,
                                                                          'stock_move_line_id': move_line.id,
                                                                          'engine_number': move_line.engine_no,
                                                                          'registration_number': move_line.reg_no,
                                                                          'state_id': int(
                                                                              self.env['fleet.vehicle.state'].search(
                                                                                  [('draft_state', '=', True)]))
                                                                          })
                                move_line.lot_id.write({'engine_no': move_line.engine_no,
                                                        'reg_no': move_line.reg_no,
                                                        'fleet_id': fleet.id,
                                                        })

                                move_line.write({'fleet_id': fleet.id})

        for stock_picking in self:
            if stock_picking.move_ids_without_package.is_expire == True:
                for line in stock_picking.move_ids_without_package.move_line_ids:
                    stock_quant = self.env['stock.quant'].search([('lot_id.name','=',line.lot_name)])
                    if stock_quant:
                        stock_quant.write({'is_expire': True,'expiry_date':stock_picking.move_ids_without_package.expiry_date})
        return res