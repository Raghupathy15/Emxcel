# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetType(models.Model):
    _name = "fleet.type"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code")

    _sql_constraints = [
             ('check_code', 'unique (code)', "Vehicle type code should be unique!"),
         ]


