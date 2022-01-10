# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    swipe_status = fields.Selection([
        ('approved', 'Swipe Approved'),
        ('missed', 'Missed Swipe')],"Swipe Status")