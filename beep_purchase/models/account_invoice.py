# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
	_inherit = "account.invoice"
	_description = "Invoice"


	def compute_receipt_count(self):
		for record in self:
			record.receipt_count = self.env['purchase.order'].search_count([('name', '=', record.origin)])


	origin = fields.Char(string='Source Document', help="Reference of the document that produced this invoice.", 
						readonly=True)
	receipt_count = fields.Integer('Receipt',compute='compute_receipt_count')

	def get_receipts(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': 'Receipts',
			'view_mode': 'tree,form',
			'res_model': 'stock.picking',
			'domain': [('origin', '=', self.origin)],
			'context': "{'create': False}"
		}
	