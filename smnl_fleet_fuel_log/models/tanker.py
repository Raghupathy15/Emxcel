# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = "res.users"

    tanker_ids = fields.One2many('tanker.notify', 'user_id', string="Notify")


class TankerNotify(models.Model):
    _name = "tanker.notify"
    _order = 'id desc'

    user_id = fields.Many2one('res.users', string="User")
    tanker_id = fields.Many2one('fleet.tanker', string="Tanker")
    capacity = fields.Float('Tank Capacity')
    qty = fields.Float(string="Quantity")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company')
    notify_limit = fields.Float(string="Notify Qty Limit")
    date = fields.Date(string="Date")


class FleetTanker(models.Model):
    _name = "fleet.tanker"
    _inherit = ['mail.thread']
    _description = 'Tanker Master'
    _order = 'id desc'

    @api.model
    def _default_uom(self):
        return self.env['uom.uom'].search([('name', '=', 'Liter(s)')], limit=1)

    name = fields.Char(required=True, string='Name', track_visibility='onchange')
    capacity = fields.Float('Tank Capacity', track_visibility='onchange', required=True)
    uom_id = fields.Many2one('uom.uom', string='UOM', default=_default_uom)
    qty = fields.Float(string="Quantity", required=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id, string='Company',
                                 track_visibility='onchange')
    notify_limit = fields.Float(string="Notify Qty Limit", required=True, )
    driver_id = fields.Many2one('fleet.driver.registration', string="Driver")
    active = fields.Boolean(string="Active", default=True)

    @api.multi
    def _cron_notify_min_qty(self):
        for remove in self.env['tanker.notify'].search([]):
            remove.unlink()
        for group in self.env['res.groups'].search([('category_id.name', '=', 'Fleet'), ('name', '=', 'Manager')]):
            for user in group.users:
                for tank in self.env['fleet.tanker'].sudo().search([]):
                    current_date = datetime.today()
                    if tank.qty <= tank.notify_limit:
                        self.env['tanker.notify'].create({
                            'tanker_id': tank.id,
                            'user_id': user.id,
                            'date': current_date,
                        })
                for mail in user.partner_id:
                    template_id = self.env.ref('smnl_fleet_fuel_log.email_template_tanker_minimum_qty')
                    template_id.write({'email_to': mail.email})
                    template_id.send_mail(user.id, force_send=True, raise_exception=True)
