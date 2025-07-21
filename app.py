from flask import Flask, render_template, request, redirect, flash, url_for
import json
import os
from collections import Counter

app = Flask(__name__)
app.secret_key = 'clave_secreta'

DATA_FILE = 'data/inventario.json'
MODULOS_DIR = 'modulos'

# Asegúrate de que exista el directorio de módulos
if not os.path.exists(MODULOS_DIR):
    os.makedirs(MODULOS_DIR)

# ---------------- FUNCIONES AUXILIARES ----------------

def cargar_datos(archivo=DATA_FILE):
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
            if contenido:
                return json.loads(contenido)
    return []

def guardar_datos(datos, archivo):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def obtener_modulos():
    archivos = os.listdir(MODULOS_DIR)
    return [f.replace('.json', '') for f in archivos if f.endswith('.json')]

# ---------------- RUTAS PRINCIPALES ----------------

@app.context_processor
def inyectar_modulos():
    return {'modulos_disponibles': obtener_modulos()}

@app.route('/')
def redirigir_a_modulos():
    return redirect('/modulos')

@app.route('/inventario')
def index():
    equipos = cargar_datos()
    tipos = [e['tipo'] for e in equipos]
    conteo_tipos = dict(Counter(tipos))
    total_equipos = len(equipos)
    marcas = [e['marca'] for e in equipos]
    conteo_marcas = dict(Counter(marcas))
    equipos_con_comentarios = [e for e in equipos if e['comentario'].strip()]
    ultimos_registrados = sorted(equipos, key=lambda e: e['numero'], reverse=True)[:5]

    return render_template(
        'index.html',
        equipos=equipos,
        conteo_tipos=conteo_tipos,
        total_equipos=total_equipos,
        conteo_marcas=conteo_marcas,
        equipos_con_comentarios=equipos_con_comentarios,
        ultimos_registrados=ultimos_registrados,
        modulo_actual=None
    )

@app.route('/agregar', methods=['POST'])
def agregar():
    equipos = cargar_datos()
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
    equipos = cargar_datos()
    equipos = [eq for eq in equipos if eq['numero'] != numero]
    for i, equipo in enumerate(equipos, start=1):
        equipo['numero'] = i
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo eliminado", "success")
    return redirect('/inventario')

@app.route('/editar/<int:numero>', methods=['POST'])
def editar(numero):
    equipos = cargar_datos()
    for equipo in equipos:
        if equipo['numero'] == numero:
            for campo in ["tipo", "serial", "marca", "modelo", "comentario", "procesador", "almacenamiento", "ram", "codigo"]:
                equipo[campo] = request.form.get(campo)
            break
    guardar_datos(equipos, DATA_FILE)
    flash("Equipo editado exitosamente", "success")
    return redirect('/inventario')

# ---------------- RUTAS PARA MÓDULOS ----------------

@app.route('/modulos')
def ver_modulos():
    modulos = obtener_modulos()
    return render_template('modulos.html', modulos=modulos)

@app.route('/crear_modulo', methods=['POST'])
def crear_modulo():
    nombre = request.form.get('nombre_modulo').strip()
    if not nombre.isalnum():
        flash("Nombre de módulo no válido. Solo se permiten letras y números.", "error")
        return redirect('/modulos')

    ruta = os.path.join(MODULOS_DIR, f"{nombre}.json")
    if not os.path.exists(ruta):
        guardar_datos([], ruta)
        flash(f"Módulo '{nombre}' creado", 'success')
    else:
        flash(f"El módulo '{nombre}' ya existe", 'error')
    return redirect('/modulos')

@app.route('/eliminar_modulo/<modulo>', methods=['POST'])
def eliminar_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    if os.path.exists(ruta):
        os.remove(ruta)
        flash(f"Módulo '{modulo}' eliminado", 'success')
    else:
        flash(f"Módulo '{modulo}' no encontrado", 'error')
    return redirect('/modulos')

@app.route('/modulo/<modulo>')
def ver_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    if not os.path.exists(ruta):
        flash(f"El módulo '{modulo}' no existe", 'error')
        return redirect('/modulos')

    equipos = cargar_datos(ruta)
    tipos = [e['tipo'] for e in equipos]
    conteo_tipos = dict(Counter(tipos))
    total_equipos = len(equipos)
    marcas = [e['marca'] for e in equipos]
    conteo_marcas = dict(Counter(marcas))
    equipos_con_comentarios = [e for e in equipos if e['comentario'].strip()]
    ultimos_registrados = sorted(equipos, key=lambda e: e['numero'], reverse=True)[:5]

    return render_template(
        'index.html',
        equipos=equipos,
        conteo_tipos=conteo_tipos,
        total_equipos=total_equipos,
        conteo_marcas=conteo_marcas,
        equipos_con_comentarios=equipos_con_comentarios,
        ultimos_registrados=ultimos_registrados,
        modulo_actual=modulo
    )

@app.route('/modulo/<modulo>/agregar', methods=['POST'])
def agregar_equipo_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
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
    guardar_datos(equipos, ruta)
    flash("Equipo agregado exitosamente", "success")
    return redirect(f"/modulo/{modulo}")

@app.route('/modulo/<modulo>/eliminar/<int:numero>', methods=['POST'])
def eliminar_equipo_modulo(modulo, numero):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
    equipos = [eq for eq in equipos if eq['numero'] != numero]
    for i, equipo in enumerate(equipos, start=1):
        equipo['numero'] = i
    guardar_datos(equipos, ruta)
    flash("Equipo eliminado", "success")
    return redirect(f"/modulo/{modulo}")

@app.route('/modulo/<modulo>/editar/<int:numero>', methods=['POST'])
def editar_equipo_modulo(modulo, numero):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
    for equipo in equipos:
        if equipo['numero'] == numero:
            for campo in ["tipo", "serial", "marca", "modelo", "comentario", "procesador", "almacenamiento", "ram", "codigo"]:
                equipo[campo] = request.form.get(campo)
            break
    guardar_datos(equipos, ruta)
    flash("Equipo editado exitosamente", "success")
    return redirect(f"/modulo/{modulo}")

# ---------------- EJECUTAR APP ----------------

if __name__ == '__main__':
    app.run(debug=True)