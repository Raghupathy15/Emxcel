# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    def _get_picking_type_create_values(self, max_sequence):
        """ Inherited method to change Delivery order label
        """
        ret = super(Warehouse, self)._get_picking_type_create_values(max_sequence)
        out_type_id = ret[0].get('out_type_id')
        if out_type_id:
            if out_type_id.get('name'):
                out_type_id['name'] = 'Product Issue'
        return ret
        
        