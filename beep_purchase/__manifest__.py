# -*- coding: utf-8 -*-

{
    'name': 'Beep Purchase Order',
    'version': '12.0',
    'summary': 'Beep Purchase Order',
    'description': """Purchase Order customization""",
    'category': 'Purchase',
    'author': 'Emxcel Solutions',
    'website': 'https://emxcelsolutions.com/',
    'depends': ['purchase','hr','product','purchase_requisition'],
    'data': [
        'security/hr_security.xml',
        'data/email_templates.xml',
        'views/purchase_order_view.xml',
        'views/inherit_purchase_report.xml',
        'views/account_view.xml',
        'wizard/cancel_remarks_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}