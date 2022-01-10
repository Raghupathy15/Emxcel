# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def compute_spare_count(self):
        for record in self:
            record.vehicle_spare_count = self.env['vehicle.spare.parts'].search_count(
                [('product_id', '=', self.id)])

    is_spare_part = fields.Boolean("Is Spare-Part")
    vehicle_spare_count = fields.Integer(
        'Spare', compute='compute_spare_count')

    def get_vehicle_spare_parts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Spare Parts',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.spare.parts',
            'domain': [('product_id', '=', self.id)],
            'context': "{'create': False}"
        }


class FleetSparePart(models.Model):
    _name = "fleet.spare.part"
    _description = "Fleet Spare Part"
    _rec_name = 'product_tmpl_id'

    product_tmpl_id = fields.Many2one('product.template', 'Product')
    use_qty = fields.Float('Required Quantity', default=1)
    product_cost = fields.Float(
        related="product_tmpl_id.standard_price", string='Cost')
    qty_available = fields.Float(
        related="product_tmpl_id.qty_available", string='Available Quantity')
    total_cost = fields.Float(string='Total Cost')
    serial_ids = fields.Many2many('stock.production.lot', string='Serial No')
    vehicle_log_service_id = fields.Many2one(
        'fleet.vehicle.log.services', 'Service Log')
    require_po_qty = fields.Float('Request Quantity')
    received_qty = fields.Float(string="Received Qty")
    purchase_id = fields.Many2one('purchase.order', string='PO Reference')
    purchase_request_ids = fields.One2many(
        related='vehicle_log_service_id.spare_part_pr_ids', string="PR Reference")

    @api.onchange('product_tmpl_id')
    @api.multi
    def onchange_product_tmpl_id(self):
        for rec in self:
            rec.use_qty = 1
            rec.total_cost = rec.product_cost * rec.use_qty

    @api.constrains('use_qty')
    @api.onchange('use_qty')
    @api.multi
    def check_product_qty(self):
        for rec in self:
            if rec.product_tmpl_id:
                if rec.use_qty < 1:
                    raise UserError(_("You can't 0 or negative quantity."))
                rec.total_cost = rec.product_cost * rec.use_qty

    @api.onchange('use_qty', 'product_tmpl_id')
    @api.multi
    def onchange_product_qty(self):
        for rec in self:
            if rec.product_tmpl_id:
                if rec.use_qty > rec.qty_available:
                    rec.require_po_qty = rec.use_qty - rec.qty_available
                else:
                    rec.require_po_qty = 0.0

    @api.multi
    def spare_part_po_generated(self):
        for rec in self:
            if rec.require_po_qty > 0:
                if not rec.product_tmpl_id.product_variant_id.seller_ids:
                    raise UserError(_("Kindly set the vendor in product..."))

                seller_partner = False
                for seller in rec.product_tmpl_id.product_variant_id.seller_ids:
                    seller_partner = self.env['res.partner'].search(
                        [('id', '=', seller.name.id)])

                purchase_order = self.env['purchase.order'].create({
                    'partner_id': seller_partner.id,
                    'vehicle_log_service_id': rec.vehicle_log_service_id.id,
                    'order_line': [(0, 0, {
                        'is_fleet': False,
                        'product_id': rec.product_tmpl_id.product_variant_id.id,
                        'name': rec.product_tmpl_id.product_variant_id.name or " ",
                        'spare_part_id': rec.id,
                        'product_qty': rec.require_po_qty,
                        'price_unit': rec.product_tmpl_id.product_variant_id.standard_price,
                        'date_planned': fields.Date.today(),
                        'product_uom': self.env['uom.uom'].search([('name', '=', 'Unit(s)')]).id
                    })]
                })
                # Avoid confirm the PO
                # purchase_order.button_confirm()
                rec.purchase_id = purchase_order
                if rec.vehicle_log_service_id.state != 'sp_request':
                    rec.vehicle_log_service_id.write({'state': 'sp_request'})
                rec.vehicle_log_service_id.message_post(
                    body=_('For the spare-part(%s) RFQ is raised & RFQ number is %s') % (
                        rec.product_tmpl_id.name, purchase_order.name,))
