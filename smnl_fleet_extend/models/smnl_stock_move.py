# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_fleet = fields.Boolean(related='product_id.is_fleet', string="Is Fleet", store=True, readonly=False)
    is_expire = fields.Boolean(string="Is Expire")
    expiry_date = fields.Date(string='Expiry Date')


    @api.multi
    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        if not self.expiry_date > fields.Date.today():
            raise ValueError(_('Kindly select the future Expire date.'))

    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()

        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        if self.picking_id.picking_type_id.show_reserved and not self.product_id.is_fleet:
            view = self.env.ref('stock.view_stock_move_operations')
        elif self.picking_id.picking_type_id.show_reserved and self.product_id.is_fleet:
            view = self.env.ref('smnl_fleet_extend.smnl_view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_lots_m2o=self.has_tracking != 'none' and (
                            picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),
                # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.location_id.child_ids and self.picking_type_id.code != 'incoming',
                show_destination_location=self.location_dest_id.child_ids and self.picking_type_id.code != 'outgoing',
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done'
            ),
        }
