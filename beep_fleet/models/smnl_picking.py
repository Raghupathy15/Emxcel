# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fleet_service_id = fields.Many2one(
        'fleet.vehicle.log.services', 'Fleet Service')

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).action_done()
        for pick in self:
            for move_line in pick.move_lines:
                if move_line.purchase_line_id.spare_part_id:
                    move_line.purchase_line_id.spare_part_id.received_qty = move_line.quantity_done
                    move_line.purchase_line_id.spare_part_id.vehicle_log_service_id.message_post(
                        body=_(
                            "Raised RFQ for spare-part(%s) is done & it's purchase number is %s") % (
                            move_line.purchase_line_id.spare_part_id.product_tmpl_id.name,
                            move_line.purchase_line_id.order_id.name,))
                    if not move_line.purchase_line_id.spare_part_id.vehicle_log_service_id.spare_part_ids.filtered(
                            lambda m: m.use_qty > m.qty_available and not m.purchase_id):
                        move_line.purchase_line_id.spare_part_id.vehicle_log_service_id.action_in_progress()
        return res
