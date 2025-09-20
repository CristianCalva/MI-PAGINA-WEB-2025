# modelo.py

from math import e
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    precio = db.Column(db.Float, nullable=False, default=0.0)  # para demo

    def __repr__(self):
        return f'<Producto {self.id} {self.nombre}>'

    def to_tuple(self):
        # ejemplo de tupla: (id, nombre, cantidad, precio)
        return (self.id, self.nombre, self.cantidad, self.precio)
    
class Cliente(db.Model):
        __tablename__ = 'Cliente'
        id_cliente = db.Column(db.Integer, primary_key=True)
        nombre = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), nullable=False, unique=True)
        telefono = db.Column(db.String(20), nullable=True)

        def __repr__(self):
            return f'<Cliente {self.id_cliente} {self.nombre}>'

        def to_tuple(self):
            # ejemplo de tupla: (id_cliente, nombre, email)
            return (self.id_cliente, self.nombre, self.email)


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)  # hashed password

    @property
    def id(self):
        return self.id_usuario

    def __repr__(self):
        return f'<Usuario {self.id_usuario} {self.nombre}>'

    def to_tuple(self):
        return (self.id_usuario, self.nombre, self.email)