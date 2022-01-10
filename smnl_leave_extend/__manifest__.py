# -*- coding: utf-8 -*-

{
    'name': "SMNL Leave Extended",
    'summary': """
		SMNL Leave Type""",
    'description': """
		SMNL Leave Extended
        Manage compensatory Holiday leave and allocation.
	""",
    'author': "Emxcel Solutions",
    'website': "",
    'category': 'Leave',
    "license": "AGPL-3",
    'version': '12.0.1.1.0',
    'images': [],
    'depends': ['hr_holidays', 'beep_hr'],
    'data': ['security/hr_leave_security.xml',
             'data/leave_data.xml',
             'data/ir_cron.xml',
             'views/leave_type.xml',
             'views/hr_leave_views.xml',
             'views/hr_leave_allocation_views.xml'],
    'installable': True,
}
