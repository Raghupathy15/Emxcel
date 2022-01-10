# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"
    _description = "Resource Working Time"

    active = fields.Boolean(default=True)


class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"
    _description = "Resource Leaves Detail"

    is_optional_holiday = fields.Boolean(string="Is Optional Holiday")
