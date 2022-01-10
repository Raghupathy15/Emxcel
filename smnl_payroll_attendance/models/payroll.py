# -*- coding: utf-8 -*-

from datetime import datetime, time

from odoo import models, api, fields, _
from pytz import timezone


class HRPayslip(models.Model):
	_inherit = "hr.payslip"
	_description = 'Hr Payslip'

	@api.model
	def get_worked_day_lines(self, contracts, date_from, date_to):
		"""
		@param contract: Browse record of contracts
		@return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
		"""
		res = []
		# fill only if the contract as a working schedule linked
		for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
			day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
			day_to = datetime.combine(fields.Date.from_string(date_to), time.max)
			# compute leave days
			leaves = {}
			calendar = contract.resource_calendar_id
			tz = timezone(calendar.tz)
			day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to,
																   calendar=contract.resource_calendar_id)
			for day, hours, leave in day_leave_intervals:
				holiday = leave[:1].holiday_id
				current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
					'name': holiday.holiday_status_id.name or _('Global Leaves'),
					'sequence': 5,
					'code': holiday.holiday_status_id.name or 'GLOBAL',
					'number_of_days': 0.0,
					'number_of_hours': 0.0,
					'contract_id': contract.id,
				})
				current_leave_struct['number_of_hours'] += hours
				work_hours = calendar.get_work_hours_count(
					tz.localize(datetime.combine(day, time.min)),
					tz.localize(datetime.combine(day, time.max)),
					compute_leaves=False,
				)
				# Default Leave Day calculation
				if work_hours and not holiday.holiday_status_id.name:
					current_leave_struct['number_of_days'] += hours / work_hours

			emp_leaves = self.env['hr.leave'].search(
				[('employee_id', '=', contract.employee_id.id), ('state', '=', 'validate'),
				 ('request_date_from', '>=', date_from), ('request_date_to', '<=', date_to)
				 ], order='holiday_status_id')
			for emp_l in emp_leaves:
				for k, v in leaves.items():
					if v['name'] == emp_l.holiday_status_id.name:
						v['number_of_days'] += emp_l.number_of_days_display

			# compute Global Leave days
			# leave_dict = dict((leave['request_date_from'], leave['request_date_to']) for leave in emp_leaves)
			# global_leave_count = 0
			# global_leave_condition = False
			# for g_leave in calendar.global_leave_ids.filtered(
			#         lambda x: x.date_from.date() >= date_from and x.date_to.date() <= date_to):
			#     for lead in leave_dict.items():
			#         if g_leave.date_from.date() >= lead[0] and g_leave.date_to.date() <= lead[1]:
			#             global_leave_condition = True
			#     if not global_leave_condition:
			#         global_leave_count += (g_leave.date_to.date() - g_leave.date_from.date()).days + 1
			# for k, v in leaves.items():
			#     if v['name'] == 'Global Leaves':
			#         v['number_of_days'] = global_leave_count

			# compute worked days
			work_data = contract.employee_id.get_work_days_data(day_from, day_to,
																calendar=contract.resource_calendar_id)
			attendances = {
				'name': _("Normal Working Days paid at 100%"),
				'sequence': 1,
				'code': 'WORK100',
				'number_of_days': work_data['days'],
				'number_of_hours': work_data['hours'],
				'contract_id': contract.id,
			}

			# compute present days
			days_count = 0
			for attn in self.env['hr.attendance'].search(
					[('employee_id', '=', contract.employee_id.id), ('check_in', '!=', False),
					 ('check_out', '!=', False)]):
				if self.employee_id == contract.employee_id and attn.check_in.date() >= date_from and attn.check_out.date() <= date_to:
					if attn.check_out and attn.check_in:
						diff = attn.check_out - attn.check_in
						diff_str = str(diff)
						vals = diff_str.split(':')
						t, hours = divmod(float(vals[0]), 24)
						t, minutes = divmod(float(vals[1]), 60)
						minutes = minutes / 60.0
						var = hours + minutes
						if var >= 8:
							days_count = days_count + 1
			present_hours = days_count * contract.resource_calendar_id.hours_per_day
			present_attendance = {
				'name': _("Normal of present Days"),
				'sequence': 2,
				'code': 'PRESENT',
				'number_of_days': days_count,
				'number_of_hours': present_hours,
				'contract_id': contract.id,
			}
			res.append(attendances)
			res.append(present_attendance)
			res.extend(leaves.values())
		return res


class HRAttendance(models.Model):
	_inherit = "hr.attendance"

	present_hours = fields.Char('Total', compute='compute_present_hours')
	emp_code = fields.Char('Employee Code',compute='compute_emp_id',store=True)

	@api.depends('employee_id')
	def compute_emp_id(self):
		for attendance in self:
			if attendance.employee_id and attendance.employee_id.emp_code:
				attendance.emp_code = attendance.employee_id.emp_code

	@api.model
	def compute_present_hours(self):
		# compute present days
		for attn in self:
			if attn.check_out and attn.check_in:
				diff = attn.check_out - attn.check_in
				attn.present_hours = diff