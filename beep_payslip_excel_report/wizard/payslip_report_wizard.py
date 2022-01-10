from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
# from datetime import datetime, date
import calendar
import datetime

class PayslipReportButton(models.TransientModel):
	_name = 'wizard.payslip.report'


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
	date_from = fields.Date(string='Date From')
	date_to = fields.Date(string='Date To')
	company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True, 
                default=lambda self: self.env.user.company_id)


	def last_day_of_month(self, any_day):
		next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
		return next_month - datetime.timedelta(days=next_month.day)

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

	@api.multi
	def print_payslip_report_xls(self):
		data = {
			'ids': self.ids,
			'model': self._name,
		}
		return self.env.ref('beep_payslip_excel_report.project_xlsx').report_action(self, data=data)
