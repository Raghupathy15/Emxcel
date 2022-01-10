# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import logging

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model
    def create(self, vals):
        # Inherited method to create compensatory leave for Holiday.
        res = super(HrAttendance, self).create(vals)
        if vals.get('check_out'):
            # get date from datetime field to compare with holiday date.
            if not isinstance(vals.get('check_out'), datetime.date):
                check_out_date = datetime.datetime.strptime(
                    vals.get('check_out'), '%Y-%m-%d %H:%M:%S').date()
            else:
                check_out_date = vals.get('check_out').date()
            holiday_found = self.env['resource.calendar.leaves'].search([('is_optional_holiday', '=', False), ('calendar_id', '=', res.employee_id.resource_calendar_id.id), '|',
                                                                         ('date_from', '=', check_out_date), ('date_to', '=', check_out_date)])
            if holiday_found:
                # Get compensatory holiday type
                compansate_type = self.env.ref(
                    'smnl_leave_extend.holiday_smnl_status_comp')
                if compansate_type:
                    # Create compensatory leave allocation.
                    self.env['hr.leave.allocation'].sudo().create({'name': 'Allocation of Holiday Compensate Leave',
                                                                   'holiday_status_id': compansate_type.id,
                                                                   'number_of_days': 1.0,
                                                                   'employee_id': res.employee_id.id,
                                                                   'holiday_date': check_out_date})
                else:
                    _logger.warning(
                        "Compensatory Leave can not be create for user %s", res.employee_id.name)

        return res

    @api.multi
    def write(self, vals):
        # Inherited method to create compensatory leave for Holiday.
        res = super(HrAttendance, self).write(vals)
        if vals.get('check_out'):
            # get date from datetime field to compare with holiday date.
            if not isinstance(vals.get('check_out'), datetime.date):
                check_out_date = datetime.datetime.strptime(
                    vals.get('check_out'), '%Y-%m-%d %H:%M:%S').date()
            else:
                check_out_date = vals.get('check_out').date()
            holiday_found = self.env['resource.calendar.leaves'].search([('calendar_id', '=', self.employee_id.resource_calendar_id.id), ('is_optional_holiday', '=', False), '|',
                                                                         ('date_from', '=', check_out_date), ('date_to', '=', check_out_date)])
            if holiday_found:
                compansate_type = self.env.ref(
                    'smnl_leave_extend.holiday_smnl_status_comp')
                if compansate_type:
                    # Check if compensatory leave is already created for that holiday respect to employee.
                    rec_created = self.env['hr.leave.allocation'].search(
                        [('employee_id', '=', self.employee_id.id), ('holiday_date', '=', check_out_date)])
                    if not rec_created:
                        # Create compensatory leave allocation.
                        self.env['hr.leave.allocation'].sudo().create({'name': 'Allocation of Holiday Compensate Leave',
                                                                       'holiday_status_id': compansate_type.id,
                                                                       'number_of_days': 1.0,
                                                                       'employee_id': self.employee_id.id,
                                                                       'holiday_date': check_out_date})
                else:
                    _logger.warning(
                        "Compensatory Leave can not be create for user %s", self.employee_id.name)

        return res
