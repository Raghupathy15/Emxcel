# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'

    is_leave_alocated = fields.Boolean()

    def action_match_partners_and_users(self):
        res_users = self.env['res.users'].search([('id','>',1691)])
        for users in res_users:
            if users.partner_id:
                partner = users.env['res.partner'].sudo().search([('emp_code','=',users.login),('company_id','=',self.id)])
                if partner:
                    users.partner_id = partner.id
        emp = self.env['hr.employee'].search([('user_id','=',False)])
        for employee in emp:
            if not employee.user_id:
                user = employee.env['res.users'].sudo().search([('login','=',employee.emp_code),('company_id','=',self.id)])
                if user:
                    employee.user_id = user.id

    def action_map_hr_contract(self):
        emp = self.env['hr.employee'].search([])
        for employee in emp:
            con = self.env['hr.contract'].search([('employee','=',employee.name),('employee_id','=',False)])
            if con:
                for contract in con:
                    contract.employee_id = employee.id

    def action_create_leave_allocation(self):
        employee = self.env['hr.employee'].search([('id','>',1687)])
        employeessss = self.env['hr.employee'].search_count([('id','>',1687)])
        # if self.is_leave_alocated == False:
        for emp in employee:
            leave = self.env['hr.leave.allocation']
            leave_type_pl = self.env['hr.leave.type'].search([('name','=','Privilege Leave')])
            leave_type_cl = self.env['hr.leave.type'].search([('name','=','Casual Leave')])
            leave_type_sl = self.env['hr.leave.type'].search([('name','=','Sick Leave')])
            if leave_type_pl and leave_type_pl.double_validation == False:
                leave_type_pl.double_validation = True
            if leave_type_cl and leave_type_cl.double_validation == False:
                leave_type_cl.double_validation = True
            if leave_type_sl and leave_type_sl.double_validation == False:
                leave_type_sl.double_validation = True
            pl = leave.create({'name':'Privilege Leave Allocation',
                                    'holiday_type': 'employee',
                                    'employee_id': emp.id,
                                    'holiday_status_id': leave_type_pl.id,
                                    'number_of_days': 15,
                                    'state': 'validate',
                                    })
            el = leave.create({'name':'Casual Leave Allocation',
                                    'holiday_type': 'employee',
                                    'employee_id': emp.id,
                                    'holiday_status_id': leave_type_cl.id,
                                    'number_of_days': 12,
                                    'state': 'validate',
                                    })
            sl = leave.create({'name':'Sick Leave Allocation',
                                    'holiday_type': 'employee',
                                    'employee_id': emp.id,
                                    'holiday_status_id': leave_type_sl.id,
                                    'number_of_days': 12,
                                    'state': 'validate',
                                    })
                # self.is_leave_alocated = True
        # else:
        #     raise ValidationError(_("Leave is already allocated for employees"))
