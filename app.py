#Aplicación en Flask
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '¡Hola! Bienvenido a mi aplicación Flask.'

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

@app.route('/acerca',strict_slashes=False)
def acerca():
    return "Este es una aplicación de ejemplo Flask"

@app.route('/contacto')
def contacto():
    return "Contactate con nosotros en paulcalva95"

if __name__ == '__main__':
    app.run(debug=True)
