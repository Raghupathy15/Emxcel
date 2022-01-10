# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread']
    _description = 'Purchase request'

    name = fields.Char(readonly=True, copy=False, string="PR Reference")
    state = fields.Selection(
        [('request', 'Request'), ('confirm', 'Confirm')], 'State', default='request')
    vehicle_service_id = fields.Many2one(
        'fleet.vehicle.log.services', string='Service')
    lead_time = fields.Integer(string="Lead Time", help="Lead time in days.")
    responsible_id = fields.Many2one('res.users', string="Requisitioner", track_visibility='onchange',
                                     default=lambda self: self.env.uid)
    sp_pr_ids = fields.One2many(
        'spare_part.purchase.request', 'pr_id', string='Spare-part')
    purchase_order_ids = fields.One2many(
        'purchase.order', 'purchase_request_id', string='Purchase Reference')
    pr_purchase_order_count = fields.Integer(
        string="PO Reference", compute='_compute_purchase_order_count')

    @api.model
    def create(self, vals):
        if 'code' not in vals or vals['code'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fleet.vehicle.spare.part.requisition') or _('New')
        return super(PurchaseRequest, self).create(vals)

    @api.multi
    def _compute_purchase_order_count(self):
        # count the total link purchase order's.
        for rec in self:
            rec.pr_purchase_order_count = len(self.purchase_order_ids)

    def action_pr_purchase_order(self):
        ''' Return : Action Purchase Order '''
        action_vals = {
            'name': _('Purchase Order'),
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'context': {'create': False},
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(self.purchase_order_ids.ids) == 1:
            action_vals.update(
                {'res_id': self.purchase_order_ids[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

    @api.multi
    def action_confirm_pr(self):
        for rec in self:
            if rec.sp_pr_ids and rec.sp_pr_ids.filtered(lambda m: not m.vendor_id or not m.pr_cost):
                raise UserError(
                    _('Kindly insert fill all data in Spare-Part table.'))
            vendor_list = set(
                [spare_part.vendor_id.id for spare_part in rec.sp_pr_ids])
            for vendor in vendor_list:
                purchase_order = self.env['purchase.order'].create({'partner_id': vendor or False,
                                                                    'vehicle_log_service_id': rec.vehicle_service_id.id,
                                                                    'purchase_request_id': rec.id})
                for spare_part in rec.sp_pr_ids.filtered(lambda m: m.vendor_id.id == vendor):
                    purchase_order.update({'order_line': [(0, 0, {
                        'is_fleet': False,
                        'product_id': spare_part.product_tmpl_id.product_variant_id.id,
                        'name': spare_part.product_tmpl_id.product_variant_id.name or " ",
                        'spare_part_id': spare_part.spare_part_id.id,
                        'spare_part_purchase_request_id': spare_part.id,
                        'product_qty': spare_part.pr_qty,
                        'price_unit': spare_part.pr_cost,
                        'date_planned': fields.datetime.now(),
                        'product_uom': self.env['uom.uom'].search([('name', '=', 'Unit(s)')]).id
                    })]})
                    for order in purchase_order.order_line:
                        spare_part.write({'purchase_order_line_id': order.id})
                    spare_part.spare_part_id.write(
                        {'purchase_id': purchase_order.id})
            rec.state = 'confirm'
