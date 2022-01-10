# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime 
import calendar


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    carry_date = fields.Char(string="Carry Forward Year")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, readonly=True)

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year,month)[1])
        return datetime.date(year, month, day)

    def compute_expiry_holiday(self):
        # Compute expiry date after 6 month
        for record in self:
            if record.holiday_date:
                record.holiday_expiry_date = self.add_months(record.holiday_date,6)

    holiday_date = fields.Date(string="Date of Holiday")
    holiday_expiry_date = fields.Date(string="Expiry of Holiday", compute='compute_expiry_holiday')

    @api.model
    def _update_leave_allocation(self):
        for record in self.search([('state', '=', 'validate')]):
            if record.holiday_expiry_date :
                if record.holiday_expiry_date < datetime.datetime.now().date():
                    record.action_refuse()


    