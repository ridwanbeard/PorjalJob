import base64
from flask import Flask, jsonify, request , current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from flask_cors import CORS, cross_origin
import jwt

cors_config = {
    "origins": ['http://127.0.0.1:5000'],
    "methods": ['GET, POST, OPTIONS, PUT, PATCH, DELETE']
}

app = Flask(__name__)
app.debug = True

CORS(app, resources = {
    r"/*": cors_config
})

ctx = app.app_context()
ctx.push()

app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:sql123@localhost:5432/dbportaljob?sslmode=disable'


db = SQLAlchemy(app)

class Jobseeker(db.Model):
    idjobseeker = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=True)
    education = db.Column(db.String(5), nullable=True)
    major = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    bio = db.Column(db.String(500), nullable=True)
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
# db.create_all()
# db.session.commit()



# ------------------------------------------------------------------------------------------->>> Basic Auth
def auth_jobseeker(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    jobseeker = Jobseeker.query.filter_by(username=username).filter_by(password=password).first()
    if jobseeker:
        tokenJS = jwt.encode({
                'UID': jobseeker.idjobseeker,
				'passkey' :jobseeker.password,
                # 'exp': datetime.datetime.now() + datetime.timedelta(hours=24)
            },'secret' ,algorithm='HS256')
        return {
            "message": tokenJS
        }
    else :
        return {
            "message": "False"
        }
        
def auth_employer(auth):
    encode = base64.b64decode(auth[6:])
    str_encode = encode.decode('ascii')
    lst = str_encode.split(':')
    username = lst[0]
    password = lst[1]   
    employer = Employer.query.filter_by(username=username).filter_by(password=password).first()
    if employer:
        tokenEmp = jwt.encode({
                'UID': employer.idemployer,
				'passkey' :employer.password,
                # 'exp': datetime.datetime.now() + datetime.timedelta(hours=24)
            },'secret' ,algorithm='HS256')
        return {
            "message": tokenEmp
        }
    else :
        return {
            "message": "False"
        }


# ------------------------------------------------------------------------------------------->>> Home BE&FE UDAH
@app.route('/login', methods=['POST'])
def login_user():
    decode = request.headers['Authorization']
    allowJS = auth_jobseeker(decode)
    allowE = auth_employer(decode)
    if allowJS['message'] != "False":
        return{
            "token" : allowJS['message'],
            "status" : "trueJobS"
        }, 200
    elif allowE['message'] != "False":
        return{
            "token" : allowE['message'],
            "status" : "trueEmp"
        }, 200
    return {
        "message": "Login Failed"
    }, 401

# ------------------------------------------------------------------------------------------->>> Home BE&FE UDAH
@app.route('/', methods=['GET'])
def home():
    return jsonify(
        "Home"
    )

# ------------------------------------------------------------------------------------------->>> Jobseeker
@app.route('/jobseeker/register', methods=['POST'])           # Register Account Jobseeker >>>>> BE&FE UDAH
def create_jobseeker():
    data = request.get_json(force=True)
    registered = Jobseeker.query.filter_by(email=data['email']).first()
    sameusername = Jobseeker.query.filter_by(username=data['username']).first()
    if sameusername and registered :
        return{
            "message" : "error 0"
            # "message" : "Account with this email and username have already registered account"
        }, 422
    if sameusername :
        return{
            "message" : "error 1"
            # "message" : "Username is already taken, please choose another username"
        }, 422
    if registered :
        return{
            "message" : "error 2"
            # "message" : "Account with this email have already registered"
        }, 422
    else :
        jobseeker = Jobseeker(
            username = data['username'],
            password = data['password'],
            name = data['name'],
            email = data['email']
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

@app.route('/employerjs/profile/<id>', methods=['GET'])             # Account Profile Jobseeker >>>>> BE&FE UDAH
def get_jobseeker_byemployer(id):
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    employer = Employer.query.filter_by(idemployer=uid).first()
    jobseeker = Jobseeker.query.filter_by(idjobseeker=id).first()

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

@app.route('/jobseeker/profile', methods=['GET'])             # Account Profile Jobseeker >>>>> BE&FE UDAH
def get_jobseeker_login():
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    jobseeker = Jobseeker.query.filter_by(idjobseeker=uid).first()

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
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    
    data  = request.get_json(force=True)
    jobseeker = Jobseeker.query.filter_by(idjobseeker=uid).first()

    registered = Jobseeker.query.filter_by(email=data['email']).filter(Jobseeker.idjobseeker!=uid).first()
    sameusername = Jobseeker.query.filter_by(username=data['username']).filter(Jobseeker.idjobseeker!=uid).first()

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
        # jobseeker.password = data['password']
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
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    jobseeker = Jobseeker.query.filter_by(idjobseeker=uid).first()

    db.session.delete(jobseeker)
    db.session.commit()
    return {
        "Message": " Account delete success"
        }, 201

@app.route('/searchjobseeker', methods=['POST'])              # Search Jobseeker By Criteria
def search_jobseeker():
    data = request.get_json(force=True)

    if data['name'] == "" and data['gender'] == "" and data['education'] == "" and data['major'] == "" :
        return jsonify([
        {
            "name" : jobseeker.name,
            "gender" : jobseeker.gender,
            "education" : jobseeker.education,
            "major" : jobseeker.major,
            "email" : jobseeker.email,
            "bio" : jobseeker.bio
        } for jobseeker in Jobseeker.query.all()
        ]), 200
    else :
        result = Jobseeker.query.filter(Jobseeker.name.ilike('%'+data['name']+'%')).filter(Jobseeker.gender.ilike('%'+data['gender']+'%')).filter(Jobseeker.education.ilike('%'+data['education']+'%')).filter(Jobseeker.major.ilike('%'+data['major']+'%')).all()
        arr =[]
        for x in result:
            arr.append(
            {
                "name" : x.name,
                "gender" : x.gender,
                "education" : x.education,
                "major" : x.major,
                "email" : x.email,
                "bio" : x.bio
            }
            )
        return jsonify(arr), 200



# ------------------------------------------------------------------------------------------->>> Employer
@app.route('/employer/register', methods=['POST'])            # Register Account Employer >>>>> BE&FE UDAH
def create_employer():
    data = request.get_json(force=True)
    registered = Employer.query.filter_by(email=data['email']).first()
    sameusername = Employer.query.filter_by(username=data['username']).first()

    if sameusername and registered :
        return{
            "message" : "error 0"
        }
    if sameusername :
        return{
            "message" : "error 1"
        }
    if registered :
        return{
            "message" : "error 2"
        }
    else :
        employer = Employer(
            username = data['username'],
            password = data['password'],
            companyname = data['companyname'],
            email = data['email'],
            bio = ""
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

@app.route('/employer/profile', methods=['POST'])              # Account Profile  >>>>> BE&FE UDAH
def get_employer_login():

    data  = request.get_json(force=True)
    decoded = jwt.decode(data["token"], 'secret', algorithms=['HS256'])

    uid = decoded["UID"]
    employer = Employer.query.filter_by(idemployer=uid).first()

    return {
            'name':employer.companyname,
            'username':employer.username,
            'password':employer.password,
            'email':employer.email,
            'bio':employer.bio
        }, 201

@app.route('/employer/updateprofile', methods=['PUT'])        # Update Account Employer >>>>> BE&FE UDAH
def update_employer():
    data  = request.get_json(force=True)
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    employer = Employer.query.filter_by(idemployer=uid).first()

    employer.username = data.get('username', employer.username)
    employer.companyname = data.get('companyname', employer.companyname)
    employer.email = data.get('email', employer.email)
    employer.bio = data.get('bio', employer.bio)
    db.session.commit()

    return {
        "mess": employer.username
    }


@app.route('/employer/deleteaccount', methods=['DELETE'])     # Delete Account Employer >>>>> BE&FE UDAH
def delete_employer():
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]

    employer = Employer.query.filter_by(idemployer=uid).first()

    db.session.delete(employer)
    db.session.commit()
    return {
        "Message": "Account delete success"
    }, 500    



# ------------------------------------------------------------------------------------------->>> Job
@app.route('/getjobdetail/<id>', methods=['GET'])            # Get Detail a Posted Job harus login
def get_jobdetail(id):
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]

    jobseeker = Jobseeker.query.filter_by(idjobseeker=uid).first()
    job = Job.query.filter_by(idjob=id).first()

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

@app.route('/getjobdetailxlog/<id>', methods=['GET'])            # Get Detail a Posted Job tanpa login
def get_jobdetailxlog(id):
    job = Job.query.filter_by(idjob=id).first()

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


@app.route('/getapostedjob/<id>', methods=['GET'])            # Get a Posted Job >>>>> BE&FE UDAH
def get_apostedjob(id):
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    job = Job.query.filter_by(idjob=id).filter_by(idemployer = uid).first()

    return jsonify([
        {   
            "Job_ID" :job.idjob,
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

@app.route('/getallpostedjob', methods=['GET'])               # Get All Posted Job >>>>> BE&FE UDAH
def get_allpostedjob():
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    job2 = Job.query.filter_by(idemployer = uid).all()

    if job2 :
        return jsonify([
            {   "Job_ID" :job.idjob,
                "Job_Title" : job.title,
                "Job_Description" : job.description,
                "Job_Requirement" : job.requirement,
                "Job_Salary" : job.salary,
                "Job_Category" : job.category,
                "Area" : job.area,
                "Posting_Date" : job.postingdate,
                "Expired_Date" :	job.expiredate,
                "Status" : job.status
            } for job in job2
        ]), 201
    return{
        'message' : "Job is null"
    }

@app.route('/getavailablejob', methods=['GET'])               # List All Available Job >>>>> BE&FE UDAH
def get_availablejob():
    today = datetime.now()
    job = Job.query.filter_by(status='Available').filter(Job.expiredate > today).all()
    if job :
        return jsonify([
        {
            "Emp_ID": x.idemployer,
            "Job_ID": x.idjob,
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

@app.route('/getjoboncriteria', methods=['POST'])              # Search Job By Criteria <<<<<
def get_joboncriteria():
    data = request.get_json(force=True)
    if data['title'] == "" and data['category'] == "" and data['salary'] == "" and data['area'] == "" :
        return jsonify([
        {
            "Job_Title" : job.title,
            "Emp_ID" : job.idemployer,
            "Job_ID": job.idjob,
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
                "Emp_ID" : x.idemployer,
                "Job_ID": x.idjob,
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

@app.route('/create/job', methods=['POST'])                   # Create Job >>>>> BE&FE UDAH
def create_job():
    data = request.get_json(force=True)
    token = data['Access-Token']
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    employer = Employer.query.filter_by(idemployer=uid).first()
    posted = Job.query.filter_by(title=data['title']).filter_by(idemployer=uid).first()

    if posted :
        return{
            "message" : "Job with this title already posted"
        }

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
        idemployer = uid
    )
    db.session.add(job)
    db.session.commit()
    return {
        "Message": "Job save success"
    }, 201

@app.route('/update/job/<id>', methods=['PUT'])               # Update Job >>>>> BE&FE UDAH
def update_job(id):
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    data = request.get_json(force=True)
    job = Job.query.filter_by(idjob=id).filter_by(idemployer = uid).first()
    posted = Job.query.filter_by(title=data['title']).filter(Job.idemployer == uid).filter(Job.idjob != id).first()
    
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

@app.route('/delete/job/<id>', methods=['DELETE'])            # Delete Job >>>>> XXXXXXXXXXXXXXXXXX
def delete_job(id):
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]

    job = Job.query.filter_by(idjob=id).filter_by(idemployer = uid).first_or_404()
 
    db.session.delete(job)
    db.session.commit()
    return {
        "Message": " Job delete success"
    }, 201


# ------------------------------------------------------------------------------------------->>> Application
@app.route('/appliedjob', methods=['GET'])                    # Applied Job List >>>>>
def get_appliedjob():
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]
    jobseeker = Jobseeker.query.filter_by(idjobseeker=uid).first()

    result = db.engine.execute(f''' SELECT application.status, application.application_date, employer.companyname, job.title, job.description, 
    job.salary, job.postingdate, job.expiredate, application.idjobseeker from application JOIN job ON application.idjob = job.idjob JOIN 
    employer ON job.idemployer = employer.idemployer WHERE application.idjobseeker = '{uid}' ''')   
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

@app.route('/applicantlist/<id>', methods=['GET'])            # Applicant list >>>>> HARUSNYA YG KELUAR LIST SEMUA APPLICANT BERDASARKAN ID JOB      BE&FE UDAH
def get_application(id):
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]

    employer = Employer.query.filter_by(idemployer=uid).first()
    
    result = db.engine.execute(f''' SELECT jobseeker.name, jobseeker.idjobseeker, jobseeker.gender, jobseeker.education, jobseeker.major, jobseeker.email from application  JOIN jobseeker ON application.idjobseeker = jobseeker.idjobseeker WHERE application.idjob = '{id}'  ''')
    return jsonify([
        {
            'name' : x.name,
            'idjobseeker':x.idjobseeker,
            'gender' : x.gender,
            'education': x.education,
            'major': x.major,
            'email': x.email
        } for x in result
    ]), 200

@app.route('/createapplication/<id>', methods=['POST'])       # Create Application >>>>>
def create_application(id):
    today = datetime.now()
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]

    jobseeker = Jobseeker.query.filter_by(idjobseeker=uid).first()
    applied = Application.query.filter((Application.idjobseeker == uid) & (Application.idjob==id)).first()
    today = date.today()

    if applied :
        return {
            "Message" : "You already applied this job"
        }

    if jobseeker :
        job = Job.query.filter_by(idjob=id).first()
        application = Application(
            status = "Application Sent",
            application_date = today,
            idjobseeker = uid,
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
    token = request.headers.get('Access-Token')
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    uid = decoded["UID"]

    employer = Employer.query.filter_by(idemployer=uid).first()
    if not employer :
        return {
            "Message": 'ACCESS DENIED !'
        }
    elif employer :
        data  = request.get_json(force=True)
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


@app.after_request
def after_request_func(response):
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS':
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Accept, Authorization, Access-Token, HTTP_ACCESS_TOKEN')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'PUT')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    return response


if __name__ == '__main__':
    app.run(debug=True)