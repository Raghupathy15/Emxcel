from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import re


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    puc_date = fields.Date(default=fields.Date.context_today,
                           string="PUC date", track_visibility='always')
    puc_exp_date = fields.Date(
        string="PUC Expiration date", track_visibility='always')
    insurance_date = fields.Date(
        string="Insurance date", track_visibility='always')
    insurance_type = fields.Selection([('3rd_party', '3rd Party'),
                                       ('comprehensive', 'Comprehensive')], 'Insurance Type', track_visibility='always')
    insurance_provider = fields.Char(
        'Insurance Provider', track_visibility='always')
    insurance_idv = fields.Char(
        'Insurance IDV Value', track_visibility='always')
    insurance_exp_date = fields.Date(
        string="Expiry date", track_visibility='always')
    odometer_unit = fields.Selection([
        ('kilometers', 'Kilometers'),
        ('hours', 'Hours')
    ], 'Odometer Unit', default='kilometers', help='Unit of the odometer ', required=True)
    spare_part_ids = fields.One2many(
        'vehicle.spare.parts', 'vehicle_id', string="Spare Parts")
    empty_vehicle_mileage = fields.Float("Empty Vehicle's Mileage")
    loaded_vehicle_mileage = fields.Float("Loaded Vehicle's Mileage")
    insurance_number = fields.Char("Insurance Number")
    owned_by_id = fields.Many2one('res.partner', string='Owned By')
    contract_end_date = fields.Date(string="Contract end date")
    puc_number = fields.Char("PUC Number")
    fastag_number = fields.Char(string="FasTag Number", size=16)
    fastag_balance = fields.Monetary(
        string="FasTag Balance", currency_field='company_currency_id')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, 
                default=lambda self: self.env.user.company_id)

    @api.constrains('residual_value')
    def _check_residual_value(self):
        if self.residual_value and self.residual_value < 0:
            raise ValidationError(
                _("Residual Value	should not allow negative value."))

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        vehicle_ids = []
        if name:
            vehicle_ids = self._search([('license_plate', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not vehicle_ids:
            vehicle_ids = self._search([('smnl_doors', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not vehicle_ids:
            vehicle_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(vehicle_ids).name_get()

    @api.multi
    @api.constrains('fastag_number')
    def _check_fastag_number_validation(self):
        r = re.compile("[0-9]*[.,]?[0-9]*\Z")
        for data in self:
            if data.fastag_number and len(data.fastag_number) != 16:
                raise ValidationError(
                    _("Values not sufficient !.. Please Enter 16 digit 'FasTag Number'"))
            if not bool(r.match(data.fastag_number)):
                raise ValidationError(
                    _("Please enter only numeric caharcter for FasTag number."))
