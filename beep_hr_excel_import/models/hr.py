# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    # @api.multi
    # def _cron_create_employee_code(self):
    #     emp_data = self.env['hr.employee'].search([('id', '>', 1687)])
    #     for employee in emp_data:
    #         location = employee.location or "LOC"
    #         dep_code = employee.department_id.department_code or "DEP"
    #         section = employee.hr_section_id.code or "SEC"
    #         position = employee.job_id.code or "JOB"
    #         prefix_code = 'SMNL' + "/" + location + "/" + dep_code + "/" + section + "/" + position + "/"
    #         prefix = self.env['ir.sequence'].search([('code', '=', 'beep.hr.employee.code')])
    #         prefix.write({'prefix': prefix_code})
    #         sequence = self.env['ir.sequence'].next_by_code('beep.hr.employee.code') or _('New')
    #         employee.emp_code = sequence
    #         employee.pin = employee.emp_code[-4:]
    #         employee.pre_code = location + "/" + dep_code + "/" + section + "/" + position
    #     # Update employee code without changing the sequence no and also update login in users.
    #     # emp_record = self.env['hr.employee'].search(
    #     #     [('emp_code', '!=', False), ('emp_code', '!=', 'New'), ('active', '=', True), ('id', '!=', 1)])
    #     # for emp in emp_record:
    #     #     location = emp.location or "LOC"
    #     #     dep_code = emp.department_id.department_code or "DEP"
    #     #     section = emp.hr_section_id.code or "SEC"
    #     #     position = emp.job_id.code or "JOB"
    #     #     prefix_code = 'SMNL' + "/" + location + "/" + dep_code + "/" + section + "/" + position + "/" + emp.emp_code[
    #     #                                                                                                     -4:]
    #     #     emp.emp_code = prefix_code
    #     #     emp.pin = emp.emp_code[-4:]
    #     #     emp.pre_code = location + "/" + dep_code + "/" + section + "/" + position
    #         if employee.user_id and employee.emp_code != employee.user_id.login:
    #             employee.user_id.login = employee.emp_code


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    smnl_id = fields.Integer('Smnl Id')
    department_code = fields.Char(string='Department Code', required=True)


class HrJob(models.Model):
    _inherit = 'hr.job'

    smnl_id = fields.Integer('Smnl Id')
