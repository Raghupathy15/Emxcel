# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetVehicleModel(models.Model):
    _inherit = "fleet.vehicle.model"

    product_id = fields.Many2one("product.product", string="Product", ondelete='cascade')
    model_name = fields.Char("Vehicle Model", compute='_compute_model_name', store=True)
    fleet_type = fields.Many2one('fleet.type', string='Fleet Type')
    fleet_ids = fields.One2many(related='product_id.fleet_ids', string="Fleet")
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)

    _sql_constraints = [
        ('check_model_name', 'check (1=1)', "Vehicle model already exists !"),
    ]

    @api.depends('name', 'brand_id')
    @api.multi
    def _compute_model_name(self):
        for rec in self:
            rec.model_name = rec.brand_id.name + '/' + rec.name

    @api.model
    def create(self, vals):
        result = super(FleetVehicleModel, self).create(vals)
        product = self.env['product.product'].create({'name': result.display_name,
                                                      'is_fleet': True,
                                                      'type': 'product',
                                                      'tracking': 'serial',
                                                      'fleet_model_id': result.id,
                                                      'image_medium': result.image_medium
                                                      })
        result.product_id = product
        return result
