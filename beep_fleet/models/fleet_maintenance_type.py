# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class RepairMaintenanceType(models.Model):
    _name = "repair.maintenance.type"
    _description = "Repair Maintenance Type"

    name = fields.Char('Name')
    is_breakdown = fields.Boolean('Is Breakdown')


class BreakdownType(models.Model):
    _name = "breakdown.type"
    _description = "Breakdown Type"

    name = fields.Char('Name')
