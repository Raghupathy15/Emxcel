# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vehicle_log_service_id = fields.Many2one(
        'fleet.vehicle.log.services', 'Service Log')
    purchase_request_id = fields.Many2one(
        'purchase.request', string="PR Reference")


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    spare_part_id = fields.Many2one('fleet.spare.part', string='Spare Part')
    spare_part_purchase_request_id = fields.Many2one(
        'spare_part.purchase.request', string='PR Spare Part')
