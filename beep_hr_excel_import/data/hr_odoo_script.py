# -*- coding: utf-8 -*-
# ./odoo-bin shell <  script_path -c project_path -d db_name

from odoo import api, fields, models, _
import xlrd

loc = (
    "/home/emxcel/01_work_space/p_emxcel_project/utk_smnl_erp/bit-qa-smnl-erp/beep_hr_excel_import/data/employee_and_contract_creation.xlsx")
wb = xlrd.open_workbook(loc)

sheet = wb.sheet_by_index(0)
emp_sheet = wb.sheet_by_index(1)

non_create_department = []
non_create_job_position = []
non_create_section = []
non_create_employee = []
for i in range(52 - 1):
    department_name = sheet.cell_value(i + 2, 0)
    department_code = sheet.cell_value(i + 2, 1)
    if not self.env['hr.department'].sudo().search(
            ['|', ('name', '=', department_name), ('department_code', '=', department_code)]):
        department = self.env['hr.department'].sudo().create(
            {'name': department_name, 'department_code': department_code})
    else:
        non_create_department.append(department_name)

for j in range(118 - 1):
    job_position_name = sheet.cell_value(j + 2, 3)
    job_position_code = sheet.cell_value(j + 2, 4)
    if not self.env['hr.job'].sudo().search(
            ['|', ('name', '=', job_position_name), ('code', '=', job_position_code)]):
        job_position = self.env['hr.job'].sudo().create(
            {'name': job_position_name, 'code': job_position_code})
    else:
        non_create_job_position.append(job_position_name)

for k in range(21 - 1):
    section_name = sheet.cell_value(k + 2, 6)
    section_code = sheet.cell_value(k + 2, 7)
    if not self.env['hr.section'].sudo().search(
            ['|', ('name', '=', section_name), ('code', '=', section_code)]):
        job_position = self.env['hr.section'].sudo().create(
            {'name': section_name, 'code': section_code})
    else:
        non_create_section.append(section_name)

for emp in range(emp_sheet.nrows - 2):
    employee_name = emp_sheet.cell_value(emp + 2, 1)
    employee_department = emp_sheet.cell_value(emp + 2, 3)
    employee_job_position = emp_sheet.cell_value(emp + 2, 4)
    employee_work_mobile = emp_sheet.cell_value(emp + 2, 5)
    if emp_sheet.cell_value(emp + 2, 8) != '-':
        employee_aadhar_number = int(emp_sheet.cell_value(emp + 2, 8))
    employee_marital = emp_sheet.cell_value(emp + 2, 14)
    employee_date_of_birth = emp_sheet.cell_value(emp + 2, 15)
    employee_place_of_birth = emp_sheet.cell_value(emp + 2, 16)
    employee_first_name = emp_sheet.cell_value(emp + 2, 17)
    employee_middle_name = emp_sheet.cell_value(emp + 2, 18)
    employee_last_name = emp_sheet.cell_value(emp + 2, 19)
    employee_pan = emp_sheet.cell_value(emp + 2, 20)
    employee_uan = emp_sheet.cell_value(emp + 2, 21)
    employee_pf_no = emp_sheet.cell_value(emp + 2, 22)
    employee_payment_type = emp_sheet.cell_value(emp + 2, 23)
    employee_esic_no = emp_sheet.cell_value(emp + 2, 25)
    employee_religion = emp_sheet.cell_value(emp + 2, 26)
    employee_location = emp_sheet.cell_value(emp + 2, 27)
    employee_section = emp_sheet.cell_value(emp + 2, 28)
    employee_type = emp_sheet.cell_value(emp + 2, 31)
    employee_notice_period = emp_sheet.cell_value(emp + 2, 32)
    employee_actual_date_of_joining = emp_sheet.cell_value(emp + 2, 33)

    if not self.env['hr.employee'].sudo().search([('identification_id', '=', employee_aadhar_number)]) and len(str(employee_aadhar_number)) == 12:
        employee = self.env['hr.employee'].sudo().create({
            'name': employee_name,
            'department_id': self.env['hr.department'].sudo().search([('name', '=', employee_department)]).id or False,
            'job_id': self.env['hr.job'].sudo().search([('name', '=', employee_job_position)]).id or False,
            # 'mobile_phone': employee_work_mobile or False,
            'identification_id': employee_aadhar_number,
            # 'marital': employee_marital,
            # 'birthday': employee_date_of_birth,
            'place_of_birth': employee_place_of_birth or False,
            'first_name': employee_first_name,
            'middle_name': employee_middle_name or False,
            'last_name': employee_last_name or False,
            # 'pan': employee_pan,
            # 'uan': employee_uan,
            # 'pf_no': employee_pf_no or False,
            # 'payment_type': employee_payment_type,
            # 'esic_no': employee_esic_no,
            'religion': employee_religion or False,
            'location': employee_location or False,
            'hr_section_id': self.env['hr.section'].sudo().search([('name', '=', employee_section)]).id or False,
            # 'employee_type': employee_type,
            'notice_period': int(employee_notice_period) or False,
            # 'actual_doj': employee_actual_date_of_joining,
        })
    else:
        non_create_employee.append(employee_name)

print("\nNot created department name are:\n", non_create_department)
print("\nNot created department count:\n", len(non_create_department))
print("\nNot created job position name are:\n", non_create_job_position)
print("\nNot created job position count:\n", len(non_create_job_position))
print("\nNot created section name are:\n", non_create_section)
print("\nNot created section count:\n", len(non_create_section))
print("\nNot created employee name are:\n", non_create_employee)
print("\nNot created employee count:\n", len(non_create_employee))

self.env.cr.commit()
