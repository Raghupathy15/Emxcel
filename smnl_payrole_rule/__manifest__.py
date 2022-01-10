# -*- coding: utf-8 -*-

{
    'name': "SMNL Payroll Rules",
    'summary': 'SMNL Payroll Rules',
    'description': 'SMNL Payroll Rules',
    'author': "Emxcel Solutions",
    'website': "",
    'category': 'HR Management',
    "license": "AGPL-3",
    'version': '12.0.1.1.0',
    'images': [],
    'depends': ['hr', 'beep_hr', 'hr_payroll'],
    'data': ['security/ir.model.access.csv',
             'security/hr_payroll_security.xml',
             'data/payroll_rule.xml',
             'views/smnl_hr_payslip.xml',
             'data/cron.xml'],
    'installable': True,
}
