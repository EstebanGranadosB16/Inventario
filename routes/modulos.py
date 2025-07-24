# routes/modulos.py
from flask import Blueprint, render_template, request, redirect, flash, url_for
import os
from collections import Counter
import re # Importa el módulo de expresiones regulares

# --- Importa las funciones de utilidad desde helpers.py ---
from utils.helpers import cargar_datos, guardar_datos

modulos_bp = Blueprint('modulos', __name__)

# Definir la ruta absoluta para la carpeta de módulos
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Ir un nivel arriba (a la raíz del proyecto)
MODULOS_DIR = os.path.join(BASE_DIR, 'modulos')

# Asegúrate de que el directorio de módulos exista al iniciar el Blueprint si es necesario
if not os.path.exists(MODULOS_DIR):
    os.makedirs(MODULOS_DIR)

@modulos_bp.route('/modulos')
def ver_modulos():
    # Asegúrate de que MODULOS_DIR exista antes de listar
    if not os.path.exists(MODULOS_DIR):
        modulos = []
    else:
        archivos = os.listdir(MODULOS_DIR)
        modulos = [f.replace('.json', '') for f in archivos if f.endswith('.json')]
    return render_template('modulos.html', modulos=modulos)

@modulos_bp.route('/crear_modulo', methods=['POST'])
def crear_modulo():
    nombre_original = request.form.get('nombre_modulo', '').strip()

    if not nombre_original:
        flash("El nombre del módulo no puede estar vacío.", "error")
        return redirect(url_for('modulos.ver_modulos'))
    
    # --- INICIO DE LA CORRECCIÓN Y MEJORA DE LA SANITIZACIÓN ---
    # Sanitizar el nombre:
    # 1. Eliminar caracteres que NO sean letras, números, espacios, guiones o guiones bajos.
    #    Esto es crucial para eliminar comillas (", ', etc.) y otros símbolos problemáticos.
    nombre_sanitizado = re.sub(r'[^\w\s-]', '', nombre_original) 
    
    # 2. Reemplazar uno o más espacios con un solo guion bajo para nombres de archivo más 'limpios'.
    nombre_sanitizado = re.sub(r'\s+', '_', nombre_sanitizado) 
    
    # 3. Reemplazar múltiples guiones o guiones bajos consecutivos con un solo guion bajo.
    nombre_sanitizado = re.sub(r'_+', '_', nombre_sanitizado) 
    nombre_sanitizado = re.sub(r'-+', '-', nombre_sanitizado) # También para guiones
    
    # 4. Eliminar guiones bajos o guiones al inicio o al final del nombre.
    nombre_sanitizado = nombre_sanitizado.strip('_-') 

    # Si después de sanitizar, el nombre queda vacío (ej. si el original era solo caracteres inválidos)
    if not nombre_sanitizado:
        flash("El nombre del módulo resultante no es válido después de la sanitización. Intente con otro nombre.", "error")
        return redirect(url_for('modulos.ver_modulos'))

    # Si el nombre sanitizado es diferente del original, notifica al usuario del cambio.
    if nombre_sanitizado != nombre_original:
        flash(f"El nombre del módulo '{nombre_original}' se ha ajustado a '{nombre_sanitizado}' para ser compatible con el sistema de archivos.", "warning")
        nombre_final = nombre_sanitizado
    else:
        nombre_final = nombre_original
    # --- FIN DE LA CORRECCIÓN Y MEJORA DE LA SANITIZACIÓN ---

    ruta = os.path.join(MODULOS_DIR, f"{nombre_final}.json") # Usa el nombre_final sanitizado

    if not os.path.exists(ruta):
        guardar_datos([], ruta) # Inicializa el archivo JSON del nuevo módulo como una lista vacía
        flash(f"Módulo '{nombre_final}' creado", 'success')
    else:
        flash(f"El módulo '{nombre_final}' ya existe", 'error')

    return redirect(url_for('modulos.ver_modulos'))

@modulos_bp.route('/eliminar_modulo/<modulo>', methods=['POST'])
def eliminar_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    if os.path.exists(ruta):
        os.remove(ruta)
        flash(f"Módulo '{modulo}' eliminado", 'success')
    else:
        flash(f"Módulo '{modulo}' no encontrado", 'error')
    return redirect(url_for('modulos.ver_modulos'))

@modulos_bp.route('/modulo/<modulo>')
def ver_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    
    # Si el archivo JSON del módulo no existe, redirige con un error
    if not os.path.exists(ruta):
        flash(f"El módulo '{modulo}' no existe o no se ha inicializado.", 'error')
        return redirect(url_for('modulos.ver_modulos'))

    equipos = cargar_datos(ruta) # Carga los equipos del JSON ESPECÍFICO DEL MÓDULO

    # Cálculos para la vista
    tipos = [e.get('tipo', 'Desconocido') for e in equipos]
    conteo_tipos = dict(Counter(tipos))
    total_equipos = len(equipos)
    marcas = [e.get('marca', 'Desconocida') for e in equipos]
    conteo_marcas = dict(Counter(marcas))
    equipos_con_comentarios = [e for e in equipos if e.get('comentario', '').strip()]
    ultimos_registrados = sorted(equipos, key=lambda e: e.get('numero', 0), reverse=True)[:5]

    return render_template(
        'modulo_detail.html', # ¡Renderiza la plantilla específica del detalle del módulo!
        equipos=equipos,
        conteo_tipos=conteo_tipos,
        total_equipos=total_equipos,
        conteo_marcas=conteo_marcas,
        equipos_con_comentarios=equipos_con_comentarios,
        ultimos_registrados=ultimos_registrados,
        modulo_actual=modulo # Pasa el nombre del módulo actual
    )

@modulos_bp.route('/modulo/<modulo>/agregar', methods=['POST'])
def agregar_equipo_modulo(modulo):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta) # Carga los equipos del JSON del módulo
    
    # Asegúrate de manejar el caso donde equipos no es una lista (ej. archivo vacío/corrupto)
    if not isinstance(equipos, list):
        equipos = [] # Inicializa como lista vacía si hay un problema
        flash("Error al cargar datos del módulo. Se inicializará vacío.", "warning")

    nuevo = {
        "numero": len(equipos) + 1, # Asigna el número basado en la longitud actual
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
    guardar_datos(equipos, ruta) # Guarda los equipos en el JSON del módulo
    flash("Equipo agregado exitosamente", "success")
    return redirect(url_for('modulos.ver_modulo', modulo=modulo)) # Redirige al módulo específico

@modulos_bp.route('/modulo/<modulo>/eliminar/<int:numero>', methods=['POST'])
def eliminar_equipo_modulo(modulo, numero):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
    # Filtra el equipo a eliminar
    equipos = [eq for eq in equipos if eq.get('numero') != numero]
    # Re-indexa los números después de la eliminación
    for i, equipo in enumerate(equipos, start=1):
        equipo['numero'] = i
    guardar_datos(equipos, ruta)
    flash("Equipo eliminado", "success")
    return redirect(url_for('modulos.ver_modulo', modulo=modulo))

@modulos_bp.route('/modulo/<modulo>/editar/<int:numero>', methods=['POST'])
def editar_equipo_modulo(modulo, numero):
    ruta = os.path.join(MODULOS_DIR, f"{modulo}.json")
    equipos = cargar_datos(ruta)
    for equipo in equipos:
        if equipo.get('numero') == numero:
            for campo in ["tipo", "serial", "marca", "modelo", "comentario", "procesador", "almacenamiento", "ram", "codigo"]:
                equipo[campo] = request.form.get(campo)
            break
    guardar_datos(equipos, ruta)
    flash("Equipo editado exitosamente", "success")
    return redirect(url_for('modulos.ver_modulo', modulo=modulo))