from flask import Flask
from routes.inventario import inventario_bp
from routes.modulos import modulos_bp

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Registrar los módulos
app.register_blueprint(inventario_bp)
app.register_blueprint(modulos_bp)

if __name__ == '__main__':
    app.run(debug=True)
