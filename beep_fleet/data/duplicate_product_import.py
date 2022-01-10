# -*- coding: utf-8 -*-
# ./odoo-bin --addons-path= addons_path shell <  script_path -d db_name

# from odoo import api, fields, models, _
import xlrd
import odoorpc

# Global Variables
HOST = "localhost"
USER = "admin"
PSWD = "SMNL@EMXCEL#1"
DB = "emxcel_smnl_prod_import_product_22_june_test8_v12c"
PORT = "5432"
odoo = odoorpc.ODOO("localhost", port=9000)

odoo.login(DB, USER, PSWD)
user = odoo.env.user

wb = xlrd.open_workbook("237.Inventory final duplicate part import_06_July_2021.xlsx")
res = len(wb.sheet_names())
non_create_product = []
inventory_ids = []
duplicate = []

print("Start script ...", DB)
for sheet in wb.sheet_names():
    sheet_name = wb.sheet_by_name(sheet)
    print("\nsheet_name=======>\t", sheet)
    for rec in range(sheet_name.nrows - 2):
        part_number = sheet_name.cell_value(rec + 2, 1)
        product_name = sheet_name.cell_value(rec + 2, 2)
        remark = sheet_name.cell_value(rec + 2, 9)
        uom = sheet_name.cell_value(rec + 2, 3)
        on_hand_quantity = sheet_name.cell_value(rec + 2, 4)
        cost_price = sheet_name.cell_value(rec + 2, 5)
        purpose = sheet_name.cell_value(rec + 2, 7)
        store_name = sheet_name.cell_value(rec + 2, 8)
        if isinstance(part_number, float):
            part_number = int(part_number)
        if isinstance(product_name, float):
            product_name = int(product_name)

        if not odoo.env['stock.location'].search([('name', '=', store_name)]):
            store_location = odoo.env['stock.location'].create(
                {'name': store_name,
                 'usage': 'internal',
                 'company_id': odoo.env.user.company_id.id})

        rec_found = odoo.env['product.product'].search(
            [('is_spare_part', '=', True), ('part_number', '=', str(part_number)), ('name', '=', str(product_name)),
             ('remark', '=', str(remark))])

        if rec_found and len([rec_found]) == 1:
            products = odoo.env['product.product'].browse(rec_found)
            print("\n products------------>\t", rec, rec_found, products.name)
            for product in products:
                inventory_id = odoo.env['stock.inventory'].search(
                    [('state', '=', 'draft'), ('product_id', '=', product.id)])
                if inventory_id:
                    inventory_id = inventory_id[0]
                    if product.tracking == 'serial':
                        product_sequence = odoo.env['stock.production.lot'].search(
                            [('product_id', '=', product.id)], order='id desc', limit=1)
                        print("\n>>1 product_sequence======>\t", product_sequence, product.id)
                        if product_sequence:
                            product_sequence_number = odoo.env['stock.production.lot'].browse(product_sequence).product_sequence
                        else:
                            product_sequence_number = 0
                        for lot in range(int(on_hand_quantity)):
                            lot_stock_id = odoo.env['stock.production.lot'].create(
                                {'name': str(product.part_number) + '-' + str(product.remark) + '-' + str(
                                    product_sequence_number + lot + 1),
                                 # 'name': str(part_number) + '-' + str(lot).zfill(6),
                                 'product_id': product.id})
                            line = odoo.env['stock.inventory.line'].create({
                                'product_id': product.id,
                                'inventory_id': inventory_id,
                                'prod_lot_id': lot_stock_id,
                                'product_qty': 1.0,
                                'location_id': odoo.env['stock.location'].search([('name', '=', store_name)], limit=1)[0]
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
                        product_sequence = odoo.env['stock.production.lot'].search(
                            [('product_id', '=', product.id)], order='id desc', limit=1)
                        if product_sequence:
                            product_sequence_number = odoo.env['stock.production.lot'].browse(product_sequence).product_sequence
                        else:
                            product_sequence_number = 0

                        for lot in range(int(on_hand_quantity)):
                            lot_stock_id = odoo.env['stock.production.lot'].create(
                                {'name': str(product.part_number) + '-' + str(product.remark) + '-' + str(
                                    product_sequence_number + lot + 1),
                                 # 'name': str(part_number) + '-' + str(lot).zfill(6),
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
            print("product creation", remark)
            product = odoo.env['product.template'].create(
                {'name': product_name,
                 'sale_ok': True,
                 'purchase_ok': True,
                 'is_spare_part': True,
                 'type': 'product',
                 'part_number': str(part_number),
                 'purpose': purpose,
                 'remark': remark,
                 'default_code': remark,
                 'uom_id': odoo.env['uom.uom'].search([('name', '=', uom)], limit=1)[0] or False,
                 'uom_po_id': odoo.env['uom.uom'].search([('name', '=', uom)], limit=1)[0] or False,
                 'standard_price': cost_price,
                 })
            product_item = odoo.env['product.template'].browse(product)
            if product_item.uom_id.name == 'Unit(s)':
                product_item.update({'tracking': 'serial'})
            else:
                product_item.update({'tracking': 'none'})
            print("\n======product & product_item======>\t", product, product_item)
            rec_found = odoo.env['product.product'].search(
                [('is_spare_part', '=', True), ('part_number', '=', str(part_number)), ('name', '=', str(product_name)),
                 ('remark', '=', str(remark))])
            if rec_found and len([rec_found]) == 1:
                product_product = odoo.env['product.product'].browse(rec_found)

                inventory_id = odoo.env['stock.inventory'].create({'name': product_name,
                                                                   'product_id': product_product.id,
                                                                   'filter': 'product',
                                                                   'location_id': odoo.env['stock.location'].search(
                                                                       [('name', '=', store_name)], limit=1)[0], })
                if product_product.tracking == 'serial':
                    product_sequence = odoo.env['stock.production.lot'].search(
                        [('product_id', '=', product_product.id)], order='id desc', limit=1)
                    if product_sequence:
                        product_sequence_number = odoo.env['stock.production.lot'].browse(product_sequence).product_sequence
                    else:
                        product_sequence_number = 0
                    for lot in range(int(on_hand_quantity)):
                        lot_stock_id = odoo.env['stock.production.lot'].create(
                            {'name': str(product_product.part_number) + '-' + str(product_product.remark) + '-' + str(
                                product_sequence_number + lot + 1),
                             # 'name': str(part_number) + '-' + str(lot).zfill(6),
                             'product_id': product_product.id})
                        line = odoo.env['stock.inventory.line'].create({
                            'product_id': product_product.id,
                            'inventory_id': inventory_id,
                            'prod_lot_id': lot_stock_id,
                            'product_qty': 1.0,
                            'location_id': odoo.env['stock.location'].search([('name', '=', store_name)],
                                                                             limit=1)[0]
                        })
                else:
                    line = odoo.env['stock.inventory.line'].create({
                        'product_id': product_product.id,
                        'inventory_id': inventory_id,
                        'product_qty': on_hand_quantity,
                        'location_id': odoo.env['stock.location'].search([('name', '=', store_name)], limit=1)[0]
                    })
                if inventory_id not in inventory_ids:
                    inventory_ids.append(inventory_id)

        inventory_recs = odoo.env['stock.inventory'].browse(inventory_ids)
        for inventory in inventory_recs:
            inventory.action_validate()
