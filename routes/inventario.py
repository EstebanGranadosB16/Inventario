from flask import Blueprint, render_template, request, redirect, flash, url_for
from collections import Counter
import os # Necesario para DATA_FILE

# --- Importa las funciones de utilidad desde helpers.py ---
from utils.helpers import cargar_datos, guardar_datos

inventario_bp = Blueprint('inventario', __name__)

# Definir la ruta absoluta para el archivo de datos del inventario general
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Ir un nivel arriba (a la raíz del proyecto)
DATA_FILE = os.path.join(BASE_DIR, 'data', 'inventario.json')

# Asegúrate de que el archivo inventario.json exista e inicialízalo si no
if not os.path.exists(os.path.dirname(DATA_FILE)):
    os.makedirs(os.path.dirname(DATA_FILE))
if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
    guardar_datos([], DATA_FILE)


@inventario_bp.route('/')
def index():
    equipos = cargar_datos(DATA_FILE) # Carga del inventario general
    tipos = [e.get('tipo', 'Desconocido') for e in equipos]
    conteo_tipos = dict(Counter(tipos))
    total_equipos = len(equipos)
    marcas = [e.get('marca', 'Desconocida') for e in equipos]
    conteo_marcas = dict(Counter(marcas))
    equipos_con_comentarios = [e for e in equipos if e.get('comentario', '').strip()]
    ultimos_registrados = sorted(equipos, key=lambda e: e.get('numero', 0), reverse=True)[:5]

    return render_template(
        'index.html', # Esta es tu plantilla para el inventario general
        equipos=equipos,
        conteo_tipos=conteo_tipos,
        total_equipos=total_equipos,
        conteo_marcas=conteo_marcas,
        equipos_con_comentarios=equipos_con_comentarios,
        ultimos_registrados=ultimos_registrados,
        modulo_actual=None # No hay módulo específico aquí
    )

@inventario_bp.route('/agregar', methods=['POST'])
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
    return redirect(url_for('inventario.index')) # Redirige a la vista principal del inventario general

@inventario_bp.route('/eliminar/<int:numero>', methods=['POST'])
def eliminar(numero):
    equipos = cargar_datos(DATA_FILE)
    equipos = [eq for eq in equipos if eq['numero'] != numero]
    for i, equipo in enumerate(equipos, start=1):
        equipo['numero'] = i # Re-indexar los números
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo eliminado", "success")
    return redirect(url_for('inventario.index'))

@inventario_bp.route('/editar/<int:numero>', methods=['POST'])
def editar(numero):
    equipos = cargar_datos(DATA_FILE)
    for equipo in equipos:
        if equipo.get('numero') == numero:
            for campo in ["tipo", "serial", "marca", "modelo", "comentario", "procesador", "almacenamiento", "ram", "codigo"]:
                equipo[campo] = request.form.get(campo)
            break
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo editado exitosamente", "success")
    return redirect(url_for('inventario.index'))