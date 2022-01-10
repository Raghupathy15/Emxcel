# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_lease = fields.Boolean(string="On Lease")
