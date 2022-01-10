# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class FleetVehicleLogServices(models.Model):
    _name = 'fleet.vehicle.log.services'
    _inherit = ['fleet.vehicle.log.services', 'mail.thread']

    def compute_third_party(self):
        for service in self:
            if service.cost_subtype_id.category == 'third_party':
                service.is_third_party = True
            else:
                service.is_third_party = False

    def compute_total(self):
        for record in self:
            spare_count = 0
            service_count = 0
            for service in record.cost_ids:
                service_count = service_count + service.amount
            for spare in record.spare_part_ids:
                spare_count = spare_count + spare.total_cost
            record.total_amount = spare_count + service_count

    def compute_check_delay(self):
        for record in self:
            if record.date_of_delivery and record.date_of_delivery < datetime.now() and record.state == 'in_progress':
                record.is_check = True
                record.delay_type = 'yes'
            else:
                record.is_check = False
                record.delay_type = 'no'

    def compute_gate_pass_count(self):
        # Get count of gate pass for each service log.
        for record in self:
            record.gate_pass_count = self.env['gate.pass'].search_count(
                [('service_id', '=', record.id)])

    name = fields.Char(readonly=True, copy=False, default="New")
    date_of_delivery = fields.Datetime(
        string="Expected Delivery Date", track_visibility='always')
    next_service_date = fields.Date(string="Next service date")
    odometer_unit = fields.Selection([
        ('hours', 'Hours'),
        ('kilometers', 'Kilometers')], default='kilometers', string='Unit', required='1')
    hr_reading = fields.Float('Hour Reading')
    hr_reading_unit = fields.Char(string='hr_reading', default='Hours')
    total_amount = fields.Float(string='Amount', compute='compute_total')
    workshop_id = fields.Many2one(
        'fleet.workshop', 'Workshop', track_visibility='always')
    state = fields.Selection(
        [('job_card', 'Job Card'), ('draft', 'Draft'), ('request', 'Requested'), ('approve', 'Approve'),
         ('sp_request', 'On Hold'), ('in_progress', 'In-progress'), ('done', 'Done'), ('reject', 'Reject')], 'State',
        default='job_card', track_visibility='always')
    # Relational fields
    assign_id = fields.Many2one('res.users', string='Assigned Mechanic', default=lambda self: self.env.user,
                                domain=lambda self: [('groups_id', 'in',
                                                      self.env.ref('beep_fleet.fleet_group_service_mechanic').id)
                                                     ])
    driver_id = fields.Many2one(
        'res.users', string='Driver Name', track_visibility='always', help="Requested By")
    spare_part_ids = fields.One2many('fleet.spare.part', 'vehicle_log_service_id', string='Spare Part',
                                     track_visibility='always')
    picking_id = fields.Many2one(
        'stock.picking', string='Spare-part Transfer Reference')
    purchase_order_ids = fields.Many2many(
        'purchase.order', string='Purchase Order')
    purchase_order_count = fields.Integer(
        string="PO Reference", compute='_compute_purchase_order_count')
    third_party_service = fields.Boolean("Third Party Service")
    spare_part_pr_ids = fields.One2many(
        "purchase.request", "vehicle_service_id", string="Spare-part PR")
    sp_pr_visibility = fields.Boolean(
        string="PR Smart-button Visibility", compute='_compute_sp_pr_visibility')
    service_approve_time = fields.Datetime(
        "Service Request Date & Time", default=fields.Datetime.now)
    service_done_time = fields.Datetime("Service Completion Date & Time")
    service_completion_time = fields.Char(string="Breakdown Period", compute="_compute_service_completion_time",
                                          stored=True)
    delay_type = fields.Selection(
        [('yes', 'Yes'), ('no', 'No')], string="Is Delay", compute="compute_check_delay")
    is_check = fields.Boolean(string="Delay", compute="compute_check_delay")
    service_delay_reason = fields.Text(string="Delay Reason", copy=False)
    service_request_number = fields.Char(string="Service Request No.")
    vehicle_type = fields.Many2one("fleet.type",
                                   related='vehicle_id.model_id.fleet_type', string="Vehicle Type")
    fleet_supervisor_id = fields.Many2one('res.users', string='Reported By', default=lambda self: self.env.user,
                                          help="Fleet Supervisor Name")
    workshop_supervisor_id = fields.Many2one(
        'res.users', string='Workshop Supervisor', help="Fleet Supervisor Name")
    short_issue_note = fields.Text(string="Short Issue Note")
    towing_facility = fields.Boolean(string="Towing Facility Required")
    location = fields.Char(string="Location")
    priority_level = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string='Priority',
                                      default='high', required=True)
    repair_maintenance_type_id = fields.Many2one(
        'repair.maintenance.type', string='Repair and Maintenance Type', track_visibility='onchange',
        help="Repair and Maintenance Type")
    is_breakdown = fields.Boolean(
        related='repair_maintenance_type_id.is_breakdown', string="Is Breakdown")
    breakdown_type_id = fields.Many2one(
        'breakdown.type', string='Breakdown Type', help="Breakdown Type")
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, readonly=True,
                                 default=lambda self: self.env.user.company_id)
    smnl_doors = fields.Char(related='vehicle_id.smnl_doors', string="Doors")
    is_third_party = fields.Boolean('Third Party',compute='compute_third_party')
    gate_pass_count = fields.Integer(
        'Gate Pass', compute='compute_gate_pass_count')

    @api.multi
    @api.constrains('date_of_delivery', 'service_approve_time')
    def get_delivery_service(self):
        if self.date_of_delivery and self.service_approve_time and self.service_approve_time > self.date_of_delivery:
            raise ValidationError(
                "'Expected Delivery Date' should be greater than the 'Service Requested Date’'")

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fleet.vehicle.log.services') or _('New')
        return super(FleetVehicleLogServices, self).create(vals)

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_gate_pass(self):
        return {
            'name': _('Gate Pass'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'gate.pass',
            'target': 'new',
            'context': {
                'default_service_id': self.id
            }
        }
        

    @api.multi
    @api.depends('service_approve_time', 'service_done_time')
    def _compute_service_completion_time(self):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        if self.service_done_time and self.service_approve_time:
            request_done_time = datetime.strftime(
                self.service_done_time, datetime_format)
            request_time = datetime.strftime(
                self.service_approve_time, datetime_format)
            self.service_completion_time = datetime.strptime(str(request_done_time),
                                                             datetime_format) - datetime.strptime(str(request_time),
                                                                                                  datetime_format)

    @api.multi
    def _compute_sp_pr_visibility(self):
        # Spare-part PR smart button visibility.
        for rec in self:
            if rec.state in ('approve', 'sp_request') and len(
                    rec.spare_part_ids.filtered(lambda m: m.use_qty > m.qty_available)) != 0:
                rec.sp_pr_visibility = True
            elif rec.state in ('sp_request', 'in_progress', 'done') and len(rec.spare_part_pr_ids) != 0:
                rec.sp_pr_visibility = True

    @api.multi
    def action_spare_part_purchase_request(self):
        for rec in self:
            if rec.spare_part_ids.filtered(
                    lambda m: m.use_qty > m.qty_available and not m.purchase_id and not rec.spare_part_pr_ids):
                purchase_request = self.env['purchase.request'].create(
                    {'vehicle_service_id': rec.id})
                if rec.state != 'sp_request':
                    rec.state = 'sp_request'
                    rec.message_post(
                        body=_('The PR raise for the required spare-part and its PR reference is %s') % (
                            purchase_request.name))
                for spare_part in rec.spare_part_ids.filtered(
                        lambda m: m.use_qty > m.qty_available and not m.purchase_id):
                    purchase_request.update({'sp_pr_ids': [(0, 0, {'spare_part_id': spare_part.id,
                                                                   'product_tmpl_id': spare_part.product_tmpl_id.id,
                                                                   'pr_qty': spare_part.require_po_qty,
                                                                   'pr_cost': spare_part.product_tmpl_id.standard_price,
                                                                   })]})
                return {'name': _('Spare-part PR'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'purchase.request',
                        'type': 'ir.actions.act_window',
                        'res_id': purchase_request.id,
                        }
            else:
                return {'name': _('Spare-part PR'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'purchase.request',
                        'type': 'ir.actions.act_window',
                        'res_id': self.env['purchase.request'].search([('vehicle_service_id', '=', rec.id)],
                                                                      limit=1).id,
                        }

    @api.multi
    @api.constrains('spare_part_ids')
    def _check_exist_product_in_line(self):
        for parts in self:
            exist_product_list = []
            for line in parts.spare_part_ids:
                if line.product_tmpl_id.id in exist_product_list:
                    raise UserError(_('Duplicate Product should not allow.'))
                exist_product_list.append(line.product_tmpl_id.id)

    @api.onchange('cost_subtype_id')
    @api.multi
    def onchange_cost_subtype_id(self):
        for rec in self:
            if rec.cost_subtype_id.category == 'third_party':
                rec.third_party_service = True
            else:
                rec.third_party_service = False

    @api.onchange('repair_maintenance_type_id')
    def onchange_repair_maintenance_type_id(self):
        # Onchange field reset breakdown field.
        for rec in self:
            rec.breakdown_type_id = False

    @api.multi
    def _compute_purchase_order_count(self):
        # count the total link purchase order's.
        for fleet_vehicle_cost in self:
            fleet_vehicle_cost.purchase_order_count = len(
                self.purchase_order_ids)

    def action_purchase_order(self):
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
    def service_gate_pass(self):
        form_view = self.env.ref('beep_fleet.smnl_gate_pass_form').id
        tree_view = self.env.ref('beep_fleet.smnl_gate_pass_tree').id
        search_view = self.env.ref('beep_fleet.smnl_gate_pass_search').id
        
        return_val = {
            'name': "Gate Pass",
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(tree_view, 'tree'), (form_view, 'form')],
            'search_view_id': search_view,
            'res_model': 'gate.pass',
            'type': 'ir.actions.act_window',
            'domain': [('service_id', '=', self.id)],
            'target': 'current',
            'context': "{'create': False}"
        }
        return return_val

    @api.multi
    def po_generated(self):
        ''' Make Purchase Order and confirm.
        Order Line : take the any reference service product
        Vendor & Product Price shold be add as per the Included Services.
        '''
        if self.cost_subtype_id.category == 'third_party':
            purchase_order_list = []
            for include_service in self.cost_ids.filtered(lambda x: x.vendor_id):
                purchase_order = self.env['purchase.order'].create({
                    'partner_id': include_service.vendor_id.id or False,
                    'order_line': [(0, 0, {
                        'is_fleet': False,
                        'product_id': self.cost_subtype_id.product_template_id.product_variant_id.id,
                        'name': include_service.cost_subtype_id.name or " ",
                        'product_qty': 1,
                        'price_unit': include_service.amount,
                        'date_planned': fields.Date.today(),
                        'product_uom': 1
                    })]
                })
                purchase_order_list.append(purchase_order.id)
                # Removed in implementation of gate pass
                # purchase_order.button_confirm()
            self.purchase_order_ids = [(6, 0, purchase_order_list)]

    @api.multi
    def action_request(self):
        if not self.vehicle_id:
            raise UserError(_('Kindly select vehicle'))
        self.write({'state': 'request'})

    @api.multi
    def action_approve(self):
        if not self.vehicle_id:
            raise UserError(_('Kindly select vehicle'))
        if self.spare_part_ids:
            self.po_generated()
            self.write({'state': 'approve'})
        else:
            self.po_generated()
            self.write({'state': 'in_progress'})

    @api.multi
    def action_reject(self):
        if not self.vehicle_id:
            raise UserError(_('Kindly select vehicle'))
        self.write({'state': 'reject'})

    @api.multi
    def action_in_progress(self):
        if not self.vehicle_id:
            raise UserError(_('Kindly select vehicle'))
        in_progress_state = True
        for rec in self:
            if rec.spare_part_ids:
                if rec.spare_part_ids.filtered(lambda m: m.use_qty > m.qty_available and not m.purchase_id):
                    raise UserError(
                        _('Kindly check the require quantity higher then available quantity or raise PR.'))
                if rec.spare_part_ids.filtered(lambda m: m.purchase_id and m.require_po_qty != m.received_qty):
                    in_progress_state = False
                    if rec.state != 'sp_request':
                        self.write({'state': 'sp_request'})
                else:
                    if not rec.picking_id:
                        rec.picking_id = self.env['stock.picking'].sudo().create(
                            {'picking_type_id': self.env['stock.picking.type'].search([
                                ('code', '=', 'outgoing'),
                                ('warehouse_id.company_id', '=', self.env.user.company_id.id)], limit=1).id,
                             'location_id': self.env['stock.location'].search([
                                 ('name', '=', 'Stock'), ('usage', '=', 'internal'),
                                 ('company_id', '=', self.env.user.company_id.id)], limit=1).id,
                             'location_dest_id': self.env.ref('stock.location_inventory').id, })

                        for part in rec.spare_part_ids:
                            rec.picking_id.sudo().write({'move_ids_without_package': [(
                                0, 0, {'product_id': part.product_tmpl_id.product_variant_id.id,
                                       'name': part.product_tmpl_id.name,
                                       'product_uom_qty': part.use_qty,
                                       'product_uom': self.env.ref('uom.product_uom_unit').id,
                                       'location_id': self.env['stock.location'].search([
                                           ('name', '=', 'Stock'), ('usage', '=', 'internal'),
                                           ('company_id', '=', self.env.user.company_id.id)], limit=1).id,
                                       'location_dest_id': self.env.ref('stock.location_inventory').id,
                                       })]})
                        rec.picking_id.sudo().action_confirm()
                        rec.picking_id.sudo().action_assign()
                        rec.picking_id.sudo().button_validate()

                        for move in rec.picking_id.sudo().move_lines.filtered(
                                lambda m: m.state not in ['done', 'cancel']):
                            for move_line in move.move_line_ids:
                                move_line.qty_done = move_line.product_uom_qty

                                # vehicle spare parts serial number
                                for line in rec.spare_part_ids:
                                    if line.product_tmpl_id == move_line.lot_id.product_id.product_tmpl_id:
                                        vehicle_spare = self.env['vehicle.spare.parts'].create(
                                            {'product_id': line.product_tmpl_id.id,
                                             'service_id': line.vehicle_log_service_id.id,
                                             'vehicle_id': rec.vehicle_id.id,
                                             'name': move_line.lot_id.name, })

                                        if line.product_tmpl_id == move_line.lot_id.product_id.product_tmpl_id:
                                            s_no_list = []

                                            for s_no in self.env['stock.production.lot'].search(
                                                    [('name', '=', vehicle_spare.name)]):
                                                s_no_list.append(s_no)
                                                line.write(
                                                    {'serial_ids': [(4, s_no.id)]})

                                # vehicle spare parts serial number
                        rec.picking_id.sudo().action_done()
                        rec.picking_id.sudo().write({'fleet_service_id': rec.id})

        if in_progress_state:
            self.write({'state': 'in_progress'})

    @api.multi
    def action_done(self):
        form_view = self.env.ref('beep_fleet.form_vehicle_delay_remark_wizard')
        return {
            'name': "Are you sure want to Submit",
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': form_view.id,
            'res_model': 'vehicle.delay.remark',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_service_log_id': self.id, 'is_reject': True
            }
        }

    @api.multi
    @api.constrains('date', 'next_service_date')
    def get_date_comp(self):
        if self.date and self.next_service_date and self.date >= self.next_service_date:
            raise UserError(
                "next service date should be greater than current date")


class FleetVehicleCost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    vendor_id = fields.Many2one(
        'res.partner', 'Vendor', domain="[('supplier','=',True)]")
