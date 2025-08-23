#Aplicación en Flask
from turtle import title
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def indexfl():
    #return '¡Hola! Bienvenido a mi aplicación Flask.'
    return render_template('index.html', title='Inicio') 

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

@app.route('/about')
def about():
    #return "Este es una aplicación de ejemplo Flask"
    return render_template('about.html', title='Aserca de') 


@app.route('/contacto')
def contacto():
    return "Contactate con nosotros en paulcalva95"

if __name__ == '__main__':
    app.run(debug=True)
