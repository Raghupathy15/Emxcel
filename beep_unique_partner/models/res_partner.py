# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [('email_uniq', 'unique(email)', 'Email must be unique.'),
                        ('mobile_uniq', 'unique(mobile)', 'Mobile must be unique.')]
