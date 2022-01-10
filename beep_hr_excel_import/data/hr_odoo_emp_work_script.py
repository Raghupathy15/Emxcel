# -*- coding: utf-8 -*-
# ./odoo-bin shell <  script_path -c project_path -d db_name

from odoo import api, fields, models, _
from datetime import date
import calendar
import xlrd
import os

loc = os.path.join("os.getcwd()", "bitbucket/UAT/erp-smnl/beep_hr_excel_import/data/Emxcel Format - Attendance.xlsx")
# loc = ("/home/emxcel/01_work_space/p_emxcel_project/utk_smnl_erp/bit-qa-smnl-erp/beep_hr_excel_import/data/Emxcel Format - Attendance.xlsx")

wb = xlrd.open_workbook(loc)
emp_sheet = wb.sheet_by_name('Sheet1')
updated_employee_resource_calendar = []

for emp in range(emp_sheet.nrows - 2):
    employee_remark = emp_sheet.cell_value(emp + 2, 4)
    if employee_remark and employee_remark == 'WO':
        employee_code = emp_sheet.cell_value(emp + 2, 0)
        employee_punch_date = xlrd.xldate.xldate_as_datetime(emp_sheet.cell_value(emp + 2, 1), 0).date()
        employee = self.env['hr.employee'].sudo().search([('emp_code', '=', employee_code)])
        employee.write({
            "resource_calendar_id": self.env['resource.calendar'].sudo().search(
                [('name', 'ilike', str(calendar.day_name[employee_punch_date.weekday()]))]).id
        })
        updated_employee_resource_calendar.append(employee_code)
print("\nupdated_employee_resource_calendar==========>\t", set(updated_employee_resource_calendar))
print("\nupdated_employee_resource_calendar count==========>\t", len(set(updated_employee_resource_calendar)))
self.env.cr.commit()
