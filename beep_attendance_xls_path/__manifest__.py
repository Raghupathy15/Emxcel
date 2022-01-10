# -*- encoding: utf-8 -*-
{
    'name': 'Beep Attendance Excel Import Path',
    'description': """
        Beep Attendance Excel Import Path

        Requirement:
        sudo -H  pip3 install xlrd
""",
    'version': '12.0.1.0.0',
    'author': "Emxcel Solutions",
    'license': '',
    'summary': """Beep Attendance Excel Import """,
    'category': 'attendance',
    'website': 'www.emxcelsolutions.com',
    'depends': ['beep_hr', 'hr_attendance'],
    'data': [
        'wizard/beep_attendance_import_views.xml'
    ],
    'active': False,
    'installable': True,
    'application': True,
}
