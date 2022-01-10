# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import Counter


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    fleet_id = fields.Many2one("fleet.vehicle", "Fleet Model", ondelete='cascade')
    engine_no = fields.Char('Engine Number')
    reg_no = fields.Char('Registration Number')
    is_fleet = fields.Boolean(related='product_id.is_fleet', string="Is Fleet", store=True, readonly=False)

    _sql_constraints = [
        ('check_move_line_vehicle_registration_number', 'unique (reg_no)',
         "Please enter unique vehicle registration number!!!"),
        ('check_move_line_vehicle_engine_number', 'unique (engine_no)',
         "Please enter unique vehicle engine number!!!")
    ]

    @api.constrains('lot_id')
    @api.multi
    def _check_lot_id(self):
        for rec in self:
            if rec.product_id.fleet_model_id and not rec.lot_name and not rec.lot_id:
                raise ValidationError(_('Please enter vehicle chassis number...'))

    @api.onchange('lot_name', 'lot_id')
    def onchange_serial_number(self):
        res = {}
        if self.product_id.tracking == 'serial':
            if not self.qty_done:
                self.qty_done = 1

            message = None
            if self.lot_name or self.lot_id:
                move_lines_to_check = self._get_similar_move_lines() - self
                if self.lot_name:
                    counter = Counter([line.lot_name for line in move_lines_to_check])
                    if counter.get(self.lot_name) and counter[self.lot_name] > 1:
                        message = _("Please enter unique 'Chassis Number' number !!!")
                elif self.lot_id:
                    counter = Counter([line.lot_id.id for line in move_lines_to_check])
                    if counter.get(self.lot_id.id) and counter[self.lot_id.id] > 1:
                        message = _("Please enter unique 'Chassis Number' number !!!")
            if message:
                res['warning'] = {'title': _('Warning'), 'message': message}
        return res
