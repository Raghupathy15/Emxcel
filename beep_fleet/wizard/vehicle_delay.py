# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


# Vehicle Delay Remark
class VehicleDelayRemark(models.TransientModel):
    _name = 'vehicle.delay.remark'
    _description = 'Vehicle Delay Remark Wizard'

    delay_type = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Is Delay",
                                  related="service_log_id.delay_type")
    name = fields.Text('Delay Remarks')
    service_log_id = fields.Many2one('fleet.vehicle.log.services', 'Service')
    is_check = fields.Boolean(
        string="Delay", related="service_log_id.is_check")

    @api.multi
    def action_done_remark(self):
        if self._context.get('is_reject'):
            for service_log in self.env['fleet.vehicle.log.services'].browse(
                    self._context.get('default_service_log_id', False)):
                if self.service_log_id.date_of_delivery and self.service_log_id.date_of_delivery < datetime.now() and not self.name:
                    raise ValidationError(_("Kindly provide delay reason."))
                service_log.write({'state': 'done', 'service_delay_reason': self.name,
                                   'service_done_time': datetime.now()})
