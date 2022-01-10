# -*- coding: utf-8 -*-

{
    'name': "SMNL Fleet Management",
    'summary': """
        SMNL Fleet Management""",
    'description': """
        SMNL Fleet Management
    """,
    'author': "Emxcel Solutions",
    'website': "",
    'category': 'Fleet Management',
    "license": "AGPL-3",
    'version': '12.0.1.1.0',
    'images': [],
    'depends': ['base', 'fleet', 'purchase', 'product', 'stock', 'account', 'hr', 'smnl_date_format'],
    'data': ['security/smnl_fleet_security.xml',
             'security/ir.model.access.csv',
             'data/fleet_type_data.xml',
             'data/smnl_fleet_cron.xml',
             'views/smnl_product.xml',
             'views/smnl_purchase.xml',
             'views/smnl_fleet_model.xml',
             'views/smnl_fleet.xml',
             'views/smnl_fleet_state.xml',
             'views/smnl_menu.xml',
             'views/smnl_stock_move.xml',
             'views/smnl_stock_inventory_line_views.xml',
             'views/smnl_invoice.xml',
             'wizard/smnl_fleet_cost_wiz.xml',
             'wizard/smnl_fleet_fuel_wiz.xml',
             'views/smnl_fleet_report_menu.xml',
             'report/fleet_cost_report_template.xml',
             'report/fleet_fuel_report_template.xml',
             'report/fleet_report_action.xml',
             'views/smnl_driver_registration.xml',
             'views/smnl_hr_employee.xml',
             'views/stock_quant_views.xml',
             ],
    'installable': True,
}
