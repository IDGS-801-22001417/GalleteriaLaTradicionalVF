from extensions import db
from model.persona import Persona
from model.usuario import Usuario

class Cliente(db.Model):
    __tablename__ = 'cliente'

    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPersona = db.Column(db.Integer, db.ForeignKey('persona.idPersona'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    # Relaciones con las tablas Persona y Usuario

    persona = db.relationship('Persona', backref=db.backref('clientes', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('clientes', lazy=True))