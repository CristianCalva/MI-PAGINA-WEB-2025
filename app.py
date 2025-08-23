from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='Inicio')

@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/contacto')
def contacto():
    return "Contáctate con nosotros en paulcalva95"

if __name__ == '__main__':
    app.run(debug=True)
