from pydoc import text
from sys import version
from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
from modelo import db, Producto
from formulario import ProductoForm
from sqlalchemy import text
import os

# Crear la app
app = Flask(__name__)

# Configuración de la base de datos (usa PyMySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/urbanwalk_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'

# Inicializar SQLAlchemy
db.init_app(app)

# Inyectar variable 'now' para usar en plantillas
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

# Crear tablas al iniciar
with app.app_context():
    db.create_all()

# --- RUTAS PRINCIPALES ---

# Página de inicio
@app.route('/')
def index():
    return render_template('index.html', title='Inicio')

# Lista de productos
@app.route('/productos')
def listar_productos():
    productos = Producto.query.all()
    return render_template('productos/lista.html', title='Productos', productos=productos)

# Crear producto
@app.route('/productos/nuevo', methods=['GET', 'POST'])
def crear_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        try:
            nuevo_producto = Producto(
                nombre=form.nombre.data,
                cantidad=form.cantidad.data,
                precio=form.precio.data
            )
            db.session.add(nuevo_producto)
            db.session.commit()
            flash('Producto agregado correctamente.', 'success')
            return redirect(url_for('listar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'danger')
            # No retornamos aquí, queremos mostrar el formulario con errores

    return render_template('productos/formulario.html', title='Nuevo Producto', form=form)
            
@app.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)

    if form.validate_on_submit():
        try:
            producto.nombre = form.nombre.data
            producto.cantidad = form.cantidad.data
            producto.precio = form.precio.data
            db.session.commit()
            flash('✅ Producto actualizado correctamente.', 'success')
            return redirect(url_for('listar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}', 'danger')

    return render_template('productos/formulario.html', title='Editar Producto', form=form)
    
    # Si hay error o es GET, muestra formulario
    return render_template('productos/formulario.html', title='Nuevo Producto', form=form)

# Eliminar producto
@app.route('/productos/<int:id>/eliminar', methods=['POST'])
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        flash('Producto eliminado.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar: {str(e)}', 'danger')
    return redirect(url_for('listar_productos'))

# Acerca de
@app.route('/about/')
def about():
    return render_template('about.html', title='Acerca de')

# Contacto
@app.route('/contacto/')
def contacto():
    return "Contactate con nosotros en @UrbanWalk"

# Prueba de conexión (opcional)
@app.route('/test-mysql-connection')
def test_mysql_connection():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION();"))
            version = result.scalar()
            return f"Conexión exitosa a MySQL: {version}"
    except Exception as e:
            return f"Error de conexión a MySQL: {str(e)}"

# --- EJECUCIÓN ---
if __name__ == '__main__':
    app.run(debug=True)