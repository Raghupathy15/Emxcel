# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FleetVehicleState(models.Model):
    _inherit = "fleet.vehicle.state"

    draft_state = fields.Boolean("Draft")

    @api.constrains('draft_state')
    @api.multi
    def check_draft_state(self):
        draft_check = self.env['fleet.vehicle.state'].search([('draft_state', '=', True)])
        for rec in self:
            if len(draft_check) > 1 and rec.draft_state:
                raise UserError(_('You cannot check more than 1 draft...'))
