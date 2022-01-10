# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
import calendar


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _carry_forward_leave(self):
        for record in self.search([]):
            allocation_obj = self.env['hr.leave.allocation']
            start_of_current_year = datetime.now().date().replace(month=1, day=1)
            end_of_current_year = datetime.now().date().replace(month=12, day=31)

            epoch_year = datetime.today().year
            last_year_start = datetime(epoch_year-1, 1, 1).date()
            last_year_end = datetime(epoch_year-1, 12, 31).date()

            for leave in allocation_obj.search([('employee_id', '=', record.id), ('state', '=', 'validate')]):
                if leave.holiday_status_id.validity_start >= last_year_start and leave.holiday_status_id.validity_stop <= last_year_end:
                    
                    virtual_remaining_leaves = leave.holiday_status_id.with_context(
                        {'employee_id': record.id}).virtual_remaining_leaves
                    holiday_type = self.env['hr.leave.type'].search([('name', '=', leave.holiday_status_id.name),
                                                                     ('validity_start', '>=', start_of_current_year), ('validity_stop', '<=', end_of_current_year)])

                    current_year_allo = allocation_obj.search(
                        [('employee_id', '=', record.id), ('holiday_status_id', '=', holiday_type.id)])
                        
                    if current_year_allo and holiday_type.name in ['Casual Leave', 'Privilege Leave']:
                        current_year_allo.write({'number_of_days': current_year_allo.number_of_days + virtual_remaining_leaves})
                        leave.action_refuse()
                    else:
                        leave.action_refuse()

