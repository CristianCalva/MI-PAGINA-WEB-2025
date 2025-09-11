from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    cantidad = StringField('Cantidad', validators=[DataRequired()])
    precio = StringField('Precio', validators=[DataRequired()])
    submit = SubmitField('Guardar')