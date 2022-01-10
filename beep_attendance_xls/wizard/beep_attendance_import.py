# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
import datetime
import pytz
import xlrd
import base64
import time
import calendar
leaves_not_created = []
employee_not_found = []


class BeepAttendanceImport(models.TransientModel):
    _name = "beep.attendance.import"
    _description = "Beep Attendance Import"

    upload_file = fields.Binary(
        string="Upload File", required=True, help="Upload file to import attendance")
    log = fields.Text()

    @api.multi
    def update_employee_details(self):
        file_data = base64.decodestring(self.upload_file)
        book = xlrd.open_workbook(file_contents=file_data)
        sheet = book.sheet_by_index(0)
        self.log = '\nAll Adhar No are not found \n'

        for i in range(sheet.nrows - 1):
            code = sheet.cell_value(i + 1, 1).split('/')[-1]
            adhar_no = str(int(sheet.cell_value(i + 1, 0)))
            emp = self.env['hr.employee'].search([('identification_id', '=', adhar_no), ('id', '!=', 1)], limit=1)
            if emp:
                if not emp.emp_code.split('/')[-1].isdigit():
                    emp_code = emp.emp_code + '/'+str(code)
                    emp.sudo().write({'emp_code': emp_code})
            else:
                self.log+= str(adhar_no) + '\n'

        return {
            'name': _('Employee Updated'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'beep.attendance.import',
            'res_id': self.id,
            'target': 'new',
        }

    # @api.multi
    # def update_employee_details(self):
    # #Update job, designation and department details in employee
    #     file_data = base64.decodestring(self.upload_file)
    #     book = xlrd.open_workbook(file_contents=file_data)
    #     sheet = book.sheet_by_index(0)
    #     self.log = '\nBelow new records are created:\n'
    #     jobs=[]
    #     sections=[]
    #     departments=[]
    #     for i in range(sheet.nrows - 1):
    #         adhar_no = str(int(sheet.cell_value(i + 1, 0)))
    #         designation = sheet.cell_value(i + 1, 7).strip()
    #         section = sheet.cell_value(i + 1, 8).strip()
    #         department = sheet.cell_value(i + 1, 9).strip()
            
    #         job_id = self.env['hr.job'].search([('name', '=ilike', designation)], limit=1)
    #         hr_section_id = self.env['hr.section'].search([('name', '=ilike', section)], limit=1)
    #         department_id = self.env['hr.department'].search([('name', '=ilike', department)], limit=1)
            
    #         if not job_id:
    #             job_id= self.env['hr.job'].create({'name': designation})
    #             jobs.append(designation)

    #         if not hr_section_id:
    #             hr_section_id=self.env['hr.section'].create({'name': section})
    #             sections.append(section)
    #         if not department_id:
    #             department_id=self.env['hr.department'].create({'name': department})
    #             departments.append(department)

    #         employee = self.env['hr.employee'].search([('identification_id', '=', adhar_no)], limit=1)
    #         employee.sudo().write({'job_id': job_id.id, 'hr_section_id': hr_section_id.id, 'department_id': department_id.id})
    #     self.log += "Jobs = " + ','.join(jobs)
    #     self.log += "\nSections = " + ','.join(sections)
    #     self.log += "\nDepartments = " + ','.join(departments)
    #     print ("jobs", jobs)
    #     print ("sections", sections)
    #     print ("departments", departments)

    #     return {
    #         'name': _('Employee Updated'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'beep.attendance.import',
    #         'res_id': self.id,
    #         'target': 'new',
    #     }

    @api.multi
    def import_attendance(self):
        """ Execute query to fetch data
        """
        file_data = base64.decodestring(self.upload_file)
        book = xlrd.open_workbook(file_contents=file_data)
        sheet = book.sheet_by_index(0)
        self.log = ''
        # employee_not_found = []
        punch_in_time = False
        punch_out_time = False

        for i in range(sheet.nrows - 2):
            punch_in_time = False
            punch_out_time = False
            emp_code = sheet.cell_value(i + 2, 1)
            date = xlrd.xldate.xldate_as_datetime(
                sheet.cell_value(i + 2, 2), book.datemode)
            remark = sheet.cell_value(i + 2, 5)
            if sheet.cell_value(i + 2, 3):
                punch_in = xlrd.xldate_as_tuple(sheet.cell_value(i + 2, 3), 0)
                punch_in_time = date.replace(
                    hour=punch_in[3], minute=punch_in[4], second=punch_in[5])
            if sheet.cell_value(i + 2, 4):
                punch_out = xlrd.xldate_as_tuple(sheet.cell_value(i + 2, 4), 0)
                punch_out_time = date.replace(
                    hour=punch_out[3], minute=punch_out[4], second=punch_out[5])
            # print("\n\nemp_code", emp_code, punch_in_time, punch_out_time)
            self.create_update_attendance(date, emp_code, punch_in_time, punch_out_time, remark)

        self.log += "Attendance Imported Successfully.\n\n"
        if employee_not_found:
            self.log += "Following employee code(s) are either not created or already deactivated. \n" + ',\n'.join(
                employee_not_found)

        return {
            'name': _('Attendance Import'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'beep.attendance.import',
            'res_id': self.id,
            'target': 'new',
        }

    def create_update_attendance(self, att_date, emp_code, punch_in, punch_out, remark):
        # create attendance based on xls data
        hr_attendance_obj = self.env['hr.attendance']
        start_time = att_date.strftime('%m/%d/%Y 00:00:00')
        end_time = att_date.strftime('%m/%d/%Y 23:59:59')
        # Compute to UTC timezone
        local_time = pytz.timezone("Asia/Kolkata")
        punch_out_utc = False
        punch_in_utc = False
        if punch_in:
            in_local_datetime = local_time.localize(punch_in, is_dst=None)
            punch_in_utc = in_local_datetime.astimezone(
                pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        if punch_out:
            out_local_datetime = local_time.localize(punch_out, is_dst=None)
            punch_out_utc = out_local_datetime.astimezone(
                pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
        # Sometime it will be in float or integer field via xls so need to convert in string and removed .
        if isinstance(emp_code, float):
            attendance_id = str(int(emp_code)).split("'")[-1]
        else:
            attendance_id = str(emp_code).split("'")[-1]

        employee = self.env['hr.employee'].search(
            [('emp_code', '=like', '%'+attendance_id)], limit=1)

        # Map Attendance ID with employee ID
        if employee:
            employee_id = employee.id
            employee_rec = self.env['hr.employee'].browse(employee_id)
            if not (punch_in_utc and punch_out_utc) and remark in ["A", "SL", "CL", "PL", "L"]:
                if remark == "SL":
                    leave_type = self.env['hr.leave.type'].search(
                        [('name', '=', 'Sick Leave')], limit=1)
                if remark == "CL":
                    leave_type = self.env['hr.leave.type'].search(
                        [('name', '=', 'Casual Leave')], limit=1)
                if remark == "PL":
                    leave_type = self.env['hr.leave.type'].search(
                        [('name', '=', 'Privilege Leave')], limit=1)
                if remark in ["L", "A"]:
                    leave_type = self.env['hr.leave.type'].search(
                        [('name', '=', 'Leave Without Pay (LWP)')], limit=1)

                try:
                    employee_found = self.env['hr.leave'].search([('employee_id', '=', employee_rec.id),
                                                                  ('holiday_status_id',
                                                                   '=', leave_type.id),
                                                                  ('date_from', '=', att_date.date().strftime(
                                                                      '%m/%d/%Y')),
                                                                  ('date_to', '=', att_date.date().strftime('%m/%d/%Y'))])
                    if not employee_found:
                        a = att_date.date().strftime('%m/%d/%Y'),  self.env['hr.leave'].create({'name': employee_rec.name + str(remark),
                                                                                                'holiday_status_id': leave_type.id,
                                                                                                'number_of_days': 1.0,
                                                                                                'employee_id': employee_rec.id,
                                                                                                'date_from': att_date.date().strftime('%m/%d/%Y 3:30:00'),
                                                                                                'date_to': att_date.date().strftime('%m/%d/%Y 12:30:00'),
                                                                                                'request_date_from': att_date.date().strftime('%m/%d/%Y 3:30:00'),
                                                                                                'request_date_to': att_date.date().strftime('%m/%d/%Y 12:30:00')})
                except Exception:
                    leaves_not_created.append(employee_rec.id)
            if punch_in_utc and punch_out_utc:
                employee_id = employee_id
                punch_in_today = hr_attendance_obj.search([('employee_id', '=', int(employee_id)),
                                                           ('check_in', '>=',
                                                            start_time),
                                                           ('check_out', '<=', end_time)])
                if not punch_in_today:
                    # Create attendance
                    hr_attendance_obj.create(
                        {'employee_id': employee_id, 'check_in': punch_in_utc, 'check_out': punch_out_utc})
            if punch_in_utc and not punch_out_utc:
                # if any employee do not have punch out more than 2 times rest entry will be absent only.
                employee_id = employee_id
                punch_in_month_date = datetime.datetime.strptime(
                    punch_in_utc, '%Y-%m-%d %H:%M:%S')
                punch_in_today = hr_attendance_obj.search([('employee_id', '=', int(employee_id)),
                                                           ('check_in', '=',
                                                            punch_in_utc),
                                                           ('check_out', '=', False)])
                month_range = calendar.monthrange(
                    punch_in_month_date.year, punch_in_month_date.month)
                start_month = att_date.strftime(
                    str(punch_in_month_date.month) + '/1/%Y 00:00:00')
                end_month = att_date.strftime(
                    str(punch_in_month_date.month) + '/' + str(month_range[1])+'/%Y 00:00:00')

                punch_limit = hr_attendance_obj.search([('employee_id', '=', int(employee_id)),
                                                        ('check_in', '>=', start_month), (
                                                            'check_in', '<=', end_month),
                                                        ('swipe_status', '=', 'approved')])
                
                if not punch_in_today and len(punch_limit) < 2:
                    punch_out_utc = datetime.datetime.strptime(
                        punch_in_utc, '%Y-%m-%d %H:%M:%S') + timedelta(hours=9)
                    punch_out_utc = punch_out_utc.strftime('%Y-%m-%d %H:%M:%S')

                    hr_attendance_obj.create({'employee_id': employee_id, 'check_in': punch_in_utc,
                                              'check_out': punch_out_utc, 'swipe_status': 'approved'})
                else:
                    punch_in_missed = hr_attendance_obj.search([('employee_id', '=', int(employee_id)),
                                                           ('check_in', '=', punch_in_utc),
                                                           ])
                    if not punch_in_missed:
                        hr_attendance_obj.create({'employee_id': employee_id, 'check_in': punch_in_utc,
                                                  'swipe_status': 'missed'})

        else:
            if emp_code not in employee_not_found:
                employee_not_found.append(emp_code)
