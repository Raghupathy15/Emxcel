# -*- coding: utf-8 -*-
{
    'name': "Product Part Number",

    'summary': """
        Product Part Number""",

    'description': """
        Product Part Number
    """,

    'author': 'Emxcel Solutions',
    'website': 'https://emxcelsolutions.com/',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'beep_fleet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    
}