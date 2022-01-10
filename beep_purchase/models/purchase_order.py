# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
	_inherit = "purchase.order"


	@api.multi
	@api.depends('name')
	def _compute_po_name(self):
		for purchase in self:
			if purchase.name != 'New':
				purchase.update({'pr_sequence': 'PR'+''+purchase.name[2:]})

	partner_id = fields.Many2one('res.partner', string='Vendor', 
								required=False,
								change_default=True, 
								track_visibility='always', 
								help="You can find a vendor by its Name, TIN, Email or Internal Reference.")
	state = fields.Selection([
		('draft', 'PR'),
		('sent', 'RFQ Sent'),
		('req_store_manager_app_1', 'Requested SM 1st Approval'),
		('req_hod_app', 'Requested HOD Approval'),
		('req_store_manager_app_2', 'Requested SM 2nd Approval'),
		('sm_approved', 'SM Approved'),
		('to approve', 'To Approve'),
		('purchase', 'Purchase Order'),
		('done', 'Locked'),
		('cancel', 'Cancelled')
	], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
	cancel_remarks = fields.Text(string='Cancel Remarks',track_visibility='always')
	requisition_id = fields.Many2one('purchase.requisition', string='Purchase Agreement', copy=False, readonly=True)
	is_po_requisition = fields.Boolean(string='Purchase Requisition',compute='_compute_po_requisition')
	is_po_confirmed = fields.Boolean(string='PO confirmed')
	pr_sequence = fields.Char('Order Reference',store=True, copy=False,compute='_compute_po_name')


	@api.multi
	@api.depends('requisition_id')
	def _compute_po_requisition(self):
		for po in self:
			if po.requisition_id:
				po.update({'is_po_requisition':True})

	@api.multi
	def print_po(self):
		return self.env.ref('purchase.action_report_purchase_order').report_action(self)

	@api.multi
	def button_sm_request(self):
		employee = self.env['hr.employee'].search([('active', '=', True),
												('company_id', '=', self.company_id.id)])
		for emp in employee:
			if emp.work_email:
				sm_user = emp.user_id.has_group('beep_purchase.group_purchase_store_manager_one')
				hod_user = emp.user_id.has_group('beep_purchase.group_purchase_hod_one')
				if sm_user or hod_user:
					template_id = self.env.ref('beep_purchase.email_template_button_sm_request')
					template_id.write({'email_to': emp.work_email})
					template_id.sudo().send_mail(self.id, force_send=True)
		self.write({'state': 'req_store_manager_app_1'})

	@api.multi
	def button_req_sm_approve_1(self):
		employee = self.env['hr.employee'].search([('active', '=', True),
												('company_id', '=', self.company_id.id)])
		for emp in employee:
			if emp.work_email:
				sm_user = emp.user_id.has_group('beep_purchase.group_purchase_store_manager_one')
				hod_user = emp.user_id.has_group('beep_purchase.group_purchase_hod_one')
				if sm_user or hod_user:
					template_id = self.env.ref('beep_purchase.email_template_button_sm_approval')
					template_id.write({'email_to': emp.work_email})
					template_id.sudo().send_mail(self.id, force_send=True)
		self.write({'state': 'req_hod_app'})

	@api.multi
	def button_direct_sm_approve(self):
		self.write({'state': 'sm_approved'})

	@api.multi
	def button_req_sm_approve_2(self):
		employee = self.env['hr.employee'].search([('active', '=', True),
												('company_id', '=', self.company_id.id)])
		for emp in employee:
			if emp.work_email:
				sm_user = emp.user_id.has_group('beep_purchase.group_purchase_store_manager_one')
				hod_user = emp.user_id.has_group('beep_purchase.group_purchase_hod_one')
				if sm_user or hod_user:
					template_id = self.env.ref('beep_purchase.email_template_button_sm_approval_2')
					template_id.write({'email_to': emp.work_email})
					template_id.sudo().send_mail(self.id, force_send=True)
		for purchase in self:
			po_requisition = self.env['purchase.requisition']
			po_requisition_line = self.env['purchase.requisition.line']
			po_obj = po_requisition.create({
											'type_id':2,
											'company_id': self.env.user.company_id.id,
											'state':'draft'
											})
			for line in purchase.order_line:
				po_obj_line = po_requisition_line.create({
													'product_id': line.product_id.id,
													'requisition_id': po_obj.id,
													'product_uom_id': line.product_uom.id,
													'product_qty': line.product_qty,
													'price_unit': line.price_unit,
													})
			po_obj.action_in_progress()
		self.write({'requisition_id': po_obj.id,'origin': po_obj.name,'state': 'sm_approved'})

	@api.multi
	def button_hod_approve(self):
		employee = self.env['hr.employee'].search([('active', '=', True),
												('company_id', '=', self.company_id.id)])
		for emp in employee:
			if emp.work_email:
				sm_user = emp.user_id.has_group('beep_purchase.group_purchase_store_manager_one')
				hod_user = emp.user_id.has_group('beep_purchase.group_purchase_hod_one')
				if sm_user or hod_user:
					template_id = self.env.ref('beep_purchase.email_template_button_hod_approval')
					template_id.write({'email_to': emp.work_email})
					template_id.sudo().send_mail(self.id, force_send=True)
		self.write({'state': 'req_store_manager_app_2'})

	@api.multi
	def action_confirm_pr(self):
		self.write({'state': 'draft'})

	def button_cancel(self):
		form_view = self.env.ref('beep_purchase.cancel_remark_view_id')
		return {
				'name': "Cancel Remarks",
				'view_mode': 'form',
				'view_type': 'form',
				'view_id': form_view.id,
				'res_model': 'cancel.remark',
				'type': 'ir.actions.act_window',
				'target': 'new',
			}

	# To add the custom state 'sm_approved'
	@api.multi
	def button_confirm(self):
		for order in self:
			if not order.partner_id:
				raise ValidationError(_("Please select the vendor before confirming the order"))
			if order.requisition_id:
				purchase_obj = self.env['purchase.order'].search([('requisition_id', '=', order.requisition_id.id),
																('state','not in',('purchase','cancel')),
																('id', '!=', order.id),])
				if purchase_obj:
					for purchase in purchase_obj:
						purchase.state = 'cancel'
						purchase.cancel_remarks = 'Auto cancelled due to another vendor is confirmed this purchase aggrement'
			if order.state not in ['draft', 'sent', 'sm_approved']:
				continue
			order._add_supplier_to_product()
			# Deal with double validation process
			if order.company_id.po_double_validation == 'one_step' \
					or (order.company_id.po_double_validation == 'two_step' \
						and order.amount_total < self.env.user.company_id.currency_id._convert(
						order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
						order.date_order or fields.Date.today())) \
					or order.user_has_groups('purchase.group_purchase_manager'):
				order.button_approve()
			else:
				order.write({'state': 'to approve'})
		order.write({'is_po_confirmed': True})
		return True

class purchase_order_line(models.Model):
	_inherit = 'purchase.order.line'

	discount = fields.Float('Discount %')
	discount_unit_price = fields.Float('Discount Unit Price')
	qty_available = fields.Float(
		related="product_id.qty_available", string='Available Quantity')
	last_po_price = fields.Float('Last Purchase Price', help="Shows the last purchase price of the product for selected supplier from the Past two Purchase order", readonly=True)


	@api.depends('product_qty', 'price_unit', 'taxes_id','discount','discount_unit_price')
	def _compute_amount(self):
		for line in self:
			if line.discount == 0:
				line.discount_unit_price = line.price_unit
			if line.discount > line.price_unit:
				raise ValidationError(_("Discount should be less than Unit Price"))
			taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
			if line.discount:
				discount = (line.price_unit * line.discount * line.product_qty)/100
				line.update({
					'price_tax': taxes['total_included'] - taxes['total_excluded'],
					'price_total': taxes['total_included'] ,
					'discount_unit_price': line.price_unit - line.discount,
					'price_subtotal': taxes['total_excluded'] - discount,
				})
			else:
				line.update({
					'price_tax': taxes['total_included'] - taxes['total_excluded'],
					'price_total': taxes['total_included'],
					'price_subtotal': taxes['total_excluded'],
				})

	# To get the latest price of the product for the selected customer.
	@api.onchange('product_id')
	def onchange_product_id(self):
		super(purchase_order_line, self).onchange_product_id()
		result = {}
		last_price = 0.0
		for record in self:
			line_ids = []
			if record.product_id:
				purchase_lines = self.env['purchase.order.line'].sudo().search([('partner_id', '=', record.partner_id.id),('product_id', '=', record.product_id.id),('order_id.state','in',('purchase','done'))])
				if purchase_lines:
					for lines in purchase_lines:
						line_ids.append(lines.id)
			final_list = sorted(line_ids, key=int, reverse=True)
			if len(final_list)>=1:
				last_price = self.env['purchase.order.line'].sudo().browse(final_list[0])
				record.last_po_price = last_price.price_unit