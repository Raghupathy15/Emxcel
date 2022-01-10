# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Inventory(models.Model):
    _inherit = "stock.inventory"

    is_fleet = fields.Boolean(related='product_id.is_fleet', string="Is Fleet", store=True, readonly=False)

    def _get_inventory_lines_values(self):
        # TDE CLEANME: is sql really necessary ? I don't think so
        locations = self.env['stock.location'].search([('id', 'child_of', [self.location_id.id])])
        domain = ' location_id in %s AND quantity != 0 AND active = TRUE'
        args = (tuple(locations.ids),)

        vals = []
        Product = self.env['product.product']

        # Fetch registration and engine number from lot or chassis number.
        Lot = self.env['stock.production.lot']

        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']
        # Empty recordset of products to filter
        products_to_filter = self.env['product.product']

        # case 0: Filter on company
        if self.company_id:
            domain += ' AND company_id = %s'
            args += (self.company_id.id,)

        # case 1: Filter on One owner only or One product for a specific owner
        if self.partner_id:
            domain += ' AND owner_id = %s'
            args += (self.partner_id.id,)
        # case 2: Filter on One Lot/Serial Number
        if self.lot_id:
            domain += ' AND lot_id = %s'
            args += (self.lot_id.id,)
        # case 3: Filter on One product
        if self.product_id:
            domain += ' AND product_id = %s'
            args += (self.product_id.id,)
            products_to_filter |= self.product_id
        # case 4: Filter on A Pack
        if self.package_id:
            domain += ' AND package_id = %s'
            args += (self.package_id.id,)
        # case 5: Filter on One product category + Exahausted Products
        if self.category_id:
            categ_products = Product.search([('categ_id', 'child_of', self.category_id.id)])
            domain += ' AND product_id = ANY (%s)'
            args += (categ_products.ids,)
            products_to_filter |= categ_products

        self.env.cr.execute("""SELECT product_id, sum(quantity) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
            FROM stock_quant
            LEFT JOIN product_product
            ON product_product.id = stock_quant.product_id
            WHERE %s
            GROUP BY product_id, location_id, lot_id, package_id, partner_id """ % domain, args)

        for product_data in self.env.cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
            for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
                product_data['fleet_chassis_id'] = Lot.browse(product_data['prod_lot_id']).id
                product_data['reg_no'] = Lot.browse(product_data['prod_lot_id']).reg_no
                product_data['engine_no'] = Lot.browse(product_data['prod_lot_id']).engine_no
                product_data['fleet_id'] = Lot.browse(product_data['prod_lot_id']).fleet_id.id

                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)
        if self.exhausted:
            exhausted_vals = self._get_exhausted_inventory_line(products_to_filter, quant_products)
            vals.extend(exhausted_vals)
        return vals

    def _action_done(self):
        res = super(Inventory, self)._action_done()
        for rec in self:
            if rec.state == 'done':
                for inventory_line in rec.line_ids:
                    if inventory_line.product_id.is_fleet and inventory_line.prod_lot_id and inventory_line.product_qty == 1:
                        if not self.env['fleet.vehicle'].search([('vin_sn', '=', inventory_line.prod_lot_id.name)]):
                            fleet = self.env['fleet.vehicle'].create({'vin_sn': inventory_line.prod_lot_id.name,
                                                                      'model_id': inventory_line.product_id.fleet_model_id.id,
                                                                      'product_id': inventory_line.product_id.id,
                                                                      'image_medium': inventory_line.product_id.image_medium,
                                                                      # 'engine_number': inventory_line.engine_no,
                                                                      # 'registration_number': inventory_line.reg_no,
                                                                      'stock_inventory_id': rec.id,
                                                                      'stock_inventory_line_id': inventory_line.id,
                                                                      'state_id': int(
                                                                          self.env['fleet.vehicle.state'].search(
                                                                              [('draft_state', '=', True)]))
                                                                      })
                            inventory_line.write({'fleet_id': fleet.id})
                            inventory_line.prod_lot_id.write({'fleet_id': fleet.id,
                                                              'reg_no': inventory_line.reg_no,
                                                              'engine_no': inventory_line.engine_no, })
        return res
