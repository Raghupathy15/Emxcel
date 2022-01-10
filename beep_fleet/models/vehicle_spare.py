# -*- coding: utf-8 -*-

from odoo import models, fields


class SmnlVehicleSpareParts(models.Model):
    _name = "vehicle.spare.parts"
    _description = 'Smnl Vehicle Spare Parts'

    product_id = fields.Many2one('product.template', string="Product")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    service_id = fields.Many2one(
        'fleet.vehicle.log.services', string="Service")
    name = fields.Char(string="Chassis Number")
