# -*- coding: utf-8 -*-
# Install Library: sudo -H pip3 install OdooRPC
# python3 hr_emp_work_script.py
import xlrd
import calendar
import odoorpc
import os
from datetime import date

# Global Variables
HOST = "65.0.43.50"
USER = "admin"
PSWD = "SMNL@EMXCEL"
DB = "UAT"
PORT = "5432"
odoo = odoorpc.ODOO("65.0.43.50", port=8069)
leaves_not_created = []
employee_not_found = []

odoo.login(DB, USER, PSWD)
user = odoo.env.user
loc = os.path.join("os.getcwd()",
                   "bitbucket/UAT/erp-smnl/beep_hr_excel_import/data/187. March Attendance Upload 1-25.xlsx")
# loc = "/home/emxcel/01_work_space/p_emxcel_project/utk_smnl_erp/bit-qa-smnl-erp/beep_hr_excel_import/data/187. March Attendance Upload 1-25.xlsx"
wb = xlrd.open_workbook(loc)
emp_sheet = wb.sheet_by_name('Sheet3')
print("Script Started")
updated_employee_resource_calendar = []
not_updated_employee_resource_calendar = []
for emp in range(emp_sheet.nrows - 2):
    employee_remark = emp_sheet.cell_value(emp + 2, 4)
    if employee_remark and employee_remark == 'WO':
        employee_code = emp_sheet.cell_value(emp + 2, 0)
        employee_punch_date = xlrd.xldate.xldate_as_datetime(emp_sheet.cell_value(emp + 2, 1), 0).date()
        emp_rec = odoo.env['hr.employee'].search([('emp_code', '=like', '%' + employee_code)])
        employee = odoo.env['hr.employee'].browse(emp_rec)
        work_calender = odoo.env['resource.calendar'].search(
            [('name', 'ilike', str(calendar.day_name[employee_punch_date.weekday()]))])[0] or False
        if work_calender:
            employee.write({"resource_calendar_id": work_calender})
            updated_employee_resource_calendar.append(employee_code)
        else:
            not_updated_employee_resource_calendar.append(employee_code)

print("\nupdated_employee_resource_calendar==========>\t", set(updated_employee_resource_calendar))
print("\nupdated_employee_resource_calendar count==========>\t", len(set(updated_employee_resource_calendar)))
print("\nnot_updated_employee_resource_calendar==========>\t", set(not_updated_employee_resource_calendar))
print("\nnot_updated_employee_resource_calendar count==========>\t", len(set(not_updated_employee_resource_calendar)))
