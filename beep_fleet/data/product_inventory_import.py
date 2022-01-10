# -*- coding: utf-8 -*-
# ./odoo-bin --addons-path= addons_path shell <  script_path -d db_name

# from odoo import api, fields, models, _
import xlrd
import odoorpc

# Global Variables
HOST = "localhost"
USER = "admin"
PSWD = "SMNL@EMXCEL#1"
DB = "emxcel_smnl_prod_import_product_22_june_test4_v12c"
PORT = "5432"
odoo = odoorpc.ODOO("localhost", port=9000)

odoo.login(DB, USER, PSWD)
user = odoo.env.user

wb = xlrd.open_workbook("236. Inventory Final - Merged_Updated - May 2021_09.06.2021.xlsx")
res = len(wb.sheet_names())
non_create_product = []
inventory_ids = []
duplicate = []

print("Start script ...")
for sheet in wb.sheet_names():
    sheet_name = wb.sheet_by_name(sheet)
    print("\nsheet_name=======>\t", sheet)
    for rec in range(sheet_name.nrows - 2):
        part_number = sheet_name.cell_value(rec + 2, 1)
        if isinstance(part_number, float):
            part_number = int(part_number)
        rec_found = odoo.env['product.product'].search([('part_number', '=', str(part_number))])
        if rec_found:
            duplicate.append(str(part_number))
        if not rec_found:
            product_name = sheet_name.cell_value(rec + 2, 2)
            uom = sheet_name.cell_value(rec + 2, 3)
            on_hand_quantity = sheet_name.cell_value(rec + 2, 4)
            cost_price = sheet_name.cell_value(rec + 2, 5)
            purpose = sheet_name.cell_value(rec + 2, 7)
            store_name = sheet_name.cell_value(rec + 2, 8)
            remark = sheet_name.cell_value(rec + 2, 9)

            if not odoo.env['stock.location'].search([('name', '=', store_name)]):
                store_location = odoo.env['stock.location'].create(
                    {'name': store_name,
                     'usage': 'internal',
                     'company_id': odoo.env.user.company_id.id})
            if not odoo.env['product.template'].search([('name', '=', product_name), ('part_number', '=', str(part_number))]):
                product = odoo.env['product.template'].create(
                    {'name': product_name,
                     'sale_ok': True,
                     'purchase_ok': True,
                     'is_spare_part': True,
                     'type': 'product',
                     'part_number': str(part_number),
                     'purpose': purpose,
                     'remark': remark,
                     'uom_id': odoo.env['uom.uom'].search([('name', '=', uom)], limit=1)[0] or False,
                     'uom_po_id': odoo.env['uom.uom'].search([('name', '=', uom)], limit=1)[0] or False,
                     'standard_price': cost_price,
                     })
                product_item = odoo.env['product.template'].browse(product)
                if product_item.uom_id.name == 'Unit(s)':
                    product_item.update({'tracking': 'serial'})
                else:
                    product_item.update({'tracking': 'none'})
            else:
                product = odoo.env['product.template'].search([('name', '=', product_name), ('part_number', '=', str(part_number))], limit=1)[0]
                product_item = odoo.env['product.template'].browse(product)
                product_item.write(
                    {'part_number': str(part_number),
                     'purpose': purpose,
                     'remark': remark,
                     'uom_id': odoo.env['uom.uom'].search([('name', '=', uom)], limit=1)[0] or False,
                     'uom_po_id': odoo.env['uom.uom'].search([('name', '=', uom)], limit=1)[0] or False,
                     'standard_price': cost_price,
                     })
                if product_item.uom_id.name == 'Unit(s)':
                    product_item.update({'tracking': 'serial'})
                else:
                    product_item.update({'tracking': 'none'})

            products = odoo.env['product.product'].search(
                [('is_spare_part', '=', True), ('name', '=', product_name), ('part_number', '=', part_number)])[0] or False
            if len([products]) == 1:
                products = odoo.env['product.product'].browse(products)
                print("\n products------------>\t", rec, products.name)
                for product in products:
                    inventory_id = odoo.env['stock.inventory'].search(
                        [('state', '=', 'draft'), ('product_id', '=', product.id)])
                    if inventory_id:
                        inventory_id = inventory_id[0]
                        if product.tracking == 'serial':
                            for lot in range(int(on_hand_quantity)):
                                lot_stock_id = odoo.env['stock.production.lot'].create(
                                    {'name': str(part_number) + '-' + str(lot).zfill(6),
                                     'product_id': product.id})
                                line = odoo.env['stock.inventory.line'].create({
                                    'product_id': product.id,
                                    'inventory_id': inventory_id,
                                    'prod_lot_id': lot_stock_id,
                                    'product_qty': 1.0,
                                    'location_id': odoo.env['stock.location'].search([('name', '=', store_name)], limit=1)[
                                        0]
                                })
                        else:
                            line = odoo.env['stock.inventory.line'].create({
                                'product_id': product.id,
                                'inventory_id': inventory_id,
                                'product_qty': on_hand_quantity,
                                'location_id': odoo.env['stock.location'].search([('name', '=', store_name)], limit=1)[0]
                            })
                    else:
                        inventory_id = odoo.env['stock.inventory'].create({'name': product_name,
                                                                           'product_id': product.id,
                                                                           'filter': 'product',
                                                                           'location_id': odoo.env['stock.location'].search(
                                                                               [('name', '=', store_name)], limit=1)[0], })
                        if product.tracking == 'serial':
                            for lot in range(int(on_hand_quantity)):
                                lot_stock_id = odoo.env['stock.production.lot'].create(
                                    {'name': str(part_number) + '-' + str(lot).zfill(6),
                                     'product_id': product.id})
                                line = odoo.env['stock.inventory.line'].create({
                                    'product_id': product.id,
                                    'inventory_id': inventory_id,
                                    'prod_lot_id': lot_stock_id,
                                    'product_qty': 1.0,
                                    'location_id': odoo.env['stock.location'].search([('name', '=', store_name)],
                                                                                     limit=1)[0]
                                })
                        else:
                            line = odoo.env['stock.inventory.line'].create({
                                'product_id': product.id,
                                'inventory_id': inventory_id,
                                'product_qty': on_hand_quantity,
                                'location_id': odoo.env['stock.location'].search([('name', '=', store_name)], limit=1)[0]
                            })
                    if inventory_id not in inventory_ids:
                        inventory_ids.append(inventory_id)
            else:
                duplicate.append(str(part_number))
    print("**********************", inventory_ids)
    print("duplicate", duplicate)
    inventory_recs = odoo.env['stock.inventory'].browse(inventory_ids)
    for inventory in inventory_recs:
        inventory.action_validate()
