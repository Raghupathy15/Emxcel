# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DeliveryOrder(models.Model):
    _inherit = 'stock.warehouse'

    def _get_picking_type_create_values(self, max_sequence):
        """ When a warehouse is created this method return the values needed in
        order to create the new picking types for this warehouse. Every picking
        type are created at the same time than the warehouse howver they are
        activated or archived depending the delivery_steps or reception_steps.
        """
        input_loc, output_loc = self._get_input_output_locations(self.reception_steps, self.delivery_steps)
        return {'in_type_id': {
            'name': _('Receipts'),
            'code': 'incoming',
            'use_create_lots': True,
            'use_existing_lots': False,
            'default_location_src_id': False,
            'sequence': max_sequence + 1,
            'barcode': self.code.replace(" ", "").upper() + "-RECEIPTS",
        }, 'out_type_id': {
            'name': _('Product Issue'),
            'code': 'outgoing',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_dest_id': False,
            'sequence': max_sequence + 5,
            'barcode': self.code.replace(" ", "").upper() + "-DELIVERY",
        }, 'pack_type_id': {
            'name': _('Pack'),
            'code': 'internal',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_src_id': self.wh_pack_stock_loc_id.id,
            'default_location_dest_id': output_loc.id,
            'sequence': max_sequence + 4,
            'barcode': self.code.replace(" ", "").upper() + "-PACK",
        }, 'pick_type_id': {
            'name': _('Pick'),
            'code': 'internal',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_src_id': self.lot_stock_id.id,
            'sequence': max_sequence + 3,
            'barcode': self.code.replace(" ", "").upper() + "-PICK",
        }, 'int_type_id': {
            'name': _('Internal Transfers'),
            'code': 'internal',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_src_id': self.lot_stock_id.id,
            'default_location_dest_id': self.lot_stock_id.id,
            'active': self.reception_steps != 'one_step' or self.delivery_steps != 'ship_only' or self.user_has_groups(
                'stock.group_stock_multi_locations'),
            'sequence': max_sequence + 2,
            'barcode': self.code.replace(" ", "").upper() + "-INTERNAL",
        },
               }, max_sequence + 6
