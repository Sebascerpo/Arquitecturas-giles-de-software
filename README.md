# Microservicio de Gestión de Clientes y Canales de Comunicación

Este microservicio está diseñado para gestionar clientes y sus canales de comunicación ya sea correos electrónicos o llamadas. Utiliza Flask para el framework web y SQLAlchemy para la gestión de la base de datos con SQLite.

## Configuración

### Requisitos

- Python 3.x
- Flask
- Flask==2.3.0
- Flask-SQLAlchemy==3.0.0

### Instalación

1. Clona este repositorio o descarga el código fuente.

2. Crea un entorno virtual:

```bash
   python -m venv venv
   source venv/bin/activate (en mac)
   venv\Scripts\activate (en windows) 
```
3. Ejecuta la aplicacion:

```bash
flask run
```

# Documentación API

## Endpoints

### 1. Estado de salud

**URL:** `/health`  
**Method:** `GET`

#### Descripción:
Este endpoint verifica el estado de salud del servicio y devuelve un mensaje que indica si el servicio está funcionando correctamente.

#### Respuesta:
- **Status Code:** `200 OK`
- **Body:**
    ```json
    {
        "status": "healthy"
    }
    ```

---

### 2. Registrar Cliente

**URL:** `/cliente`  
**Method:** `POST`

#### Descripción:
Este endpoint permite registrar un nuevo cliente en la base de datos.



#### Cuerpo Requerido:
Debe ser un JSON con los siguientes campos:

- `nombre`: El nombre del cliente (requerido).
- `tipo_servicio`: El tipo de servicio que se ofrece al cliente (requerido).

#### Cuerpo de muestra:
```json
{
    "nombre": "Juan Pérez",
    "tipo_servicio": "soporte"
}
```
### Respuesta:
- **Status Code:** `201 Created`
- **Body:**
    ```json
    {
        "mensaje": "Cliente registrado exitosamente"
    }
    ```

### Respuesta:

- **Status Code:** `400 Bad Request`

- **Body:**
    ```json
    {
        "mensaje": "Nombre y tipo de servicio son obligatorios"
    }
    ```

### Respuesta:

- **Status Code:** ` 500 Internal Server Error`

- **Body:**
    ```json
    {
        "mensaje": "Error al registrar cliente"
    }
    ```


### 3. Obtener Clientes

**URL:** `/clientes`  
**Method:** `GET`

#### Descripción:
Este endpoint obtiene la lista de todos los clientes registrados en la base de datos.

#### Respuesta:
- **Status Code:** `200 OK`
- **Body:**
    ```json
    [
        {
            "id": 1,
            "nombre": "Juan Pérez",
            "tipo_servicio": "soporte"
        },
        {
            "id": 2,
            "nombre": "Ana Gómez",
            "tipo_servicio": "consultoría"
        }
        // ... más clientes
    ]
    ```

#### Respuesta:
- **Status Code:** `404 Not Found`
- **Body:**
    ```json
    {
        "mensaje": "No hay clientes registrados"
    }
    ```



### 4. Recibir Canal

**URL:** `/canal`  
**Method:** `POST`

#### Descripción:
Este endpoint permite registrar un nuevo canal de comunicación (correo electrónico o llamada) para un cliente.

#### Cuerpo requerido:
Debe ser un JSON con los siguientes campos:

- `tipo`: El tipo de canal (debe ser "email" o "llamada", requerido).
- `contenido`: El contenido del canal (requerido).
- `cliente_id`: El ID del cliente al que se asigna el canal (debe ser un número entero, requerido).

#### Cuerpo de muestra:
```json
{
    "tipo": "email",
    "contenido": "Correo de prueba",
    "cliente_id": 1
}
```

#### Respuestas:

- **Status Code:** `201 Created`
- **Body:**
    ```json
    {
        "mensaje": "Información recibida exitosamente"
    }
    ```

#### Respuestas:

- **Status Code:** `400 Bad Request`
- **Body:**
    ```json
    {
        "mensaje": "Tipo de canal inválido"
    }
    ```
- **Body:**
  ```json
    {
        "mensaje": "Contenido y cliente_id son obligatorios"
    }
    ```
- **Body:**
  ```json
    {
        "mensaje": "cliente_id debe ser un número"
    }
    ```

- **Body:**
  ```json
    {
        "mensaje": "El cliente con id {cliente_id} no existe"
    }
    ```

- **Status Code:** `500 Internal Server Error`
- **Body:**
    ```json
    {
        "mensaje": "Error al guardar la información"
    }
    ```

### 5. Obtener Mensajes por Tipo

**URL:** `/mensajes/<string:tipo_canal>`  
**Method:** `GET`

#### Descripción:
Este endpoint permite obtener todos los mensajes para un tipo específico de canal (por ejemplo, "email" o "llamada"). 

#### Parametros de la URL:
- `tipo_canal`: El tipo de canal para el cual se desean obtener los mensajes. Puede ser "email" o "llamada".

#### Respuesta:
- **Status Code:** `200 OK`
- **Body:**
    ```json
    [
        {
            "id": 1,
            "tipo": "email",
            "contenido": "Contenido del mensaje",
            "timestamp": "2024-09-08T12:34:56",
            "cliente_id": 2
        },
        {
            "id": 2,
            "tipo": "email",
            "contenido": "Otro contenido",
            "timestamp": "2024-09-08T13:45:67",
            "cliente_id": 3
        }
    ]
    ```

- **Status Code:** `400 Bad Request`
  - **Body:**
    ```json
    {
        "mensaje": "Tipo de canal inválido"
    }
    ```

- **Status Code:** `404 Not Found`
  - **Body:**
    ```json
    {
        "mensaje": "No hay mensajes para el tipo de canal 'tipo_canal'"
    }
    ```


### 6. Obtener Canales por Cliente

**URL:** `/canales/<int:cliente_id>`  
**Method:** `GET`

#### Descripción:
Este endpoint permite obtener todos los canales registrados para un cliente específico.

#### Parametros URL:
- `cliente_id`: El ID del cliente para el cual se desean obtener los canales.

#### Respuesta:
- **Status Code:** `200 OK`
- **Body:**
    ```json
    [
        {
            "id": 1,
            "tipo": "email",
            "contenido": "Contenido del canal",
            "timestamp": "2024-09-08T12:34:56"
        },
        {
            "id": 2,
            "tipo": "llamada",
            "contenido": "Otro contenido",
            "timestamp": "2024-09-08T13:45:67"
        }
    ]
    ```

- **Status Code:** `404 Not Found`
  - **Body:**
    ```json
    {
        "mensaje": "No hay canales registrados para este cliente"
    }
    ```

### 7. Probar Servidor Caido

**URL:** `/test-error`  
**Method:** `GET`

#### Descripción:
Este endpoint simula un error interno del servidor para probar la gestión de errores en la aplicación.

#### Respuesta:
- **Status Code:** `500 Internal Server Error`
  - **Body:**
    ```json
    {
        "mensaje": "Error interno del servidor"
    }
    ```
