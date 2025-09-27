# formulario.py

from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, IntegerField, FloatField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length, NumberRange, Optional as WtOptional)

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="El nombre es obligatorio.")])
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(message="La cantidad es obligatoria."),
        NumberRange(min=0, message="No puede ser negativo.")
    ])
    precio = FloatField('Precio', validators=[
        DataRequired(message="El precio es obligatorio."),
        NumberRange(min=0.0, message="No puede ser negativo.")
    ])
    submit = SubmitField('Guardar')

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono')
    submit = SubmitField('Guardar')

class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir.')
    ])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class UsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message="El nombre es obligatorio.")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    # Solo requiere longitud si se ingresa algo
    password = PasswordField(
        'Nueva Contraseña (opcional)',
        validators=[
            WtOptional(),           # No es obligatorio
            Length(min=6, message="La contraseña debe tener al menos 6 caracteres.")
        ]
    )
    submit = SubmitField('Guardar')