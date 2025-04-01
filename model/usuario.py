from extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombreUsuario = db.Column(db.String(20), unique=True, nullable=False)
    token = db.Column(db.String(255))
    estatus = db.Column(db.Integer, nullable=False, default=1)  # 0: Inactivo, 1: Activo
    contrasenia = db.Column(db.Text, nullable=False)
    rol = db.Column(db.String(4), nullable=False)  # ADMS, CAJA, PROD, CLIE
    ultima_conexion = db.Column(db.DateTime)
    
    # Relaciones
    cliente = db.relationship('Cliente', back_populates='usuario', uselist=False)