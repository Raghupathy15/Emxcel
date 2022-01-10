# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'

    def action_assign_holiday_leave(self):
        # Method to assign holiday to each working schedule.
        holidays = self.env['smnl.holiday'].search([])
        working_schedule = self.env['resource.calendar'].search([])
        for ws in working_schedule:
            for holiday in holidays:
                holiday_found = self.env['resource.calendar.leaves'].search([('name', '=', holiday.name), ('calendar_id', '=', ws.id)])
                if not holiday_found:
                    # if no holiday found then we will assign holiday to working schedule
                    self.env['resource.calendar.leaves'].create({
                        'name': holiday.name,
                        'date_from': holiday.date_from,
                        'date_to': holiday.date_to,
                        'calendar_id': ws.id,
                        'is_optional_holiday': holiday.is_optional,
                    })
