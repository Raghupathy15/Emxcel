# -*- coding: utf-8 -*-
import xlrd
import psycopg2
import datetime

#Global Variables
HOST="localhost"
USER="emxcel"
PSWD="emxcel"
DB="feb_16"
PORT="5432"

def hr_master():
    hr_resource()
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("hr_master.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Employee")
    # Resource
    resource_query = """SELECT id,name from resource_resource"""
    cursor.execute(resource_query)
    resource_fetch = cursor.fetchall()
    # Employee
    query = """SELECT id,name from hr_employee"""
    insert_employee = """INSERT INTO hr_employee (name, resource_id, job_id, department_id, hr_section_id, active) VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    # Designation
    designation_cursor = database.cursor()
    designation_query = """SELECT id,smnl_id from hr_job"""
    designation_cursor.execute(designation_query)
    designation = designation_cursor.fetchall()
    desig_id = []
    desig_exist = []
    for hr_designation in designation:
        desig_id.append(hr_designation[0])
        desig_exist.append(hr_designation[1])
    # Department
    department_cursor = database.cursor()
    department_query = """SELECT id,smnl_id from hr_department"""
    department_cursor.execute(department_query)
    department = department_cursor.fetchall()
    dept_id = []
    dept_exist = []
    # Partner
    # partner_cursor = database.cursor()
    # partner_query = """SELECT id,name from res_partner"""
    # partner_cursor.execute(partner_query)
    # partner_fetch = partner_cursor.fetchall()
    # Section
    section_cursor = database.cursor()
    section_query = """SELECT id,smnl_id from hr_section"""
    section_cursor.execute(section_query)
    section = section_cursor.fetchall()
    sec_id = []
    sec_exist = []
    for hr_section in section:
        sec_id.append(hr_section[0])
        sec_exist.append(hr_section[1])

    for hr_department in department:
        dept_id.append(hr_department[0])
        dept_exist.append(hr_department[1])
    for r in range (1, emp_sheet.nrows):
        name = emp_sheet.cell(r,1).value
        active = True
        exist = []
        res_id = []
        resource_exist = []
        vals_res = []
        for resource in resource_fetch:
            res_id.append(resource[0])
            resource_exist.append(resource[1])
            if resource[1] == name and name not in exist:
                vals_res.append(resource[0])
        # partner
        # vals_partner = []
        # for partner in partner_fetch:
        #     if partner[1] == name:
        #         vals_partner.append(partner[0])
        # if vals_res and vals_partner:
        #         resource_id = vals_res[0]
        #         address_home_id = vals_partner[0]
        if emp_sheet.cell(r,2).value:
            get_designation_id = int(emp_sheet.cell(r,2).value)
            line = desig_exist.index(get_designation_id)
            job_id = desig_id[line]
            # department
            get_department_id = int(emp_sheet.cell(r,3).value)
            department_line = dept_exist.index(get_department_id)
            department_id = dept_id[department_line]
            # section
            get_section_id = int(emp_sheet.cell(r,4).value)
            section_line = sec_exist.index(get_section_id)
            hr_section_id = sec_id[section_line]
        emp_id = []
        exit = []
        for emp_data in myresult:
            emp_id.append(emp_data[0])
            exit.append(emp_data[1])
        if name not in exit:
            if vals_res:
                resource_id = vals_res[0]
                values = (name, resource_id, job_id, department_id, hr_section_id, active)
                cursor.execute(insert_employee, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print ('HR Employee Imported')

def hr_resource():
    hr_designation()
    hr_department()
    hr_section()
    # create_partner()
    # create_user()
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("hr_master.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Employee")
    query = """SELECT id,name from resource_resource"""
    insert_query = """INSERT INTO resource_resource (name, resource_type, calendar_id, active, tz, time_efficiency) VALUES (%s, %s, %s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    emp_id = []
    exist = []
    for hr_res in myresult:
        emp_id.append(hr_res[0])
        exist.append(hr_res[1])
    for r in range (1, emp_sheet.nrows):
        name = emp_sheet.cell(r,1).value
        resource_type = 'user'
        calendar_id = 1
        active = True
        tz = 'Asia/Calcutta'
        time_efficiency = 100
        if name not in exist:
            values = (name, resource_type, calendar_id, active, tz, time_efficiency)
            cursor.execute(insert_query, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('HR Resource Imported')

def hr_department():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("hr_master.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("department")
    query = """SELECT id,name from hr_department"""
    insert_department = """INSERT INTO hr_department (name, department_code, complete_name, smnl_id, active) VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    emp_id = []
    exist = []
    for hr_dept in myresult:
        emp_id.append(hr_dept[0])
        exist.append(hr_dept[1])
    for r in range (1, emp_sheet.nrows):
        rec = emp_sheet.cell(r,1).value
        code = emp_sheet.cell(r,2).value
        if rec not in exist:
            complete_name = str(emp_sheet.cell(r,1).value)
            active = True
            smnl_id = int(emp_sheet.cell(r,0).value)
            values = (rec, code, complete_name, smnl_id, active)
            cursor.execute(insert_department, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('HR Department Imported')

def hr_designation():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("hr_master.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("designation")
    mail_alias_query = """SELECT id from mail_alias where alias_name='jobs' """
    cursor.execute(mail_alias_query)
    mail_alias_fetch = cursor.fetchall()
    alias = str(mail_alias_fetch).replace('[', '')
    alias1 = str(alias).replace(']', '')
    alias2 = str(alias1).replace("'", '')
    alias3 = str(alias2).replace("(", '')
    alias4 = str(alias3).replace(")", '')
    alias_id = str(alias4).replace(",", '')
    query = """SELECT id,name from hr_job"""
    insert_department = """INSERT INTO hr_job (name, state, smnl_id, alias_id) VALUES (%s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    dept_cursor = database.cursor()
    emp_id = []
    exist = []
    for hr_dept in myresult:
        emp_id.append(hr_dept[0])
        exist.append(hr_dept[1])
    for r in range (1, emp_sheet.nrows):
        rec = emp_sheet.cell(r,1).value
        if rec not in exist:
            state = 'recruit'
            alias_id = alias_id
            smnl_id = int(emp_sheet.cell(r,0).value)
            values = (rec, state, smnl_id, alias_id)
            cursor.execute(insert_department, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('HR designation Imported')

def create_partner():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("hr_master.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Employee")
    query = """SELECT id,name from res_partner"""
    insert_partner = """INSERT INTO res_partner (name, active, display_name) VALUES (%s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    emp_id = []
    exist = []
    for hr_res in myresult:
        emp_id.append(hr_res[0])
        exist.append(hr_res[1])
    for r in range (1, emp_sheet.nrows):
        name = str(emp_sheet.cell(r,1).value)
        display_name = str(emp_sheet.cell(r,1).value)
        # company_id =  1
        active = True
        if name not in exist:
            values = (name, active, display_name)
            cursor.execute(insert_partner, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('Partner Imported')

def hr_section():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("hr_master.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("section")
    query = """SELECT id,name from hr_section"""
    insert_section = """INSERT INTO hr_section (name, code, smnl_id) VALUES (%s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    emp_id = []
    exist = []
    for hr_dept in myresult:
        emp_id.append(hr_dept[0])
        exist.append(hr_dept[1])
    for r in range (1, emp_sheet.nrows):
        name = emp_sheet.cell(r,1).value
        code = emp_sheet.cell(r,2).value
        if name not in exist:
            smnl_id = int(emp_sheet.cell(r,0).value)
            values = (name, code, smnl_id)
            cursor.execute(insert_section, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('HR Section Imported')

def update_location():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("hr_master.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Employee")
    query = """SELECT name from hr_employee"""
    update_location = """UPDATE hr_employee set location = %s where name = %s"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    for r in range (1, emp_sheet.nrows):
        name = emp_sheet.cell(r,1).value
        location = emp_sheet.cell(r,5).value
        for employee in myresult:
            if name in employee:
                values = (location, name)
                cursor.execute(update_location, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('Employee Location Updated')

hr_master()
update_location()