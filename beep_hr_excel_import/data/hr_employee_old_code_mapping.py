# -*- coding: utf-8 -*-
# ./odoo-bin shell <  script_path -c project_path -d db_name

from odoo import api, fields, models, _
import xlrd

loc = (
    "/home/emxcel/01_work_space/p_emxcel_project/utk_smnl_erp/bit-qa-smnl-erp/beep_hr_excel_import/data/hr_employee_old_code_mapping.xlsx")
wb = xlrd.open_workbook(loc)

emp_sheet = wb.sheet_by_index(1)

non_create_employee_code = []
create_employee_code = []
for emp in range(emp_sheet.nrows - 1):
    old_employee_code = emp_sheet.cell_value(emp + 1, 1)
    employee_name = emp_sheet.cell_value(emp + 1, 4)
    if emp_sheet.cell_value(emp + 1, 17) != '-':
        employee_aadhar_no = int(emp_sheet.cell_value(emp + 1, 17))

    employee = self.env['hr.employee'].sudo().search([('identification_id', '=', employee_aadhar_no)])
    if employee:
        employee.sudo().write({'old_emp_code': old_employee_code})
        create_employee_code.append(employee_name)
    else:
        non_create_employee_code.append(employee_name)

print("\nNot updated code -> employee name are:\n", non_create_employee_code)
print("\nNot updated code -> employee count:\n", len(non_create_employee_code))
print("\nUpdated code -> employee name are:\n", create_employee_code)
print("\nUpdated code -> employee count:\n", len(create_employee_code))
self.env.cr.commit()
