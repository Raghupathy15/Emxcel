# -*- coding: utf-8 -*-

from odoo import api, models,fields

class Module(models.Model):
	_inherit = "ir.module.module"
	_description = "Module"

	company_website = fields.Char("Website", readonly=True,default="https://emxcelsolutions.com")
