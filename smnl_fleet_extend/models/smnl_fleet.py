# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    product_id = fields.Many2one("product.product", string="Product")
    purchase_id = fields.Many2one("purchase.order", string="Purchase Order")
    purchase_line_id = fields.Many2one("purchase.order.line", string="Purchase Order Line")
    registration_number = fields.Char('Temporary Registration Number', size=30)
    license_plate = fields.Char(track_visibility="onchange",
                                help='License plate number of the vehicle (i = plate number for a car)',
                                string="License Plate / Registration Number")
    smnl_doors = fields.Char('Door No', help='Number of smnl_doors of the vehicle')
    fleet_type = fields.Many2one("fleet.type", string="Fleet type", related='model_id.fleet_type', store=True,
                                 readonly=True)
    warranty_expiry_date = fields.Date("Warranty Expiry Date")
    purchase_date = fields.Date("Purchase Date")
    bill_number = fields.Char("Bill No.")
    purchase_price = fields.Monetary(currency_field='company_currency_id', string="Purchase Price")
    purchase_shop = fields.Many2one('res.partner', string="Purchase Shop")
    engine_number = fields.Char("Engine Number", size=30)
    bill_ids = fields.Many2many(related='purchase_id.invoice_ids', string="Bill")
    company_currency_id = fields.Many2one('res.currency', readonly=True,
                                          default=lambda self: self.env.user.company_id.currency_id)
    stock_move_id = fields.Many2one("stock.move", string="Stock Move", ondelete='cascade')
    stock_move_line_id = fields.Many2one("stock.move.line", string="Move line", ondelete='cascade')
    stock_inventory_id = fields.Many2one("stock.inventory", string="Stock Inventory", ondelete='cascade')
    stock_inventory_line_id = fields.Many2one("stock.inventory.line", string="Stock Inventory line", ondelete='cascade')
    load_capacity = fields.Float('Load Capacity(in MT)')
    fuel_capacity = fields.Float("Fuel Tank Capacity (in Ltrs.)")
    lifetime = fields.Float(string='Lifetime')
    lifetime_unit = fields.Selection([
        ('hours', 'Hours'),
        ('km', 'Kilometers')], default='hours', string='Lifetime', required=True)
    model_year = fields.Char('Model Year', help='Year of the model')
    vin_sn = fields.Char('Chassis Number', help='Unique number written on the vehicle motor (VIN/SN number)',
                         copy=False, size=30)
    own_lease = fields.Selection([
        ('OWN', 'OWN'),
        ('LEASE', 'LEASE'),
        ('HIRE', 'HIRE')], string='Lease/Hire/Own')
    own_company = fields.Many2one("res.partner", string='Own/Hire/Company')

    _sql_constraints = [
        ('check_vehicle_registration_number', 'unique (registration_number)',
         "Please enter unique vehicle registration number!!!"),
        ('check_vehicle_engine_number', 'unique (engine_number)',
         "Please enter unique vehicle engine number!!!"),
        ('check_vin_sn', 'unique (vin_sn)',
         "Please enter unique vehicle chassis number!!!"),
    ]

    @api.multi
    @api.depends('name', 'brand_id', 'smnl_doors')
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.brand_id.name:
                smnl_doors = ''
                if record.smnl_doors:
                    smnl_doors = '[' + record.smnl_doors + ']'
                name = smnl_doors + record.brand_id.name + '/' + name
            res.append((record.id, name))
        return res

    @api.multi
    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate', 'smnl_doors')
    def _compute_vehicle_name(self):
        for record in self:
            record.name = record.model_id.brand_id.name + '/' + record.model_id.name + '/' + (
                        record.license_plate or _('No Plate')) + '/' + (record.smnl_doors or _('No Door'))

    @api.onchange('vin_sn', 'engine_number', 'registration_number')
    @api.multi
    def onchange_vin_sn(self):
        for rec in self:
            if rec.stock_move_line_id:
                if rec.vin_sn != rec.stock_move_line_id.lot_id.name:
                    rec.stock_move_line_id.lot_id.write({'name': rec.vin_sn})
                    rec.stock_move_line_id.write({'lot_name': rec.vin_sn})
                if rec.engine_number != rec.stock_move_line_id.engine_no:
                    rec.stock_move_line_id.write({'engine_no': rec.engine_number})
                    rec.stock_move_line_id.lot_id.write({'engine_no': rec.engine_number})
                if rec.registration_number != rec.stock_move_line_id.reg_no:
                    rec.stock_move_line_id.write({'reg_no': rec.registration_number})
                    rec.stock_move_line_id.lot_id.write({'reg_no': rec.registration_number})
            if rec.stock_inventory_line_id:
                if rec.vin_sn != rec.stock_inventory_line_id.prod_lot_id.name:
                    rec.stock_inventory_line_id.prod_lot_id.write({'name': rec.vin_sn, })
                if rec.engine_number != rec.stock_inventory_line_id.prod_lot_id.engine_no:
                    rec.stock_inventory_line_id.prod_lot_id.write({'engine_no': rec.engine_number,
                                                                   })
                if rec.registration_number != rec.stock_inventory_line_id.prod_lot_id.reg_no:
                    rec.stock_inventory_line_id.prod_lot_id.write({'reg_no': rec.registration_number})

            stock = self.env['stock.inventory.line'].search([('prod_lot_id.name', '=', rec.vin_sn)])
            if stock:
                stock.write({'engine_no': rec.engine_number})
                stock.write({'reg_no': rec.registration_number})

    # @api.multi
    # @api.constrains('model_year')
    # def _check_validations(self):
    #     for data in self:
    #         if data.model_year and not data.model_year.isdigit():
    #             raise UserError(_("'Model Year' Should be Integer."))

    @api.multi
    def _cron_remove_decimal_fleet_engine_and_chassis(self):
        fleet_records = self.env['fleet.vehicle'].search(
            ['|', ('vin_sn', '=like', '%' + '.0'), ('engine_number', '=like', '%' + '.0')])

        for fleet in fleet_records:
            if fleet.vin_sn and fleet.vin_sn[-2:] == '.0':
                fleet_vin_sn = fleet.vin_sn
                fleet.vin_sn = fleet_vin_sn[:-2]
            if fleet.engine_number and fleet.engine_number[-2:] == '.0':
                fleet_engine_number = fleet.engine_number
                fleet.engine_number = fleet_engine_number[:-2]


class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'
    _description = 'Odometer log for a vehicle'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)


class FleetVehicleCost(models.Model):
    _inherit = 'fleet.vehicle.cost'
    _description = 'Cost related to a vehicle'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'
    _description = 'Contract information on a vehicle'

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)
