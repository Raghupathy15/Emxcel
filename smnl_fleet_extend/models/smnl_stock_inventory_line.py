# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    fleet_id = fields.Many2one("fleet.vehicle", "Fleet Model", ondelete='cascade')
    fleet_chassis_id = fields.Many2one('stock.production.lot', 'Chassis Number',
                                       domain="[('product_id','=',product_id)]")
    engine_no = fields.Char('Engine Number')
    reg_no = fields.Char('Registration Number')
    is_fleet = fields.Boolean(related='product_id.is_fleet', string="Is Fleet", store=True, readonly=False)

    _sql_constraints = [
        ('check_inventory_line_vehicle_registration_number', 'CHECK(1=1)',
         "Please enter unique vehicle registration number!!!"),
        ('check_inventory_line_vehicle_engine_number', 'CHECK(1=1)',
         "Please enter unique vehicle engine number!!!")
    ]

    @api.onchange('prod_lot_id', 'fleet_chassis_id', 'product_qty')
    @api.multi
    def check_prod_lot_qty(self):
        for rec in self:
            if rec.product_id.is_fleet:
                if rec.prod_lot_id != rec.fleet_chassis_id:
                    rec.prod_lot_id = rec.fleet_chassis_id
            else:
                rec.fleet_chassis_id = rec.prod_lot_id
            if rec.product_id.is_fleet:
                rec.product_qty = 1.0
                if rec.product_qty != 1.0:
                    raise UserError(_("Real quantity should be 1."))
