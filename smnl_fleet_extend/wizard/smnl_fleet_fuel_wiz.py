# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FleetFuelWiz(models.TransientModel):
    _name = 'fleet.fuel.wiz'
    _description = 'Fleet Fuel Wiz'

    from_date = fields.Date(string="From Date", required=True)
    to_date = fields.Date(string="To Date", required=True)
    fleet_id = fields.Many2one("fleet.vehicle", "Fleet/Vehicle")

    @api.multi
    def action_fleet_fuel_report(self):
        if self.from_date > self.to_date:
            raise UserError(_('From date should be less than To date...!!!'))

        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        if self.fleet_id:
            domain.append(('vehicle_id', '=', self.fleet_id.id))
        self.ensure_one()
        copy_context = dict(self.env.context)
        copy_context.pop('group_by', None)
        res = self.env['ir.actions.act_window'].for_xml_id('fleet', 'fleet_vehicle_log_fuel_action')
        res.update(
            context=dict(copy_context, default_vehicle_id=self.fleet_id.id),
            domain=domain
        )
        return res

    @api.multi
    def print_fuel_report(self):
        if self.from_date > self.to_date:
            raise UserError(_('From date should be less than To date...!!!'))

        domain = [('date', '>=', self.from_date), ('date', '<=', self.to_date)]
        if self.fleet_id:
            domain.append(('vehicle_id', '=', self.fleet_id.id))
        fuel_ids = self.env['fleet.vehicle.log.fuel'].search(domain)
        fuels = fuel_ids.ids
        datas = {'ids': fuels, 'from_date': self.from_date, 'to_date': self.to_date}
        return self.env.ref('smnl_fleet_extend.report_fleet_fuel_action').report_action([], data=datas)
