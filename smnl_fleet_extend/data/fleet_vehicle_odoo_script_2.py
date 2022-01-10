# -*- coding: utf-8 -*-
# ./odoo-bin --addons-path= addons_path shell <  script_path -d db_name

# from odoo import api, fields, models, _
import xlrd
import odoorpc

# Global Variables
HOST = "localhost"
USER = "admin"
PSWD = "admin"
DB = "emxcel_smnl_production_8_june_v12c"
PORT = "5432"
odoo = odoorpc.ODOO("localhost", port=9000)

odoo.login(DB, USER, PSWD)
user = odoo.env.user

# file_location = os.path.join("os.getcwd()", "bitbucket/UAT/erp-smnl/smnl_fleet_extend/data/166. Updated vehicle master - 18.03.2021.xlsx")
wb = xlrd.open_workbook("TUNA VEHICLE MASTER.xlsx")

res = len(wb.sheet_names())

non_create_models = []
non_create_fleet = []
inventory_ids = []
print("Start script ...")
for sheet in wb.sheet_names():
    sheet_name = wb.sheet_by_name(sheet)
    print("\nsheet_name=======>\t", sheet)
    for rec in range(sheet_name.nrows - 3):
        make_name = sheet_name.cell_value(rec + 3, 1)
        model_name = sheet_name.cell_value(rec + 3, 2)
        fleet_type = sheet_name.cell_value(rec + 3, 3)
        engine_number = sheet_name.cell_value(rec + 3, 4)
        vin_sn = str(sheet_name.cell_value(rec + 3, 5))
        company = sheet_name.cell_value(rec + 3, 11)
        company_id = odoo.env['res.company'].search([('name', '=', company)], limit=1)[0],

        if not odoo.env['fleet.vehicle.model.brand'].search(
                [('name', '=', make_name)]):
            make = odoo.env['fleet.vehicle.model.brand'].create(
                {'name': make_name})

        if not odoo.env['fleet.type'].search(
                [('name', '=', fleet_type)]):
            f_type = odoo.env['fleet.type'].create(
                {'name': fleet_type})

        if not odoo.env['fleet.vehicle.model'].search(
                [('name', '=', model_name), ('brand_id.name', '=', make_name)]):
            odoo.env['fleet.vehicle.model'].create(
                {'name': model_name, 'brand_id': odoo.env['fleet.vehicle.model.brand'].search(
                    [('name', '=', make_name)], limit=1)[0],
                 'fleet_type': odoo.env['fleet.type'].search([('name', '=', fleet_type)], limit=1)[0],
                 'company_id': odoo.env['res.company'].search([('name', '=', company)], limit=1)[0]})
        else:
            if model_name not in non_create_models:
                non_create_models.append(model_name)

        if not odoo.env['fleet.vehicle'].search([('vin_sn', '=', vin_sn)]):
            products = odoo.env['product.product'].search(
                [('is_fleet', '=', True), ('name', '=', str(make_name) + '/' + str(model_name))])

            products = odoo.env['product.product'].browse(products)
            for product in products:

                inventory_id = odoo.env['stock.inventory'].search(
                    [('state', '=', 'draft'), ('product_id', '=', product.id)])
                warehouse = odoo.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
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
                        'location_id': warehouse_rec.lot_stock_id.id
                    })
                if inventory_id not in inventory_ids:
                    inventory_ids.append(inventory_id)

    print("**********************", inventory_ids)
    inventory_recs = odoo.env['stock.inventory'].browse(inventory_ids)
    for inventory in inventory_recs:
        inventory.action_validate()

    for record in range(sheet_name.nrows - 3):
        engine_number = sheet_name.cell_value(record + 3, 4)
        vin_sn = str(sheet_name.cell_value(record + 3, 5))
        smnl_doors = sheet_name.cell_value(record + 3, 6)
        immatriculation_date = sheet_name.cell_value(record + 3, 7)
        if immatriculation_date:
            immatriculation_dt = xlrd.xldate.xldate_as_datetime(immatriculation_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            immatriculation_dt = False

        load_capacity = sheet_name.cell_value(record + 3, 8)
        own_lease = sheet_name.cell_value(record + 3, 9).upper()
        own_company_sheet = sheet_name.cell_value(record + 3, 10)
        if odoo.env['res.partner'].search([('name', '=', own_company_sheet)], limit=1):
            own_company = odoo.env['res.partner'].search([('name', '=', own_company_sheet)], limit=1)[0]
        else:
            own_company = odoo.env['res.partner'].create({
                'name': own_company_sheet,
                'company_type': 'company',
            })
        company = sheet_name.cell_value(record + 3, 11)
        company_id = odoo.env['res.company'].search([('name', '=', company)], limit=1)[0] or False
        uom = sheet_name.cell_value(record + 3, 12)
        license_plate = sheet_name.cell_value(record + 3, 13)
        model_year = sheet_name.cell_value(record + 3, 15)
        fuel_tank_capacity = sheet_name.cell_value(record + 3, 16)
        puc_number = sheet_name.cell_value(record + 3, 17)
        puc_date = sheet_name.cell_value(record + 3, 18)
        if puc_date:
            puc_dt = xlrd.xldate.xldate_as_datetime(puc_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            puc_dt = False
        puc_expire_date = sheet_name.cell_value(record + 3, 19)
        if puc_expire_date:
            puc_expire_dt = xlrd.xldate.xldate_as_datetime(puc_expire_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            puc_expire_dt = False
        insurance_number = sheet_name.cell_value(record + 3, 20)
        insurance_date = sheet_name.cell_value(record + 3, 21)
        if insurance_date:
            insurance_dt = xlrd.xldate.xldate_as_datetime(insurance_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            insurance_dt = False
        insurance_type = sheet_name.cell_value(record + 3, 22)
        insurance_provider = sheet_name.cell_value(record + 3, 23)
        insurance_idv_value = sheet_name.cell_value(record + 3, 24)
        insurance_expire_date = sheet_name.cell_value(record + 3, 25)
        if insurance_expire_date:
            insurance_expire_dt = xlrd.xldate.xldate_as_datetime(insurance_expire_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            insurance_expire_dt = False
        empty_vehicle_mileage = sheet_name.cell_value(record + 3, 26)
        loaded_vehicle_mileage = sheet_name.cell_value(record + 3, 27)
        first_contract_date = sheet_name.cell_value(record + 3, 28)
        if first_contract_date:
            first_contract_dt = xlrd.xldate.xldate_as_datetime(first_contract_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            first_contract_dt = False
        contract_end_date = sheet_name.cell_value(record + 3, 29)
        if contract_end_date:
            contract_end_dt = xlrd.xldate.xldate_as_datetime(contract_end_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            contract_end_dt = False
        fastag_number = sheet_name.cell_value(record + 3, 30)
        if fastag_number:
            fastag_number = sheet_name.cell_value(record + 3, 30)
        else:
            fastag_number = ''
        fastag_balance = sheet_name.cell_value(record + 3, 31)
        purchase_date = sheet_name.cell_value(record + 3, 32)
        if purchase_date:
            # purchase_dt = xlrd.xldate.xldate_as_datetime(purchase_date, 0)
            purchase_dt = xlrd.xldate.xldate_as_datetime(purchase_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            purchase_dt = False
        vendor_name = sheet_name.cell_value(record + 3, 33)
        if vendor_name:
            vendor_nm = odoo.env['res.partner'].search([('name', '=', vendor_name)], limit=1)[0]
        else:
            vendor_nm = False
        purchase_price = sheet_name.cell_value(record + 3, 34)
        warranty_expiry_date = sheet_name.cell_value(record + 3, 35)
        if warranty_expiry_date:
            warranty_expiry_dt = xlrd.xldate.xldate_as_datetime(warranty_expiry_date, 0).strftime('%m/%d/%Y %H:%M:%S')
        else:
            warranty_expiry_dt = False
        vehicle_color = sheet_name.cell_value(record + 3, 36)
        if vehicle_color:
            vehicle_color = sheet_name.cell_value(record + 3, 36)
        else:
            vehicle_color = False

        lifetime = sheet_name.cell_value(record + 3, 37)
        transmission = sheet_name.cell_value(record + 3, 38)
        if transmission:
            transmisn = sheet_name.cell_value(record + 3, 38)
        else:
            transmisn = False
        fuel_type = sheet_name.cell_value(record + 3, 39)
        if fuel_type:
            fuel_type = sheet_name.cell_value(record + 3, 39)
        else:
            fuel_type = False

        fleet_found = odoo.env['fleet.vehicle'].search([('vin_sn', '=', str(vin_sn))], limit=1)
        if fleet_found:
            fleet_found = odoo.env['fleet.vehicle'].browse(fleet_found)

            fleet_found.write({'smnl_doors': smnl_doors,
                               'acquisition_date': immatriculation_dt,
                               'load_capacity': load_capacity,
                               'engine_number': engine_number,
                               'own_lease': own_lease,
                               'own_company':
                                   odoo.env['res.partner'].search([('name', '=', own_company_sheet)], limit=1)[0],
                               'company_id': company_id,
                               'odometer_unit': uom,
                               'license_plate': license_plate or False,
                               'model_year': model_year or False,
                               'fuel_capacity': fuel_tank_capacity or False,
                               'puc_number': puc_number or False,
                               'puc_date': puc_dt,
                               'puc_exp_date': puc_expire_dt,
                               'insurance_number': insurance_number or False,
                               'insurance_date': insurance_dt,
                               'insurance_type': insurance_type or False,
                               'insurance_provider': insurance_provider or False,
                               'insurance_idv': insurance_idv_value or False,
                               'insurance_exp_date': insurance_expire_dt,
                               'empty_vehicle_mileage': empty_vehicle_mileage or False,
                               'loaded_vehicle_mileage': loaded_vehicle_mileage or False,
                               'first_contract_date': first_contract_dt,
                               'contract_end_date': contract_end_dt,
                               'fastag_number': fastag_number,
                               'fastag_balance': fastag_balance or False,
                               'purchase_date': purchase_dt,
                               'purchase_shop': vendor_nm,
                               'purchase_price': purchase_price or False,
                               'warranty_expiry_date': warranty_expiry_dt,
                               'color': vehicle_color or False,
                               'lifetime': lifetime or False,
                               'transmission': transmisn or False,
                               'fuel_type': fuel_type or False
                               })
print("END")
