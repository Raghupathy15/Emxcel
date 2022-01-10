# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class GatePass(models.Model):
    _name = "gate.pass"
    _description = "Gate Pass"
    
    name = fields.Char(readonly=True, copy=False, string="Gate Pass")
    product_id = fields.Char(string="Product")
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    gate_pass_type = fields.Selection([
        ('return', 'Returnable'),
        ('non_return', 'Non returnable')], "Gate Pass Type")
    description = fields.Char("Description")
    cost_price = fields.Float("Cost Price")
    gate_pass_days = fields.Integer("Gate Pass Validity (in Days)")
    security_check = fields.Boolean("Security Check")
    service_id = fields.Many2one(
        "fleet.vehicle.log.services", track_visibility="onchange", string="Service Log")
    vehicle_id = fields.Many2one("fleet.vehicle", related='service_id.vehicle_id', string="Vehicle")
    purchase_id = fields.Many2one(
        "purchase.order", track_visibility="onchange", strisng="Purchase")
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('rejected', 'Rejected')], string='State', default='draft')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'gate.pass') or _('New')
        return super(GatePass, self).create(vals)
    
    def button_approved(self):
        for record in self:
            record.write({'state': 'approved'})

    def button_rejected(self):
        for record in self:
            record.write({'state': 'rejected'})

    def button_print(self):
        datas = {'ids': self.ids}
        return self.env.ref('beep_fleet.report_gate_pass_action').report_action([], data=datas)
