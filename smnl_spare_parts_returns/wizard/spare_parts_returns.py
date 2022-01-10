# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class SpartPartsReturn(models.TransientModel):
	_name = 'spare.parts.returns'
	_description = 'Spare Parts Returns Wizard'


	return_spare_part_ids = fields.One2many('fleet.spare.parts.returns', 'return_id', string='Spare Part Returns')

	@api.multi
	def action_spare_parts_return(self):
		active_id = self.env.context.get('active_id')
		rec = self.env['fleet.vehicle.log.services'].browse(int(active_id))
		for line in self.return_spare_part_ids:
			if line.qty < 1:
				raise ValidationError('Quanity should be greater 0 !..')
			approvals = self.env['spare.parts.returns.approval']
			approvals_obj = approvals.sudo().create({'product_id': line.product_id.id,
									'qty': line.qty,
									'part_number': line.part_number,
									'lot_id': line.lot_id.id,
									'service_log_id': rec.id,
									'location_id': line.location_id.id,
									'name': self.env['ir.sequence'].next_by_code('spare.part.return.approvals') or '/',
									})
			rec.write({'is_returned': True})

class FleetSparePartReturns(models.TransientModel):
	_name = "fleet.spare.parts.returns"
	_description = "Fleet Spare Part Returns"
	rec_name ='product_id'


	product_id = fields.Many2one('product.template', 'Product', required=True)
	part_number = fields.Char('Part Number',readonly=True)
	lot_id = fields.Many2one('stock.production.lot', string='Serial No',required=True)
	qty = fields.Float('Quantity', default="1",help="The total number of products you need to return")
	return_id = fields.Many2one('spare.parts.returns', string='Spare Parts returns')
	location_id = fields.Many2one('stock.location', string='Return Location', required=True, domain="[('usage', '=', 'internal'),('company_id', '=',company_id)]")
	company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True, 
				default=lambda self: self.env.user.company_id)

	@api.onchange('product_id','qty')
	@api.multi
	def onchange_product_id(self):
		active_id = self.env.context.get('active_id')
		rec = self.env['fleet.vehicle.log.services'].browse(int(active_id))
		product_list = []
		lots_list = []
		if self.product_id:
			self.lot_id = False
			self.part_number = self.product_id.part_number
			for line in self.return_id:				
				for product in line.return_spare_part_ids:
					for service_logs in rec.spare_part_ids:
						product_list.append(service_logs.product_tmpl_id.id)
						if product.product_id.id == service_logs.product_tmpl_id.id:
							if product.qty > service_logs.use_qty:
								raise ValidationError('Quanity should not be greater than Spare Part Required quantity.')
			if not (product.product_id.id in product_list):
				raise ValidationError('Please select only the products in Spare Part List')

	@api.onchange('lot_id')
	@api.multi
	def onchange_lot_id(self):
		active_id = self.env.context.get('active_id')
		rec = self.env['fleet.vehicle.log.services'].browse(int(active_id))
		lots_list = []
		for line in self.return_id:				
			for product in line.return_spare_part_ids:
				for service_logs in rec.spare_part_ids:
					if product.product_id.id == service_logs.product_tmpl_id.id:
						for lots in service_logs.serial_ids:
							lots_list.append(lots.id)
		if product.lot_id:
			if not (product.lot_id.id in lots_list):
				raise ValidationError('Please select only the "Serial No" mentioned in Spare Part List')
		location_rec = self.env['stock.location'].search([('name', '=', 'Stock'),('company_id', '=', self.company_id.id)])
		self.location_id = location_rec.id	