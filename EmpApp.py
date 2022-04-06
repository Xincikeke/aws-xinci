from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/addEmpPage", methods=['GET', 'POST'])
def addEmpPage():
    return render_template('addEmp.html')

@app.route("/editEmpPage", methods=['POST'])
def editEmpPage():
    emp_id = request.form['emp_id']
    get_sql = "SELECT emp_id, last_name, first_name, emailAddress, phoneNum, homeAdd, pri_skill, hiringDate FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    cursor.execute(get_sql, (emp_id))
    db_conn.commit()
    for i in cursor:
       emp_id = i[0]
       last_name = i[1]
       first_name = i[2]
       emailAddress = i[3]
       phoneNum = i[4]
       homeAdd = i[5]
       pri_skill = i[6]
       hiringDate = i[7]

    cursor.close()
    return render_template('editEmp.html', emp_id=emp_id, last_name=last_name, first_name=first_name, emailAddress=emailAddress, phoneNum=phoneNum, homeAdd=homeAdd, pri_skill=pri_skill, hiringDate=hiringDate)


@app.route("/addEmp", methods=['POST'])
def AddEmp():
    emp_id=""
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    pri_skill = request.form['pri_skill']
    email = request.form['emailAdd']
    cotactNum = request.form['contactNum']
    homeAdd = request.form['homeAdd']
    hiringDate = request.form['hiringDate']
    payrollID = request.form['payrollID']
    attdID = request.form['attdID']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s,%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id,first_name, last_name, email, cotactNum, homeAdd, pri_skill, payrollID, attdID, hiringDate))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addEmpOutput.html', name=emp_name)

# edit #
@app.route("/editEmp", methods=['POST'])
def editEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    pri_skill = request.form['pri_skill']
    email = request.form['emailAdd']
    phoneNum = request.form['phoneNum']
    homeAdd = request.form['homeAdd']


    update_sql = "UPDATE employee SET first_name = %s, last_name = %s, emailAddress = %s, phoneNum = %s, homeAdd = %s, pri_skill = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (first_name, last_name, email, phoneNum, homeAdd, pri_skill, emp_id))
    db_conn.commit()
    cursor.close()

    print("all modification done...")
    return render_template('editEmpOutput.html')

#retreve all#
@app.route("/fetchdata",methods=['POST'])
def fetchdata():
    cursor = db_conn.cursor()
    cursor.execute("SELECT emp_id, last_name, first_name, emailAddress,phoneNum, homeAdd, pri_skill, payRollID,attendanceID, hiringDate FROM employee")
    i = cursor.fetchall()
    return render_template('employeeInfo.html', data=i)

# search  #
@app.route("/showData", methods=['POST'])
def showData():

    emp_id = request.form['emp_id']
    select_employee_query = "SELECT emp_id, last_name, first_name, emailAddress,phoneNum, homeAdd, pri_skill, payRollID,attendanceID, hiringDate FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    
    cursor.execute(select_employee_query,(emp_id))
    db_conn.commit()
    
    for i in cursor:
       emp_id = i[0]
       first_name = i[1]
       last_name = i[2]
       emailAddress = i[3]
       phoneNum = i[4]
       homeAdd = i[5]
       pri_skill = i[6]
       payRollID = i[7]
       attendanceID = i[8]
       hiringDate = i[9]
       
    cursor.close()   
    return render_template('searchedData.html', emp_id=emp_id, first_name=first_name, last_name=last_name, emailAddress=emailAddress, phoneNum=phoneNum, homeAdd=homeAdd, pri_skill=pri_skill, payRollID=payRollID, attendanceID=attendanceID, hiringDate=hiringDate)

#delete#
@app.route("/deleteEmp", methods=['GET', 'POST'])
def deleteEmp():
    emp_id = request.form['emp_id']
    del_sql = "DELETE FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(del_sql, (emp_id))
    db_conn.commit()
    cursor.close()
    return render_template('deleteEmpOutput.html')


#Attendance#
#DisplayAll#
@app.route("/DisplayAll", methods=['POST'])
def DisplayAll():
    cursor = db_conn.cursor()
    cursor.execute("SELECT attendance_id, emp_name, date, time_in, time_out, benefit from timeandattendance")
    a = cursor.fetchall()
    return render_template('allAttendance.html', data=a)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
