# -*- coding: utf-8 -*-
from odoo import fields, models, api


class  CancelRemark(models.TransientModel):
	_name = 'cancel.remark'
	_description = 'PO Cancel Remark Wizard'

	name = fields.Text('Remarks')

	@api.multi
	def action_cancel_remark(self):
		active_id = self.env.context.get('active_id')
		rec = self.env['purchase.order'].browse(int(active_id))		
		rec.write({'cancel_remarks':self.name,'state':'cancel'})
		employee = self.env['hr.employee'].search([('active', '=', True),
												('company_id', '=', rec.company_id.id)])
		for emp in employee:
			if emp.work_email:
				sm_user = emp.user_id.has_group('beep_purchase.group_purchase_store_manager_one')
				hod_user = emp.user_id.has_group('beep_purchase.group_purchase_hod_one')
				if sm_user or hod_user:
					template_id = self.env.ref('beep_purchase.email_template_pr_cancell')
					template_id.write({'email_to': emp.work_email})
					template_id.sudo().send_mail(rec.id, force_send=True)