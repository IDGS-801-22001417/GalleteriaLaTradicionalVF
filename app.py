from flask import Flask, render_template, request, redirect, url_for
from extensions import csrf, db
from config import DevelopmentConfig
from extensions import db
from controller.controller_administracion import admin_bp
from controller.controller_venta import venta_bp
from flask_wtf import CSRFProtect
from controller.portal_controller import portal_cliente_bp
from controller.controller_insumo import insumo_bp
from controller.controller_ordenes import orden_bp
from controller.controller_produccion import produccion_bp
from controller.controller_galletas import galletas_bp

app = Flask(__name__, template_folder='view')
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect(app)
db.init_app(app)
csrf.init_app(app)

app.config['SECRET_KEY'] = 'clave-secreta-segura'
app.config['WTF_CSRF_ENABLED'] = True

app.register_blueprint(admin_bp, url_prefix='/administracion')
app.register_blueprint(venta_bp, url_prefix='/venta')
app.register_blueprint(insumo_bp, url_prefix='/insumos')
app.register_blueprint(orden_bp, url_prefix='/orden')
app.register_blueprint(admin_bp)
app.register_blueprint(portal_cliente_bp)

@app.route("/administracion")
@app.route("/administrador")
def proveedores():
    return redirect(url_for('administracion.proveedor.proveedores'))

@app.route('/')
def index():
    return redirect(url_for('administracion.clientes.clientes'))

@app.route('/administracion')
def administracion():
    return render_template('layout_administracion.html')

@app.route("/")
@app.route("/venta")
@app.route("/ventas")
def ventas():
    return redirect(url_for('venta.ventas'))

@app.route("/")
def index():
    return redirect(url_for('insumo.insumos'))

@app.route("/galletas")
def galletas():
    return render_template("layout_clientes.html", active_page="galletas")

@app.route("/ventas")
def ventas():
    return render_template("layout_clientes.html", active_page="ventas")

@app.route("/produccion")
def produccion():
    return render_template("layout_login.html", active_page="produccion")

@app.route("/")
def home():
    return render_template("index.html", active_page="home")

@app.route("/ventas")
def ventas():
    return render_template("layout_galleteria.html", active_page="ventas")

@app.route("/insumos")
def insumos():
    return render_template("insumos.html", active_page="insumos")

@app.route("/administrador")
def administrador():
    return render_template("administrador.html", active_page="administrador")

@app.route("/ordenes")
def ordenes():
    return render_template("ordenes.html", active_page="ordenes")

@app.route("/ganancias")
def ganancias():
    return render_template("layout_clientes.html", active_page="ganancias")

@app.route("/administracion")
def administracion():
    return render_template("layout_clientes.html", active_page="administracion")

@app.route("/proveedores")
def proveedores():
    return render_template("layout_clientes.html", active_page="proveedores")


@app.route("/clientes")
def clientes():
    return render_template("layout_clientes.html", active_page="clientes")

@app.route("/recetas")
def recetas():
    return render_template("layout_clientes.html", active_page="recetas")


if __name__ == '__main__':    
    with app.app_context():
        db.create_all()
