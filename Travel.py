import base64
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:sql123@localhost:5432/travelbus?sslmode=disable'

class Order(db.Model):
    noorder = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    namacustomer = db.Column(db.String(50), nullable=False)
    notelp = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    jmlkursi = db.Column(db.Integer, nullable=False)
    jadwal_harga = db.Column(db.Integer)
    totalharga = db.Column(db.Integer)
    jadwal_jamberangkat = db.Column(db.String(20))
    nojadwal = db.Column(db.Integer, db.ForeignKey('jadwal.nojadwal'), nullable=False)

class Jadwal(db.Model):
    nojadwal = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True) #----- id
    berangkat = db.Column(db.String(50), nullable=False)
    tujuan = db.Column(db.String(50), nullable=False)
    jamberangkat = db.Column(db.String(20), nullable=False)
    harga = db.Column(db.Integer, nullable=False)
    bus_kapasitas = db.Column(db.Integer) 
    nobus = db.Column(db.Integer, db.ForeignKey('bus.nobus'), nullable=False) #----- id
    nodriver = db.Column(db.Integer, db.ForeignKey('driver.nodriver'), nullable=False)
    order_rel=db.relationship('Order', backref='jadwal')

class Bus(db.Model):
    nobus = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True) #----- id
    nopol = db.Column(db.String(20), nullable=False)
    kapasitas = db.Column(db.Integer, nullable=False)
    kelas = db.Column(db.String(20), nullable=False)
    jadwal_rel=db.relationship('Jadwal', backref='bus')

class Driver(db.Model):
    nodriver = db.Column(db.Integer, primary_key=True, index=True, nullable=False, unique=True)
    nama = db.Column(db.String(50), nullable=False)
    alamat = db.Column(db.String(100), nullable=False)
    notelp = db.Column(db.String(20), nullable=False)  



# ------ generate first if db is empty
# db.create_all()
# db.session.commit()



def BasicAuth() :
    pass_str = request.headers.get('Authorization')     #untuk mengambil authorization di postman
    pass_bersih = pass_str.replace('Basic ',"")         #untuk memotong "basic" (pada value authorization)
    hasil_decode = base64.b64decode(pass_bersih)        #untuk merubah password (decode) "dGVzbWlrOnRlczEyMw==" menjadi "tes123" (base64.b64code merupakan package fungsi dari python)
    hasil_decode_bersih = hasil_decode.decode('utf-8')  #untuk membuang "b" pada hasil_decode (.decode('utf-8))
    username_aja = hasil_decode_bersih.split(":")[0]    #untuk slicing apabila ingin menampilkan username saja (username:)
    pass_aja = hasil_decode_bersih.split(":")[1]        #untuk slicing apabila ingin menampilkan pass saja (:password)
    return[username_aja,pass_aja]
    # if username_aja == 'tes' and pass_aja == 'tes123' : #kondisional apabila user memasukan pass dan username sesuai 
    #     return True


# ------ Home
@app.route('/', methods=['GET'])
def home():
    return jsonify(
        "Home"
    )



# ------ Bus
@app.route('/bus', methods=['GET'])
def get_bus():
    parsed = BasicAuth()
    username = parsed[0]
    password= parsed[1]
    if password == "pass123" and username == "sql123" :
        return jsonify([
            {
                'nopol':bus.nopol,
                'kapasitas' :bus.kapasitas,
                'kelas' :bus.kelas
            } for bus in Bus.query.all() #Query semua data di table
        ]), 201

@app.route('/bus', methods=['POST'])
def create_bus():
    data = request.get_json(force=True)
    bus = Bus(
    nopol=data['nopol'],
    kapasitas=data['kapasitas'],
    kelas = data['kelas']
	)
    try:
        db.session.add(bus)
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/bus/<id>', methods=['PUT'])
def update_bus(id):
    data  = request.get_json()
    bus = Bus.query.filter_by(nobus=id).first()
    bus.nopol = data['nopol'] 
    bus.kapasitas = data['kapasitas'] 
    bus.kelas = data['kelas'] 
    try:
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/bus/<id>', methods=['DELETE'])
def delete_bus(id):
    try:
        bus = Bus.query.filter_by(nobus=id).first()
        db.session.delete(bus)
        db.session.commit()
    except:
        return {
            "Message": "delete data failed"
        }, 500
    return {
        "Message": "delete data success"
    }, 201



# ------ driver
@app.route('/driver', methods=['GET'])
def get_driver():
    return jsonify ([
        {
            'nama': driver.nama,
            'alamat': driver.alamat,
            'notelp': driver.notelp
        } for driver in Driver.query.all()
    ]), 201

@app.route('/driver', methods=['POST'])
def create_driver():
    data = request.get_json(force=True)
    driver = Driver(
        nama = data['nama'],
        alamat = data['alamat'],
        notelp = data['notelp']
	)
    try:
        db.session.add(driver)
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/driver/<id>', methods=['PUT'])
def update_driver(id):
    data  = request.get_json()
    driver = Driver.query.filter_by(nodriver=id).first()
    driver.nama = data['nama']
    driver.alamat = data['alamat']
    driver.notelp = data['notelp']
    try:
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/driver/<id>', methods=['DELETE'])
def delete_driver(id):
    try:
        driver = Driver.query.filter_by(nodriver=id).first()
        db.session.delete(driver)
        db.session.commit()
    except:
        return {
            "Message": "delete data failed"
        }, 500

    return {
        "Message": "delete data success"
    }, 201



# ------ jadwal
@app.route('/jadwal', methods=['GET'])
def get_jadwal():
    return jsonify ([
        {
            'berangkat': jadwal.berangkat,
            'tujuan': jadwal.tujuan,
            'jamberangkat': jadwal.jamberangkat,
            'harga' : jadwal.harga,
            'nobus' : jadwal.nobus
        } for jadwal in Jadwal.query.all()
    ]), 201

@app.route('/jadwal', methods=['POST'])
def create_jadwal():
    data = request.get_json(force=True)
    bus = Bus.query.filter_by(nobus=data['nobus']).first()
    jadwal = Jadwal(
        berangkat = data['berangkat'],
        tujuan = data['tujuan'],
        jamberangkat = data['jamberangkat'],
        harga = data['harga'],
        bus_kapasitas = bus.kapasitas,
        nobus = data['nobus'],
        nodriver = data['nodriver']
	)
    try:
        db.session.add(jadwal)
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/jadwal/<id>', methods=['PUT'])
def update_jadwal(id):
    data  = request.get_json()
    jadwal = Jadwal.query.filter_by(nojadwal=id).first()
    jadwal.berangkat = data['berangkat']
    jadwal.tujuan = data['tujuan']
    jadwal.jamberangkat = data['jamberangkat']
    jadwal.harga = data['harga']
    try:
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/jadwal/<id>', methods=['DELETE'])
def delete_jadwal(id):
    try:
        jadwal = Jadwal.query.filter_by(nojadwal=id).first()
        db.session.delete(jadwal)
        db.session.commit()
    except:
        return {
            "Message": "delete data failed"
        }, 500

    return {
        "Message": "delete data success"
    }, 201



# ------ order
@app.route('/order', methods=['GET'])
def get_order():
    result = db.engine.execute(f'''SELECT "order".*, driver.nama FROM driver INNER JOIN jadwal ON driver.nodriver = jadwal.nodriver INNER JOIN "order" ON jadwal.nojadwal = "order".nojadwal''')
    for x in result:
        return jsonify([
            {
                'nama customer': x.namacustomer,
                'notelp': x.notelp,
                'email': x.email,
                'jmlkursi' : x.jmlkursi,
                'nama driver' : x.nama
            }
        ])

@app.route('/order', methods=['POST'])
def create_order():
    data = request.get_json(force=True)
    jadwal = Jadwal.query.filter_by(nojadwal=data['nojadwal']).first()
    order = Order(
        namacustomer = data['namacustomer'],
        notelp = data['notelp'],
        email = data['email'],
        jmlkursi = data['jmlkursi'],
        jadwal_harga = jadwal.harga,
        jadwal_jamberangkat = jadwal.jamberangkat,
        totalharga = data['jmlkursi'] * jadwal.harga,
        nojadwal = data['nojadwal']
	)
    jadwal.bus_kapasitas -= data['jmlkursi']
    try:
        db.session.add(order)
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/order/<id>', methods=['PUT'])
def update_order(id):
    data  = request.get_json()
    order = Order.query.filter_by(noorder=id).first()
    order.namacustomer = data['namacustomer']
    order.notelp = data['notelp']
    order.email = data['email']
    order.jmlkursi = data['jmlkursi']
    order.nojadwal = data['nojadwal']
    try:
        db.session.commit()
    except:
        return {
            "Message": "save data failed"
        }, 400
    return {
        "Message": "save data success"
    }, 201

@app.route('/order/<id>', methods=['DELETE'])
def delete_order(id):
    try:
        order = Order.query.filter_by(noorder=id).first()
        db.session.delete(order)
        db.session.commit()
    except:
        return {
            "Message": "delete data failed"
        }, 500

    return {
        "Message": "delete data success"
    }, 201

if __name__ == "__main__":
    app.run()