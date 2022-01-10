# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class FleetVehicleLogServices(models.Model):
	_inherit = 'fleet.vehicle.log.services'


	def compute_count(self):
		for record in self:
			record.return_count = self.env['spare.parts.returns.approval'].search_count([('service_log_id', '=', self.id)])

	def compute_spare_part(self):
		for vehicle in self:
			if len(vehicle.spare_part_ids) > 0:
				vehicle.is_spare_part = True
			else:
				vehicle.is_spare_part = False
		
	return_count = fields.Integer('Returns',compute='compute_count')
	is_returned = fields.Boolean('Returned')
	is_spare_part = fields.Boolean('Spare part',compute='compute_spare_part')
	return_id = fields.Many2one('spare.parts.returns.approval', string='Return')

	def get_spare_returns(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Spare Returns',
			'view_mode': 'tree,form',
			'res_model': 'spare.parts.returns.approval',
			'domain': [('service_log_id', '=', self.id)],
			'context': "{'create': False}"
		}
	
	@api.multi
	def service_parts_return(self):
		form_view = self.env.ref('smnl_spare_parts_returns.form_spare_parts_return_wizard')
		return {
			'name': "Spare Parts Returns",
			'view_mode': 'form',
			'view_type': 'form',
			'view_id': form_view.id,
			'res_model': 'spare.parts.returns',
			'type': 'ir.actions.act_window',
			'target': 'new',
		}
