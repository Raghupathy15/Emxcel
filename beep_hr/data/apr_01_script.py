# -*- coding: utf-8 -*-
import xlrd
import psycopg2
import datetime

#Global Variables
HOST="localhost"
USER="emxcel"
PSWD="emxcel"
DB="UAT"
PORT="5432"

def hr_master():
    hr_resource()
    database = psycopg2.connect (host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    cursor_fetch = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet1")
    resource_query = """SELECT id,name from resource_resource"""
    cursor_fetch.execute(resource_query)
    resource_fetch = cursor_fetch.fetchall()
    query = """SELECT id,name,old_emp_code from hr_employee"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    # To check bank start
    query = """SELECT id from res_partner_bank where acc_number = '-'"""
    cursor.execute(query)
    select = cursor.fetchall()
    values3=''
    for line in select:
        values1 = str(line).replace('(', '')
        values2 = str(values1).replace(')', '')
        values3 = str(values2).replace(',', '')
    # To check bank end
    emp_id = []
    exist = []
    exist_emp = []
    for hr_emp in myresult:
        emp_id.append(hr_emp[0])
        exist.append(hr_emp[1])
        exist_emp.append(hr_emp[2])
    designation_cursor = database.cursor()
    designation_query = """SELECT id,smnl_id from hr_job"""
    designation_cursor.execute(designation_query)
    designation = designation_cursor.fetchall()
    desig_id = []
    desig_exist = []
    for hr_designation in designation:
        desig_id.append(hr_designation[0])
        desig_exist.append(hr_designation[1])
    department_cursor = database.cursor()
    department_query = """SELECT id,smnl_id from hr_department"""
    department_cursor.execute(department_query)
    department = department_cursor.fetchall()
    dept_id = []
    dept_exist = []
    for hr_department in department:
        dept_id.append(hr_department[0])
        dept_exist.append(hr_department[1])
    partner_cursor = database.cursor()
    partner_query = """SELECT id,name from res_partner"""
    partner_cursor.execute(partner_query)
    partner_fetch = partner_cursor.fetchall()
    bank_cursor = database.cursor()
    bank_query = """SELECT id,acc_number from res_partner_bank"""
    bank_cursor.execute(bank_query)
    bank_fetch = bank_cursor.fetchall()
    # State starts
    state_query = """SELECT id,name from res_country_state"""
    cursor_fetch.execute(state_query)
    state_fetch = cursor_fetch.fetchall()
    # state ends
    for r in range (1, emp_sheet.nrows):
        name = emp_sheet.cell(r,4).value
        emp_code = str(emp_sheet.cell(r,2).value)
        old_emp_code = str(emp_sheet.cell(r,2).value)
        location = emp_sheet.cell(r,1).value
        esic = emp_sheet.cell(r,3).value
        first_name =  str(emp_sheet.cell(r,5).value)
        middle_name =  str(emp_sheet.cell(r,6).value)
        last_name =  str(emp_sheet.cell(r,7).value)
        company_id =  int(emp_sheet.cell(r,8).value)
        gender =  str(emp_sheet.cell(r,12).value)
        marital =  str(emp_sheet.cell(r,13).value)
        conf_dc =  str(emp_sheet.cell(r,14).value)
        resig_dc =  str(emp_sheet.cell(r,15).value)
        passport_id =  str(emp_sheet.cell(r,16).value)
        place_of_birth =  str(emp_sheet.cell(r,18).value)
        pan =  str(emp_sheet.cell(r,19).value)
        identification_id =  str(emp_sheet.cell(r,20).value)
        if identification_id and len(identification_id) > 3 and identification_id[-2] == '.':
            identification_id = identification_id[:-2]
        voter_id =  str(emp_sheet.cell(r,21).value)
        uan =  str(emp_sheet.cell(r,22).value)
        if uan and len(uan) > 3 and uan[-2] == '.':
            uan = uan[:-2]
        pf_no =  str(emp_sheet.cell(r,23).value)
        esic_no =  str(emp_sheet.cell(r,24).value)
        if esic_no and len(esic_no)>3 and esic_no[-2] == '.':
            esic_no = esic_no[:-2]
        
        mobile_phone =  int(emp_sheet.cell(r,25).value)
        personal_mail =  str(emp_sheet.cell(r,26).value)
        work_email =  str(emp_sheet.cell(r,27).value)
        actual_doj = xlrd.xldate.xldate_as_datetime(emp_sheet.cell_value(r, 29), 0)
        birthday = xlrd.xldate.xldate_as_datetime(emp_sheet.cell_value(r, 30), 0)

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
        get_section_id = int(emp_sheet.cell(r,56).value)
        section_line = sec_exist.index(get_section_id)
        hr_section_id = sec_id[section_line]

        religion =  emp_sheet.cell(r,33).value
        employee_type =  emp_sheet.cell(r,38).value
        biometric =  emp_sheet.cell(r,39).value
        notice_period =  emp_sheet.cell(r,40).value
        work_phone =  emp_sheet.cell(r,41).value
        certificate =  str(emp_sheet.cell(r,42).value)
        spouse_complete_name =  str(emp_sheet.cell(r,43).value)
        children_1 =  str(emp_sheet.cell(r,44).value)
        children_2 =  str(emp_sheet.cell(r,45).value)
        father =  str(emp_sheet.cell(r,46).value)
        mother =  str(emp_sheet.cell(r,47).value)
        brother =  str(emp_sheet.cell(r,48).value)
        sister =  str(emp_sheet.cell(r,49).value)
        previous_company =  str(emp_sheet.cell(r,50).value)
        payment_type =  str(emp_sheet.cell(r,51).value)
        notes =  str(emp_sheet.cell(r,52).value)
        account =  str(emp_sheet.cell(r,35).value)
        age =  str(emp_sheet.cell(r,53).value)
        if age and age[-2] == '.':
            age = age[:-2]
        wage =  str(emp_sheet.cell(r,54).value)
        active = True
        if emp_sheet.cell(r,9).value:
            get_designation_id = int(emp_sheet.cell(r,9).value)
            line = desig_exist.index(get_designation_id)
            job_id = desig_id[line]
            get_department_id = int(emp_sheet.cell(r,10).value)
            department_line = dept_exist.index(get_department_id)
            department_id = dept_id[department_line]
            res_id = []
            resource_exist = []
            vals_res = []
            vals_partner = []
            for resource in resource_fetch:
                res_id.append(resource[0])
                resource_exist.append(resource[1])
                if resource[1] == name and name not in exist:
                    vals_res.append(resource[0])
            for partner in partner_fetch:
                if partner[1] == name:
                    vals_partner.append(partner[0])
            bank_list = []
            for bank in bank_fetch:
                account =  str(emp_sheet.cell(r,35).value)              
                if bank[1] == account[:-2]:
                    bank_list.append(bank[0])
            for line in bank_list:
                var_bank = line
            if account == '-':
                bank_account_id = values3
            else:
                bank_account_id = var_bank
            if vals_res and vals_partner:
                resource_id = vals_res[0]
                address_home_id = vals_partner[0]
                insert_query = """INSERT INTO hr_employee (name, emp_code,old_emp_code, location, esic, first_name, middle_name, last_name, company_id, gender, marital, conf_dc, resig_dc, passport_id, place_of_birth, pan, identification_id, voter_id, uan, pf_no, esic_no, mobile_phone, work_email, religion, employee_type, biometric, notice_period, work_phone, certificate, spouse_complete_name, children_1, children_2, father, mother, brother, sister, previous_company, payment_type, notes, personal_mail, resource_id, active, job_id, department_id, address_home_id, bank_account_id, wage, actual_doj, birthday, hr_section_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (name, emp_code, old_emp_code, location, esic, first_name, middle_name, last_name, company_id, gender, marital, conf_dc, resig_dc, passport_id, place_of_birth, pan, identification_id, voter_id, uan, pf_no, esic_no, mobile_phone, work_email, religion, employee_type, biometric, notice_period, work_phone, certificate, spouse_complete_name, children_1,children_2, father, mother,brother,sister, previous_company, payment_type, notes, personal_mail, resource_id, active, job_id, department_id, address_home_id, bank_account_id, wage, actual_doj, birthday, hr_section_id)
                cursor.execute(insert_query, values)
                print ('Employees Imported ===>',r)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)

def hr_resource():
    hr_designation()
    create_partner()
    create_user()
    hr_section()
    user_company()
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet1")
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
        name = emp_sheet.cell(r,4).value
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
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("department")
    query = """SELECT id,name from hr_department"""
    insert_department = """INSERT INTO hr_department (name, complete_name, active, smnl_id) VALUES (%s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    emp_id = []
    exist = []
    for hr_dept in myresult:
        emp_id.append(hr_dept[0])
        exist.append(hr_dept[1])
    for r in range (1, emp_sheet.nrows):
        rec = emp_sheet.cell(r,1).value
        if rec not in exist:
            complete_name = str(emp_sheet.cell(r,1).value)
            active = True
            smnl_id = int(emp_sheet.cell(r,0).value)
            values = (rec, complete_name, active, smnl_id)
            cursor.execute(insert_department, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('HR Department Imported')

def hr_designation():
    hr_department()
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
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
    insert_department = """INSERT INTO hr_job (name, state, department_id, smnl_id, alias_id) VALUES (%s, %s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    dept_cursor = database.cursor()
    
    query = """SELECT id,smnl_id from hr_department"""
    dept_cursor.execute(query)
    department = dept_cursor.fetchall()
    dept_id = []
    dept_exist = []
    for hr_dept in department:
        dept_id.append(hr_dept[0])
        dept_exist.append(hr_dept[1])

    emp_id = []
    exist = []
    for hr_dept in myresult:
        emp_id.append(hr_dept[0])
        exist.append(hr_dept[1])
    for r in range (1, emp_sheet.nrows):
        rec = emp_sheet.cell(r,1).value
        if rec not in exist:
            state = 'recruit'
            get_dept_id = int(emp_sheet.cell(r,2).value)
            line = dept_exist.index(get_dept_id)
            department_id = dept_id[line]
            alias_id = alias_id
            smnl_id = int(emp_sheet.cell(r,0).value)
            values = (rec, state, department_id, smnl_id, alias_id)
            cursor.execute(insert_department, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('HR designation Imported')

def create_user():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    cursor_fetch = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet1")
    rpartner_query = """SELECT id,name from res_partner"""
    cursor_fetch.execute(rpartner_query)
    partner_fetch = cursor_fetch.fetchall()
    query = """SELECT id,login from res_users"""
    insert_users = """INSERT INTO res_users ( login, password, notification_type, odoobot_state, company_id, active, partner_id, share,sale_team_id) VALUES ( %s ,%s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    emp_id = []
    exist = []
    for hr_res in myresult:
        emp_id.append(hr_res[0])
        exist.append(hr_res[1])
    for r in range (1, emp_sheet.nrows):
        login = str(emp_sheet.cell(r,2).value)
        password = 'SMNL@123'
        company_id =  int(emp_sheet.cell(r,8).value)
        notification_type = "email"
        odoobot_state = "disabled"
        active = True
        share = False
        sale_team_id = 1
        if login not in exist:
            part_id = []
            partner_exist = []
            partner_id = 1
            values = (login, password, notification_type, odoobot_state, company_id, active, partner_id, share,sale_team_id)
            cursor.execute(insert_users, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('User Imported !..')

def user_company():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    cursor_fetch = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet1")
    users = """SELECT id,company_id from res_users"""
    cursor.execute(users)
    myresult = cursor.fetchall()
    for user,company in myresult:
        # Need to call manually created ids
        # if not user in (1,2,3,4,5):
        if user > 1691:
            insert_user = """INSERT INTO res_company_users_rel (cid,user_id) VALUES ( %s ,%s)"""
            values = (1, user)
            cursor.execute(insert_user, values)
    cursor.close()
    database.commit()
    database.close()
    print('Company Imported !..')
    
def create_partner():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet1")
    query = """SELECT id,name from res_partner"""
    insert_partner = """INSERT INTO res_partner (name, active, company_id, display_name, phone, email, emp_code) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    emp_id = []
    exist = []
    for hr_res in myresult:
        emp_id.append(hr_res[0])
        exist.append(hr_res[1])
    for r in range (1, emp_sheet.nrows):
        name = str(emp_sheet.cell(r,4).value)
        emp_code = str(emp_sheet.cell(r,2).value)
        display_name = str(emp_sheet.cell(r,4).value)
        phone =  str(emp_sheet.cell(r,25).value)
        email =  str(emp_sheet.cell(r,27).value)
        company_id =  int(emp_sheet.cell(r,8).value)
        active = True
        if name not in exist:
            values = (name, active, company_id, display_name, phone, email, emp_code)
            cursor.execute(insert_partner, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('Partner Imported !..')
    create_partner_bank()

def create_partner_bank():
    create_bank()
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet1")
    query = """SELECT id,acc_number,partner_id from res_partner_bank"""
    insert_bank = """INSERT INTO res_partner_bank (acc_number, bank_id, partner_id) VALUES (%s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    bank_partner_id = []
    bank_partner_name = []
    bank_partner_exist = []
    for hr_bank in myresult:
        bank_partner_id.append(hr_bank[0])
        bank_partner_name.append(hr_bank[2])
        bank_partner_exist.append(hr_bank[1])
    bank_cursor = database.cursor()
    bank_query = """SELECT id,name,bic from res_bank"""
    bank_cursor.execute(bank_query)
    bank_fetch = bank_cursor.fetchall()
    partner_cursor = database.cursor()
    partner_query = """SELECT id,name from res_partner"""
    partner_cursor.execute(partner_query)
    partner_fetch = partner_cursor.fetchall()
    for r in range (1, emp_sheet.nrows):
        acc_number = str(emp_sheet.cell(r,35).value)
        bic = str(emp_sheet.cell(r,37).value)
        partner_name = str(emp_sheet.cell(r,4).value)
        partner_id = 5
        var_bank_id = []
        var_bank = ''
        bank_exist = []
        bank_bic = []
        var_partner_id = []
        partner_exist = []
        if acc_number != '-' and acc_number:
            for bank in bank_fetch:
                var_bank_id.append(bank[0])
                bank_exist.append(bank[1])
                bank_bic.append(bank[2])
                if bank[2] == bic and acc_number not in bank_partner_exist:
                    bank_id = bank[0]
                    for partner in partner_fetch:
                        var_partner_id.append(partner[0])
                        partner_exist.append(partner[1])
                        if partner[1] == partner_name and partner_name not in bank_partner_name:
                            partner_id = partner[0]
                            values = (acc_number[:-2], bank_id, partner_id)
                            cursor.execute(insert_bank, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('Partner bank Imported !..')

def create_bank():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet1")
    query = """SELECT id,name from res_bank"""
    insert_bank = """INSERT INTO res_bank (name, bic, bank_branch, active) VALUES (%s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    bank_id = []
    bank_exist = []
    for hr_bank in myresult:
        bank_id.append(hr_bank[0])
        bank_exist.append(hr_bank[1])
    bic_dup = []
    for r in range (1, emp_sheet.nrows):
        name = str(emp_sheet.cell(r,34).value)
        bic = str(emp_sheet.cell(r,37).value)
        bank_branch = str(emp_sheet.cell(r,36).value)
        active = True
        if name not in bank_exist and name != '-' and name and bic not in bic_dup:
            bic_dup.append(bic)
            values = (name, bic, bank_branch, active)
            cursor.execute(insert_bank, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('Bank Imported !..')
    print('HR Employee imported !..')

def hr_section():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Section")
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

def hr_contract():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("apr_01.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Contract Details")
    query = """SELECT id,name from hr_contract"""
    insert_contract = """INSERT INTO hr_contract (employee, name, type_id, struct_id, date_start, resource_calendar_id, wage, active, state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query)
    myresult = cursor.fetchall()
    for r in range (1, emp_sheet.nrows):
        employee = emp_sheet.cell(r,1).value
        name = emp_sheet.cell(r,2).value
        active = True
        state = 'open'
        wage = emp_sheet.cell(r,7).value
        type_id = 1
        struct_id = 3
        resource_calendar_id = 1
        date_start = xlrd.xldate.xldate_as_datetime(emp_sheet.cell_value(r, 5), 0)
        values = (employee, name, type_id, struct_id, date_start, resource_calendar_id, wage, active, state)
        cursor.execute(insert_contract, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('HR Contract Imported')

hr_master()
hr_contract()