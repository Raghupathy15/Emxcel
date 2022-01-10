# -*- coding: utf-8 -*-

{
    'name': "SMNL Fleet Fuel Logs",
    'summary': """
		SMNL Fleet Fuel Logs""",
    'description': """
		SMNL Fleet Fuel Logs
	""",
    'author': "Emxcel Solutions",
    'website': "",
    'category': 'Fleet Management',
    "license": "AGPL-3",
    'version': '12.0.1.1.0',
    'images': [],
    'depends': ['fleet', 'stock', 'smnl_fleet_extend', 'hr'],
    'data': ['security/ir.model.access.csv',
             'security/groups.xml',
             'data/email_templates.xml',
             'data/sequence.xml',
             'data/custom_data.xml',
             'data/stock_data.xml',
             'views/cron.xml',
             'views/tanker.xml',
             'views/fuel_filling.xml',
             'views/stock_location.xml',
             ],
    'installable': True,
}
