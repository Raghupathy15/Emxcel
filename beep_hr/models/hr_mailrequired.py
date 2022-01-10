from odoo import fields, models


class Hrmail(models.Model):
    _inherit = 'hr.applicant'

    partner_name = fields.Char(string='Applicants name', required=True)
    email_from = fields.Char(string='Email', required=True)
