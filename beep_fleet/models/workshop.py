# -*- coding: utf-8 -*-

from odoo import api, fields, models


class JobOrder(models.Model):
    _name = 'fleet.workshop'
    _inherit = 'mail.thread'
    _description = 'Workshop details'

    def compute_count(self):
        for record in self:
            record.service_count = self.env['fleet.vehicle.log.services'].search_count(
                [('workshop_id', '=', self.id)])

    service_count = fields.Integer('Service', compute='compute_count')
    name = fields.Char('Port', track_visibility='always')
    assign_id = fields.Many2one('res.users', string='Name of Mechanic Assigned', default=lambda self: self.env.user,
                                required=True, track_visibility='always')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True, 
                default=lambda self: self.env.user.company_id)

    def get_service_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Workshop',
            'view_mode': 'tree,form',
            'res_model': 'fleet.vehicle.log.services',
            'domain': [('workshop_id', '=', self.id)],
            'context': "{'create': False}"
        }

    @api.multi
    def action_create_job(self):
        for data in self:
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'context': {
                    'default_assign_id': data.assign_id.id,
                    'default_workshop_id': data.id,
                },
                'res_model': 'fleet.vehicle.log.services',
                'type': 'ir.actions.act_window',
            }
