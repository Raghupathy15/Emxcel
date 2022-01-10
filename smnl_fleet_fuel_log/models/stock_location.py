# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_fuel = fields.Boolean(string='Is a Fuel Location?')


# class Warehouse(models.Model):
#     _inherit = "stock.warehouse"
#
#     @api.model
#     def create(self, vals):
#         # Create Internal Fuel
#         code = _(vals.get('code'))
#         warehouse = super(Warehouse, self).create(vals)
#         fuel_vals = self.env['stock.location'].create([{
#             'name': 'Internal Fuel Location',
#             'usage': 'internal',
#             'is_fuel': True,
#             'location_id': self.env['stock.location'].search([('name', '=', code)]).id,
#             'company_id': self.env.user.company_id.id}])
#         return warehouse
#
# class ResCompany(models.Model):
#     _inherit = "res.company"
#
#     @api.model
#     def create(self, vals):
#         # Create company Internal Fuel
#         company = super(ResCompany, self).create(vals)
#         company_location = self.env['stock.location'].sudo().create({
#             'name': 'Internal Fuel Location',
#             'usage': 'internal',
#             'is_fuel': True,
#             'location_id': self.env['stock.location'].search([('name', '=', company.name[:5])]).id,
#             'company_id': company.id})
#         return company
