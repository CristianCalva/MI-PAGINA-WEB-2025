#Aplicación en Flask
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '¡Hola! Bienvenido a mi aplicación Flask.'

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

@app.route('/contacto')
def contacto():
    return "Contacta con nosotros en contacto@midominio.com"

@app.route('/acerca')
def acerca():
    return "Esta es una aplicación de ejemplo desarrollada en Flask."


if __name__ == '__main__':
    app.run(debug=True)
