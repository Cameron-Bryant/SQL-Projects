from mysql.connector import connect, Error 
from getpass import getpass
import datetime
import xlrd
###need to have installed MySQL and the Python connector. 
###goal: get temperature data and store it in a mysql database
#first MySQL Script


def getExcelData(fname):
    data = []
    wb = xlrd.open_workbook(fname)
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        data.append(sheet.row_values(i))
    return data
wc45_data = getExcelData("C://Users//camer//Downloads//WC45_Temp_HourlyR_2020.xls")

# MySQL datetime format: YYYY-MM-DD hh:mm:ss
# wc45 file format:MM/DD/YY HH:MM so we need to convert before we can use datetimes
def convert_dates(data):
    dates = []
    clean_and_formatted_data = []
    for i in range(len(data)):
        for j in range(len(data[i])):
            if i > 3 and j == 0 and type(data[i][j]) != str:
                excel_anchor = datetime.datetime(1900, 1, 1)
                if (data[i][j] < 60):
                    delta_in_days = datetime.timedelta(days=(data[i][j] - 1))
                else:
                    delta_in_days = datetime.timedelta(days=(data[i][j] - 2))

                converted_date = excel_anchor + delta_in_days
                #list of dates in right format
                clean_and_formatted_data.append([converted_date, data[i][1]])
    return clean_and_formatted_data

formatted_data = convert_dates(wc45_data)

create_table_query = """
CREATE TABLE wc45_temps(
    date DATETIME,
    temperature FLOAT(10, 5)
)
"""
def write(data):
    try:
        with connect(
            host="localhost",
            user=input("Enter username: "),
            password=getpass("Enter password: "),
            database = "temp_records",
        ) as connection:
            db_create = "CREATE DATABASE temp_records"
            with connection.cursor() as cursor:
                cursor.execute(db_create)
            #temp_records is the temperature database

            ###use this to show what databases you have    
            with connection.cursor() as cursor:
                ##create wc45_temps table
                cursor.execute(create_table_query)
                ##put data in table
                for i in range(len(data)):
                    if data[i][1] >= 0:
                        print(data[i])
                        sql = 'INSERT INTO wc45_temps (date, temperature) VALUES (%s, %s)'
                        vals = (data[i][0], data[i][1])
                        cursor.execute(sql, vals)
                    

                connection.commit()
                connection.close()
                cursor.close()
        
    except Error as e:
        print(e)
        connection.rollback()

write(formatted_data)
