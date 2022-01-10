{
    'name': 'Payslip Excel Report',
    'version': '12.0.1.1.0',
    "category": "Payroll",
    'author': 'Emxcel Solutions',
    'website': "https://emxcelsolutions.com/",
    'summary': """Advanced XLS Reports for payroll""",
    'depends': ['report_xlsx','hr_payroll'],
    'license': 'AGPL-3',
    'data': [
            'wizard/payslip_report_wizard_view.xml',
            'views/payslip_report.xml'
             ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}