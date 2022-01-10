# -*- coding: utf-8 -*-
# Install Library: sudo -H pip3 install OdooRPC
# python3 import_attendance.py
import xlrd
import datetime
import odoorpc
import pytz
import os

#Global Variables
HOST="65.0.43.50"
USER="admin"
PSWD="SMNL@EMXCEL"
DB="UAT"
PORT="5432"
odoo = odoorpc.ODOO("65.0.43.50", port=8069)
leaves_not_created = []
employee_not_found = []

def create_update_attendance(att_date, emp_code, punch_in, punch_out, remark):
        # create attendance based on xls data
    hr_attendance_obj = odoo.env['hr.attendance']
    start_time = att_date.strftime('%m/%d/%Y 00:00:00')
    end_time = att_date.strftime('%m/%d/%Y 23:59:59')
    # Compute to UTC timezone
    local_time = pytz.timezone("Asia/Kolkata")
    punch_out_utc = False
    punch_in_utc = False
    if punch_in:
        in_local_datetime = local_time.localize(punch_in, is_dst=None)
        punch_in_utc = in_local_datetime.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    if punch_out:
        out_local_datetime = local_time.localize(punch_out, is_dst=None)
        punch_out_utc = out_local_datetime.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    # Sometime it will be in float or integer field via xls so need to convert in string and removed .o
    if isinstance(emp_code, float):
        attendance_id = str(int(emp_code)).split('/')[-1]
    else:
        attendance_id = str(emp_code).split('/')[-1]
    
    employee_id = odoo.env['hr.employee'].search([('emp_code', '=like', 'SMNL/KPCL%'+attendance_id)])
    
    # Map Attendance ID with employee ID
    if employee_id:
        employee_rec = odoo.env['hr.employee'].browse(employee_id)
        if not (punch_in_utc and punch_out_utc) and remark in ["SL", "CL", "PL"]:
            if remark == "SL":
                leave_type = odoo.env['hr.leave.type'].search([('name', '=', 'Sick Leave')], limit=1)
            if remark == "CL":
                leave_type = odoo.env['hr.leave.type'].search([('name', '=', 'Casual Leave')], limit=1)
            if remark == "PL":
                leave_type = odoo.env['hr.leave.type'].search([('name', '=', 'Privilege Leave')], limit=1)
            try:
                employee_found = odoo.env['hr.leave'].search([('employee_id', '=', employee_rec.id),
                    ('holiday_status_id', '=', leave_type[0]),
                    ('date_from', '=', att_date.date().strftime('%m/%d/%Y')),
                    ('date_to', '=', att_date.date().strftime('%m/%d/%Y'))])
                if not employee_found:
                    att_date.date().strftime('%m/%d/%Y'),  odoo.env['hr.leave'].create({'name': employee_rec.name + str(remark),
                                               'holiday_status_id': leave_type[0],
                                               'number_of_days': 1.0,
                                               'employee_id': employee_rec.id,
                                               'date_from': att_date.date().strftime('%m/%d/%Y'),
                                               'date_to': att_date.date().strftime('%m/%d/%Y'),
                                               'request_date_from': att_date.date().strftime('%m/%d/%Y'),
                                               'request_date_to': att_date.date().strftime('%m/%d/%Y')})
            except Exception:
                leaves_not_created.append(employee_rec.id)

        if punch_in_utc and punch_out_utc:
            employee_id = employee_id[0]
            punch_in_today = hr_attendance_obj.search([('employee_id', '=', int(employee_id)),
                                                       ('check_in', '>=', start_time),
                                                       ('check_out', '<=', end_time)])
            if not punch_in_today:
                # Create attendance
                hr_attendance_obj.create(
                    {'employee_id': employee_id, 'check_in': punch_in_utc, 'check_out': punch_out_utc})
    else:
        if emp_code not in employee_not_found:
            employee_not_found.append(emp_code)

odoo.login(DB, USER, PSWD)
user = odoo.env.user
file_location = os.path.join("os.getcwd()", "bitbucket/UAT/erp-smnl/beep_hr_excel_import/data/Emxcel Format - Attendance.xlsx")
book = xlrd.open_workbook(file_location)
print ("Script Started")
sheet = book.sheet_by_index(0)
punch_in_time = False
punch_out_time = False

for i in range(sheet.nrows - 2):
    print ("Line", i)
    emp_code = sheet.cell_value(i + 2, 0)
    date = xlrd.xldate.xldate_as_datetime(
        sheet.cell_value(i + 2, 1), book.datemode)
    remark = sheet.cell_value(i + 2, 4)

    if sheet.cell_value(i + 2, 2):
        punch_in = xlrd.xldate_as_tuple(sheet.cell_value(i + 2, 2), 0)
        punch_in_time = date.replace(
            hour=punch_in[3], minute=punch_in[4], second=punch_in[5])
    if sheet.cell_value(i + 2, 3):
        punch_out = xlrd.xldate_as_tuple(sheet.cell_value(i + 2, 3), 0)
        punch_out_time = date.replace(
            hour=punch_out[3], minute=punch_out[4], second=punch_out[5])
    
    create_update_attendance(date, emp_code, punch_in_time, punch_out_time, remark)
    
    punch_in_time = False
    punch_out_time = False
print ("\nLeaves not created for employee: ", leaves_not_created)
print ("\nEmployee not found for employee code: ", employee_not_found)
print ("\nScript Completed Successfully")

