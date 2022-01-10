# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ReturnRejectRemark(models.TransientModel):
	_name = 'return.reject.remark'
	_description = 'Rejection Remark'

	name = fields.Text('Rejection Remarks')

	def action_spare_reject_remark(self):
		active_id = self.env.context.get('active_id')
		rec = self.env['spare.parts.returns.approval'].browse(int(active_id))
		rec.write({'reject_remarks':self.name,'state':'reject'})