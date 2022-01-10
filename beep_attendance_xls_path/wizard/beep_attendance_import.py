# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
import datetime
import pytz
import xlrd
import base64
import time
import os
import fnmatch
from pathlib import Path
import pandas as pd
from xlrd import open_workbook


class BeepAttendanceImportPath(models.TransientModel):
    _name = "beep.attendance.import.path"
    _description = "Beep Attendance Import"

    file_path = fields.Char()
    file_name = fields.Char()
    log = fields.Text()

    # @api.multi
    # def import_attendance_file(self):
    #     entries = os.listdir('/home/odoo/Downloads')
    #     data_file = Path('/home/odoo/Downloads/custom_import_attendance_server.xlsx')
    #     book = open_workbook('/home/odoo/Downloads/custom_import_attendance_server.xlsx',on_demand=True)
    #     for name in book.sheet_names():
    #         sheet = book.sheet_by_name(name)
    #         for cell in sheet.col(0): 
    #             print (cell.value)
    #     # df = pd.read_excel(io='/home/odoo/Downloads/custom_import_attendance_server.xlsx', sheet_name='Sheet1')
    #     # print(df.head(5))

    #     # for file_name in os.listdir('/home/odoo/Downloads'):
    #     #     if fnmatch.fnmatch(file_name, '*.xlsx'):
    #     #         print(file_name)
    #     print ("entries", data_file)
    #     with open(data_file, 'r') as f:
    #         # data = f.read()
    #         print (f)
    #     print (po)

    @api.multi
    def import_attendance(self):
        """ Execute query to fetch data
        """
        # file_data = base64.decodestring(self.upload_file)
        if self.file_path.endswith("/"):
            filename = self.file_path + self.file_name
        else:
            filename = self.file_path + '/' + self.file_name
        wb = open_workbook(filename,on_demand=True)
        # wb = xlrd.open_workbook(file_contents=file_data)
        sheet = wb.sheet_by_index(0)
        self.log = 'Missing Employee code as below (If Any): \n'
        punch_in_time = False
        punch_out_time = False

        for i in range(sheet.nrows - 1):
            date = xlrd.xldate.xldate_as_datetime(
                sheet.cell_value(i + 1, 2), wb.datemode)
            emp_code = sheet.cell_value(i + 1, 0)
            if sheet.cell_value(i + 1, 3):
                punch_in = xlrd.xldate_as_tuple(sheet.cell_value(i + 1, 3), 0)
                punch_in_time = date.replace(
                    hour=punch_in[3], minute=punch_in[4], second=punch_in[5])
            if sheet.cell_value(i + 1, 4):
                punch_out = xlrd.xldate_as_tuple(sheet.cell_value(i + 1, 4), 0)
                punch_out_time = date.replace(
                    hour=punch_out[3], minute=punch_out[4], second=punch_out[5])

            self.create_update_attendance(
                date, emp_code, punch_in_time, punch_out_time)
        self.log += "\n\nAttendance Imported Successfully."
        return {
            'name': _('Attendance Import'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'beep.attendance.import.path',
            'res_id': self.id,
            'target': 'new',
        }

    def create_update_attendance(self, date, attendance_id, punch_in, punch_out):
            # create attendance based on xls data
        hr_attendance_obj = self.env['hr.attendance']
        start_time = datetime.datetime.strptime(
            date.strftime('%d/%m/%Y 00:00:00'), '%d/%m/%Y 00:00:00')
        end_time = datetime.datetime.strptime(date.strftime(
            '%d/%m/%Y 23:59:59'), '%d/%m/%Y 23:59:59').replace(minute=59, hour=23, second=59)
        # Compute to UTC timezone
        local_time = pytz.timezone("Asia/Kolkata")
        punch_out_utc = False
        punch_in_utc = False
        if punch_in:
            in_local_datetime = local_time.localize(punch_in, is_dst=None)
            punch_in_utc = in_local_datetime.astimezone(pytz.utc)
        if punch_out:
            out_local_datetime = local_time.localize(punch_out, is_dst=None)
            punch_out_utc = out_local_datetime.astimezone(pytz.utc)
        # Sometime it will be in float or integer field via xls so need to convert in string and removed .o
        if isinstance(attendance_id, float):
            attendance_id = str(int(attendance_id))
        employee_id = self.env['hr.employee'].search(
            [('emp_code', '=', attendance_id)], limit=1).id

        # Map Attendance ID with employee ID
        if not employee_id:
            self.log += str(attendance_id) + ' '
            return True
        punch_in_today = hr_attendance_obj.search([('employee_id', '=', int(employee_id)),
                                                   ('check_in', '>=', start_time),
                                                   ('check_out', '<=', end_time)])

        if not punch_in_today:
            hr_attendance_obj.create(
                {'employee_id': employee_id, 'check_in': punch_in_utc, 'check_out': punch_out_utc})
