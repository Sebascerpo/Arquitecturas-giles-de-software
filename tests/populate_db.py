from faker import Faker
import requests

NO_CLIENTES = 300
NO_REGISTROS_POR_CLIENTE = 20

CANALES_HOST = "localhost"
CANALES_PORT = "5002"

CREAR_CLIENTE_URL = f"http://{CANALES_HOST}:{CANALES_PORT}/cliente"
CREAR_REGISTRO_CANAL_URL = f"http://{CANALES_HOST}:{CANALES_PORT}/canal"

fake = Faker()

def crear_cliente():
    nombre = fake.name()
    tipo_servicio = fake.random_element(elements=("TV", "Internet", "Telefonía", "Móvil", "Crédito", "Seguros", "Energía"))
    data = {
        "nombre": nombre,
        "tipo_servicio": tipo_servicio
    }
    response = requests.post(CREAR_CLIENTE_URL, json=data)
    if response.status_code == 201:
        print(f"Cliente creado: {nombre}")
    else:
        print(f"Error al crear cliente: {response.json()}")

def crear_registros_canal(cliente_id):
    for _ in range(NO_REGISTROS_POR_CLIENTE):
        tipo = fake.random_element(elements=("email", "llamada"))
        contenido = fake.text()
        data = {
            "tipo": tipo,
            "contenido": contenido,
            "cliente_id": cliente_id
        }
        response = requests.post(CREAR_REGISTRO_CANAL_URL, json=data)
        if response.status_code == 201:
            print(f"Registro de canal creado para cliente {cliente_id}")
        else:
            print(f"Error al crear registro de canal: {response.json()}")

def populate_db():
    for _ in range(NO_CLIENTES):
        crear_cliente()

    clientes = requests.get(f"http://{CANALES_HOST}:{CANALES_PORT}/clientes").json()
    for cliente in clientes:
        cliente_id = cliente["id"]
        crear_registros_canal(cliente_id)

if __name__ == "__main__":
    populate_db()
