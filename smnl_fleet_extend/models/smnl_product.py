# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_fleet = fields.Boolean("Is Fleet")
    fleet_model_id = fields.Many2one("fleet.vehicle.model", "Fleet Model", ondelete='cascade')
    fleet_type = fields.Many2one('fleet.type', string="Fleet type", related='fleet_model_id.fleet_type', store=True,
                                 readonly=True)
    fleet_ids = fields.One2many("fleet.vehicle", "product_id", string="Fleet")

    @api.onchange("fleet_model_id")
    @api.multi
    def _onchange_fleet_model(self):
        for rec in self:
            if rec.is_fleet:
                if rec.fleet_model_id:
                    rec.name = rec.fleet_model_id.display_name

    # @api.constrains('standard_price', 'lst_price')
    # @api.multi
    # def _check_price(self):
    #     for rec in self:
    #         if rec.standard_price > rec.lst_price:
    #             raise UserError(_("Cost should be less than Sales Price."))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_fleet = fields.Boolean(related='product_variant_id.is_fleet', string="Is Fleet")
    fleet_model_id = fields.Many2one("fleet.vehicle.model", related='product_variant_id.fleet_model_id',
                                     string="Fleet Model")
    fleet_type = fields.Many2one('fleet.type', string="Fleet type", related='product_variant_id.fleet_type')
    fleet_ids = fields.One2many(related="product_variant_id.fleet_ids", string="Fleet")
