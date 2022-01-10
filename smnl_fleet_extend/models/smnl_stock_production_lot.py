# -*- coding: utf-8 -*-


from odoo import api, fields, models, _


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    name = fields.Char(
        'Chassis Number',
        default=lambda self: self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        required=True, help="Unique Lot/Serial Number/Chassis Number")
    engine_no = fields.Char('Engine Number')
    reg_no = fields.Char('Registration Number')
    fleet_id = fields.Many2one("fleet.vehicle", "Fleet Model", ondelete='cascade')

    _sql_constraints = [
        ('check_lot_vehicle_registration_number', 'unique (reg_no)',
         "Please enter unique vehicle registration number!!!"),
        ('check_lot_vehicle_engine_number', 'unique (engine_no)',
         "Please enter unique vehicle engine number!!!")
    ]
