# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SmnlHoliday(models.Model):
    _name = 'smnl.holiday'
    _description = 'SMNL Holiday'

    name = fields.Char('Reason')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string="Company")
    date_from = fields.Datetime('Start Date', required=True)
    date_to = fields.Datetime('End Date', required=True)
    is_optional = fields.Boolean('Is optional Holiday?')
