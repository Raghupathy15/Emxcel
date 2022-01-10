# -*- encoding: utf-8 -*-

from odoo import api, models, fields



class HrAttendance(models.Model):
    _inherit = "hr.attendance"
    _description = "HR Attendance"

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
    	return True



    
