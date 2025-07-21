# Copilot Instructions for inventario

## Visión general

Este proyecto es una aplicación Flask para la gestión de inventario de equipos, organizada por módulos. Cada módulo es un archivo JSON en `modulos/` que almacena una lista de equipos. La aplicación permite crear, editar, eliminar y listar módulos y equipos, así como mostrar estadísticas básicas.

## Estructura y componentes clave

- `routes/modulos.py`: Define las rutas Flask para operaciones CRUD sobre módulos y equipos. Toda la lógica de negocio principal está aquí.
- `modulos/`: Carpeta donde cada archivo JSON representa un módulo con su inventario.
- `utils/helpers.py`: Funciones para cargar y guardar datos en JSON.
- `templates/`: Plantillas HTML para la interfaz web.

## Patrones y convenciones

- **Persistencia**: Cada módulo es un archivo JSON independiente. No se usa base de datos relacional.
- **Identificador de equipo**: El campo `numero` es único por módulo y se reenumera tras eliminaciones.
- **Campos de equipo**: Los equipos tienen campos fijos: `tipo`, `serial`, `marca`, `modelo`, `comentario`, `procesador`, `almacenamiento`, `ram`, `codigo`, `numero`.
- **Edición**: Al editar, todos los campos excepto `numero` se actualizan desde el formulario.
- **Mensajes**: Se usa `flash` de Flask para notificaciones tras operaciones.
- **Estadísticas**: Al mostrar un módulo, se calculan conteos de tipos, marcas, equipos con comentarios y los últimos registrados.

## Ejemplo de flujo de edición

```python
for equipo in equipos:
    if equipo['numero'] == numero:
        for campo in equipo:
            if campo != "numero":
                equipo[campo] = request.form.get(campo)
        break
guardar_datos(equipos, ruta)
```

## Flujos de desarrollo

- Ejecuta la app con `flask run` desde la raíz.
- Instala dependencias con `pip install flask` y las que estén en `requirements.txt`.
- Los módulos se crean desde la interfaz; si no existen, se inicializan como `[]`.

## Integraciones

- Solo dependencias estándar de Python y Flask.
- No hay integración con bases de datos externas ni servicios de terceros.

## Archivos clave

- `routes/modulos.py`: Lógica principal.
- `modulos/`: Datos de inventario.
- `utils/helpers.py`: Utilidades de persistencia.

---

¿Hay algún flujo, convención o integración que deba detallarse más?
