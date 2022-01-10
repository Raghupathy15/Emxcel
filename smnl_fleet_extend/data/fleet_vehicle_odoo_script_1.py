# -*- coding: utf-8 -*-
# ./odoo-bin --addons-path= addons_path shell <  script_path -d db_name

# from odoo import api, fields, models, _
import xlrd
import odoorpc

# Global Variables
HOST = "localhost"
USER = "admin"
PSWD = "admin"
DB = "APRIL_17"
PORT = "5432"
odoo = odoorpc.ODOO("localhost", port=8020)

odoo.login(DB, USER, PSWD)
user = odoo.env.user

# file_location = os.path.join("os.getcwd()", "bitbucket/UAT/erp-smnl/smnl_fleet_extend/data/166. Updated vehicle master - 18.03.2021.xlsx")
wb = xlrd.open_workbook("166. Updated vehicle master - 18.03.2021.xlsx")

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
    make_name = excavators_sheet.cell_value(exc + 3, 1)
    model_name = excavators_sheet.cell_value(exc + 3, 2)
    engine_number = excavators_sheet.cell_value(exc + 3, 4)
    vin_sn = str(excavators_sheet.cell_value(exc + 3, 5))

    if not odoo.env['fleet.vehicle.model.brand'].search(
            [('name', '=', make_name)]):
        make = odoo.env['fleet.vehicle.model.brand'].create(
            {'name': make_name})

    if not odoo.env['fleet.vehicle.model'].search([('name', '=', model_name), ('brand_id.name', '=', make_name)]):
        odoo.env['fleet.vehicle.model'].create(
            {'name': model_name,
             'brand_id': odoo.env['fleet.vehicle.model.brand'].search(
                 [('name', '=', make_name)], limit=1)[0],
             'fleet_type': odoo.env.ref('smnl_fleet_extend.fleet_type_1').id})
    else:
        if model_name not in non_create_excavators_models:
            non_create_excavators_models.append(model_name)
    if not odoo.env['fleet.vehicle'].search([('vin_sn', '=', vin_sn)]):
        products = odoo.env['product.product'].search(
            [('is_fleet', '=', True), ('name', '=', str(make_name) + '/' + str(model_name))])
        
        products = odoo.env['product.product'].browse(products)
        for product in products:
            
            inventory_id = odoo.env['stock.inventory'].search(
                [('state', '=', 'draft'), ('product_id', '=', product.id)])
            warehouse = odoo.env['stock.warehouse'].search([('company_id', '=', odoo.env.user.company_id.id)], limit=1)
            warehouse_rec = odoo.env['stock.warehouse'].browse(warehouse[0])

            if inventory_id:
                inventory_id = inventory_id[0]
                
                lot_stock_id = odoo.env['stock.production.lot'].create(
                    {'name': vin_sn, 'product_id': product.id})
                
                line = odoo.env['stock.inventory.line'].create({
                    'product_id': product.id,
                    'inventory_id': inventory_id,
                    'fleet_chassis_id': lot_stock_id,
                    'prod_lot_id': lot_stock_id,
                    'engine_no': engine_number,
                    'product_qty': 1.0,
                    'location_id': warehouse_rec.lot_stock_id.id
                })

            else:
                inventory_id = odoo.env['stock.inventory'].create({'name': str(model_name),
                                                                   'product_id': product.id,
                                                                   'filter': 'product'})

                lot_stock_id = odoo.env['stock.production.lot'].create({'name': vin_sn, 'product_id': product.id})
                line = odoo.env['stock.inventory.line'].create({
                    'product_id': product.id,
                    'inventory_id': inventory_id,
                    'fleet_chassis_id': lot_stock_id,
                    'prod_lot_id': lot_stock_id,
                    'engine_no': engine_number,
                    'product_qty': 1.0,
                    'location_id':warehouse_rec.lot_stock_id.id
                })
            if not inventory_id in inventory_ids:
                inventory_ids.append(inventory_id)


for load in range(loaders_sheet.nrows - 3):
    make_name = loaders_sheet.cell_value(load + 3, 1)
    model_name = loaders_sheet.cell_value(load + 3, 2)
    engine_number = loaders_sheet.cell_value(load + 3, 4)
    vin_sn = str(loaders_sheet.cell_value(load + 3, 5))

    if not odoo.env['fleet.vehicle.model.brand'].search(
            [('name', '=', make_name)]):
        make = odoo.env['fleet.vehicle.model.brand'].create(
            {'name': make_name})

    if not odoo.env['fleet.vehicle.model'].search([('name', '=', model_name), ('brand_id.name', '=', make_name)]):
        odoo.env['fleet.vehicle.model'].create(
            {'name': model_name,
             'brand_id': odoo.env['fleet.vehicle.model.brand'].search(
                 [('name', '=', make_name)], limit=1)[0],
             'fleet_type': odoo.env.ref('smnl_fleet_extend.fleet_type_2').id})
    else:
        if model_name not in non_create_loaders_models:
            non_create_excavators_models.append(model_name)
    
    if not odoo.env['fleet.vehicle'].search([('vin_sn', '=', vin_sn)]):
        products = odoo.env['product.product'].search(
            [('is_fleet', '=', True), ('name', '=', str(make_name) + '/' + str(model_name))])
        products = odoo.env['product.product'].browse(products)
        for product in products:
            inventory_id = odoo.env['stock.inventory'].search([('state', '=', 'draft'), ('product_id', '=', product.id)])
            warehouse = odoo.env['stock.warehouse'].search([('company_id', '=', odoo.env.user.company_id.id)], limit=1)
            warehouse_rec = odoo.env['stock.warehouse'].browse(warehouse[0])
            if inventory_id:
                inventory_id = inventory_id[0]
                lot_stock_id = odoo.env['stock.production.lot'].create({'name': vin_sn, 'product_id': product.id})
                odoo.env['stock.inventory.line'].create({
                                                           'product_id': product.id,
                                                           'inventory_id': inventory_id,
                                                           'fleet_chassis_id': lot_stock_id,
                                                           'prod_lot_id': lot_stock_id,
                                                           'engine_no': engine_number,
                                                           'product_qty': 1.0,
                                                           'location_id': warehouse_rec.lot_stock_id.id
                                                           })

            else:
                inventory_id = odoo.env['stock.inventory'].create({'name': str(model_name),
                                                                   'product_id': product.id,
                                                                   'filter': 'product'})
                lot_stock_id = odoo.env['stock.production.lot'].create({'name': vin_sn, 'product_id': product.id})
                odoo.env['stock.inventory.line'].create({
                                                           'product_id': product.id,
                                                           'inventory_id': inventory_id,
                                                           'fleet_chassis_id': lot_stock_id,
                                                           'prod_lot_id': lot_stock_id,
                                                           'engine_no': engine_number,
                                                           'product_qty': 1.0,
                                                           'location_id': warehouse_rec.lot_stock_id.id
                                                           })
            if not inventory_id in inventory_ids:
                inventory_ids.append(inventory_id)

for dum in range(dumpers_sheet.nrows - 5):
    make_name = dumpers_sheet.cell_value(dum + 5, 1)
    model_name = dumpers_sheet.cell_value(dum + 5, 2)
    # engine_number = loaders_sheet.cell_value(dum + 5 4)
    vin_sn = str(dumpers_sheet.cell_value(dum + 5, 4))
    smnl_doors = dumpers_sheet.cell_value(dum + 5, 5)

    if not odoo.env['fleet.vehicle.model.brand'].search(
            [('name', '=', make_name)]):
        make = odoo.env['fleet.vehicle.model.brand'].create(
            {'name': make_name})

    if not odoo.env['fleet.vehicle.model'].search(
            [('name', '=', model_name)]):
        odoo.env['fleet.vehicle.model'].create(
            {'name': model_name,
             'brand_id': odoo.env['fleet.vehicle.model.brand'].search(
                 [('name', '=', make_name)], limit=1)[0],
             'fleet_type': odoo.env.ref('smnl_fleet_extend.fleet_type_3').id})
    else:
        if model_name not in non_create_dumpers_models:
            non_create_dumpers_models.append(model_name)

    if not odoo.env['fleet.vehicle'].search([('vin_sn', '=', vin_sn)]):
        products = odoo.env['product.product'].search(
            [('is_fleet', '=', True), ('name', '=', str(make_name) + '/' + str(model_name))])
        products = odoo.env['product.product'].browse(products)
        for product in products:
            inventory_id = odoo.env['stock.inventory'].search(
                [('state', '=', 'draft'), ('product_id', '=', product.id)])
            warehouse = odoo.env['stock.warehouse'].search([('company_id', '=', odoo.env.user.company_id.id)], limit=1)
            warehouse_rec = odoo.env['stock.warehouse'].browse(warehouse[0])
            if inventory_id:
                inventory_id = inventory_id[0]
                lot_stock_id = odoo.env['stock.production.lot'].create(
                    {'name': vin_sn, 'product_id': product.id})
                odoo.env['stock.inventory.line'].create({
                    'product_id': product.id,
                    'inventory_id': inventory_id,
                    'fleet_chassis_id': lot_stock_id,
                    'prod_lot_id': lot_stock_id,
                    # 'engine_no': engine_number,k
                    'product_qty': 1.0,
                    'location_id': warehouse_rec.lot_stock_id.id
                })

            else:
                inventory_id = odoo.env['stock.inventory'].create({'name': str(model_name),
                                                                   'product_id': product.id,
                                                                   'filter': 'product'})
                lot_stock_id = odoo.env['stock.production.lot'].create(
                    {'name': vin_sn, 'product_id': product.id})
                odoo.env['stock.inventory.line'].create({
                    'product_id': product.id,
                    'inventory_id': inventory_id,
                    'fleet_chassis_id': lot_stock_id,
                    'prod_lot_id': lot_stock_id,
                    # 'engine_no': engine_number,
                    'product_qty': 1.0,
                    'location_id': warehouse_rec.lot_stock_id.id
                })
            if not inventory_id in inventory_ids:
                inventory_ids.append(inventory_id)

print("**********************", inventory_ids)
inventory_recs = odoo.env['stock.inventory'].browse(inventory_ids)
for inventory in inventory_recs:
    inventory.action_validate()

for exc in range(excavators_sheet.nrows - 3):
    vin_sn = str(excavators_sheet.cell_value(exc + 3, 5))
    smnl_doors = excavators_sheet.cell_value(exc + 3, 6)
    po_date = excavators_sheet.cell_value(exc + 3, 7)
    load_capacity = excavators_sheet.cell_value(exc + 3, 8)
    engine_number = excavators_sheet.cell_value(exc + 3, 4)
    own_lease = excavators_sheet.cell_value(exc + 3, 9).upper()
    own_company_sheet = excavators_sheet.cell_value(exc + 3, 10)

    own_company = odoo.env['res.partner'].search([('name', '=', own_company_sheet)], limit=1)

    fleet_found = odoo.env['fleet.vehicle'].search(
        [('vin_sn', '=', vin_sn)], limit=1)
    if fleet_found:
        fleet_found = odoo.env['fleet.vehicle'].browse(fleet_found)
        
        fleet_found.write(
            {'smnl_doors': smnl_doors, 'purchase_date': xlrd.xldate.xldate_as_datetime(po_date, 0).strftime('%m/%d/%Y %H:%M:%S'),
             'load_capacity': load_capacity,'engine_number': engine_number,
             'own_lease': own_lease, 'own_company': own_company[0]})

for load in range(loaders_sheet.nrows - 3):
    vin_sn = str(loaders_sheet.cell_value(load + 3, 5))
    smnl_doors = loaders_sheet.cell_value(load + 3, 6)
    po_date = loaders_sheet.cell_value(load + 3, 7)
    load_capacity = loaders_sheet.cell_value(load + 3, 8)
    engine_number = loaders_sheet.cell_value(load + 3, 4)
    own_lease = loaders_sheet.cell_value(load + 3, 9).upper()
    own_company_sheet = loaders_sheet.cell_value(load + 3, 10)

    own_company = odoo.env['res.partner'].search([('name', '=', own_company_sheet)], limit=1)

    fleet_found = odoo.env['fleet.vehicle'].search(
        [('vin_sn', '=', vin_sn)], limit=1)
    if fleet_found:
        fleet_found = odoo.env['fleet.vehicle'].browse(fleet_found)
        fleet_found.write(
            {'smnl_doors': smnl_doors, 'purchase_date': xlrd.xldate.xldate_as_datetime(po_date, 0).strftime('%m/%d/%Y %H:%M:%S'),
             'load_capacity': load_capacity, 'engine_number': engine_number,
             'own_lease': own_lease, 'own_company': own_company[0]})

for dum in range(dumpers_sheet.nrows - 5):
    vin_sn = str(dumpers_sheet.cell_value(dum + 5, 4))
    smnl_doors = dumpers_sheet.cell_value(dum + 5, 5)
    po_date = dumpers_sheet.cell_value(dum + 5, 6)
    load_capacity = dumpers_sheet.cell_value(dum + 5, 7)
    own_lease = dumpers_sheet.cell_value(dum + 5, 8).upper()
    own_company_sheet = dumpers_sheet.cell_value(dum + 5, 9)

    own_company = odoo.env['res.partner'].search([('name', '=', own_company_sheet)], limit=1)
    
    fleet_found = odoo.env['fleet.vehicle'].search(
        [('vin_sn', '=', vin_sn)], limit=1)
    if fleet_found:
        fleet_found = odoo.env['fleet.vehicle'].browse(fleet_found)
        fleet_found.write(
            {'smnl_doors': smnl_doors, 'purchase_date': xlrd.xldate.xldate_as_datetime(po_date, 0).strftime('%m/%d/%Y %H:%M:%S'),
             'load_capacity': load_capacity, 'own_lease': own_lease, 'own_company': own_company[0]})

print("END")
