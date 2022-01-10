# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FuelFilling(models.Model):
    _name = "fuel.filling"
    _inherit = ['mail.thread']
    _description = 'Fuel Filling'

    @api.onchange('product_id')
    def onchange_avail_qty(self):
        for record in self:
            qty = self.env['stock.quant'].search([('product_id', '=', record.product_id.id)])
            total_qty = 0
            for available in qty:
                if available.location_id.name == 'Stock':
                    total_qty = total_qty + available.quantity
            record.avail_qty = total_qty

    @api.onchange('tank_id')
    def onchange_capacity(self):
        for record in self:
            record.capacity = record.tank_id.capacity
            record.tank_qty = record.tank_id.qty

    name = fields.Char(copy=False, readonly=True, default='New', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string='State', default='draft')
    tank_id = fields.Many2one('fleet.tanker', string="Tanker", required=True, track_visibility='onchange')
    driver_id = fields.Many2one('fleet.driver.registration', string="Driver", related="tank_id.driver_id")
    product_id = fields.Many2one('product.product', string="Fuel Type")
    picking_id = fields.Many2one('stock.picking', string="Picking", copy=False)
    picking_count = fields.Integer(string="Picking")
    responsible_id = fields.Many2one('res.users', string="Responsible Person", track_visibility='onchange',
                                     default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string="Currency", related="company_id.currency_id")
    capacity = fields.Float('Tank Capacity', track_visibility='onchange')
    tank_qty = fields.Float('Tank Quantity', track_visibility='onchange')
    avail_qty = fields.Float('Available Quantity', track_visibility='onchange')
    qty = fields.Float(string="Fill up Quantity", required=True, track_visibility='onchange')
    date_purchase = fields.Date(string="Date of purchase")
    price_per_ltr = fields.Float(string="Price/ltr.", related="product_id.lst_price")

    @api.model
    def create(self, values):
        if 'name' not in values or values['name'] == ('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('fuel.filling')
        return super(FuelFilling, self).create(values)

    @api.multi
    def action_confirm(self):
        if self.avail_qty < self.qty:
            raise ValidationError("Fill up Quantity should be less than Available Quantity")
        elif 1000 <= self.qty:
            raise ValidationError("Fill up Quantity should be less than 1000")
        for rec in self:
            rec.picking_id = self.env['stock.picking'].create(
                {'picking_type_id': self.env['stock.picking.type'].search(
                    [('code', '=', 'internal'),
                     ('warehouse_id.company_id', '=', self.company_id.id)], limit=1).id,
                 'location_id': self.env['stock.location'].search(
                     [('name', '=', 'Stock'), ('company_id', '=', self.company_id.id)], limit=1).id,
                 'location_dest_id': self.env['stock.location'].search(
                     [('is_fuel', '=', True), ('name', '=', 'Internal Fuel Locations')], limit=1).id,
                 'tank_id': rec.id,
                 'origin': rec.name, })
            rec.picking_id.write({'move_ids_without_package': [(
                0, 0, {'product_id': rec.product_id.id,
                       'name': rec.product_id.name,
                       'product_uom_qty': rec.qty,
                       'product_uom': rec.product_id.uom_id.id,
                       'location_id': self.env['stock.location'].search(
                           [('name', '=', 'Stock'), ('company_id', '=', self.company_id.id)], limit=1).id,
                       'location_dest_id': self.env['stock.location'].search(
                           [('is_fuel', '=', True), ('name', '=', 'Internal Fuel Locations')], limit=1).id,
                       })]})
            update_qty = rec.qty + rec.tank_id.qty
            if rec.tank_id.capacity < update_qty:
                raise ValidationError("Tank Quantity should less than Tank Capacity")
            rec.tank_id.write({'qty': update_qty})
            rec.picking_id.action_confirm()
            rec.picking_id.action_assign()
            rec.picking_id.button_validate()
            for move in rec.picking_id.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            rec.picking_id.action_done()
            rec.write({'state': 'confirm', 'tank_qty': update_qty})


class VehicleLog(models.Model):
    _inherit = "fleet.vehicle.log.fuel"
    _description = 'Fleet Vehicle Log Fuel'

    state = fields.Selection([('fuel_request', 'Fuel Request'), ('draft', 'Draft'), ('confirm', 'Confirm')],
                             string='State', default='fuel_request')
    tanker_id = fields.Many2one('fleet.tanker', string="Tanker")
    lifetime_value = fields.Selection([
        ('hours', 'Hours'),
        ('km', 'Kilometers')], default='km', string='Lifetime', related='vehicle_id.lifetime_unit')
    request_number = fields.Char("Request No.")
    vehicle_type = fields.Many2one('fleet.type', related='vehicle_id.model_id.fleet_type', string="Vehicle Type")
    driver_id = fields.Many2one('res.users', string='Driver Name')
    requester_by_id = fields.Many2one('res.users', string='Requested by')
    request_date_time = fields.Datetime("Request Date & Time")

    @api.multi
    def action_accept(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_confirm(self):
        if not self.tanker_id:
            raise ValidationError("Kindly select tanker...")
        var = self.tanker_id.qty - self.liter
        if var < 0:
            raise ValidationError("Tanker quantity is not available")
        for tank in self.tanker_id:
            tank.write({'qty': var})
            self.write({'state': 'confirm'})

    @api.multi
    def action_cancel(self):
        var = self.tanker_id.qty + self.liter
        for tank in self.tanker_id:
            tank.write({'qty': var})
        self.write({'liter': 0, 'state': 'draft'})


class StockPicking(models.Model):
    _inherit = "stock.picking"

    tank_id = fields.Many2one('fuel.filling', string='Fuel Filling')
