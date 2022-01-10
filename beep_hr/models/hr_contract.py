# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime


class Contract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Contracts'

    gross = fields.Monetary('Gross', digits=(16, 2))
    wage = fields.Monetary('Basic', digits=(16, 2), required=True, track_visibility="onchange",
                           help="Employee's monthly gross wage.")
    employee = fields.Char(string='Employee')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        employee = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        if employee:
            self.gross = employee.wage

    @api.multi
    def _cron_notify_non_active_employee_contract(self):
        non_contract_emp_name = []
        non_contract_emp_data = self.env['hr.employee'].search([('contract_ids', '=', False)]).ids
        contract_notification_list = non_contract_emp_data
        expire_contract_emp_data = self.env['hr.employee'].search([('contract_ids', '!=', False)])
        for emp in expire_contract_emp_data:
            count = 0
            for emp_contract in emp.contract_ids:
                if emp_contract.state == 'open':
                    count += 1
                    if emp_contract.date_end and emp_contract.date_end < datetime.today().date():
                        count += 1
            if count == 0 or count == 2:
                contract_notification_list.append(emp.id)
        for emp_name in self.env['hr.employee'].search([('id', 'in', contract_notification_list)]):
            non_contract_emp_name.append(emp_name)

        user_group = self.env.ref("hr.group_hr_manager")
        user = self.env['res.users'].search([('groups_id', 'in', self.env.ref("hr.group_hr_manager").id)], limit=1).id
        email_list = [usr.partner_id.email for usr in user_group.users if usr.partner_id.email]
        email_to = ",".join(email_list)
        template_id = self.env.ref('beep_hr.email_template_employee_contract_notification')
        template_id.write({'email_to': email_to})
        template_id.with_context(non_contract_emp_name=non_contract_emp_name).send_mail(user,
                                                                                        force_send=True,
                                                                                        raise_exception=True,
                                                                                        )
