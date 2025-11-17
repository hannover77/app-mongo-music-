from bson import ObjectId

def to_object_id(value):
    """Convierte string a ObjectId, o retorna None si no es válido"""
    if isinstance(value, ObjectId):
        return value
    try:
        return ObjectId(str(value))
    except Exception:
        return None

def parse_bool(value):
    """Convierte valores a booleano"""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).lower() in ["true", "1", "on", "yes", "si"]

# Normalizadores por colección
def normalize_artista(form, custom_id=None):
    """Normaliza datos de artista. Opcionalmente acepta un ID personalizado"""
    doc = {
        "nombre": form.get("nombre", "").strip(),
        "pais": form.get("pais", "").strip(),
        "genero": form.get("genero", "").strip(),
        "activo": parse_bool(form.get("activo"))
    }
    if custom_id:
        doc["_id"] = to_object_id(custom_id)
    return doc

def normalize_cliente(form, custom_id=None):
    """Normaliza datos de cliente. Opcionalmente acepta un ID personalizado"""
    doc = {
        "nombre": form.get("nombre", "").strip(),
        "correo": form.get("correo", "").strip(),
        "telefono": form.get("telefono", "").strip(),
    }
    if custom_id:
        doc["_id"] = to_object_id(custom_id)
    return doc

def normalize_inventario(form, custom_id=None):
    """Normaliza datos de inventario. Opcionalmente acepta un ID personalizado"""
    doc = {
        "artista_id": to_object_id(form.get("artista_id")),
        "nombre_artista": form.get("nombre_artista", "").strip(),
        "album": form.get("album", "").strip(),
        "año": int(form.get("año")),
        "genero": form.get("genero", "").strip(),
        "stock": int(form.get("stock")),
        "precio_unitario": int(form.get("precio_unitario")),
    }
    if custom_id:
        doc["_id"] = to_object_id(custom_id)
    return doc

def normalize_venta(form, custom_id=None):
    """Normaliza datos de venta. Opcionalmente acepta un ID personalizado"""
    doc = {
        "cliente_id": to_object_id(form.get("cliente_id")),
        "nombre_cliente": form.get("nombre_cliente", "").strip(),
        "artista_id": to_object_id(form.get("artista_id")),
        "nombre_artista": form.get("nombre_artista", "").strip(),
        "album": form.get("album", "").strip(),
        "fecha_venta": form.get("fecha_venta", "").strip(),
        "cantidad": int(form.get("cantidad")),
        "precio_unitario": int(form.get("precio_unitario")),
    }
    if custom_id:
        doc["_id"] = to_object_id(custom_id)
    return doc

# ========== AUTENTICACIÓN Y ROLES ==========

USUARIOS = {
    "ldaza": {
        "password": "admin123",
        "rol": "administrador",
        "nombre": "Luis Daza"
    },
    "sbarbosa": {
        "password": "consulta123",
        "rol": "consulta",
        "nombre": "Sebastian Barbosa"
    },
    "dandrade": {
        "password": "operativo123",
        "rol": "operativo",
        "nombre": "Daniel Andrade"
    }
}

ROLES = {
    "administrador": {
        "permisos": ["find", "insert", "update", "remove"],
        "descripcion": "Acceso completo a CRUD - Consulta, crear, editar y eliminar"
    },
    "consulta": {
        "permisos": ["find"],
        "descripcion": "Solo lectura - Solo puede consultar datos"
    },
    "operativo": {
        "permisos": ["find", "insert"],
        "descripcion": "Lectura e inserción - Puede consultar y crear datos"
    }
}

def validar_usuario(usuario, password):
    """
    Valida credenciales de usuario.
    
    Args:
        usuario: nombre de usuario
        password: contraseña
    
    Returns:
        dict: Información del usuario si es válido, None si no
    """
    if usuario in USUARIOS:
        if USUARIOS[usuario]["password"] == password:
            return USUARIOS[usuario]
    return None

def obtener_rol(usuario):
    """
    Obtiene información del rol del usuario.
    
    Args:
        usuario: nombre de usuario
    
    Returns:
        dict: Permisos y descripción del rol
    """
    if usuario in USUARIOS:
        rol = USUARIOS[usuario]["rol"]
        return ROLES.get(rol, {})
    return {}

def tiene_permiso(usuario, permiso):
    """
    Verifica si un usuario tiene permiso para una acción.
    
    Args:
        usuario: nombre de usuario
        permiso: permiso a verificar (find, insert, update, remove)
    
    Returns:
        bool: True si tiene permiso, False si no
    """
    if usuario not in USUARIOS:
        return False
    
    rol = USUARIOS[usuario]["rol"]
    permisos = ROLES.get(rol, {}).get("permisos", [])
    return permiso in permisos
