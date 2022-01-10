# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class SparePartReturnsApproval(models.Model):
	_name = "spare.parts.returns.approval"
	_inherit = 'mail.thread'
	_description = "Spare Part Returns Approval"
	
	
	name = fields.Char(string='Sequence No')	
	product_id = fields.Many2one('product.template', 'Product', required=True)
	part_number = fields.Char('Part Number')
	qty = fields.Float('Quantity', help="The total number of products you need to return")
	state = fields.Selection([('wfa', 'Waiting for Approval'),
							('approve', 'Approved'),
							('reject', 'Rejected')],string="State",
							track_visibility='always', default="wfa")
	reject_remarks = fields.Text(string='Rejection Remarks')
	note = fields.Text(string='Notes')
	service_log_id = fields.Many2one('fleet.vehicle.log.services',string='vehicle service log')
	location_id = fields.Many2one('stock.location', 'Return Location', track_visibility='always')
	lot_id = fields.Many2one('stock.production.lot', 'Serial No', index=True,
        ondelete='restrict', readonly=False)
	company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True, 
				default=lambda self: self.env.user.company_id)

	@api.multi
	def button_approve(self):
		if not self.location_id:
			raise ValidationError('Please select the Return location for the product')
		for spare_return in self:
			stock = self.env['stock.quant']
			stock_obj = stock.sudo().create({'product_id': spare_return.product_id.id,
									'quantity': spare_return.qty,
									'location_id':spare_return.location_id.id,
									'lot_id': spare_return.lot_id.id,
									})
			self.write({'state': 'approve'})

	def button_reject(self):
		form_view = self.env.ref('smnl_spare_parts_returns.reject_details_view_id')
		return {
				'name': "Return Reject Remarks",
				'view_mode': 'form',
				'view_type': 'form',
				'view_id': form_view.id,
				'res_model': 'return.reject.remark',
				'type': 'ir.actions.act_window',
				'target': 'new',
			}