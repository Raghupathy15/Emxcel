# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from odoo import models, api, fields, tools, _
from odoo.exceptions import ValidationError, UserError
import babel


class HrPayslip(models.Model):
	_inherit = 'hr.payslip'
	_description = 'Pay Slip'


	@api.multi
	def _compute_leaves(self):
		for rec in self:
			# Calculate remaining CL
			allocation_cl = self.env['hr.leave.allocation'].search([('employee_id', '=', rec.employee_id.id), 
																	('holiday_status_id.name', '=', 'Casual Leave'), 
																	('state', '=', 'validate')])
			cl_leaves_count = 0
			for cl in allocation_cl:
				rec.remaining_cl += cl.number_of_days_display
			cl_leaves_count = cl.number_of_days_display
			leave_cl = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
													('holiday_status_id.name', '=', 'Casual Leave'),
													('state', '=', 'validate')])
			if leave_cl:
				for leaves_obj in leave_cl:
					cl_leaves_count = cl_leaves_count - leaves_obj.number_of_days_display
					rec.remaining_cl = cl_leaves_count
			else:
				rec.remaining_cl = cl_leaves_count	
			
			# Calculate remaining PL
			allocation_pl = self.env['hr.leave.allocation'].search([('employee_id', '=', rec.employee_id.id), 
																	('holiday_status_id.name', '=', 'Privilege Leave'), 
																	('state', '=', 'validate')])
			pl_leaves_count = 0
			for pl in allocation_pl:
				rec.remaining_pl += pl.number_of_days_display
			pl_leaves_count = pl.number_of_days_display
			leave_pl = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
													('holiday_status_id.name', '=', 'Privilege Leave'),
													('state', '=', 'validate')])
			if leave_pl:
				for leaves_pl in leave_pl:
					pl_leaves_count = pl_leaves_count - leaves_pl.number_of_days_display
					rec.remaining_pl = pl_leaves_count
			else:
				rec.remaining_pl = pl_leaves_count
			
			# Calculate remaining SL
			allocation_sl = self.env['hr.leave.allocation'].search([('employee_id', '=', rec.employee_id.id), 
																	('holiday_status_id.name', '=', 'Sick Leave'), 
																	('state', '=', 'validate')])
			sl_leaves_count = 0
			for sl in allocation_sl:
				rec.remaining_sl += sl.number_of_days_display
			sl_leaves_count = sl.number_of_days_display
			leave_sl = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
													('holiday_status_id.name', '=', 'Sick Leave'),
													('state', '=', 'validate')])
			if leave_sl:
				for leaves_sl in leave_sl:
					sl_leaves_count = sl_leaves_count - leaves_sl.number_of_days_display
					rec.remaining_sl = sl_leaves_count
			else:
				rec.remaining_sl = sl_leaves_count

			# Calculate remaining SPL
			allocation_spl = self.env['hr.leave.allocation'].search([('employee_id', '=', rec.employee_id.id), 
																	('holiday_status_id.name', '=', 'Special Leave'), 
																	('state', '=', 'validate')])
			spl_leaves_count = 0
			for spl in allocation_spl:
				spl_leaves_count += spl.number_of_days_display
			leave_spl = self.env['hr.leave'].search([('employee_id', '=', rec.employee_id.id),
													('holiday_status_id.name', '=', 'Special Leave'),
													('state', '=', 'validate')])
			if leave_spl:
				for leaves_spl in leave_spl:
					spl_leaves_count = spl_leaves_count - leaves_spl.number_of_days_display
					rec.remaining_spl = spl_leaves_count
			else:
				rec.remaining_spl = spl_leaves_count

	govt_basic = fields.Float('Govt. Allowed Minimum Basic', required=True)
	emp_code = fields.Char('Employee Code',compute='compute_emp_id',store=True)
	remaining_leaves = fields.Float(related='employee_id.remaining_leaves',string="Total Remaining Leaves")
	remaining_cl = fields.Float(compute=_compute_leaves,string="Remaining CL")
	remaining_pl = fields.Float(compute=_compute_leaves,string="Remaining PL")
	remaining_sl = fields.Float(compute=_compute_leaves,string="Remaining SL")
	remaining_spl = fields.Float(compute=_compute_leaves,string="Remaining SPL")

	@api.depends('employee_id')
	def compute_emp_id(self):
		for payslip in self:
			if payslip.employee_id and payslip.employee_id.emp_code:
				payslip.emp_code = payslip.employee_id.emp_code

	@api.multi
	def compute_sheet(self):
		res = super(HrPayslip, self).compute_sheet()
		for rec in self:
			if rec.contract_id.wage < rec.govt_basic:
				raise ValidationError(
					_('"Basic salary" (%s) Should be greater than "Govt. Allowed Minimum Basic" (%s)' % (
						rec.contract_id.wage, rec.govt_basic)))
		return res

	@api.onchange('employee_id')
	def onchange_employee_id(self):
		employee = self.env['hr.employee'].search(
			[('id', '=', self.employee_id.id)])
		if employee:
			self.govt_basic = employee.govt_basic

	# @api.multi
	# def action_payslip_done(self):
	#     res = super(HrPayslip, self).action_payslip_done()
	#     if self.line_ids:
	#         for line in self.line_ids:
	#             if line.category_id.name == 'Basic':
	#                 if line.amount < self.govt_basic:
	#                     raise ValidationError(
	#                         _('"Basic salary" should be greater than "Govt. Allowed Minimum Basic"'))
	#     return res

	@api.model
	def _get_current_year(self):
		now = datetime.datetime.now()
		return now.year

	month = fields.Selection(selection=[(1, 'January'), (2, 'February'), (3, 'March'),
										(4, 'April'), (5, 'May'), (6, 'June'),
										(7, 'July'), (8, 'August'), (9, 'September'),
										(10, 'October'), (11, 'November'), (12, 'December')],
							 required=True, string="Month", help="Month")
	year = fields.Char("Year", default=_get_current_year,
					   size=4, required=True)
	date_from = fields.Date(string='Date From',
							states={'draft': [('readonly', False)]})
	date_to = fields.Date(string='Date To tttt',
						  states={'draft': [('readonly', False)]})

	def last_day_of_month(self, any_day):
		# this will never fail
		# get close to the end of the month for any day, and add 4 days 'over'
		next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
		# subtract the number of remaining 'overage' days to get last day of current month, or said programattically said, the previous day of the first of next month
		return next_month - datetime.timedelta(days=next_month.day)

	@api.multi
	def write(self, vals):
		# Update date from and date to field.
		month = vals.get('month') or self.month
		if month:
			now = datetime.datetime.now()
			year = int(vals.get('year') or self.year)
			if not year:
				year = int(now.year)
			vals.update({'date_from': datetime.date(year, month, 1)})
			vals.update({'date_to': self.last_day_of_month(
				datetime.date(year, month, 1))})
		ret = super(HrPayslip, self).write(vals)
		return ret

	@api.model
	def create(self, vals):
		# Update field date from and dte to while create
		ret = super(HrPayslip, self).create(vals)
		if ret.month:
			now = datetime.datetime.now()
			year = int(ret.year)
			if not year:
				year = int(now.year)
			ret.date_from = datetime.date(year, ret.month, 1)
			ret.date_to = ret.last_day_of_month(
				datetime.date(year, ret.month, 1))
		return ret

	@api.onchange('month', 'year')
	def onchange_month_set_period(self):
		# onchange update fields
		if self.month:
			now = datetime.datetime.now()
			year = int(self.year)
			if not year:
				year = int(now.year)
			self.date_from = datetime.date(year, self.month, 1)
			self.date_to = self.last_day_of_month(
				datetime.date(year, self.month, 1))
			# self.last_day_of_month(datetime.date(self.year, self.month, 1)))

	@api.multi
	def _cron_create_auto_payslip(self):
		from datetime import datetime
		month = datetime.today().date().strftime('%-m')
		day = datetime.today().date().strftime('%-d')
		year = datetime.today().date().strftime('%Y')
		# if day == 5:
		emp = self.env['hr.employee'].search([('active', '=', True)])
		for employee in emp:
			contract = self.env['hr.contract'].search([('employee_id', '=', employee.id), ('active', '=', True)],
													  order='id desc', limit=1)
			payslip = self.create({'employee_id': employee.id,
								   'month': int(month) - 1 if int(month) > 1 else 12,
								   'year': int(year) - 1 if int(month) == 1 else year,
								   'govt_basic': employee.govt_basic,
								   'struct_id': contract.struct_id.id,
								   'contract_id': contract.id})

	@api.multi
	def _cron_compute_auto_payslip(self):
		from datetime import datetime
		emp = []
		month_val = datetime.today().date().strftime('%-m')
		month = int(month_val) - 1 if int(month_val) > 1 else 12
		year_val = datetime.today().date().strftime('%Y')
		year = int(year_val) - 1 if int(month) == 12 else year_val
		payslip = self.env['hr.payslip'].search([('month', '=', month), ('year', '=', year)])
		for record in payslip:
			try:
				record.update(
					{'name': ('Salary Slip of %s for %s-%s') % (record.employee_id.name, record.month, record.year)})
				record.compute_sheet()
			except:
				emp.append(record.employee_id)
				pass

	# The below code is written for "Payslip batches issueS"
	# YTI TODO To rename. This method is not really an onchange, as it is not in any view
	# employee_id and contract_id could be browse records
	@api.multi
	def onchange_employee_id(self, date_from, date_to, employee_id=False):
		#defaults
		res = {
			'value': {
				'line_ids': [],
				#delete old input lines
				'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
				#delete old worked days lines
				'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
				#'details_by_salary_head':[], TODO put me back
				'name': '',
				'contract_id': False,
				'struct_id': False,
			}
		}
		if (not employee_id) or (not date_from) or (not date_to):
			return res
		# ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
		employee = self.env['hr.employee'].browse(employee_id)
		locale = self.env.context.get('lang') or 'en_US'
		res['value'].update({
			'name': _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(format='MMMM-y', locale=locale))),
			'company_id': employee.company_id.id,
		})

		if not self.env.context.get('contract'):
			#fill with the first contract of the employee
			contract_ids = self.get_contract(employee, date_from, date_to)
		else:
			if contract_id:
				#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
				#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(employee, date_from, date_to)

		if not contract_ids:
			return res
		contract = self.env['hr.contract'].browse(contract_ids[0])
		res['value'].update({
			'contract_id': contract.id
		})
		struct = contract.struct_id
		if not struct:
			return res
		res['value'].update({
			'struct_id': struct.id,
		})
		#computation of the salary input
		contracts = self.env['hr.contract'].browse(contract_ids)
		worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
		input_line_ids = self.get_inputs(contracts, date_from, date_to)
		res['value'].update({
			'worked_days_line_ids': worked_days_line_ids,
			'input_line_ids': input_line_ids,
		})
		return res


class HrPayslipEmployees(models.TransientModel):
	_inherit = 'hr.payslip.employees'
	_description = 'Generate payslips for all selected employees'


	@api.multi
	def compute_sheet(self):
		payslips = self.env['hr.payslip']
		[data] = self.read()
		active_id = self.env.context.get('active_id')
		if active_id:
			[run_data] = self.env['hr.payslip.run'].browse(active_id).read(['date_start', 'date_end', 'credit_note'])
		from_date = run_data.get('date_start')
		to_date = run_data.get('date_end')
		if not data['employee_ids']:
			raise UserError(_("You must select employee(s) to generate payslip(s)."))
		for employee in self.env['hr.employee'].browse(data['employee_ids']):
			slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id)
			res = {
				'employee_id': employee.id,
				'name': slip_data['value'].get('name'),
				'struct_id': slip_data['value'].get('struct_id'),
				'contract_id': slip_data['value'].get('contract_id'),
				'payslip_run_id': active_id,
				'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids')],
				'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids')],
				'date_from': from_date,
				'date_to': to_date,
				'credit_note': run_data.get('credit_note'),
				'company_id': employee.company_id.id,
			}
			payslips += self.env['hr.payslip'].create(res)
		payslips.compute_sheet()
		return {'type': 'ir.actions.act_window_close'}