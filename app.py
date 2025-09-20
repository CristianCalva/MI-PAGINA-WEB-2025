from math import e
from pydoc import text
from sys import version
from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
from modelo import db, Producto, Usuario, Cliente
from formulario import ProductoForm, ClienteForm, UsuarioForm, RegistroForm, LoginForm
from sqlalchemy import text
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Crear la app
app = Flask(__name__)

# Configuración de la base de datos (usa PyMySQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/urbanwalk_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'
# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.init_app(app)

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
@app.route('/contacto')
@app.route('/contacto/')
def contacto():
    return render_template('contacto.html', title='Contáctanos')

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
        
        
# Cargar Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id)) #buscar por ID     

# funcion login usuario

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and check_password_hash(usuario.password, form.password.data):
            login_user(usuario)
            flash(f'Bienvenido, {usuario.nombre}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales inválidas. Intenta de nuevo.', 'danger')
    return render_template('usuarios/login.html', title='Iniciar Sesión', form=form)

# funcion registrar usuario nuevo

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistroForm()
    if form.validate_on_submit():
        try:
            # ✅ Verificar si el correo ya existe
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('❌ Ya existe un usuario con ese correo.', 'danger')
            else:
                # ✅ Encriptar contraseña solo si fue ingresada
                password_hash = None
                if form.password.data:
                    password_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')

                nuevo_usuario = Usuario(
                    nombre=form.nombre.data,
                    email=form.email.data,
                    password=password_hash
                )

                db.session.add(nuevo_usuario)
                db.session.commit()  # ⚠️ Aquí puede fallar

                flash('✅ Registro exitoso. Puedes iniciar sesión.', 'success')
                return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()  # ← ¡Importante!
            print(f"Error al registrar usuario: {e}")  # Para depurar
            flash('❌ Ocurrió un error inesperado. Inténtalo más tarde.', 'danger')

    return render_template('usuarios/registro.html', title='Crear Cuenta', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Panel de Control')

@app.route('/usuarios')
@login_required  # Opcional: solo si quieres que solo usuarios logueados vean esta página
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios/lista.html', title='Usuarios', usuarios=usuarios)

@app.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))





# --- EJECUCIÓN ---
if __name__ == '__main__':
    app.run(debug=True)