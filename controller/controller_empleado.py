from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash
import os
from forms.empleado_form import EmpleadoForm, EmpleadoFormMod
from model.persona import Persona
from model.usuario import Usuario
from model.empleado import Empleado 
from datetime import datetime
from model.usuario import Usuario
from extensions import db
from flask_login import login_required, current_user
from extensions import role_required

usuario_bp = Blueprint('usuario', __name__, template_folder='../view/', url_prefix='/usuario')

test_mode = False 

def get_current_user():
    usuario = Usuario.query.get(current_user.idUsuario)
        
    if usuario:
        return {
            "id": usuario.idUsuario,
            "nombre": usuario.nombreUsuario,
            "rol": usuario.rol
        }
    else:
        return {
            "id": None,
            "nombre": "Usuario no encontrado",
            "rol": None
        }
        


def log_error(error_message):
    log_folder = 'logs'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    with open(os.path.join(log_folder, 'app_errors.log'), 'a', encoding='utf-8') as f:
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{fecha}] ERROR: {error_message}\n")

def log_auditoria(action_message):
    log_folder = 'logs'
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
        
    with open(os.path.join(log_folder, 'auditoria.log'), 'a', encoding='utf-8') as f:
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        usuario = get_current_user()
        f.write(f"[{fecha}] Usuario: {usuario} - {action_message}\n")

rol_etiquetas = {
    'ADMS': 'Administrador',
    'CAJA': 'Cajero',
    'PROD': 'Producción'
}

@usuario_bp.route("/")
@usuario_bp.route("/catálago")
@login_required
@role_required("ADMS") 
def empleados():
    mostrar_inactivos = request.args.get('mostrar_inactivos') == 'on'

    try:
        if mostrar_inactivos:
            empleados = (Empleado.query
                         .join(Persona)
                         .join(Usuario)
                         .filter(Usuario.estatus == 0)
                         .all())
        else:
            empleados = (Empleado.query
                         .join(Persona)
                         .join(Usuario)
                         .filter(Usuario.estatus == 1)
                         .all())
    except Exception as e:
        # Logueamos el error
        log_error(f"Error al obtener la lista de empleados: {str(e)}")
        empleados = []
        flash("Ocurrió un error al cargar la lista de empleados.", "danger")

    return render_template(
        "administracion/usuarios/usuarios.html",
        active_page="administracion",
        active_page_admin="usuarios",
        empleados=empleados,
        usuario= current_user
    )

@usuario_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
def registrar_empleado():
    empleado_class = EmpleadoForm(request.form)

    if request.method == 'POST' and empleado_class.validate():
        try:
            ap_paterno = empleado_class.apPaterno.data
            ap_materno = empleado_class.apMaterno.data
            nombre = empleado_class.nombre.data
            fecha_registro = datetime.now()
            dia_mes = fecha_registro.strftime('%d%m')
            rol = empleado_class.rol.data.upper()
            puesto = rol_etiquetas.get(rol, 'Desconocido')

            nombre_usuario = f"{ap_paterno}{nombre}"
            contrasenia = f"{ap_materno}{nombre}12.".capitalize()
            contrasenia_hash = generate_password_hash(contrasenia)

            # Creación de la persona
            persona = Persona(
                apPaterno=empleado_class.apPaterno.data,
                apMaterno=empleado_class.apMaterno.data,
                nombre=empleado_class.nombre.data,
                genero=empleado_class.genero.data,
                telefono=empleado_class.telefono.data,
                email=empleado_class.email.data,
                calle=empleado_class.calle.data,
                numero=empleado_class.numero.data,
                colonia=empleado_class.colonia.data,
                codigoPostal=empleado_class.codigoPostal.data,
                fechaNacimiento=empleado_class.fechaNacimiento.data
            )
            db.session.add(persona)
            db.session.commit()
            ultimo_id_persona = persona.idPersona

            # Creación de usuario
            usuario = Usuario(
                nombreUsuario=nombre_usuario,
                contrasenia=contrasenia_hash,
                estatus=1,
                rol=empleado_class.rol.data
            )
            db.session.add(usuario)
            db.session.commit()
            ultimo_id_usuario = usuario.idUsuario

            # Creación de empleado
            empleado = Empleado(
                puesto=puesto,
                curp=empleado_class.curp.data,
                rfc=empleado_class.rfc.data,
                salarioBruto=empleado_class.salarioBruto.data,
                fechaIngreso=empleado_class.fechaIngreso.data,
                idPersona=ultimo_id_persona,
                idUsuario=ultimo_id_usuario
            )
            db.session.add(empleado)
            db.session.commit()

            flash('Empleado registrado correctamente.', 'success')

            # Log de auditoría: quién registró al empleado
            log_auditoria(f"Registró un nuevo empleado: ID {empleado.idEmpleado}, NombreUsuario {usuario.nombreUsuario}")

            return redirect(url_for('administracion.usuario.empleados'))
        except Exception as e:
            db.session.rollback()
            log_error(f"Error al registrar empleado: {str(e)}")
            flash('Error al registrar el empleado', 'danger')

    return render_template(
        "administracion/usuarios/registrar_usuarios.html",
        active_page="administracion",
        active_page_admin="usuarios",
        form=empleado_class
    )

@usuario_bp.route("/modificar", methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
def modificar_empleado():
    idEmpleado = request.args.get('idEmpleado')

    if not idEmpleado:
        flash("Empleado no encontrado", "danger")
        return redirect(url_for('administracion.usuario.empleados'))

    empleado_class = EmpleadoFormMod(request.form)
    try:
        empleado = (
            db.session.query(Empleado)
            .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
            .filter(Empleado.idEmpleado == idEmpleado)
            .first()
        )
    except Exception as e:
        log_error(f"Error al buscar empleado (ID {idEmpleado}): {str(e)}")
        flash("Error al buscar el empleado", "danger")
        return redirect(url_for('administracion.usuario.empleados'))

    if not empleado:
        flash("Empleado no encontrado", "danger")
        return redirect(url_for('administracion.usuario.empleados'))
    
    if request.method == 'GET':
        # Cargar datos en el formulario
        empleado_class.nombre.data = empleado.persona.nombre
        empleado_class.apPaterno.data = empleado.persona.apPaterno
        empleado_class.apMaterno.data = empleado.persona.apMaterno
        empleado_class.genero.data = empleado.persona.genero
        empleado_class.telefono.data = empleado.persona.telefono
        empleado_class.email.data = empleado.persona.email
        empleado_class.calle.data = empleado.persona.calle
        empleado_class.numero.data = empleado.persona.numero
        empleado_class.colonia.data = empleado.persona.colonia
        empleado_class.codigoPostal.data = empleado.persona.codigoPostal
        empleado_class.fechaNacimiento.data = empleado.persona.fechaNacimiento
        empleado_class.nombreUsuario.data = empleado.usuario.nombreUsuario
        empleado_class.rol.data = empleado.usuario.rol
        empleado_class.curp.data = empleado.curp
        empleado_class.rfc.data = empleado.rfc
        empleado_class.salarioBruto.data = empleado.salarioBruto
        empleado_class.fechaIngreso.data = empleado.fechaIngreso

    if request.method == 'POST' and empleado_class.validate():
        try:
            empleado.persona.apPaterno = empleado_class.apPaterno.data
            empleado.persona.apMaterno = empleado_class.apMaterno.data
            empleado.persona.nombre = empleado_class.nombre.data
            empleado.persona.genero = empleado_class.genero.data
            empleado.persona.telefono = empleado_class.telefono.data
            empleado.persona.calle = empleado_class.calle.data
            empleado.persona.numero = empleado_class.numero.data
            empleado.persona.colonia = empleado_class.colonia.data
            empleado.persona.codigoPostal = empleado_class.codigoPostal.data
            empleado.persona.email = empleado_class.email.data
            empleado.persona.fechaNacimiento = empleado_class.fechaNacimiento.data

            empleado.usuario.nombreUsuario = empleado_class.nombreUsuario.data

            nueva_contrasenia = empleado_class.contrasenia.data
            if nueva_contrasenia:
                empleado.usuario.contrasenia = generate_password_hash(nueva_contrasenia)

            empleado.usuario.rol = empleado_class.rol.data
            puesto = rol_etiquetas.get(empleado_class.rol.data, 'Desconocido')
            empleado.puesto = puesto
            empleado.curp = empleado_class.curp.data
            empleado.rfc = empleado_class.rfc.data
            empleado.salarioBruto = empleado_class.salarioBruto.data
            empleado.fechaIngreso = empleado_class.fechaIngreso.data

            db.session.commit()
            flash("Empleado actualizado correctamente", "success")

            # Log de auditoría: quién modificó al empleado
            log_auditoria(f"Modificó el empleado: ID {empleado.idEmpleado}, NombreUsuario {empleado.usuario.nombreUsuario}")

            return redirect(url_for('administracion.usuario.empleados'))
        except Exception as e:
            db.session.rollback()
            log_error(f"Error al modificar empleado (ID {idEmpleado}): {str(e)}")
            flash("Error al modificar el empleado", "danger")

    return render_template(
        "administracion/usuarios/modificar_usuarios.html",
        active_page="administracion",
        active_page_admin="usuarios",
        form=empleado_class
    )

@usuario_bp.route("/detalles", methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
def detalles_empleado():
    empleado = None
    if request.method == 'GET':
        idEmpleado = request.args.get('idEmpleado')
        try:
            empleado = (
                db.session.query(Empleado)
                .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
                .filter(Empleado.idEmpleado == idEmpleado)
                .first()
            )
        except Exception as e:
            log_error(f"Error al obtener detalles de empleado (ID {idEmpleado}): {str(e)}")
            flash("Error al cargar detalles del empleado", "danger")

    return render_template(
        "administracion/usuarios/detalle_usuarios.html",
        active_page="administracion",
        active_page_admin="usuarios",
        empleado=empleado
    )

@usuario_bp.route('/eliminar', methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
def eliminar_empleado():
    if request.method == 'GET':
        idEmpleado = request.args.get('idEmpleado')
        try:
            empleado = (
                db.session.query(Empleado)
                .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
                .filter(Empleado.idEmpleado == idEmpleado)
                .first()
            )
            if empleado:
                # Validación para que no se eliminen empleados Administradores
                if empleado.usuario.rol.upper() == 'ADMS':
                    flash('No se puede eliminar un empleado Administrador.', 'warning')
                    return redirect(url_for('administracion.usuario.empleados'))
                
                if empleado.usuario.estatus == 1:
                    empleado.usuario.estatus = 0
                    db.session.commit()
                    flash('Empleado eliminado correctamente.', 'success')
                    log_auditoria(f"Eliminó (baja lógica) al empleado: ID {empleado.idEmpleado}, Usuario {empleado.usuario.nombreUsuario}")
                else:
                    flash('El empleado ya está eliminado.', 'warning')
            else:
                flash('Empleado no encontrado.', 'danger')
        except Exception as e:
            db.session.rollback()
            log_error(f"Error al eliminar empleado (ID {idEmpleado}): {str(e)}")
            flash('Error al eliminar el empleado.', 'danger')

        return redirect(url_for('administracion.usuario.empleados'))

    return redirect(url_for('administracion.usuario.empleados'))

@usuario_bp.route('/reactivar', methods=['GET', 'POST'])
@login_required
@role_required("ADMS") 
def reactivar_empleado():
    if request.method == 'GET':
        idEmpleado = request.args.get('idEmpleado') 
        try:
            empleado = (
                db.session.query(Empleado)
                .options(db.joinedload(Empleado.persona), db.joinedload(Empleado.usuario))
                .filter(Empleado.idEmpleado == idEmpleado)
                .first()
            )
            if empleado:
                if empleado.usuario.estatus == 0:
                    empleado.usuario.estatus = 1 
                    db.session.commit()
                    flash('Empleado reactivado correctamente.', 'success')
                    log_auditoria(f"Reactivó al empleado: ID {empleado.idEmpleado}, Usuario {empleado.usuario.nombreUsuario}")
                else:
                    flash('El empleado ya está reactivado.', 'warning')
            else:
                flash('Empleado no encontrado.', 'danger')
        except Exception as e:
            db.session.rollback()
            log_error(f"Error al reactivar empleado (ID {idEmpleado}): {str(e)}")
            flash('Error al reactivar el empleado.', 'danger')

        return redirect(url_for('administracion.usuario.empleados'))

    return redirect(url_for('administracion.usuario.empleados'))
