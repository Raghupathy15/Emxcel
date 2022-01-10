# -*- coding: utf-8 -*-
from datetime import datetime, time
from odoo import models, api, fields, _
from pytz import timezone


class HRPayslip(models.Model):
    _inherit = "hr.payslip"
    _description = 'Hr Payslip'

    @api.model
    def compute_sheet(self):
        for payslip in self:
            for employee in self.env['hr.employee'].search([('id', '=', payslip.employee_id.id)]):
                if employee.optional_holiday_ids:
                    for line in employee.optional_holiday_ids:
                        if str(payslip.month) == line.date_from.strftime('%-m') and str(
                                payslip.year) == line.date_from.strftime('%Y'):
                            for payslip_line in payslip.worked_days_line_ids:
                                if payslip_line.code == 'GLOBAL':
                                    payslip_line.number_of_days += 1
                                    payslip_line.number_of_hours += payslip.contract_id.resource_calendar_id.hours_per_day
        record = super(HRPayslip, self).compute_sheet()
