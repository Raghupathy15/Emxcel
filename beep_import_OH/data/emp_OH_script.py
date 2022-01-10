# -*- coding: utf-8 -*-
import xlrd
import psycopg2
import datetime
import odoorpc

#Global Variables
HOST="localhost"
USER="emxcel"
PSWD="emxcel"
DB="smnl_oh"
PORT="5432"
odoo = odoorpc.ODOO("localhost", port=8069)

def OptionalHoliday():
    ResourceCalendar()
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("import_attendance_2nd_april.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet3")
    insert_optional_holiday = """INSERT INTO optional_holiday (opt_holiday_id, date_from, date_to,holiday_id) VALUES (%s, %s, %s, %s)"""
    for r in range (1, emp_sheet.nrows):
        if emp_sheet.cell(r,4).value == 'OH':
            # To compare employee code with sheet
            query = """SELECT id from hr_employee where RIGHT (emp_code, 4) = '%s' """ % (emp_sheet.cell(r,0).value)
            cursor.execute(query)
            myresult = cursor.fetchall()
            myresult1 = str(myresult).replace('[', '')
            myresult2 = str(myresult1).replace(']', '')
            myresult3 = str(myresult2).replace('(', '')
            myresult4 = str(myresult3).replace(')', '')
            myresult5 = str(myresult4).replace(',', '')
            # To check the OH in resource_calendar_leaves
            resource_query = """SELECT id from resource_calendar_leaves where name = 'MAHA SHIVRATRI' """
            cursor.execute(resource_query)
            res_result = cursor.fetchall()
            res_result1 = str(res_result).replace('[', '')
            res_result2 = str(res_result1).replace(']', '')
            res_result3 = str(res_result2).replace('(', '')
            res_result4 = str(res_result3).replace(')', '')
            res_result5 = str(res_result4).replace(',', '')
            if res_result5:
                opt_holiday_id = res_result5
                date_from = xlrd.xldate.xldate_as_datetime(emp_sheet.cell_value(r, 1), 0)
                date_to = xlrd.xldate.xldate_as_datetime(emp_sheet.cell_value(r, 1), 0)
                holiday_id = myresult5
                values = (opt_holiday_id, date_from, date_to,str(holiday_id))
                cursor.execute(insert_optional_holiday, values)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)
    print('Optional Holidays Imported')

def ResourceCalendar():
    database = psycopg2.connect(host=HOST, user=USER, password=PSWD, database=DB, port=PORT)
    book = xlrd.open_workbook("import_attendance_2nd_april.xlsx")
    cursor = database.cursor()
    emp_sheet = book.sheet_by_name("Sheet3")
    # To check the OH in resource_calendar_leaves
    resource_query = """SELECT id from resource_calendar_leaves where name = 'MAHA SHIVRATRI' """
    cursor.execute(resource_query)
    res_result = cursor.fetchall()
    if not res_result:
        insert_res_cal = """INSERT INTO resource_calendar_leaves (name, date_from, date_to) VALUES ('MAHA SHIVRATRI', '11/03/2021 00:00:00', '11/03/2021 18:29:59')"""
        cursor.execute(insert_res_cal)
    cursor.close()
    database.commit()
    database.close()
    columns = str(emp_sheet.ncols)
    rows = str(emp_sheet.nrows)

OptionalHoliday()