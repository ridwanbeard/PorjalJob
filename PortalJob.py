import base64
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

app = Flask(__name__)

# app.config['SECRET_KEY']='secret'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:sql123@localhost:5432/dbportaljob?sslmode=disable'
db = SQLAlchemy(app)


class Jobseeker(db.Model):
    idjobseeker = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    education = db.Column(db.String(5), nullable=False)
    major = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(500), nullable=False)
    jobseeker_rel = db.relationship('Application', cascade="all,delete", backref='jobseeker')

class Employer(db.Model):
    idemployer = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    companyname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(500), nullable=False)
    job_rel = db.relationship('Job', cascade="all,delete", backref="employer")

class Job(db.Model):  
    idjob = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    requirement = db.Column(db.String(500), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    postingdate = db.Column(db.Date, nullable=False)
    expiredate = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    idemployer = db.Column(db.Integer, db.ForeignKey('employer.idemployer'), nullable=False)
    job_rel = db.relationship('Application', cascade="all,delete", backref='job')

class Application(db.Model):
    idapplication = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    idjobseeker = db.Column(db.Integer, db.ForeignKey('jobseeker.idjobseeker'), nullable=False)
    idjob = db.Column(db.Integer, db.ForeignKey('job.idjob'), nullable=False)
    



# ------------------------------------------------------------------------------------------->>> generate first if db is empty
db.create_all()
db.session.commit()



def auth_jobseeker(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    jobseeker = Jobseeker.query.filter_by(username=username).filter_by(password=password).first()
    if jobseeker:
        return str(jobseeker.idjobseeker)
    else:
        return 
        
def auth_employer(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    employer = Employer.query.filter_by(username=username).filter_by(password=password).first()
    if employer:
        return (employer.idemployer)
    else:
        return 0



# ------------------------------------------------------------------------------------------->>> Home
@app.route('/', methods=['GET'])
def home():
    return jsonify(
        "Home"
    )



# ------------------------------------------------------------------------------------------->>> Jobseeker
@app.route('/jobseeker/register', methods=['POST'])           # Register Account Jobseeker >>>>>
def create_jobseeker():
    data = request.get_json(force=True)
    registered = Jobseeker.query.filter_by(email=data['email']).first()
    sameusername = Jobseeker.query.filter_by(username=data['username']).first()
    if sameusername and registered :
        return{
            "message" : "Account with this email and username have already registered account"
        }
    if sameusername :
        return{
            "message" : "Username is already taken, please choose another username"
        }
    if registered :
        return{
            "message" : "Account with this email have already registered"
        }
    else :
        jobseeker = Jobseeker(
            username = data['username'],
            password = data['password'],
            name = data['name'],
            gender = data['gender'],
            education = data['education'],
            major = data['major'],
            email = data['email'],
            bio = data['bio']
        )
        try:
            db.session.add(jobseeker)
            db.session.commit()
        except:
            return {
                "Message": "Account data save failed"
            }, 400
        return {
            "Message": "Account data save success"
        }, 201

@app.route('/jobseeker/profile', methods=['GET'])             # Account Profile Jobseeker >>>>>
def get_jobseeker_login():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    if not jobseeker :
        return {
            'message': 'ACCESS DENIED !!'
        }, 400
    else :
        return jsonify([
            {
                'name':jobseeker.name,
                'username':jobseeker.username,
                'password':jobseeker.password,
                'gender':jobseeker.gender,
                'education':jobseeker.education,
                'major':jobseeker.major,
                'email':jobseeker.email,
                'bio':jobseeker.bio
            }
            ]), 201
        
@app.route('/jobseeker/updateprofile', methods=['PUT'])       # Update Account Jobseeker >>>>>
def update_jobseeker():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    data  = request.get_json()
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    registered = Jobseeker.query.filter_by(email=data['email']).filter(Jobseeker.idjobseeker!=allow).first()
    sameusername = Jobseeker.query.filter_by(username=data['username']).filter(Jobseeker.idjobseeker!=allow).first()
    if not jobseeker :
        return {
            "Message": 'ACCESS DENIED !'
        }
    if sameusername and registered :
        return{
            "message" : "Email and username have already registered, please choose another email and username"
        }
    if sameusername :
        return{
            "message" : "Username already taken, please choose another username"
        }
    if registered :
        return{
            "message" : "Email is registered, please choose another email"
        }
    else :
        jobseeker.username = data['username']
        jobseeker.password = data['password']
        jobseeker.name = data['name']
        jobseeker.gender = data['gender']
        jobseeker.education = data['education']
        jobseeker.major = data['major']
        jobseeker.email = data['email']
        jobseeker.bio = data['bio']
        db.session.commit()
        return {
            "Message": "Account data update success"
            }, 201

@app.route('/jobseeker/deleteaccount', methods=['DELETE'])    # Delete Account Jobseeker >>>>>
def delete_jobseeker():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    if not allow :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        db.session.delete(jobseeker)
        db.session.commit()
        return {
            "Message": " Account delete success"
            }, 201

@app.route('/searchjobseeker', methods=['POST'])              # Search Jobseeker By Criteria
def search_jobseeker():
    data = request.get_json()
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer :
        return {
            'message' : 'ACCESS DENIED !!'
        }, 400
    elif data['name'] == "" and data['gender'] == "" and data['education'] == "" and data['major'] == "" :
        return jsonify([
        {
            "name" : jobseeker.name,
            "gender" : jobseeker.gender,
            "education" : jobseeker.education,
            "major" : jobseeker.major,
            "email" : jobseeker.email
        } for jobseeker in Jobseeker.query.all()
        ]), 200
    else :
        result = Jobseeker.query.filter(Jobseeker.name.ilike('%'+data['name']+'%')).filter(Jobseeker.gender.ilike('%'+data['gender']+'%')).filter(Jobseeker.education.ilike('%'+data['education']+'%')).filter(Jobseeker.major.ilike('%'+data['major']+'%')).all()
        arr =[]
        for x in result:
            arr.append([
            {
                "name" : x.name,
                "gender" : x.gender,
                "education" : x.education,
                "major" : x.major,
                "email" : x.email
            }
            ])
        return jsonify(arr), 200



# ------------------------------------------------------------------------------------------->>> Employer
@app.route('/employer/register', methods=['POST'])            # Register Account Employer >>>>>
def create_employer():
    data = request.get_json(force=True)
    registered = Employer.query.filter_by(email=data['email']).first()
    sameusername = Employer.query.filter_by(username=data['username']).first()
    if sameusername and registered :
        return{
            "message" : "Account with this email and username have already registered"
        }
    if sameusername :
        return{
            "message" : "Username is already taken, please choose another username"
        }
    if registered :
        return{
            "message" : "Account with this email have already registered"
        }
    else :
        employer = Employer(
            username = data['username'],
            password = data['password'],
            companyname = data['companyname'],
            email = data['email'],
            bio = data['bio']
        )
        try:
            db.session.add(employer)
            db.session.commit()
        except:
            return {
                "Message": "Account data save failed"
            }, 400
        return {
            "Message": "Account data save success"
        }, 201

@app.route('/employer/profile', methods=['GET'])              # Account Profile  >>>>>
def get_employer_login():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer :
        return {
            'message': 'ACCESS DENIED !!'
        }, 400
    else:
        return jsonify([
            {
                'name':employer.companyname,
                'username':employer.username,
                'password':employer.password,
                'email':employer.email,
                'bio':employer.bio
            }
        ]), 201

@app.route('/employer/updateprofile', methods=['PUT'])        # Update Account Employer >>>>>
def update_employer():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    data  = request.get_json()
    employer = Employer.query.filter_by(idemployer=allow).first()
    registered = Employer.query.filter_by(email=data['email']).filter(Employer.idemployer!=allow).first()
    sameusername = Employer.query.filter_by(username=data['username']).filter(Employer.idemployer!=allow).first()
    if not employer :
        return {
            "Message": 'ACCESS DENIED !'
        }
    if sameusername and registered :
        return{
            "message" : "Account with this email and username have already registered"
        }
    if sameusername :
        return{
            "message" : "Username is already taken, please choose another username"
        }
    if registered :
        return{
            "message" : "Account with this email have already registered"
        }
    else :
        employer.username = data['username']
        employer.password = data['password']
        employer.companyname = data['companyname']
        employer.email = data['email']
        employer.bio = data['bio']
        db.session.commit()
        return {
            "Message": "Account data update success"
            }, 201

@app.route('/employer/deleteaccount', methods=['DELETE'])     # Delete Account Employer >>>>>
def delete_employer():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        db.session.delete(employer)
        db.session.commit()
        return {
            "Message": "Account delete success"
        }, 500    



# ------------------------------------------------------------------------------------------->>> Job
@app.route('/getapostedjob/<id>', methods=['GET'])            # Get a Posted Job >>>>>
def get_apostedjob(id):
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    job = Job.query.filter_by(idjob=id).filter_by(idemployer = allow).first()
    if not job :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else:
        return jsonify([
            {
                "Job_Title" : job.title,
	            "Job_Description" : job.description,
	            "Job_Requirement" : job.requirement,
                "Job_Salary" : job.salary,
	            "Job_Category" : job.category,
	            "Area" : job.area,
	            "Posting_Date" : job.postingdate,
	            "Expired_Date" :	job.expiredate,
	            "Status" : job.status
            }
        ]), 201

@app.route('/getallpostedjob', methods=['GET'])               # Get All Posted Job >>>>>
def get_allpostedob():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    job = Job.query.filter_by(idemployer = allow).all()
    if not job :
        return {
            "Message": 'ACCESS DENIED !'
        }
    else:
        return jsonify([
            {
                "Job_Title" : job.title,
	            "Job_Description" : job.description,
	            "Job_Requirement" : job.requirement,
                "Job_Salary" : job.salary,
	            "Job_Category" : job.category,
	            "Area" : job.area,
	            "Posting_Date" : job.postingdate,
	            "Expired_Date" :	job.expiredate,
	            "Status" : job.status
            } for job in Job.query.all()
        ]), 201

@app.route('/getavailablejob', methods=['GET'])               # List All Available Job >>>>>
def get_availablejob():
    today = datetime.now()
    job = Job.query.filter_by(status='Available').filter(Job.expiredate > today).all()
    if job :
        return jsonify([
        {
            "Job_Title" : x.title,
            "Job_Description" : x.description,
            "Job_Requirement" : x.requirement,
            "Job_Salary" : x.salary,
            "Job_Category" : x.category,
            "Area" : x.area,
            "Posting_Date" : x.postingdate,
            "Expired_Date" : x.expiredate,
            "Status" : x.status
        } for x in job
        ]), 201
    else :
        return {
            "Message": 'No available job'
        }

@app.route('/getjoboncriteria', methods=['GET'])              # Search Job By Criteria <<<<<
def get_joboncriteria():
    data = request.get_json()
    if data['title'] == "" and data['category'] == "" and data['salary'] == "" and data['area'] == "" :
        return jsonify([
        {
            "Job_Title" : job.title,
            "Job_Description" : job.description,
            "Job_Requirement" : job.requirement,
            "Job_Salary" : job.salary,
            "Job_Category" : job.category,
            "Area" : job.area,
            "Posting_Date" : job.postingdate,
            "Expired_Date" : job.expiredate,
            "Status" : job.status
        } for job in Job.query.all()
        ]), 200
    elif data['salary'] == ""  :
        gaji = 0
        result = Job.query.filter(Job.title.ilike('%'+data['title']+'%')).filter(Job.category.ilike('%'+data['category']+'%')).filter(Job.salary >= gaji).filter(Job.area.ilike('%'+data['area']+'%')).all()
        return jsonify([
            {
                "Job_Title" : x.title,
                "Job_Description" : x.description,
                "Job_Requirement" : x.requirement,
                "Job_Salary" : x.salary,
                "Job_Category" : x.category,
                "Area" : x.area,
                "Posting_Date" : x.postingdate,
                "Expired_Date" : x.expiredate,
                "Status" : x.status
            } for x in result
            ]), 200
    elif data['salary'] != ""  :
        gaji = int(data['salary'])
        result = Job.query.filter(Job.title.ilike('%'+data['title']+'%')).filter(Job.category.ilike('%'+data['category']+'%')).filter(Job.salary >= gaji).filter(Job.area.ilike('%'+data['area']+'%')).all()
        return jsonify([
            {
                "Job_Title" : x.title,
                "Job_Description" : x.description,
                "Job_Requirement" : x.requirement,
                "Job_Salary" : x.salary,
                "Job_Category" : x.category,
                "Area" : x.area,
                "Posting_Date" : x.postingdate,
                "Expired_Date" : x.expiredate,
                "Status" : x.status
            } for x in result
            ]), 200

@app.route('/create/job', methods=['POST'])                   # Create Job >>>>>
def create_job():
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    data = request.get_json()
    employer = Employer.query.filter_by(idemployer=allow).first()
    posted = Job.query.filter_by(title=data['title']).first()
    if posted :
        return{
            "message" : "Job with this title already posted"
        }

    if not employer : 
        return {
            "Message": 'ACCESS DENIED !'
        }
    else :
        today=date.today()
        job = Job(
            title = data['title'],
            description = data['description'],
            requirement = data['requirement'],
            salary = data['salary'],
            category = data['category'],
            area = data['area'],
            postingdate = today ,
            expiredate = data['expiredate'],
            status = "Available",
            idemployer = employer.idemployer
	    )
        db.session.add(job)
        db.session.commit()
        return {
            "Message": "Job save success"
        }, 201

@app.route('/update/job/<id>', methods=['PUT'])               # Update Job >>>>>
def update_job(id): 
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    data = request.get_json()
    job = Job.query.filter_by(idjob=id).filter_by(idemployer = allow).first()
    posted = Job.query.filter_by(title=data['title']).filter(Job.idemployer == allow).filter(Job.idjob != id).first()
    if posted :
        return{
            "message" : "Job with this title already posted"
        }
    if not job :
        return {
                "Message": "ID job input isn't correct"
            }, 400
    else :
        job.title = data['title']
        job.description = data['description']
        job.requirement = data['requirement']
        job.salary = data['salary']
        job.category = data['category']
        job.area = data['area']
        job.expiredate = data['expiredate']
        job.status = data['status']
        db.session.commit()
        return {
            "Message": "Job data update success"
            }, 201

@app.route('/delete/job/<id>', methods=['DELETE'])            # Delete Job >>>>>
def delete_job(id):
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    job = Job.query.filter_by(idjob=id).filter_by(idemployer=allow).first()
    if not job :
        return {
            "Message": 'ACCESS DENIED !'
            }
    else : 
        db.session.delete(job)
        db.session.commit()
        return {
            "Message": " Job delete success"
        }, 201



# ------------------------------------------------------------------------------------------->>> Application
@app.route('/appliedjob', methods=['GET'])                    # Applied Job List >>>>>
def get_appliedjob():
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    if not jobseeker :
        return {
            'message': 'ACCESS DENIED !!'
        }, 400
    else :
        result = db.engine.execute(f''' SELECT application.status, application.application_date, employer.companyname, job.title, job.description, 
        job.salary, job.postingdate, job.expiredate, application.idjobseeker from application JOIN job ON application.idjob = job.idjob JOIN 
        employer ON job.idemployer = employer.idemployer WHERE application.idjobseeker = '{allow}'  ''')   
        return jsonify([
            {
                'Application_Status' : x.status,
                'Application_Date' : x.application_date,
                'Company_name': x.companyname,
                'Job_Title': x.title,
                'Job_Description': x.description,
                'Job_Salary' : x.salary,
                'Job_Postingdate' : x.postingdate,
                'Job_Expiredate' : x.expiredate
            } for x in result
        ]), 200

@app.route('/applicantlist/<id>', methods=['GET'])            # Applicant list >>>>>
def get_application(id):
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer :
        return {
            "Message": 'ACCESS DENIED !'
        }
    elif employer :
        result = db.engine.execute(f''' SELECT jobseeker.name, jobseeker.gender, jobseeker.education, jobseeker.major, jobseeker.email from application  JOIN jobseeker ON application.idjobseeker = jobseeker.idjobseeker WHERE application.idjob = '{id}'  ''')
        return jsonify([
            {
                'name' : x.name,
                'gender' : x.gender,
                'education': x.education,
                'major': x.major,
                'email': x.email
            } for x in result
        ]), 200

@app.route('/createapplication/<id>', methods=['POST'])       # Create Application >>>>>
def create_application(id):
    decode = request.headers.get('Authorization')
    allow = auth_jobseeker(decode)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=allow).first()
    applied = Application.query.filter((Application.idjobseeker==allow) & (Application.idjob==id)).first()
    today = date.today()
    if not jobseeker :
        return {
            "Message": 'ACCESS DENIED !'
        }
    elif applied :
        return {
            "Message" : "You already applied this job"
        }
    elif jobseeker :
        job = Job.query.filter_by(idjob=id).first()
        application = Application(
            status = "Application Sent",
            application_date = today,
            idjobseeker = allow,
            idjob = job.idjob
        )
        db.session.add(application)
        db.session.commit()
        return {
            "Message": "Application save success"
        }, 201
    else : 
        return {
            "Message": "Application save Failed"
        }, 500

@app.route('/updateapplication/<id>', methods=['PUT'])        # Update Application By Employer
def update_application(id):
    decode = request.headers.get('Authorization')
    allow = auth_employer(decode)
    employer = Employer.query.filter_by(idemployer=allow).first()
    if not employer :
        return {
            "Message": 'ACCESS DENIED !'
        }
    elif employer :
        data  = request.get_json()
        application = Application.query.filter_by(idapplication=id).first()
        application.status = data['status']
        try:
            db.session.commit()
        except:
            return {
                "Message": "save data failed"
            }, 400
        return {
            "Message": "save data success"
        }, 201



if __name__ == "__main__":
    app.run()