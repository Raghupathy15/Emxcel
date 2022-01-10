# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetDriverRegistration(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = "fleet.driver.registration"
    _rec_name = 'employee_id'

    employee_id = fields.Many2one(
        "hr.employee", track_visibility="onchange", string="Employee")
    blood_group = fields.Selection([
        ('a_plus', 'A+'),
        ('a_negative', 'A-'),
        ('b_plus', 'B+'),
        ('b_negative', 'B-'),
        ('o_plus', 'O+'),
        ('o_negetive', 'O-'),
        ('ab_plus', 'AB+'),
        ('ab_negative', 'AB-')], "Blood Group")
    contract_expiry_date = fields.Date("Contract Expiry Date")
    fleet_type = fields.Many2one('fleet.type', string='Specialized in')
    license_number = fields.Char("License Number")
    license_Type = fields.Selection([
        ('LMV', 'LMV'),
        ('HMV', 'HMV'),
        ('MGV', 'MGV'),
        ('HGMV', 'HGMV'),
        ('HPMV/HTV', 'HPMV/HTV')
    ], string='License Type')
    license_issue_date = fields.Date("License Issue Date")
    license_expiry_date = fields.Date("License Expiry Date")
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True, 
                default=lambda self: self.env.user.company_id)