import datetime

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounts.sqlite3'

# Descomentar para usar mysql con las credenciales y la base de datos correspondientes
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'

db = SQLAlchemy(app)


class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column('id', db.Integer, primary_key=True)
    file_number = db.Column(db.String(100))
    last_read = db.Column(db.DateTime)
    blood = db.Column(db.String(10))
    allergies = db.relationship('Allergy', backref='account')


class Allergy(db.Model):
    __tablename__ = 'allergies'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    medicine = db.Column(db.String(300))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))


@app.route('/demo/v1/accounts/<int:id>/record')
def record(id):
    _account = Account.query.filter_by(id=id).first()

    if not _account:
        return jsonify({'codigo': 400, 'mensaje': 'El id de usuario no existe'})

    _account.last_read = datetime.datetime.now()
    db.session.commit()

    result = {
        'codigo': 200,
        'mensaje': 'Petición completada',
        'payload': {
            'no_expediente': _account.file_number,
            'tipo_sangre': _account.blood,
            'fecha_ultima_consulta': _account.last_read.strftime('%d/%m/%Y'),
            'alergias': []
        }
    }

    if _account.allergies:
        for allergy in _account.allergies:
            result['payload']['alergias'].append({
                'nombre': allergy.name,
                'fecha_alta': allergy.created_at.strftime('%d/%m/%Y'),
                'medicamento': allergy.medicine
            })

    return jsonify(result)


if __name__ == "__main__":
    db.create_all()

    ''' Crear datos de prueba'''
    account = Account()
    account.file_number = '12345'
    account.blood = 'A'
    db.session.add(account)
    db.session.commit()
    allergy = Allergy()
    allergy.name = 'Rinitivis'
    allergy.created_at = datetime.datetime.now()
    allergy.medicine = 'Aspirin 100mg'
    allergy.account_id = account.id
    db.session.add(allergy)
    db.session.commit()

    app.run()
