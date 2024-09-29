import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.orm import relationship
from hashlib import md5
import signal

app = Flask(__name__)

# PostgreSQL configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@postgres:5432/{os.getenv('POSTGRES_DB', 'my_db')}"
)

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Get the secret key from the environment
HASH_SECRET_KEY = os.getenv("HASH_SECRET_KEY")


class Cliente(db.Model):
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    tipo_servicio = Column(String(50), nullable=False)
    hash = Column(String(32), nullable=False)
    canales = relationship("Canal", backref="cliente", lazy=True)


class Canal(db.Model):
    id = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    contenido = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    hash = Column(String(32), nullable=False)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route("/cliente", methods=["POST"])
def registrar_cliente():
    data = request.json
    nombre = data.get("nombre")
    tipo_servicio = data.get("tipo_servicio")

    if not nombre or not tipo_servicio:
        return jsonify({"mensaje": "Nombre y tipo de servicio son obligatorios"}), 400

    nuevo_cliente = Cliente(nombre=nombre, tipo_servicio=tipo_servicio)

    data_string = f"{nombre}{tipo_servicio}"
    nuevo_cliente.hash = generate_hash(data_string, HASH_SECRET_KEY)

    try:
        db.session.add(nuevo_cliente)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"mensaje": "Error al registrar cliente"}), 500

    return jsonify({"mensaje": "Cliente registrado exitosamente"}), 201


@app.route("/clientes", methods=["GET"])
def obtener_clientes():
    clientes = Cliente.query.all()

    if not clientes:
        return jsonify({"mensaje": "No hay clientes registrados"}), 404

    resultado = [
        {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "tipo_servicio": cliente.tipo_servicio,
        }
        for cliente in clientes
    ]

    return jsonify(resultado), 200


@app.route("/canal", methods=["POST"])
def recibir_canal():
    data = request.json
    tipo = data.get("tipo")
    contenido = data.get("contenido")
    cliente_id = data.get("cliente_id")

    if tipo not in ["email", "llamada"]:
        return jsonify({"mensaje": "Tipo de canal inválido"}), 400

    if not contenido or not cliente_id:
        return jsonify({"mensaje": "Contenido y cliente_id son obligatorios"}), 400

    try:
        cliente_id = int(cliente_id)
    except ValueError:
        return jsonify({"mensaje": "cliente_id debe ser un número"}), 400

    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"mensaje": f"El cliente con id {cliente_id} no existe"}), 404

    nuevo_canal = Canal(tipo=tipo, contenido=contenido, cliente_id=cliente_id)

    data_string = f"{tipo}{contenido}{cliente_id}"
    nuevo_canal.hash = generate_hash(data_string, HASH_SECRET_KEY)

    try:
        db.session.add(nuevo_canal)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"mensaje": "Error al guardar la información"}), 500

    return jsonify({"mensaje": "Información recibida exitosamente"}), 201


@app.route("/mensajes/<string:tipo_canal>", methods=["GET"])
def obtener_mensajes_por_tipo(tipo_canal):
    if tipo_canal not in ["email", "llamada"]:
        return jsonify({"mensaje": "Tipo de canal inválido"}), 400

    canales = Canal.query.filter_by(tipo=tipo_canal).all()

    if not canales:
        return (
            jsonify(
                {"mensaje": f"No hay mensajes para el tipo de canal '{tipo_canal}'"}
            ),
            404,
        )

    resultado = [
        {
            "id": canal.id,
            "tipo": canal.tipo,
            "contenido": canal.contenido,
            "timestamp": canal.timestamp.isoformat(),
            "cliente_id": canal.cliente_id,
        }
        for canal in canales
    ]

    return jsonify(resultado), 200


@app.route("/canales/<int:cliente_id>", methods=["GET"])
def obtener_canales(cliente_id):
    canales = Canal.query.filter_by(cliente_id=cliente_id).all()
    if not canales:
        return jsonify({"mensaje": "No hay canales registrados para este cliente"}), 404

    resultado = [
        {
            "id": c.id,
            "tipo": c.tipo,
            "contenido": c.contenido,
            "timestamp": c.timestamp.isoformat(),
        }
        for c in canales
    ]
    return jsonify(resultado), 200


@app.route("/test-error", methods=["GET"])
def test_error():
    raise Exception("Esto es una simulación de error interno")


@app.route('/stopServer', methods=['GET'])
def stopServer():
    os.kill(os.getpid(), signal.SIGINT)
    return jsonify({"success": True, "message": "Server is shutting down..."})


def create_tables():
    db.create_all()


def generate_hash(data_string, key):
    hash_string = data_string + key
    return md5(hash_string.encode()).hexdigest()


if __name__ == "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True, host="0.0.0.0")
