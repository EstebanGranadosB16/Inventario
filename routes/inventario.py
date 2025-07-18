from flask import Blueprint, render_template, request, redirect, flash
from collections import Counter
from utils.helpers import cargar_datos, guardar_datos

inventario_bp = Blueprint('inventario', __name__)
DATA_FILE = 'data/inventario.json'

@inventario_bp.route('/')
def index():
    equipos = cargar_datos(DATA_FILE)
    tipos = [e['tipo'] for e in equipos]
    conteo_tipos = dict(Counter(tipos))
    total_equipos = len(equipos)
    marcas = [e['marca'] for e in equipos]
    conteo_marcas = dict(Counter(marcas))
    equipos_con_comentarios = [e for e in equipos if e['comentario'].strip()]
    ultimos_registrados = sorted(equipos, key=lambda e: e['numero'], reverse=True)[:5]

    return render_template('index.html',
        equipos=equipos,
        conteo_tipos=conteo_tipos,
        total_equipos=total_equipos,
        conteo_marcas=conteo_marcas,
        equipos_con_comentarios=equipos_con_comentarios,
        ultimos_registrados=ultimos_registrados,
        modulo_actual=None
    )

@inventario_bp.route('/agregar', methods=['POST'])
def agregar():
    equipos = cargar_datos(DATA_FILE)
    nuevo = {campo: request.form.get(campo) for campo in [
        "tipo", "serial", "marca", "modelo", "comentario",
        "procesador", "almacenamiento", "ram", "codigo"
    ]}
    nuevo["numero"] = len(equipos) + 1
    equipos.append(nuevo)
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo agregado exitosamente", "success")
    return redirect('/')

@inventario_bp.route('/eliminar/<int:numero>', methods=['POST'])
def eliminar(numero):
    equipos = cargar_datos(DATA_FILE)
    equipos = [eq for eq in equipos if eq['numero'] != numero]
    for i, equipo in enumerate(equipos, start=1):
        equipo['numero'] = i
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo eliminado", "success")
    return redirect('/')

@inventario_bp.route('/editar/<int:numero>', methods=['POST'])
def editar(numero):
    equipos = cargar_datos(DATA_FILE)
    for equipo in equipos:
        if equipo['numero'] == numero:
            for campo in equipo:
                if campo != "numero":
                    equipo[campo] = request.form.get(campo)
            break
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo editado exitosamente", "success")
    return redirect('/')
