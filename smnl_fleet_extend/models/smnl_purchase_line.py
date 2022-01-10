# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    is_fleet = fields.Boolean("Is Fleet", default=True)
    fleet_type = fields.Many2one('fleet.type', string="Fleet type", related='product_id.fleet_type', store=True, readonly=True)
    warranty_expiry_date = fields.Date("Warranty Expiry Date")

    @api.onchange('is_fleet', 'product_id')
    @api.multi
    def onchange_fleet_order(self):
        for rec in self:
            if rec.product_id.is_fleet:
                rec.is_fleet = True
            if rec.is_fleet:
                return {'domain': {'product_id': [('is_fleet', '=', True)]}}
            else:
                return {'domain': {'product_id': []}}
