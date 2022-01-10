# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = "stock.quant"

    lot_id = fields.Many2one(
        'stock.production.lot', 'Chassis Number',
        ondelete='restrict', readonly=True)
    is_expire = fields.Boolean(string="Is Expire")
    expiry_date = fields.Date(string='Expiry Date')
