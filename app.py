from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os
from collections import Counter # Necesario para las estadísticas en ver_modulo

# --- Configuración base ---
app = Flask(__name__)
app.secret_key = 'clave_secreta_muy_segura'  # ¡CAMBIA ESTO EN PRODUCCIÓN! Usa os.urandom(24) o similar
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'inventario.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# --- Modelos ---
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="tecnico")
    # Relación uno a muchos: Un usuario puede tener muchos módulos
    modulos = db.relationship("Modulo", backref="usuario", lazy=True)

    def set_password(self, password):
        """Hashea la contraseña y la guarda."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña proporcionada coincide con la hasheada."""
        return check_password_hash(self.password_hash, password)

class Modulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    # Clave foránea para vincular el módulo a un usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    # Relación uno a muchos: Un módulo puede tener muchos equipos
    # Añadido cascade="all, delete-orphan" para eliminar equipos al borrar módulo
    equipos = db.relationship("Equipo", backref="modulo", lazy=True, cascade="all, delete-orphan") 

class Equipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Clave foránea para vincular el equipo a un módulo
    modulo_id = db.Column(db.Integer, db.ForeignKey('modulo.id'))
    tipo = db.Column(db.String(50))
    serial = db.Column(db.String(100))
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    comentario = db.Column(db.String(200))
    procesador = db.Column(db.String(50))
    almacenamiento = db.Column(db.String(50))
    ram = db.Column(db.String(50))
    codigo = db.Column(db.String(50))

@login_manager.user_loader
def load_user(user_id):
    """Callback para recargar el objeto usuario desde el ID de usuario almacenado en la sesión."""
    return Usuario.query.get(int(user_id))

# --- Autenticación ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión de usuarios."""
    if current_user.is_authenticated: # Si ya está logueado, redirige a la vista principal
        return redirect(url_for('ver_modulo_principal'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Bienvenido, {user.username}', 'success') # Añadido categoría para Bootstrap
            return redirect(url_for('ver_modulo_principal')) # Redirige a la vista principal
        else:
            flash('Credenciales incorrectas', 'danger') # Añadido categoría para Bootstrap
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Cierra la sesión del usuario actual."""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja el registro de nuevos usuarios."""
    # Solo un admin o un usuario no logueado puede acceder a esta ruta.
    # Si un usuario logueado que no es admin intenta acceder, se le redirige.
    if current_user.is_authenticated and current_user.rol != 'admin': 
        flash('No tienes permiso para registrar nuevos usuarios.', 'warning')
        return redirect(url_for('ver_modulo_principal')) # Redirige a la vista principal

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']  # "admin" o "tecnico"
        if Usuario.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'warning')
        else:
            user = Usuario(username=username, rol=rol)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# --- Módulos (ver_modulo ahora es la vista principal) ---
@app.route('/')
@app.route('/modulo/<int:modulo_id>') 
@login_required
def ver_modulo_principal(modulo_id=None): # Renombrado para claridad, y modulo_id es opcional
    """Muestra los detalles de un módulo específico o redirige al primero disponible."""
    
    # Obtener todos los módulos disponibles para el usuario actual (o todos si es admin)
    if current_user.rol == 'admin':
        modulos_disponibles = Modulo.query.all()
    else:
        modulos_disponibles = Modulo.query.filter_by(usuario_id=current_user.id).all()

    # Si no se especificó un modulo_id y hay módulos disponibles, redirige al primero
    if modulo_id is None:
        if modulos_disponibles:
            return redirect(url_for('ver_modulo_principal', modulo_id=modulos_disponibles[0].id))
        else:
            # Si no hay módulos, renderiza una página para crear el primer módulo
            flash('Aún no tienes módulos. ¡Crea tu primer módulo!', 'info')
            return render_template('no_modules.html', modulos=modulos_disponibles) # Pasar modulos para el sidebar

    # Si se especificó un modulo_id
    modulo = Modulo.query.get_or_404(modulo_id)
    # Verifica si el usuario tiene permiso para ver este módulo
    if current_user.rol != 'admin' and modulo.usuario_id != current_user.id:
        flash('No tienes acceso a este módulo', 'danger')
        return redirect(url_for('ver_modulo_principal')) # Redirige a la vista principal sin módulo específico

    equipos = Equipo.query.filter_by(modulo_id=modulo.id).all() # Obtener todos los equipos del módulo

    # Calcular estadísticas para el resumen
    total_equipos = len(equipos)
    conteo_tipos = {}
    conteo_marcas = {}
    tipos_disponibles = set()
    marcas_disponibles = set()
    rams_disponibles = set()
    almacenamientos_disponibles = set()

    for equipo in equipos:
        if equipo.tipo:
            conteo_tipos[equipo.tipo] = conteo_tipos.get(equipo.tipo, 0) + 1
            tipos_disponibles.add(equipo.tipo)
        if equipo.marca:
            conteo_marcas[equipo.marca] = conteo_marcas.get(equipo.marca, 0) + 1
            marcas_disponibles.add(equipo.marca)
        if equipo.ram:
            rams_disponibles.add(equipo.ram)
        if equipo.almacenamiento:
            almacenamientos_disponibles.add(equipo.almacenamiento)

    return render_template(
        'modulo_detail.html',
        modulo=modulo, # El módulo que se está viendo actualmente
        equipos=equipos,
        total_equipos=total_equipos,
        conteo_tipos=conteo_tipos,
        conteo_marcas=conteo_marcas,
        tipos_disponibles=sorted(list(tipos_disponibles)),
        marcas_disponibles=sorted(list(marcas_disponibles)),
        rams_disponibles=sorted(list(rams_disponibles)),
        almacenamientos_disponibles=sorted(list(almacenamientos_disponibles)),
        modulos=modulos_disponibles, # Pasar todos los módulos disponibles para el sidebar
        modulo_actual=modulo # Pasar el objeto módulo actual para resaltar en el sidebar
    )

@app.route('/crear_modulo', methods=['POST'])
@login_required
def crear_modulo():
    """Crea un nuevo módulo."""
    nombre = request.form['nombre']
    if current_user.rol == 'admin':
        # Admin puede crear módulos con nombres duplicados si son para diferentes usuarios,
        # pero aquí simplificamos y comprobamos si el nombre ya existe para CUALQUIER usuario.
        if Modulo.query.filter_by(nombre=nombre).first():
            flash(f'Ya existe un módulo global con el nombre "{nombre}".', 'warning')
            return redirect(url_for('ver_modulo_principal'))
    else:
        # Los técnicos solo pueden crear módulos para ellos mismos y no pueden duplicar nombres.
        if Modulo.query.filter_by(nombre=nombre, usuario_id=current_user.id).first():
            flash(f'Ya existe un módulo con el nombre "{nombre}" para tu usuario.', 'warning')
            return redirect(url_for('ver_modulo_principal'))

    modulo = Modulo(nombre=nombre, usuario_id=current_user.id)
    db.session.add(modulo)
    db.session.commit()
    flash('Módulo creado exitosamente', 'success')
    return redirect(url_for('ver_modulo_principal', modulo_id=modulo.id)) # Redirige al nuevo módulo

@app.route('/eliminar_modulo/<int:modulo_id>', methods=['POST'])
@login_required
def eliminar_modulo(modulo_id):
    """Elimina un módulo y todos sus equipos asociados."""
    modulo = Modulo.query.get_or_404(modulo_id)
    # Solo el admin o el propietario del módulo pueden eliminarlo
    if current_user.rol != 'admin' and modulo.usuario_id != current_user.id:
        flash('No tienes permiso para eliminar este módulo.', 'danger')
        return redirect(url_for('ver_modulo_principal'))

    db.session.delete(modulo)
    db.session.commit()
    flash(f'Módulo "{modulo.nombre}" eliminado exitosamente.', 'success')
    return redirect(url_for('ver_modulo_principal')) # Redirige a la vista principal

# --- Equipos ---
@app.route('/modulo/<int:modulo_id>/agregar_equipo', methods=['POST'])
@login_required
def agregar_equipo(modulo_id):
    """Agrega un nuevo equipo a un módulo específico."""
    modulo = Modulo.query.get_or_404(modulo_id)
    if current_user.rol != 'admin' and modulo.usuario_id != current_user.id:
        flash('No tienes acceso para agregar equipos a este módulo', 'danger')
        return redirect(url_for('ver_modulo_principal'))
    nuevo = Equipo(
        modulo_id=modulo.id,
        tipo=request.form.get("tipo"),
        serial=request.form.get("serial"),
        marca=request.form.get("marca"),
        modelo=request.form.get("modelo"),
        comentario=request.form.get("comentario"),
        procesador=request.form.get("procesador"),
        almacenamiento=request.form.get("almacenamiento"),
        ram=request.form.get("ram"),
        codigo=request.form.get("codigo"),
    )
    db.session.add(nuevo)
    db.session.commit()
    flash('Equipo agregado exitosamente', 'success')
    return redirect(url_for('ver_modulo_principal', modulo_id=modulo.id))

@app.route('/modulo/<int:modulo_id>/eliminar_equipo/<int:equipo_id>', methods=['POST'])
@login_required
def eliminar_equipo(modulo_id, equipo_id):
    """Elimina un equipo específico de un módulo."""
    modulo = Modulo.query.get_or_404(modulo_id)
    equipo = Equipo.query.get_or_404(equipo_id)
    # Verifica permisos para eliminar el equipo
    if current_user.rol != 'admin' and modulo.usuario_id != current_user.id:
        flash('No tienes acceso para eliminar equipos de este módulo', 'danger')
        return redirect(url_for('ver_modulo_principal'))
    db.session.delete(equipo)
    db.session.commit()
    flash('Equipo eliminado exitosamente', 'success')
    return redirect(url_for('ver_modulo_principal', modulo_id=modulo.id))

@app.route('/modulo/<int:modulo_id>/editar_equipo/<int:equipo_id>', methods=['POST']) 
@login_required
def editar_equipo(modulo_id, equipo_id):
    """Edita un equipo específico de un módulo."""
    modulo = Modulo.query.get_or_404(modulo_id)
    equipo = Equipo.query.get_or_404(equipo_id)

    # Verifica permisos para editar el equipo
    if current_user.rol != 'admin' and modulo.usuario_id != current_user.id:
        flash('No tienes acceso para editar equipos en este módulo', 'danger')
        return redirect(url_for('ver_modulo_principal'))

    # Actualiza los campos del equipo con los datos del formulario
    equipo.tipo = request.form.get("tipo")
    equipo.serial = request.form.get("serial")
    equipo.marca = request.form.get("marca")
    equipo.modelo = request.form.get("modelo")
    equipo.comentario = request.form.get("comentario")
    equipo.procesador = request.form.get("procesador")
    equipo.almacenamiento = request.form.get("almacenamiento")
    equipo.ram = request.form.get("ram")
    equipo.codigo = request.form.get("codigo")
    
    db.session.commit()
    flash('Equipo actualizado exitosamente', 'success')
    return redirect(url_for('ver_modulo_principal', modulo_id=modulo.id))


# --- Inicializar base de datos ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Crea las tablas si no existen
        # Opcional: Crear un usuario administrador por defecto si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin_user = Usuario(username='admin', rol='admin')
            admin_user.set_password('adminpass') # ¡CAMBIA ESTA CONTRASEÑA EN PRODUCCIÓN!
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario 'admin' creado con contraseña 'adminpass'")
    app.run(debug=True)

