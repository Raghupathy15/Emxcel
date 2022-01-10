from odoo.http import request
from odoo import models, api, fields
import datetime
from dateutil.relativedelta import relativedelta
import calendar
from calendar import monthrange

class PayslipReportXls(models.AbstractModel):
	_name = 'report.payslip_excel_report.project_xlsx'
	_inherit = 'report.report_xlsx.abstract'

	def generate_xlsx_report(self, workbook, data, lines):
		# To get Active id
		active_id = self.env.context.get('active_id')
		wizard = self.env['wizard.payslip.report'].browse(int(active_id))
		payslip = self.env['hr.payslip'].sudo().search([('date_from','>=',wizard.date_from),
														('date_to','<=',wizard.date_to),
														('company_id','=',wizard.company_id.id)],order='number')
		
		# Formats
		heading_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 13,'font_color': '#D70040','border': 1})
		worksheet = workbook.add_worksheet("Payslip Excel Report")
		format1 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3','align':'left','border': 1})
		format2 = workbook.add_format({'font_size': 12, 'bold': True, 'bg_color': '#D3D3D3','align':'center','border': 1})
		format3 = workbook.add_format({'font_size': 10,'align':'center','border': 1})
		format4 = workbook.add_format({'font_size': 10,'align':'left','border': 1})
		
		if wizard.month == 1:
			month = 'January'
		if wizard.month == 2:
			month = 'February'
		if wizard.month == 3:
			month = 'March'
		if wizard.month == 4:
			month = 'April'
		if wizard.month == 5:
			month = 'May'
		if wizard.month == 6:
			month = 'June'
		if wizard.month == 7:
			month = 'July'
		if wizard.month == 8:
			month = 'August'
		if wizard.month == 9:
			month = 'September'
		if wizard.month == 10:
			month = 'October'
		if wizard.month == 11:
			month = 'November'
		if wizard.month == 12:
			month = 'December'

		# Heading
		worksheet.set_column('A:A', 5)
		worksheet.set_column('B:B', 10)
		worksheet.set_column('C:C', 19)
		worksheet.set_column('D:D', 14)
		worksheet.set_column('E:E', 14)
		worksheet.set_column('F:F', 14)
		worksheet.set_column('G:G', 6)
		worksheet.set_column('H:H', 10)
		worksheet.set_column('I:I', 6)
		worksheet.set_column('J:J', 6)
		worksheet.set_column('K:K', 11)
		worksheet.set_column('L:L', 11)
		worksheet.insert_image('B1', '/home/user/Workspace/odoo12/erp-smnl/beep_payslip_excel_report/static/description/smnl_logo.png', {'x_scale': 0.6, 'y_scale': 0.8})
		worksheet.merge_range('A1:L2', ('Employee Payslip Report for the Month of ') + str(month)+ ' - '+str(wizard.year), heading_format)
		worksheet.write('A3',"S.No", format2)
		worksheet.write('B3',"Payslip No", format2)
		worksheet.write('C3',"Name", format2)
		worksheet.write('D3',"Department", format2)
		worksheet.write('E3',"Designation", format2)
		worksheet.write('F3',"Remaining Leaves", format1)
		worksheet.write('G3',"Basic", format2)
		worksheet.write('H3',"Allowance", format2)
		worksheet.write('I3',"Gross", format2)
		worksheet.write('J3',"CTC", format2)
		worksheet.write('K3',"Total Deduction", format1)
		worksheet.write('L3',"Net Payable", format1)
		
		# datas/Values
		s_no = 0
		row = 3
		column = 0
		emp_id = []
		for value in payslip:
			if value:
				s_no += 1
				worksheet.write(row, column, s_no, format3)
				worksheet.write(row, column+1,value.number, format3)
				worksheet.write(row, column+2,value.employee_id.name, format4)
				worksheet.write(row, column+3,value.employee_id.department_id.name, format3)
				worksheet.write(row, column+4,value.employee_id.job_id.name, format3)
				worksheet.write(row, column+5,value.employee_id.remaining_leaves, format3)
				if value.line_ids:
					for line in value.line_ids:
						if line.code == "BASIC":
							worksheet.write(row, column+6,line.amount, format3)
						if line.code == "ALW":
							worksheet.write(row, column+7,line.amount, format3)
						if line.code == "GROSS":
							worksheet.write(row, column+8,line.amount, format3)
						if line.code == "CTC":
							worksheet.write(row, column+9,line.amount, format3)
						if line.code == "TD":
							worksheet.write(row, column+10,line.amount, format3)
						if line.code == "NET":
							worksheet.write(row, column+11,line.amount, format3)
				row += 1
		