# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Employee(models.Model):
    _inherit = 'hr.employee'

    # General info
    emp_code = fields.Char('Employee Code', readonly=True, size=40, default="New")
    old_emp_code = fields.Char('Old Emp Code')
    first_name = fields.Char(string='First Name', required=True, size=40)
    middle_name = fields.Char(string='Middle Name', size=40)
    last_name = fields.Char(string='Last Name', size=40)
    location = fields.Char(string='Location', size=40)
    esic = fields.Char(string='ESIC', size=40)
    conf_dc = fields.Char(string='Confirmation Dt', size=40)
    resig_dc = fields.Char(string='Resign.Dt', size=40)
    pan = fields.Char(string='PAN', size=15)
    voter_id = fields.Char(string='Voter ID')
    uan = fields.Char(string='UAN', size=20)
    pf_no = fields.Char(string='PF No', size=40)
    esic_no = fields.Char(string='ESIC No.', size=17)
    date_of_joining = fields.Date(string='Date of joining')
    actual_doj = fields.Date(string='Actual Date of joining', required=True)
    personal_mail = fields.Char(string='Personal Mail', size=40)
    work_experience = fields.Integer(string='Total Work Experience', size=40)
    mobile_phone = fields.Char('Work Mobile', size=10)
    work_phone = fields.Char('Work Phone', size=10)
    age = fields.Char('Age')
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    # Present address
    street2 = fields.Char(size=150)
    zip = fields.Char(change_default=True, size=10)
    city = fields.Char(size=40)
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    # Permanent address
    permanent_street2 = fields.Char(size=150)
    permanent_zip = fields.Char(change_default=True, size=10)
    permanent_city = fields.Char(size=40)
    permanent_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                                         domain="[('country_id', '=?', country_id)]")
    permanent_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    # Private Information
    religion = fields.Char(string="Religion", required=True, size=40)
    employee_type = fields.Selection([('permanent', 'Permanent'), ('temporary', 'Temporary')])
    biometric = fields.Char(string="Bio Metric Code", size=40)
    notice_period = fields.Char(string="Notice Period", required=True, size=40)
    children_1 = fields.Char(string="Children 1", size=40)
    children_2 = fields.Char(string="Children 2", size=40)
    father = fields.Char(string="Father Name", size=40)
    mother = fields.Char(string="Mother Name", size=40)
    brother = fields.Char(string="Brother", size=100)
    sister = fields.Char(string="Sister", size=40)
    previous_company = fields.Char(string="Previous Company", size=100)
    payment_type = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')])
    wage = fields.Monetary('Gross', digits=(16, 2), track_visibility="onchange", help="Employee's monthly gross wage.")
    govt_basic = fields.Monetary('Govt. Allowed Minimum Basic', digits=(16, 2))
    cvr_maint = fields.Monetary('CVR Maint', digits=(16, 2))
    cvr_rent = fields.Monetary('CVR Rent', digits=(16, 2))
    # HR settings
    pre_code = fields.Char("Pre Code")
    pin = fields.Char(string="PIN", default='',
                      help="PIN used to Check In/Out in Kiosk Mode (if enabled in Configuration).")
    # Defautlt field but change label name identification no to Aadhar no
    identification_id = fields.Char(string='Aadhar No', groups="hr.group_hr_user", size=20, required=True)

    # Add new values in selection
    certificate = fields.Selection(selection_add=[('diploma', 'Diploma-Mechanical'), ('mba', 'MBA-Finance & Markting'),
                                                  ('mba_hr', 'MBA-HR'), ('10th', '10th Class'), ('7th', '7th Class'),
                                                  ('9th', '9th Class'),
                                                  ('8th', '8th Class'), ('5th', '5th Class'), ('iti', 'ITI'),
                                                  ('intermediate', 'Intermediate'),
                                                  ('degree_2nd_yr', 'Degree 2nd year'), ('graduate', 'Graduate'),
                                                  ('b_tec', 'B TECH'), ('dca', 'DCA'), ('ba', 'BA'),
                                                  ('below_ssc', 'Below SSC'), ('ssc', 'SSC'), ('bsc', 'B SC'),
                                                  ('mca', 'MCA'), ('pg', 'Post graduate'), ('dme', 'DME'),
                                                  ('be', 'BE'), ('b_com', 'B Com')])
    # HR section
    hr_section_id = fields.Many2one("hr.section", "Section")

    @api.multi
    @api.onchange('pan')
    def set_upper(self):
        if self.pan:
            self.pan = self.pan.upper()
        return

    @api.multi
    @api.constrains('pan', 'esic_no', 'uan', 'mobile_phone', 'work_phone', 'identification_id')
    def _check_validations(self):
        for data in self:
            if data.pan and len(data.pan) != 10:
                raise UserError(_("Values not sufficient !.. Please Enter 10 digit 'PAN' Number"))
            pan = self.env['hr.employee'].search([('pan', '=', data.pan), ('id', '!=', data.id), ('pan', '!=', False), ('pan', '!=', '')])
            esic_no = self.env['hr.employee'].search(
                [('esic_no', '=', data.esic_no), ('id', '!=', data.id), ('esic_no', '!=', '')])
            uan = self.env['hr.employee'].search([('uan', '=', data.uan), ('id', '!=', data.id), ('uan', '!=', '')])
            if pan:
                raise UserError(_('PAN No already exists for "%s" , Please enter the correct no.' % (pan.name)))
            if esic_no:
                raise UserError(_('ESIC No already exists for "%s" , Please enter the correct no.' % (esic_no.name)))
            if uan:
                raise UserError(_('UAN No already exists for "%s" , Please enter the correct no.' % (uan.name)))
            if data.pan and not data.pan[0:5].isalpha():
                raise UserError(_("First five values of PAN no should be alphabet"))
            if data.pan and not data.pan[9].isalpha():
                raise UserError(_("Last value of PAN no should be alphabet"))
            if data.pan and not data.pan[5:9].isdigit():
                raise UserError(_("PAN no values from 5 to 8 Should be Integer"))
            if data.esic_no and len(data.esic_no) != 10:
                raise UserError(_("Values not sufficient !.. Please Enter 10 digit 'ESIC No'."))
            if data.esic_no and not data.esic_no.isdigit():
                raise UserError(_("'Esic No' Should be Integer."))
            if data.uan and len(data.uan) != 12:
                raise UserError(_("Values not sufficient !.. Please Enter 12 digit 'UAN' Number"))
            if data.uan and not data.uan.isdigit():
                raise UserError(_("'UAN' Should be Integer."))
            if data.mobile_phone and len(data.mobile_phone) != 10:
                raise UserError(_("Values not sufficient !.. Please Enter 10 digit 'Work Mobile' Number"))
            if data.mobile_phone and not data.mobile_phone.isdigit():
                raise UserError(_("'Work Mobile' Should be Integer."))
            if data.work_phone and len(data.work_phone) != 10:
                raise UserError(_("Values not sufficient !.. Please Enter 10 digit 'Work Phone' Number."))
            if data.work_phone and not data.work_phone.isdigit():
                raise UserError(_("'Work Phone' Should be Integer."))
            if data.identification_id and len(data.identification_id) != 12:
                raise UserError(_("Values not sufficient !.. Please Enter 12 digit 'Aadhar No' Number."))
            if data.identification_id and not data.identification_id.isdigit():
                raise UserError(_("'Aadhar No' Should be Integer."))
            aadhar = self.env['hr.employee'].search(
                [('identification_id', '=', data.identification_id), ('id', '!=', data.id),
                 ('identification_id', '!=', '')])
            if aadhar:
                raise ValidationError(_('Aadhar No already exists'))

    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)
        if 'emp_code' not in vals or vals['emp_code'] == _('New'):
            location = res.location or "LOC"
            dep_code = res.department_id.department_code or "DEP"
            section = res.hr_section_id.code or "SEC"
            position = res.job_id.code or "JOB"
            prefix_code = 'SMNL' + "/" + location + "/" + dep_code + "/" + section + "/" + position + "/"
            prefix = self.env['ir.sequence'].search([('code', '=', 'beep.hr.employee.code')])
            prefix.write({'prefix': prefix_code})
            sequence = self.env['ir.sequence'].next_by_code('beep.hr.employee.code') or _('New')
            res.emp_code = sequence
            res.pin = res.emp_code[-4:]
            res.pre_code = location + "/" + dep_code + "/" + section + "/" + position
        return res

    @api.multi
    @api.onchange('department_id', 'location', 'hr_section_id', 'job_id')
    def onch_department(self):
        location = self.location or "LOC"
        dep_code = self.department_id.department_code or "DEP"
        section = self.hr_section_id.code or "SEC"
        position = self.job_id.code or "JOB"
        if self.emp_code:
            matches = re.finditer("/", self.emp_code)
            matches_positions = [match.start() for match in matches]
            if matches and len(matches_positions) > 1:
                loc = self.emp_code[matches_positions[0] + 1:matches_positions[1]]
                dep = self.emp_code[matches_positions[1] + 1:matches_positions[2]]
                sec = self.emp_code[matches_positions[2] + 1:matches_positions[3]]
                pos = self.emp_code[matches_positions[3] + 1:matches_positions[4]]
                seq = self.emp_code.replace(loc, location).replace(dep, dep_code).replace(sec, section).replace(pos, position)
                self.emp_code = seq
                self.pre_code = location + "/" + dep_code + "/" + section + "/" + position

    @api.multi
    def action_update_working_hours(self):
        employee_obj = self.env['hr.employee'].search([])
        for employee in employee_obj:
            if employee.resource_calendar_id:
                contracts_obj = self.env['hr.contract'].search([('employee_id', '=', employee.name),
                                                        ('state', '=', 'open'),
                                                        ('resource_calendar_id', '!=', employee.resource_calendar_id.id)])
                if contracts_obj:
                    for contracts in contracts_obj:
                        contracts.write({'resource_calendar_id': employee.resource_calendar_id.id})
                        

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    # General info
    smnl_id = fields.Integer('Smnl Id')
    department_code = fields.Char(string='Department Code', required=True)


class HrJob(models.Model):
    _inherit = 'hr.job'

    # General info
    smnl_id = fields.Integer('Smnl Id')
    code = fields.Char("Code", size=4)


class ResBank(models.Model):
    _inherit = 'res.bank'

    # General info
    bank_branch = fields.Char('Bank Branch')
