# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: SREEJITH SASIDHARAN (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EmployeeConfig(models.Model):
    _inherit = 'hr.employee'

    sandwich = fields.Boolean(string="Apply")
    leave_notification = fields.Boolean(string="Show Notification")


class GlobalConfig(models.Model):
    _inherit = 'resource.calendar'

    sandwich = fields.Boolean(string="Sandwich Rule")

    @api.onchange('sandwich')
    def set_sandwich(self):
        for employee in self.env['hr.employee'].search([('resource_calendar_id', '=', self._origin.id)]):
            employee.write({'sandwich': self.sandwich})


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leave_ids = fields.One2many('hr.leave', 'employee_id', string="Leaves")


class LeaveApply(models.Model):
    _inherit = 'hr.leave'
    set_notification = fields.Boolean()
    extend_leave = fields.Boolean("Extend Leave")

    @api.multi
    def action_leave_extend(self):
        for rec in self:
            rec.extend_leave = True
            rec.sudo().action_refuse()
            rec.sudo().action_draft()

    @api.multi
    @api.onchange('holiday_status_id', 'request_date_from', 'request_date_to', 'employee_id')
    @api.constrains('request_date_from', 'request_date_to', 'employee_id')
    def check_leave(self):
        for record in self:
            start_date = record.date_from
            end_date = record.date_to
            if record.employee_id.sandwich and record.employee_id \
                    and record.employee_id.resource_calendar_id.sandwich and record.employee_id:
                record.set_notification = record.employee_id.leave_notification
                leave_dates = []
                for leave_days in record.employee_id.resource_calendar_id.global_leave_ids:
                    if leave_days.date_from.date() + timedelta(1) == leave_days.date_to.date():
                        leave_dates.append(str(leave_days.date_to.date()))
                    else:
                        duration = (leave_days.date_to - leave_days.date_from).days + 1
                        for single_date in (leave_days.date_from + timedelta(days) for days in range(1, duration + 1)):
                            leave_dates.append(str(single_date.date()))
                working_days = []
                for day in record.employee_id.resource_calendar_id.attendance_ids:
                    if int(day.dayofweek) not in working_days:
                        working_days.append(int(day.dayofweek))
                for day in range(1, 31):
                    next_date = (end_date + timedelta(day)).date()
                    next_dates = str(next_date) in leave_dates or next_date.weekday() not in working_days
                    plus_next_date = (start_date + timedelta(day + 1)).date()
                    if next_dates:
                        for leave in record.employee_id.leave_ids.filtered(
                                lambda r: r.employee_id == record.employee_id):
                            if plus_next_date == leave.request_date_from:
                                raise UserError(_(
                                    'You already raise leave before or after weekly-off or holiday. So kindly raise single club leave.'))
                    else:
                        break

                for day in range(1, 31):
                    previous_date = (start_date - timedelta(day)).date()
                    previous_dates = str(previous_date) in leave_dates or previous_date.weekday() not in working_days
                    plus_previous_date = (start_date - timedelta(day + 1)).date()
                    if previous_dates:
                        for leave in record.employee_id.leave_ids.filtered(
                                lambda r: r.employee_id == record.employee_id):
                            if leave.request_date_to == plus_previous_date:
                                raise UserError(_(
                                    'You already raise leave before or after weekly-off or holiday. So kindly raise single club leave.'))
                    else:
                        break

    @api.multi
    @api.onchange('number_of_days', 'request_date_from', 'request_date_to', 'employee_id')
    @api.depends('number_of_days', 'request_date_from', 'request_date_to', 'employee_id')
    def _compute_number_of_days_display(self):
        res = super(LeaveApply, self)._compute_number_of_days_display()
        for record in self:
            start_date = record.date_from
            end_date = record.date_to
            if record.employee_id.sandwich and record.employee_id \
                    and record.employee_id.resource_calendar_id.sandwich and record.employee_id:
                record.set_notification = record.employee_id.leave_notification
                total_days = (end_date - start_date).days + 1
                if start_date.date() != end_date.date():
                    record.number_of_days = total_days
                    record.number_of_days_display = record.number_of_days
                else:
                    if record.number_of_days != 0:
                        record.number_of_days = total_days
                        record.number_of_days_display = record.number_of_days
            else:
                record.set_notification = False
                record.number_of_days = record._get_number_of_days(record.date_from, record.date_to,
                                                                   record.employee_id.id)
        return res
