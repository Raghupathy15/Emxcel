
import datetime

from odoo import api, fields, models


class EmployeeConfig(models.Model):
    _inherit = 'hr.employee'

    sandwich = fields.Boolean(string="Apply")
    leave_notification = fields.Boolean(string="Show Notification")
    week_off = fields.Selection(
        [('Sunday', 'Sunday'), ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
         ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')], string='Week Off')


class LeaveApply(models.Model):
    _inherit = 'hr.leave'
    set_notification = fields.Boolean()

    @api.multi
    @api.depends('request_date_from', 'request_date_to', 'employee_id')
    def _compute_number_of_days_display(self):
        res = super(LeaveApply, self)._compute_number_of_days_display()
        for record in self:
            start_date = record.date_from.date()
            end_date = record.date_to.date()
            delta = end_date - start_date
            total_days = (delta.days + 1)
            dateList = []
            for x in range(0, total_days):
                dateList.append(start_date + datetime.timedelta(days=x))
            for date in dateList:
                for leave in self.env['resource.calendar.leaves'].search([('holiday_id', '=', False)]):
                    holiday_start_date = leave.date_from.date()
                    holiday_end_date = leave.date_to.date()
                    holiday_delta = holiday_end_date - holiday_start_date
                    holiday_total_days = (holiday_delta.days + 1)
                    holiday_dateList = []
                    for holiday_x in range(0, holiday_total_days):
                        holiday_dateList.append(holiday_start_date + datetime.timedelta(days=holiday_x))
                        for holiday in holiday_dateList:
                            if holiday == date:
                                sandwich = total_days
                                record.number_of_days = sandwich
                                record.number_of_days_display = record.number_of_days
        return res

    @api.multi
    def action_approve(self):
        res = super(LeaveApply, self).action_approve()
        for record in self:
            for leave_date in self.env['hr.leave'].search(
                    [('employee_id', '=', record.employee_id.id)]):
                print ('AAAAAAAAAAAAAAAAAA', leave_date.request_date_from)

            # start_date = record.date_from.date()
            # end_date = record.date_to.date()
            # delta = end_date - start_date
            # total_days = (delta.days + 3)
            # dateList = []
            # for x in range(0, total_days):
            #     dateList.append(start_date - datetime.timedelta(days=x))
            # for date in dateList:
            #     day = date.strftime("%A")
            #     for leave_date in self.env['hr.leave'].search(
            #             [('employee_id', '=', record.employee_id.id)]):
            #         for holiday in record.employee_id.resource_calendar_id.global_leave_ids:
            #             holiday_start_date = holiday.date_from.date()
            #             holiday_end_date = holiday.date_to.date()
            #             holiday_delta = holiday_end_date - holiday_start_date
            #             holiday_total_days = holiday_delta.days
            #             holiday_dateList = []
            #             for holiday_x in range(0, holiday_total_days):
            #                 holiday_dateList.append(holiday_start_date + datetime.timedelta(days=holiday_x))
            #                 for holiday_date in holiday_dateList:
            #                     if holiday_date == date:
            #                         sandwich = total_days
            #                         print('BBBBBBBBB', holiday, holiday_total_days)
            # stop
        return res
