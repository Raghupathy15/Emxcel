# -*- coding: utf-8 -*-

from odoo import api, models
from datetime import datetime


class FleetFuelReport(models.AbstractModel):
    _name = 'report.smnl_fleet_extend.report_fleet_fuel'
    _description = 'Fleet Fuel Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date = False
        to_date = False
        if data.get('from_date') and data.get('to_date'):
            fm_dt = datetime.strptime(data.get('from_date'), '%Y-%m-%d').date()
            from_date = '{0}-{1}-{2}'.format(fm_dt.day, fm_dt.month, fm_dt.year)
            to_dt = datetime.strptime(data.get('to_date'), '%Y-%m-%d').date()
            to_date = '{0}-{1}-{2}'.format(to_dt.day, to_dt.month, to_dt.year)
            docs = self.env['fleet.vehicle.log.fuel'].browse(data.get('ids'))
        else:
            docs = self.env['fleet.vehicle.log.fuel'].browse(docids)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'fleet.vehicle.log.fuel',
            'data': data,
            'docs': docs,
            'from_date': from_date,
            'to_date': to_date,
        }
