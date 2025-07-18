from flask import Blueprint, render_template, request, redirect, flash
import os
from collections import Counter
from utils.helpers import cargar_datos, guardar_datos

modulos_bp = Blueprint('modulos', __name__)
MODULOS_DIR = 'modulos'

if not os.path.exists(MODULOS_DIR):
    os.makedirs(MODULOS_DIR)

@modulos_bp.route('/modulos')
def ver_modulos():
    archivos = os.listdir(MODULOS_DIR)
    modulos = [f.replace('.json', '') for f in archivos if f.endswith('.json')]
    return render_template('modulos.html', modulos=modulos)

@modulos_bp.route('/crear_modulo', methods=['POST'])
def crear_modulo():
    nombre = request.form.get('nombre_modulo').strip()
    ruta = os.path.join(MODULOS_DIR, f"{nombre}.json")

    if not os.path.exists(ruta):
        guardar_datos([], ruta)
        flash(f"Módulo '{nombre}' creado", 'success')
    else:
        flash(f"El módulo '{nombre}' ya existe", 'error')

    return redirect('/modulos')

@modulos_bp.route('/eliminar_modulo/<modulo>', methods=['POST'])
def eliminar_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    if os.path.exists(ruta):
        os.remove(ruta)
        flash(f"Módulo '{modulo}' eliminado", 'success')
    else:
        flash(f"Módulo '{modulo}' no encontrado", 'error')
    return redirect('/modulos')

@modulos_bp.route('/modulo/<modulo>')
def ver_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)

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
        modulo_actual=modulo
    )

@modulos_bp.route('/modulo/<modulo>/agregar', methods=['POST'])
def agregar_equipo_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
    nuevo = {campo: request.form.get(campo) for campo in [
        "tipo", "serial", "marca", "modelo", "comentario",
        "procesador", "almacenamiento", "ram", "codigo"
    ]}
    nuevo["numero"] = len(equipos) + 1
    equipos.append(nuevo)
    guardar_datos(equipos, ruta)
    flash("Equipo agregado exitosamente", "success")
    return redirect(f'/modulo/{modulo}')

@modulos_bp.route('/modulo/<modulo>/eliminar/<int:numero>', methods=['POST'])
def eliminar_equipo_modulo(modulo, numero):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
    equipos = [eq for eq in equipos if eq['numero'] != numero]
    for i, equipo in enumerate(equipos, start=1):
        equipo['numero'] = i
    guardar_datos(equipos, ruta)
    flash("Equipo eliminado", "success")
    return redirect(f'/modulo/{modulo}')

@modulos_bp.route('/modulo/<modulo>/editar/<int:numero>', methods=['POST'])
def editar_equipo_modulo(modulo, numero):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
    for equipo in equipos:
        if equipo['numero'] == numero:
            for campo in equipo:
                if campo != "numero":
                    equipo[campo] = request.form.get(campo)
            break
    guardar_datos(equipos, ruta)
    flash("Equipo editado exitosamente", "success")
    return redirect(f'/modulo/{modulo}')
