# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class HrSection(models.Model):
    _name = 'hr.section'
    _description = 'HR Section'

    name = fields.Char("Name")
    code = fields.Char("Code", size=7)
    smnl_id = fields.Integer('Smnl Id')
