# app.py
from flask import Flask, render_template, request, redirect, flash, url_for
import os
from collections import Counter

# --- Importa las funciones de utilidad desde helpers.py ---
from utils.helpers import cargar_datos, guardar_datos

# --- Importa el Blueprint de modulos ---
from routes.modulos import modulos_bp

app = Flask(__name__)
app.secret_key = 'clave_secreta' # ¡Cambia esto por una clave más segura en producción!

# Definir la ruta base del proyecto para rutas absolutas
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Rutas de archivos de datos
DATA_FILE = os.path.join(BASE_DIR, 'data', 'inventario.json')
MODULOS_DIR = os.path.join(BASE_DIR, 'modulos')

# Asegúrate de que existan los directorios
if not os.path.exists(os.path.dirname(DATA_FILE)):
    os.makedirs(os.path.dirname(DATA_FILE))
# Asegúrate de que el archivo inventario.json exista e inicialízalo si no
if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
    guardar_datos([], DATA_FILE)

if not os.path.exists(MODULOS_DIR):
    os.makedirs(MODULOS_DIR)

# ---------------- FUNCIONES AUXILIARES (específicas de app.py si las hubiera) ----------------
# Aquí podrías tener funciones auxiliares que no son para cargar/guardar datos,
# pero que app.py necesite directamente.

def obtener_modulos():
    # Asegúrate de que MODULOS_DIR exista antes de listar su contenido
    if not os.path.exists(MODULOS_DIR):
        return []
    archivos = os.listdir(MODULOS_DIR)
    return [f.replace('.json', '') for f in archivos if f.endswith('.json')]

# ---------------- CONTEXT PROCESSOR (para pasar módulos disponibles a todas las plantillas) ----------------
@app.context_processor
def inyectar_modulos():
    return {'modulos_disponibles': obtener_modulos()}

# ---------------- RUTAS PRINCIPALES (Inventario General) ----------------

@app.route('/')
def redirigir_a_modulos():
    return redirect(url_for('modulos.ver_modulos')) # Redirige al blueprint de módulos

@app.route('/inventario')
def index():
    equipos = cargar_datos(DATA_FILE) # Carga del inventario general
    tipos = [e.get('tipo', 'Desconocido') for e in equipos]
    conteo_tipos = dict(Counter(tipos))
    total_equipos = len(equipos)
    marcas = [e.get('marca', 'Desconocida') for e in equipos]
    conteo_marcas = dict(Counter(marcas))
    equipos_con_comentarios = [e for e in equipos if e.get('comentario', '').strip()]
    ultimos_registrados = sorted(equipos, key=lambda e: e.get('numero', 0), reverse=True)[:5] # Usar .get para evitar KeyError

    return render_template(
        'index.html', # Esta es tu plantilla para el inventario general si la tienes
        equipos=equipos,
        conteo_tipos=conteo_tipos,
        total_equipos=total_equipos,
        conteo_marcas=conteo_marcas,
        equipos_con_comentarios=equipos_con_comentarios,
        ultimos_registrados=ultimos_registrados,
        modulo_actual=None # No hay módulo específico aquí
    )

@app.route('/agregar', methods=['POST'])
def agregar():
    equipos = cargar_datos(DATA_FILE)
    nuevo = {
        "numero": len(equipos) + 1,
        "tipo": request.form.get("tipo"),
        "serial": request.form.get("serial"),
        "marca": request.form.get("marca"),
        "modelo": request.form.get("modelo"),
        "comentario": request.form.get("comentario"),
        "procesador": request.form.get("procesador"),
        "almacenamiento": request.form.get("almacenamiento"),
        "ram": request.form.get("ram"),
        "codigo": request.form.get("codigo")
    }
    equipos.append(nuevo)
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo agregado exitosamente", "success")
    return redirect('/inventario')

@app.route('/eliminar/<int:numero>', methods=['POST'])
def eliminar(numero):
    equipos = cargar_datos(DATA_FILE)
    equipos = [eq for eq in equipos if eq['numero'] != numero]
    for i, equipo in enumerate(equipos, start=1):
        equipo['numero'] = i # Re-indexar los números
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo eliminado", "success")
    return redirect('/inventario')

@app.route('/editar/<int:numero>', methods=['POST'])
def editar(numero):
    equipos = cargar_datos(DATA_FILE)
    for equipo in equipos:
        if equipo.get('numero') == numero:
            for campo in ["tipo", "serial", "marca", "modelo", "comentario", "procesador", "almacenamiento", "ram", "codigo"]:
                equipo[campo] = request.form.get(campo)
            break
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo editado exitosamente", "success")
    return redirect('/inventario')


# ---------------- REGISTRA EL BLUEPRINT DE MÓDULOS ----------------
app.register_blueprint(modulos_bp) # ¡Esta línea es crucial!

# ---------------- EJECUTAR APP ----------------
if __name__ == '__main__':
    app.run(debug=True)