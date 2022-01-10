# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import datetime


class GatePassReport(models.AbstractModel):
    _name = 'report.beep_fleet.report_gate_pass'
    _description = 'Gate Pass Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        ids = data.get('ids') or docids
        docs = self.env['gate.pass'].browse(ids)
        return {
            'doc_ids': docids,
            'doc_model': 'gate.pass',
            'data': data,
            'docs': docs,
        }
