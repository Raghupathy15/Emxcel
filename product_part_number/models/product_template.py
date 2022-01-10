# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    part_number = fields.Char("Part Number")
    purpose = fields.Char("Purpose")
    remark = fields.Char("Remark/Owner")

    @api.onchange('is_spare_part')
    def onchange_employee_id(self):
        # Onchange reset field value.
        self.part_number = False
        self.purpose = False
        self.remark = False

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        product_ids = []
        if name:
            product_ids = self._search([('name', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not product_ids:
            product_ids = self._search([('part_number', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not product_ids:
            product_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(product_ids).name_get()

    @api.multi
    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.browse(self.ids).read(['name', 'default_code', 'part_number'])
        return [(template.id, '%s%s%s' % (template.default_code and '[%s] ' % template.default_code or '',
                                          template.name,
                                          template.part_number and '[%s] ' % template.part_number or ''))
                for template in self]
