# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SparePartPurchaseRequest(models.Model):
    _name = 'spare_part.purchase.request'
    _rec_name = 'product_tmpl_id'
    _description = 'Spare-part Purchase Request'

    pr_id = fields.Many2one('purchase.request', string='PR Reference')
    spare_part_id = fields.Many2one('fleet.spare.part', string='Spare Part')
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    pr_qty = fields.Float('Quantity')
    vendor_id = fields.Many2one(
        'res.partner', string='Vendor', domain="[('supplier','=',True)]")
    pr_cost = fields.Float('price')
    product_uom_id = fields.Many2one(
        related="product_tmpl_id.uom_id", string="Unit of Measure")
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line', string="Purchase Order Line Reference")
