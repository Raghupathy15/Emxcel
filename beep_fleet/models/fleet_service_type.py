from odoo import api, fields, models, _


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    category = fields.Selection(
        selection_add=[('third_party', 'Third Party'), ('service', 'In House Service')])
    product_template_id = fields.Many2one('product.template', string="Product")

    @api.model
    def create(self, vals):
        res = super(FleetServiceType, self).create(vals)
        if res.category == 'third_party' and res.name:
            product = self.env['product.template'].create({'name': res.name,
                                                           'type': 'service',
                                                           })
            res.product_template_id = product.id
            product.write({'fleet_service_type_id': res.id})
        return res

    @api.multi
    def write(self, vals):
        res = super(FleetServiceType, self).write(vals)
        for rec in self:
            if rec.category == 'third_party' and rec.name and not self.env['product.template'].search(
                    [('name', '=', rec.name)]):
                product = self.env['product.template'].create({'name': rec.name,
                                                               'type': 'service',
                                                               })
                rec.product_template_id = product.id
                product.write({'fleet_service_type_id': rec.id})
        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fleet_service_type_id = fields.Many2one(
        'fleet.service.type', string="Fleet Service")
