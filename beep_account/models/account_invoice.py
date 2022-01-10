# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.constrains('date_invoice', 'date_due')
    def validations(self):
        if self.date_due and self.date_invoice:
            if self.date_invoice > self.date_due:
                raise UserError(_("'Due date' should be greater than 'Bill date'."))

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        date_invoice = self.date_invoice
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if self.payment_term_id:
            pterm = self.payment_term_id
            pterm_list = \
                pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[
                    0]
            self.date_due = max(line[0] for line in pterm_list)
