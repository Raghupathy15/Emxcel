# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrLeaveApproval(models.Model):
	_inherit = 'hr.leave'

	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, readonly=True)
	emp_code = fields.Char('Employee Code',compute='compute_emp_id',store=True)
	medical_certificate = fields.Binary('Medical Certificate')
	attach_medical_certificate = fields.Char("Medical Certificate")
	is_special_leave = fields.Boolean("Special Leave")


	@api.onchange('holiday_status_id')
	def onchange_holiday_status_id(self):
		for leave in self:
			if leave.holiday_status_id.name == 'Special Leave':
				leave.is_special_leave = True
			else:
				leave.is_special_leave = False


	@api.depends('employee_id')
	def compute_emp_id(self):
		for leave in self:
			if leave.employee_id and leave.employee_id.emp_code:
				leave.emp_code = leave.employee_id.emp_code

	def action_create_special_leaves(self):
		leave = self.env['hr.leave.allocation']
		employee = self.env['hr.employee'].search([('company_id','=',self.company_id.id)])
		count = 0
		for emp in employee:
			leave_type_spl = self.env['hr.leave.type'].search([('name','=','Special Leave')])
			check_spl = self.env['hr.leave.allocation'].search([('holiday_status_id.name','=','Special Leave'),('employee_id','=',emp.id)])
			if not check_spl:
				spl = leave.create({'name':'Special Leave',
									'holiday_type': 'employee',
									'employee_id': emp.id,
									'holiday_status_id': leave_type_spl.id,
									'number_of_days': 14,
									'state': 'validate',
									})
				count = count + 1
				print('Total Leaves created',count)

	@api.multi
	def action_approve(self):
		# if validation_type == 'both': this method is the first approval approval
		# if validation_type != 'both': this method calls action_validate() below
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		admin_group = self.env['res.users'].has_group('base.group_system')
		hr_manager = self.env['res.users'].has_group('hr.group_hr_manager')
		employee_group = self.employee_id.user_id.has_group('hr.group_hr_manager')
		# Admin can approve all leave in first level approve
		if admin_group and self.holiday_status_id.double_validation:
			if any(holiday.state != 'confirm' for holiday in self):
				raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))
			self.filtered(lambda hol: not hol.validation_type != 'both').action_validate()
			if not self.env.context.get('leave_fast_create'):
				self.activity_update()
		# Hr manager can approve all records
		elif hr_manager and self.holiday_status_id.double_validation:
			if any(holiday.state != 'confirm' for holiday in self):
				raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))
			self.filtered(lambda hol: not hol.validation_type != 'both').action_validate()
			if not self.env.context.get('leave_fast_create'):
				self.activity_update()
		# If double validation is false
		elif current_employee == self.employee_id.parent_id and not self.holiday_status_id.double_validation:
			raise UserError(_('You must enable double validation in leave type.'))
		# Employee manager can approve first level
		elif current_employee == self.employee_id.parent_id:
			if any(holiday.state != 'confirm' for holiday in self):
				raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))
			self.filtered(lambda hol: hol.validation_type == 'both').write(
				{'state': 'validate1', 'first_approver_id': current_employee.id})
			if not self.env.context.get('leave_fast_create'):
				self.activity_update()
		else:
			raise UserError(_('You are not authorized user!'))
		return True

	@api.multi
	def action_validate(self):
		current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
		user_group = self.env['res.users'].has_group('hr.group_hr_manager')
		if user_group:
			if any(holiday.state not in ['confirm', 'validate1'] for holiday in self):
				raise UserError(_('Leave request must be confirmed in order to approve it.'))

			self.write({'state': 'validate'})
			self.filtered(lambda holiday: holiday.validation_type == 'both').write(
				{'second_approver_id': current_employee.id})
			self.filtered(lambda holiday: holiday.validation_type != 'both').write(
				{'first_approver_id': current_employee.id})

			for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'employee'):
				if holiday.holiday_type == 'category':
					employees = holiday.category_id.employee_ids
				elif holiday.holiday_type == 'company':
					employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
				else:
					employees = holiday.department_id.member_ids

				if self.env['hr.leave'].search_count(
						[('date_from', '<=', holiday.date_to), ('date_to', '>', holiday.date_from),
						 ('state', 'not in', ['cancel', 'refuse']), ('holiday_type', '=', 'employee'),
						 ('employee_id', 'in', employees.ids)]):
					raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

				values = [holiday._prepare_holiday_values(employee) for employee in employees]
				leaves = self.env['hr.leave'].with_context(
					tracking_disable=True,
					mail_activity_automation_skip=True,
					leave_fast_create=True,
				).create(values)
				leaves.action_approve()
				# FIXME RLi: This does not make sense, only the parent should be in validation_type both
				if leaves and leaves[0].validation_type == 'both':
					leaves.action_validate()
			employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
			employee_requests._validate_leave_request()
			if not self.env.context.get('leave_fast_create'):
				employee_requests.activity_update()
			return True
		else:
			raise UserError(_('You are not authorized user!'))
