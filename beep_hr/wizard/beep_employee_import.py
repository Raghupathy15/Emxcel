# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
import datetime
import pytz
import xlrd
import base64
from odoo.exceptions import UserError
from datetime import date, datetime


class BeepEmployeeImport(models.TransientModel):
    _name = "beep.employee.import"
    _description = "Beep Employee Import"

    upload_file = fields.Binary(string="Upload File", required=True, help="Upload file to import Employee")
    log = fields.Text()
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True, 
                default=lambda self: self.env.user.company_id)

    @api.onchange('upload_file')
    def onchange_upload_file(self):
        for record in self:
            record.log = ''

    @api.multi
    def import_employee(self):
        file_data = base64.decodestring(self.upload_file)
        wb = xlrd.open_workbook(file_contents=file_data)
        sheet = wb.sheet_by_index(0)
       
        for i in range(sheet.nrows - 1):
            if sheet.cell_value(i + 1, 4):
                name = sheet.cell_value(i + 1, 4)
            else:
                raise UserError(_("'Name' is missing in given import sheet at line %s.")% str(i + 1))
            if sheet.cell_value(i + 1, 2):
                old_emp_code = sheet.cell_value(i + 1, 2)
            else:
                old_emp_code = False
            location = sheet.cell_value(i + 1, 1)
            esic = sheet.cell_value(i + 1, 3)
            if sheet.cell_value(i + 1, 5):
                first_name = sheet.cell_value(i + 1, 5)
            else:
                raise UserError(_("'First Name' is missing in given import sheet at line %s.")% str(i + 1))
            middle_name = sheet.cell_value(i + 1, 6)
            last_name = sheet.cell_value(i + 1, 7)
            company = str(sheet.cell_value(i + 1, 8))
            if company[-2:] == '.0':
                company_id = company[:-2]
            else:
                company_id = company
            job_id = sheet.cell_value(i + 1, 9)
            if sheet.cell_value(i + 1, 10):
                department_id = sheet.cell_value(i + 1, 10)
            else:
                raise UserError(_("'Department' is missing in given import sheet at line %s.")% str(i + 1))
            gender = sheet.cell_value(i + 1, 12)
            marital = sheet.cell_value(i + 1, 13)
            conf_dc = sheet.cell_value(i + 1, 14)
            resig_dc = sheet.cell_value(i + 1, 15)
            # Passport No
            passport_no = str(sheet.cell_value(i + 1, 16))
            if passport_no[-2:] == '.0':
                passport_id = passport_no[:-2]
            else:
                passport_id = passport_no
            # PF No
            pf = str(sheet.cell_value(i + 1, 23))
            if pf[-2:] == '.0':
                pf_no = pf[:-2]
            else:
                pf_no = pf
            # ESIC No
            if sheet.cell_value(i + 1, 24):
                esic_number = str(sheet.cell_value(i + 1, 24))
                if esic_number[-2:] == '.0':
                    esic_no = int(esic_number[:-2])
                else:
                    esic_no = int(esic_number)
            else:
                esic_no = ''
            country_of_birth = sheet.cell_value(i + 1, 17)
            place_of_birth = sheet.cell_value(i + 1, 18)
            # PAN no
            if sheet.cell_value(i + 1, 19):
                pan_no = sheet.cell_value(i + 1, 19)
                if pan_no[-2:] == '.0':
                    pan = pan_no[:-2]
                else:
                    pan = pan_no
            else:
                pan = ''
            # Aadhar no
            if sheet.cell_value(i + 1, 20):
                aadhar = str(sheet.cell_value(i + 1, 20))
                if aadhar[-2:] == '.0':
                    identification_id = aadhar[:-2]
                else:
                    identification_id = aadhar
            else:
                raise UserError(_("'Adhar No' is missing in given import sheet at line %s.")% str(i + 1))
            # voter ID
            voter = str(sheet.cell_value(i + 1, 21))
            if voter[-2:] == '.0':
                voter_id = voter[:-2]
            else:
                voter_id = voter
            # voter ID
            uan_no = str(sheet.cell_value(i + 1, 22))
            if uan_no[-2:] == '.0':
                uan = uan_no[:-2]
            else:
                uan = uan_no
            # mobile no
            mobile = str(sheet.cell_value(i + 1, 25))
            if mobile[-2:] == '.0':
                mobile_phone = mobile[:-2]
            else:
                mobile_phone = mobile
            personal_mail = str(sheet.cell_value(i + 1, 26))
            work_email = str(sheet.cell_value(i + 1, 27))
            if sheet.cell_value(i + 1, 28):
                doj = xlrd.xldate.xldate_as_datetime(sheet.cell_value(i + 1, 28), 0)
            else:
                doj = False
            if sheet.cell_value(i + 1, 29):
                actual_doj = xlrd.xldate.xldate_as_datetime(sheet.cell_value(i + 1, 29), 0)
            else:
                raise UserError(_("'Actual Date of Joining' is missing in given import sheet at line %s.")% str(i + 1))
            if sheet.cell_value(i + 1, 30):
                birthday = xlrd.xldate.xldate_as_datetime(sheet.cell_value(i + 1, 30), 0)
            else:
                birthday = False
            if sheet.cell_value(i + 1, 33):
                religion = sheet.cell_value(i + 1, 33)
            else:
                raise UserError(_("'Religion' is missing in given import sheet at line %s.")% str(i + 1))
            bank_name = sheet.cell_value(i + 1, 34)
            acc_no = str(sheet.cell_value(i + 1, 35))
            if acc_no[-2:] == '.0':
                acc_number = acc_no[:-2]
            else:
                acc_number = acc_no
            bank_branch = str(sheet.cell_value(i + 1, 36))
            ifc_code = str(sheet.cell_value(i + 1, 37))
            employee_type = str(sheet.cell_value(i + 1, 38))
            biometric = str(sheet.cell_value(i + 1, 39))
            work_phone = str(sheet.cell_value(i + 1, 41))
            if sheet.cell_value(i + 1, 40):
                notice_period = str(sheet.cell_value(i + 1, 40))
            else:
                raise UserError(_("'Notice Period' is missing in given import sheet at line %s.")% str(i + 1))
            certificate = sheet.cell_value(i + 1, 42)
            spouse_complete_name = sheet.cell_value(i + 1, 43)
            children_1 = sheet.cell_value(i + 1, 44)
            children_2 = sheet.cell_value(i + 1, 45)
            father = sheet.cell_value(i + 1, 46)
            mother = sheet.cell_value(i + 1, 47)
            brother = sheet.cell_value(i + 1, 48)
            sister = sheet.cell_value(i + 1, 49)
            previous_company = sheet.cell_value(i + 1, 50)
            govt_basic = sheet.cell_value(i + 1, 54)
            hr_section_id = sheet.cell_value(i + 1, 56)
            contract_name = sheet.cell_value(i + 1, 57)
            # contract_start_date = '2020-09-14 00:00:00'
            if sheet.cell_value(i + 1, 58):
                contract_start_date = xlrd.xldate.xldate_as_datetime(sheet.cell_value(i + 1, 58), 0)
            else:
                raise UserError(_("'Contract Start Date' is missing in given import sheet at line %s.")% str(i + 1))
            wage = sheet.cell_value(i + 1, 59)

            # permanent address starts
            permanent_address =  str(sheet.cell_value(i + 1, 32))
            if permanent_address:
                per_addr_split=(permanent_address.split(','))
                per_state_split = per_addr_split[-1]
                per_pin_split=(per_addr_split[-1].split('-'))
                permanent_zip=per_pin_split[-1]
                permanent_city=per_pin_split[-2]
                street = str(per_addr_split[:-1]).replace('[', '')
                street1 = str(street).replace(']', '')
                permanent_street2 = str(street1).replace("'", '')
                per_state_exist=[]
            else:
                raise UserError(_("'Permanent Address' is missing in given import sheet at line %s.")% str(i + 1))
            # permanent address ends

            # # Importing Users
            user_obj = self.env['res.users']
            user_obj.create({'login': identification_id,
                            'name':name,
                            'password':'SMNL@123',
                            })
            # Importing Banks
            res_bank_obj = self.env['res.bank']
            if sheet.cell_value(i + 1, 34):
                res_bank_obj.create({'name': bank_name,
                                    'bic':ifc_code,
                                    'bank_branch': bank_branch,
                                    'active': True,
                                    })
            # Importing Bank Accounts
            res_part_bank_obj = self.env['res.partner.bank']
            if sheet.cell_value(i + 1, 35):
                find_account = self.env['res.bank'].search([('name','=',bank_name),('bic','=',ifc_code)],limit=1)
                find_partner = self.env['res.partner'].search([('name','=',name)],limit=1)
                if find_account:
                    res_part_bank_obj.create({ 'acc_number': acc_number,
                                    'bank_id':find_account.id,
                                    'partner_id': find_partner.id,
                                    'company_id':company_id,
                                    })
            # Importing Employee
            hr_emloyee_obj = self.env['hr.employee']
            partner = self.env['res.partner'].search([('name','=',name)],limit=1)
            find_partner_bank = self.env['res.partner.bank'].search([('partner_id','=',partner.id)],limit=1)
            new_emp = hr_emloyee_obj.create({ 'name': name,
                                    'old_emp_code':old_emp_code,
                                    'location':location,
                                    'esic':esic,
                                    'first_name':first_name,
                                    'middle_name':middle_name,
                                    'last_name':last_name,
                                    'company_id':company_id,
                                    'job_id':job_id,
                                    'department_id':department_id,
                                    'gender':gender,
                                    'marital':marital,
                                    'conf_dc':conf_dc,
                                    'resig_dc':resig_dc,
                                    'passport_id':passport_id,
                                    'country_of_birth':country_of_birth,
                                    'place_of_birth':place_of_birth,
                                    'pan':pan,
                                    'identification_id':identification_id,
                                    'date_of_joining':doj,
                                    'actual_doj':actual_doj,
                                    'birthday':birthday,
                                    'religion':religion,
                                    'permanent_street2':permanent_street2,
                                    'permanent_city':permanent_city,
                                    'permanent_zip':permanent_zip,
                                    'work_phone':work_phone,
                                    'notice_period':notice_period[:-2],
                                    'voter_id':voter_id,
                                    'uan':uan,
                                    'pf_no':pf_no,
                                    'esic_no':esic_no,
                                    'mobile_phone':mobile_phone,
                                    'personal_mail':personal_mail,
                                    'work_email':work_email,
                                    'employee_type':employee_type,
                                    'biometric':biometric,
                                    'certificate':certificate,
                                    'spouse_complete_name':spouse_complete_name,
                                    'children_1':children_1,
                                    'father':father,
                                    'mother':mother,
                                    'brother':brother,
                                    'sister':sister,
                                    'previous_company':previous_company,
                                    # 'govt_basic':govt_basic,
                                    'address_home_id': partner.id,
                                    'bank_account_id': find_partner_bank.id,
                                    'hr_section_id':hr_section_id,
                                    })
            # Importing Contract
            contract_obj = self.env['hr.contract']
            contract_obj.create({ 'employee': name,
                                # 'name':contract_name,
                                'name':'Job contract of '+ str(name),
                                'type_id': 1,
                                'struct_id': 3,
                                'date_start':contract_start_date,
                                'resource_calendar_id':1,
                                'wage': wage,
                                'active': True,
                                'state': "open",
                                'company_id':company_id,
                                })
            print ('Total Employees Imported',i,name)
        
        company = self.env['res.company']
        company.action_map_hr_contract()
        self.action_map_users_emp(new_emp)
        self.action_create_leaves()
        self.log = "Employees Imported Successfully !!"
        return {
            'name': _('Emloyee Import'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'beep.employee.import',
            'res_id': self.id,
            'target': 'new',
        }

    def action_map_users_emp(self, new_emp):
        # Map Employees
        user_obj = self.env['res.users'].search([('login','=',new_emp.identification_id)])
        if user_obj:
            new_emp.user_id = user_obj.id

    def action_create_leaves(self):
        leave = self.env['hr.leave.allocation']
        today =  fields.Datetime.now()
        employee = self.env['hr.employee'].search([('create_date','>=',today - timedelta(days=1))])
        # count = 0
        for emp in employee:
            check_pl_leave = self.env['hr.leave.allocation'].search([('employee_id','=',emp.id),
                                                ('holiday_status_id.name','=','Privilege Leave'),
                                                ('state','=','validate')])
            check_cl_leave = self.env['hr.leave.allocation'].search([('employee_id','=',emp.id),
                                                    ('holiday_status_id.name','=','Casual Leave'),
                                                    ('state','=','validate')])
            check_sl_leave = self.env['hr.leave.allocation'].search([('employee_id','=',emp.id),
                                                    ('holiday_status_id.name','=','Sick Leave'),
                                                    ('state','=','validate')])
            check_spl_leave = self.env['hr.leave.allocation'].search([('employee_id','=',emp.id),
                                                    ('holiday_status_id.name','=','Special Leave'),
                                                    ('state','=','validate')])

            leave_type_pl = self.env['hr.leave.type'].search([('name','=','Privilege Leave')])
            leave_type_cl = self.env['hr.leave.type'].search([('name','=','Casual Leave')])
            leave_type_sl = self.env['hr.leave.type'].search([('name','=','Sick Leave')])
            leave_type_spl = self.env['hr.leave.type'].search([('name','=','Special Leave')])
            if not check_pl_leave:
                pl = leave.create({'name':'Privilege Leave Allocation',
                                        'holiday_type': 'employee',
                                        'employee_id': emp.id,
                                        'holiday_status_id': leave_type_pl.id,
                                        'number_of_days': 15,
                                        'company_id': self.company_id.id,
                                        'state': 'validate',
                                        })
            if not check_cl_leave:
                cl = leave.create({'name':'Casual Leave Allocation',
                                        'holiday_type': 'employee',
                                        'employee_id': emp.id,
                                        'holiday_status_id': leave_type_cl.id,
                                        'number_of_days': 12,
                                        'state': 'validate',
                                        'company_id': self.company_id.id,
                                        })
            if not check_sl_leave:
                sl = leave.create({'name':'Sick Leave Allocation',
                                        'holiday_type': 'employee',
                                        'employee_id': emp.id,
                                        'holiday_status_id': leave_type_sl.id,
                                        'number_of_days': 12,
                                        'state': 'validate',
                                        'company_id': self.company_id.id,
                                        })
            if not check_spl_leave:
                spl = leave.create({'name':'Special Leave Allocation',
                                        'holiday_type': 'employee',
                                        'employee_id': emp.id,
                                        'holiday_status_id': leave_type_spl.id,
                                        'number_of_days': 14,
                                        'state': 'validate',
                                        'company_id': self.company_id.id,
                                        })
            # count = count + 1
            # print('Total Leaves created',count)