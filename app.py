# app.py

from flask import Flask, render_template, redirect, url_for, flash, request
from datetime import datetime
from modelo import db, Producto, Usuario, Cliente
from formulario import ProductoForm, ClienteForm, RegistroForm, LoginForm, UsuarioForm
from sqlalchemy import text
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/urbanwalk_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, inicia sesión para acceder."
login_manager.init_app(app)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

with app.app_context():
    db.create_all()


# === RUTAS PRINCIPALES ===

@app.route('/')
def index():
    return render_template('index.html', title='UrbanWalk')

@app.route('/about')
def about():
    return render_template('about.html', title='Acerca de')

@app.route('/contacto')
@app.route('/contacto/')
def contacto():
    return render_template('contacto.html', title='Contáctanos')

# === PRODUCTOS (CRUD) ===

@app.route('/productos')
@login_required  # 👈 Solo usuarios logueados
def listar_productos():
    q = request.args.get('q', '').strip()
    query = Producto.query
    if q:
        query = query.filter(Producto.nombre.contains(q))
    productos = query.all()
    return render_template('productos/lista.html', productos=productos, q=q)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required  # 👈 Solo usuarios logueados
def crear_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        if Producto.query.filter_by(nombre=form.nombre.data).first():
            flash('❌ Ya existe un producto con ese nombre.', 'danger')
        else:
            nuevo = Producto(
                nombre=form.nombre.data,
                cantidad=form.cantidad.data,
                precio=form.precio.data
            )
            try:
                db.session.add(nuevo)
                db.session.commit()
                flash('✅ Producto creado correctamente.', 'success')
                return redirect(url_for('listar_productos'))
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Error al guardar: {str(e)}', 'danger')
    return render_template('productos/formulario.html', form=form, modo='crear')

@app.route('/productos/<int:id>/editar', methods=['GET', 'POST'])
@login_required  # 👈 Solo usuarios logueados
def editar_producto(id):
    prod = Producto.query.get_or_404(id)
    form = ProductoForm(obj=prod)
    if form.validate_on_submit():
        if form.nombre.data != prod.nombre and Producto.query.filter_by(nombre=form.nombre.data).first():
            flash('❌ Nombre duplicado.', 'danger')
        else:
            prod.nombre = form.nombre.data
            prod.cantidad = form.cantidad.data
            prod.precio = form.precio.data
            try:
                db.session.commit()
                flash('✅ Actualizado.', 'success')
                return redirect(url_for('listar_productos'))
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Error: {str(e)}', 'danger')
    return render_template('productos/formulario.html', form=form, modo='editar')

@app.route('/productos/<int:id>/eliminar', methods=['POST'])
@login_required  # 👈 Solo usuarios logueados
def eliminar_producto(id):
    prod = Producto.query.get_or_404(id)
    try:
        db.session.delete(prod)
        db.session.commit()
        flash(f'✅ "{prod.nombre}" eliminado.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ No se pudo eliminar: {str(e)}', 'danger')
    return redirect(url_for('listar_productos'))

# === LOGIN Y REGISTRO ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'👋 Bienvenido, {user.nombre}!', 'success')
            return redirect(request.args.get('next') or url_for('index'))
        flash('❌ Email o contraseña inválidos.', 'danger')
    return render_template('usuarios/login.html', form=form)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistroForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('❌ Este email ya está registrado.', 'danger')
        else:
            hashed = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            user = Usuario(nombre=form.nombre.data, email=form.email.data, password=hashed,)
            try:
                db.session.add(user)
                db.session.commit()
                flash('✅ Registro exitoso. Inicia sesión.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('❌ Error al registrar.', 'danger')
    return render_template('usuarios/registro.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('👋 Sesión cerrada.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Panel')

@app.route('/usuarios')
@login_required # 👈 Solo usuarios logueados
def listar_usuarios():
    
    page = request.args.get('page', 1, type=int)

    # Paginar: 5 usuarios por página
    pagination = Usuario.query.paginate(
        page=page,
        per_page=5,
        error_out=False  # No lanza error si la página no existe
    )
    
    usuarios = pagination.items
    return render_template('usuarios/lista.html',
                         title='Usuarios del Sistema',
                         usuarios=usuarios,
                         pagination=pagination)
    
    # === EDITAR USUARIO ===
@app.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required # 👈 Solo usuarios logueados
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    form = UsuarioForm(obj=usuario)

    # No llenar el campo de contraseña si no se cambia
    if request.method == 'GET':
        form.password.data = ''  # Limpiar para seguridad visual

    if form.validate_on_submit():
        # Verificar si el email ya existe (y no es el mismo usuario)
        if form.email.data != usuario.email:
            if Usuario.query.filter_by(email=form.email.data).first():
                flash('❌ Ya existe un usuario con ese correo.', 'danger')
                return render_template('usuarios/formulario.html', form=form, modo='editar', title='Editar Usuario')

        # Actualizar datos
        usuario.nombre = form.nombre.data
        usuario.email = form.email.data

        # Solo actualizar contraseña si fue ingresada
        if form.password.data: # Solo si se agrego algo
            usuario.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        try:
            db.session.commit()
            flash('✅ Usuario actualizado correctamente.', 'success')
            return redirect(url_for('listar_usuarios'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar: {str(e)}', 'danger')

    return render_template('usuarios/formulario.html', form=form, modo='editar', title='Editar Usuario')


# === ELIMINAR USUARIO ===
@app.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required # 👈 Solo usuarios logueados
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    # No puedes eliminarte a ti mismo
    if current_user.id_usuario == id:
        flash('❌ No puedes eliminarte a ti mismo.', 'warning')
        return redirect(url_for('listar_usuarios'))

    nombre = usuario.nombre
    try:
        db.session.delete(usuario)
        db.session.commit()
        flash(f'✅ Usuario "{nombre}" eliminado.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ No se pudo eliminar el usuario: {str(e)}', 'danger')

    return redirect(url_for('listar_usuarios'))


# === EJECUCIÓN ===

if __name__ == '__main__':
    app.run(debug=True)