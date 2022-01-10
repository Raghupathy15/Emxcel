# -*- coding: utf-8 -*-

from datetime import datetime

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LeaveEncashment(models.Model):
    _name = "leave.encashment"
    _description = 'Leave Encashment'
    _inherit = ['mail.thread']
    _order = 'id desc'

    def _default_employee_get(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def _default_leave_type(self):
        return self.env['hr.leave.type'].search([('name', '=', 'Privilege Leave')], limit=1)

    @api.onchange('employee_id')
    def onchange_remaining_leave(self):
        for line in self:
            if line.holiday_status_id:
                val = self.env['hr.leave.report'].search([
                    ('employee_id.user_id', '=', self.env.uid),
                    ('holiday_status_id', '=', line.holiday_status_id.id),
                    ('state', 'in', [('confirm'), ('validate1'), ('validate')]),
                    ('employee_id.company_id', '=', line.company_id.id)])
                total_pl = 0
                for data in val:
                    total_pl += data.number_of_days
                    line.remaining_leave = total_pl

    name = fields.Char(string="Sequence No.", default='New', readonly=True, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submited'), ('approve', 'Approved')], string='Status',
                             default='draft', track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee_get, readonly=True,
                                  track_visibility='onchange')
    holiday_status_id = fields.Many2one('hr.leave.type', string='Leave Type', default=_default_leave_type,
                                        track_visibility='onchange')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id,
                                 track_visibility='onchange')
    remaining_leave = fields.Float('Available PL Leaves', track_visibility='onchange')
    requested_date = fields.Date(string='Requested Date', default=datetime.today().strftime('%Y-%m-%d'),
                                 track_visibility='onchange')
    encasement_days = fields.Float('Encashment days', track_visibility='onchange')
    payable_amount = fields.Float('Payable Amount', track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('leave.encashment')
        rec = super(LeaveEncashment, self).create(vals)
        return rec

    @api.multi
    def action_confirm(self):
        if self.employee_id.actual_doj:
            normal_date = self.employee_id.actual_doj + relativedelta(years=2)
            if fields.Date.today() < normal_date:
                raise ValidationError("Encashment should apply after 2 years of Joining date")
            elif self.encasement_days > self.remaining_leave:
                raise ValidationError("Encashment days should be less than Available PL leaves")
            elif self.encasement_days <= 0:
                raise ValidationError("Encashment days should be more than 0")
        else:
            raise ValidationError("You must give Joining date in Employee master !")

        encasement_days = 0
        for leave in self:
            allocation = self.env['hr.leave.allocation'].search([('employee_id.user_id', '=', self.env.uid),
                                                                 ('holiday_status_id', '=', leave.holiday_status_id.id),
                                                                 ('state', '=', 'validate')], limit=1)
            encasement_days = allocation.number_of_days - leave.encasement_days
            allocation.sudo().write({'number_of_days': encasement_days})
        if self.employee_id.sudo().contract_id.wage:
            self.payable_amount = round(self.encasement_days * (self.employee_id.sudo().contract_id.wage / 26))
        self.write({'state': 'submit'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})
