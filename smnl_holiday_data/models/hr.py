# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = 'hr.employee'

    optional_holiday_ids = fields.One2many('optional.holiday', 'holiday_id', string='Optional Holidays')

    @api.multi
    @api.constrains('optional_holiday_ids')
    def validations(self):
        if self.optional_holiday_ids and len(self.optional_holiday_ids) > 2:
            raise ValidationError(_("You can have only two optional holidays as maximum !.."))
        exist_holiday_list = []
        for values in self.optional_holiday_ids:
            if values.opt_holiday_id.id in exist_holiday_list:
                raise ValidationError(_('You can not select same optional holiday multiple times.'))
            exist_holiday_list.append(values.opt_holiday_id.id)

    class io_chart(models.Model):
        _name = "optional.holiday"
        _description = 'Optional Holiday details'

        opt_holiday_id = fields.Many2one('resource.calendar.leaves', string='Reason', required=True,
                                         help='Only optional holidays will be shown')
        date_from = fields.Datetime('Start Date', readonly=True)
        date_to = fields.Datetime('End Date', readonly=True)
        holiday_id = fields.Many2one('hr.employee', string='Employee')

        @api.onchange('opt_holiday_id')
        def onchange_opt_holiday_id(self):
            if self.opt_holiday_id:
                self.date_from = self.opt_holiday_id.date_from
                self.date_to = self.opt_holiday_id.date_to