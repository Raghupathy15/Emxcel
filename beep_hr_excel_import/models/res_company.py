# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'

    @api.multi
    def action_create_user_for_xls(self):
        user_rec = self.env['res.users']
        emp_data = self.env['hr.employee'].search([('emp_code', '!=', False),('user_id', '=', False),
                                                   ('active', '=', True),('id', '!=', 1)],limit=100)        
        # count = 0
        for emp_part in emp_data:
            res_user = user_rec.create({'login':emp_part.emp_code,
                                    'name': emp_part.name,
                                    'password': '123456',
                                    'active': True,
                                    'notification_type': 'email',
                                    'odoobot_state': 'disabled',
                                    'share': False,
                                    'company_id': 1,
                                    'sale_team_id': 1,
                                    })  
            # count= count + 1
        self.action_match_users_with_employee()

    @api.multi
    def action_match_users_with_employee(self):
        emp = self.env['hr.employee'].search([('active','=',True)])
        # count = 0
        for employee in emp:
            if not employee.user_id:
                user = self.env['res.users'].search([('login','=',employee.emp_code)])
                if user:
                    employee.user_id = user.id
                    # count = count + 1
