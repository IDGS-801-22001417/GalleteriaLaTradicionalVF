from extensions import db
from model.persona import Persona
from model.usuario import Usuario

class Cliente(db.Model):
    __tablename__ = 'cliente'

    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idPersona = db.Column(db.Integer, db.ForeignKey('persona.idPersona'), nullable=False)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)


    persona = db.relationship('Persona', backref=db.backref('clientes', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('clientes', lazy=True))
    
    
    def __repr__(self):
        return f'<Cliente {self.idCliente}>'
