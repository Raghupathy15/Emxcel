from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    emp_code = fields.Char(string='Employee Code')