# -*- coding: utf-8 -*-

{
    'name': "SMNL Leave Encashment",
    'summary': """
		SMNL Leave Encashment""",
    'description': """
		SMNL Leave Encashment
	""",
    'author': "Emxcel Solutions",
    'website': "",
    'category': 'Leave',
    "license": "AGPL-3",
    'version': '12.0.1.1.0',
    'images': [],
    'depends': ['hr_holidays'],
    'data': ['security/ir.model.access.csv',
             'security/hr_security.xml',
             'data/ir_sequence_data.xml',
             'views/leave_encashment.xml'],
    'installable': True,
}
