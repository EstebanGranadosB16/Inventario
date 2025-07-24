# utils/helpers.py
import json
import os

def cargar_datos(ruta_archivo):
    """Carga datos desde un archivo JSON. Retorna una lista vacía si el archivo no existe o está vacío/corrupto."""
    if os.path.exists(ruta_archivo):
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                if contenido:
                    return json.loads(contenido)
                else:
                    return [] # El archivo existe pero está vacío
        except json.JSONDecodeError:
            print(f"Advertencia: Archivo JSON corrupto o vacío en {ruta_archivo}. Retornando lista vacía.")
            return [] # Archivo mal formado
    return [] # El archivo no existe

def guardar_datos(datos, ruta_archivo):
    """Guarda datos (una lista) en un archivo JSON."""
    # Asegúrate de que el directorio exista antes de intentar guardar
    directorio = os.path.dirname(ruta_archivo)
    if not os.path.exists(directorio):
        os.makedirs(directorio) # Crea el directorio si no existe

    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)