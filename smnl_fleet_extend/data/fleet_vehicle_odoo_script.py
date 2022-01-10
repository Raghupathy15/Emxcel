# -*- coding: utf-8 -*-
# ./odoo-bin --addons-path= addons_path shell <  script_path -d db_name

from odoo import api, fields, models, _
import xlrd

loc = ("/home/odoo/workspace/custom/bitbuckt/SE-139/erp-smnl/smnl_fleet_extend/data/vehicle_master.xlsx")
wb = xlrd.open_workbook(loc)

excavators_sheet = wb.sheet_by_name('Excavators')
loaders_sheet = wb.sheet_by_name('Wheel loaders')
dumpers_sheet = wb.sheet_by_name('Dumpers')

non_create_excavators_models = []
non_create_excavators = []

non_create_loaders_models = []
non_create_loaders = []

non_create_dumpers_models = []
non_create_dumpers = []

inventory_ids = []
print("Start script ...")

for exc in range(excavators_sheet.nrows - 3):
    model_name = excavators_sheet.cell_value(exc + 3, 6)
    make_name = excavators_sheet.cell_value(exc + 3, 1)
    engine_number = excavators_sheet.cell_value(exc + 3, 2)
    vin_sn = str(excavators_sheet.cell_value(exc + 3, 3))
    smnl_doors = excavators_sheet.cell_value(exc + 3, 4)
    model_year = excavators_sheet.cell_value(exc + 3, 5)

    if not self.env['fleet.vehicle.model.brand'].sudo().search(
            [('name', '=', make_name)]):
        make = self.env['fleet.vehicle.model.brand'].sudo().create(
            {'name': make_name})

    if not self.env['fleet.vehicle.model'].sudo().search([('name', '=', model_name), ('brand_id.name', '=', make_name)]):
        print (make_name)
        self.env['fleet.vehicle.model'].sudo().create(
            {'name': model_name,
             'brand_id': self.env['fleet.vehicle.model.brand'].sudo().search(
                 [('name', '=', make_name)], limit=1).id,
             'fleet_type': self.env.ref('smnl_fleet_extend.fleet_type_1').id})
    else:
        if model_name not in non_create_excavators_models:
            print("else", model_name)
            non_create_excavators_models.append(model_name)
    if not self.env['fleet.vehicle'].sudo().search([('vin_sn', '=', vin_sn)]):
        products = self.env['product.product'].sudo().search(
            [('is_fleet', '=', True), ('name', '=', str(make_name) + '/' + str(model_name))])
        for product in products:
            inventory_id = self.env['stock.inventory'].sudo().search(
                [('state', '=', 'draft'), ('product_id', '=', product.id)])
            if inventory_id:
                lot_stock_id = self.env['stock.production.lot'].sudo().create(
                    {'name': vin_sn, 'product_id': product.id}).id
                line = self.env['stock.inventory.line'].sudo().create({
                    'product_id': product.id,
                    'inventory_id': inventory_id.id,
                    'fleet_chassis_id': lot_stock_id,
                    'prod_lot_id': lot_stock_id,
                    'engine_no': engine_number,
                    'product_qty': 1.0,
                    'location_id': self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id.id
                })

            else:
                inventory_id = self.env['stock.inventory'].sudo().create({'name': str(model_name),
                                                                          'product_id': product.id,
                                                                          'filter': 'product'})

                lot_stock_id = self.env['stock.production.lot'].sudo().create(
                    {'name': vin_sn, 'product_id': product.id}).id
                line = self.env['stock.inventory.line'].sudo().create({
                    'product_id': product.id,
                    'inventory_id': inventory_id.id,
                    'fleet_chassis_id': lot_stock_id,
                    'prod_lot_id': lot_stock_id,
                    'engine_no': engine_number,
                    'product_qty': 1.0,
                    'location_id': self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id.id
                })
            if not inventory_id.id in inventory_ids:
                inventory_ids.append(inventory_id.id)


for load in range(loaders_sheet.nrows - 3):
    model_name = loaders_sheet.cell_value(load + 3, 1)
    make_name = loaders_sheet.cell_value(load + 3, 6)
    engine_number = loaders_sheet.cell_value(load + 3, 2)
    vin_sn = str(loaders_sheet.cell_value(load + 3, 3))
    smnl_doors = loaders_sheet.cell_value(load + 3, 4)
    model_year = loaders_sheet.cell_value(load + 3, 5)

    if not self.env['fleet.vehicle.model.brand'].sudo().search(
            [('name', '=', make_name)]):
        make = self.env['fleet.vehicle.model.brand'].sudo().create(
            {'name': make_name})

    if not self.env['fleet.vehicle.model'].sudo().search([('name', '=', model_name), ('brand_id.name', '=', make_name)]):
        self.env['fleet.vehicle.model'].sudo().create(
            {'name': model_name,
             'brand_id': self.env['fleet.vehicle.model.brand'].sudo().search(
                 [('name', '=', make_name)], limit=1).id,
             'fleet_type': self.env.ref('smnl_fleet_extend.fleet_type_2').id})
    else:
        if model_name not in non_create_loaders_models:
            non_create_excavators_models.append(model_name)
    if not self.env['fleet.vehicle'].sudo().search([('vin_sn', '=', vin_sn)]):
        products = self.env['product.product'].sudo().search(
            [('is_fleet', '=', True), ('name', '=', str(make_name) + '/' + str(model_name))])
        for product in products:
            inventory_id = self.env['stock.inventory'].sudo().search([('state', '=', 'draft'), ('product_id', '=', product.id)])
            if inventory_id:
                lot_stock_id = self.env['stock.production.lot'].sudo().create({'name': vin_sn, 'product_id': product.id}).id
                self.env['stock.inventory.line'].sudo().create({
                                                           'product_id': product.id,
                                                           'inventory_id': inventory_id.id,
                                                           'fleet_chassis_id': lot_stock_id,
                                                           'prod_lot_id': lot_stock_id,
                                                           'engine_no': engine_number,
                                                           'product_qty': 1.0,
                                                           'location_id': self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id.id
                                                           })

            else:
                inventory_id = self.env['stock.inventory'].sudo().create({'name': str(model_name),
                                                           'product_id': product.id,
                                                           'filter': 'product'})
                lot_stock_id = self.env['stock.production.lot'].sudo().create({'name': vin_sn, 'product_id': product.id}).id
                self.env['stock.inventory.line'].sudo().create({
                                                           'product_id': product.id,
                                                           'inventory_id': inventory_id.id,
                                                           'fleet_chassis_id': lot_stock_id,
                                                           'prod_lot_id': lot_stock_id,
                                                           'engine_no': engine_number,
                                                           'product_qty': 1.0,
                                                           'location_id': self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id.id
                                                           })
            if not inventory_id.id in inventory_ids:
                inventory_ids.append(inventory_id.id)

for dum in range(dumpers_sheet.nrows - 5):
    model_name = dumpers_sheet.cell_value(dum + 5, 6)
    make_name = dumpers_sheet.cell_value(dum + 5, 2)
    # engine_number = dumpers_sheet.cell_value(dum + 5, 2)
    vin_sn = str(dumpers_sheet.cell_value(dum + 5, 5))
    smnl_doors = dumpers_sheet.cell_value(dum + 5, 1)
    model_year = dumpers_sheet.cell_value(dum + 5, 4)

    if not self.env['fleet.vehicle.model.brand'].sudo().search(
            [('name', '=', make_name)]):
        make = self.env['fleet.vehicle.model.brand'].sudo().create(
            {'name': make_name})

    if not self.env['fleet.vehicle.model'].sudo().search(
            [('name', '=', model_name)]):
        self.env['fleet.vehicle.model'].sudo().create(
            {'name': model_name,
             'brand_id': self.env['fleet.vehicle.model.brand'].sudo().search(
                 [('name', '=', make_name)], limit=1).id,
             'fleet_type': self.env.ref('smnl_fleet_extend.fleet_type_3').id})
    else:
        if model_name not in non_create_dumpers_models:
            non_create_excavators_models.append(model_name)
    if not self.env['fleet.vehicle'].sudo().search([('vin_sn', '=', vin_sn)]):
        products = self.env['product.product'].sudo().search(
            [('is_fleet', '=', True), ('name', '=', str(make_name) + '/' + str(model_name))])
        for product in products:
            inventory_id = self.env['stock.inventory'].sudo().search([('state', '=', 'draft'), ('product_id', '=', product.id)])
            if inventory_id:
                lot_stock_id = self.env['stock.production.lot'].sudo().create({'name': vin_sn, 'product_id': product.id}).id
                self.env['stock.inventory.line'].sudo().create({
                                                           'product_id': product.id,
                                                           'inventory_id': inventory_id.id,
                                                           'fleet_chassis_id': lot_stock_id,
                                                           'prod_lot_id': lot_stock_id,
                                                           # 'engine_no': engine_number,k
                                                           'product_qty': 1.0,
                                                           'location_id': self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id.id
                                                           })

            else:
                inventory_id = self.env['stock.inventory'].sudo().create({'name': str(model_name),
                                                           'product_id': product.id,
                                                           'filter': 'product'})
                lot_stock_id = self.env['stock.production.lot'].sudo().create({'name': vin_sn, 'product_id': product.id}).id
                self.env['stock.inventory.line'].sudo().create({
                                                           'product_id': product.id,
                                                           'inventory_id': inventory_id.id,
                                                           'fleet_chassis_id': lot_stock_id,
                                                           'prod_lot_id': lot_stock_id,
                                                           # 'engine_no': engine_number,
                                                           'product_qty': 1.0,
                                                           'location_id': self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id.id
                                                           })
            if not inventory_id.id in inventory_ids:
                inventory_ids.append(inventory_id.id)


inventory_recs = self.env['stock.inventory'].browse(inventory_ids)
for inventory in inventory_recs:
    inventory.action_validate()
self.env.cr.commit()

for exc in range(excavators_sheet.nrows - 3):
    vin_sn = str(excavators_sheet.cell_value(exc + 3, 3))
    smnl_doors = excavators_sheet.cell_value(exc + 3, 4)
    po_date = excavators_sheet.cell_value(exc + 3, 5)

    fleet_found = self.env['fleet.vehicle'].sudo().search(
        [('vin_sn', '=', vin_sn)], limit=1)
    if fleet_found:
        
        fleet_found.sudo().write(
            {'smnl_doors': smnl_doors, 'purchase_date': xlrd.xldate.xldate_as_datetime(po_date, 0)})

for load in range(loaders_sheet.nrows - 3):
    vin_sn = str(loaders_sheet.cell_value(load + 3, 3))
    smnl_doors = loaders_sheet.cell_value(load + 3, 4)
    po_date = loaders_sheet.cell_value(load + 3, 5)

    fleet_found = self.env['fleet.vehicle'].sudo().search(
        [('vin_sn', '=', vin_sn)], limit=1)
    if fleet_found:
        
        fleet_found.sudo().write(
            {'smnl_doors': smnl_doors, 'purchase_date': xlrd.xldate.xldate_as_datetime(po_date, 0)})

for dum in range(dumpers_sheet.nrows - 5):
    vin_sn = str(dumpers_sheet.cell_value(dum + 5, 5))
    smnl_doors = dumpers_sheet.cell_value(dum + 5, 1)
    po_date = dumpers_sheet.cell_value(dum + 5, 4)
    
    fleet_found = self.env['fleet.vehicle'].sudo().search(
        [('vin_sn', '=', vin_sn)], limit=1)
    if fleet_found:
        
        fleet_found.sudo().write(
            {'smnl_doors': smnl_doors, 'purchase_date': xlrd.xldate.xldate_as_datetime(po_date, 0)})

self.env.cr.commit()
print("END")
