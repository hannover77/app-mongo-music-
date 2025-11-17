# 🔐 SISTEMA DE AUTENTICACIÓN Y CONTROL DE ROLES

## ✅ IMPLEMENTACIÓN COMPLETADA

Se ha implementado un sistema completo de autenticación con 3 roles predefinidos con permisos específicos para cada uno.

---

## 🎯 ESTRUCTURA DE ROLES

### 1️⃣ Rol "ADMINISTRADOR"
**Usuario:** `ldaza`  
**Contraseña:** `admin123`  
**Nombre:** Luis Daza

**Permisos:**
- ✅ **find** - Consultar/Listar datos
- ✅ **insert** - Crear nuevos registros
- ✅ **update** - Editar registros existentes
- ✅ **remove** - Eliminar registros

**Acceso:** Todas las funciones CRUD completas

---

### 2️⃣ Rol "CONSULTA"
**Usuario:** `sbarbosa`  
**Contraseña:** `consulta123`  
**Nombre:** Samuel Barbosa

**Permisos:**
- ✅ **find** - Consultar/Listar datos
- ❌ **insert** - No puede crear
- ❌ **update** - No puede editar
- ❌ **remove** - No puede eliminar

**Acceso:** Solo lectura de datos

---

### 3️⃣ Rol "OPERATIVO"
**Usuario:** `dandrade`  
**Contraseña:** `operativo123`  
**Nombre:** Daniel Andrade

**Permisos:**
- ✅ **find** - Consultar/Listar datos
- ✅ **insert** - Crear nuevos registros
- ❌ **update** - No puede editar
- ❌ **remove** - No puede eliminar

**Acceso:** Lectura e inserción de datos

---

## 🔑 CREDENCIALES RÁPIDAS

```
┌─────────────────────────────────────────────────────────────────┐
│ ADMINISTRADOR                                                   │
├─────────────────────────────────────────────────────────────────┤
│ Usuario: ldaza                                                  │
│ Contraseña: admin123                                            │
│ Acceso: Consulta, Crear, Editar, Eliminar (ACCESO COMPLETO)    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CONSULTA (LECTURA)                                              │
├─────────────────────────────────────────────────────────────────┤
│ Usuario: sbarbosa                                               │
│ Contraseña: consulta123                                         │
│ Acceso: Solo ver datos (LECTURA)                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ OPERATIVO                                                       │
├─────────────────────────────────────────────────────────────────┤
│ Usuario: dandrade                                               │
│ Contraseña: operativo123                                        │
│ Acceso: Ver y crear datos (LECTURA + INSERCIÓN)                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 MATRIZ DE PERMISOS

| Operación | Administrador | Consulta | Operativo |
|-----------|:-------------:|:--------:|:---------:|
| **Listar (find)** | ✅ | ✅ | ✅ |
| **Ver Detalle (find)** | ✅ | ✅ | ✅ |
| **Crear (insert)** | ✅ | ❌ | ✅ |
| **Editar (update)** | ✅ | ❌ | ❌ |
| **Eliminar (remove)** | ✅ | ❌ | ❌ |
| **Acceso a Todos los Módulos** | ✅ | ✅ | ✅ |

---

## 🌍 MÓDULOS AFECTADOS

### Artistas
- **Listar** - Requiere permiso: `find`
- **Ver Detalle** - Requiere permiso: `find`
- **Crear** - Requiere permiso: `insert`
- **Editar** - Requiere permiso: `update`
- **Eliminar** - Requiere permiso: `remove`

### Clientes
- **Listar** - Requiere permiso: `find`
- **Ver Detalle** - Requiere permiso: `find`
- **Crear** - Requiere permiso: `insert`
- **Editar** - Requiere permiso: `update`
- **Eliminar** - Requiere permiso: `remove`

### Inventario
- **Listar** - Requiere permiso: `find`
- **Ver Detalle** - Requiere permiso: `find`
- **Crear** - Requiere permiso: `insert`
- **Editar** - Requiere permiso: `update`
- **Eliminar** - Requiere permiso: `remove`

### Ventas
- **Listar** - Requiere permiso: `find`
- **Ver Detalle** - Requiere permiso: `find`
- **Crear** - Requiere permiso: `insert`
- **Editar** - Requiere permiso: `update`
- **Eliminar** - Requiere permiso: `remove`

---

## 🔐 FLUJO DE AUTENTICACIÓN

```
1. Usuario accede a http://127.0.0.1:5000
   ↓
2. Sistema comprueba si hay sesión activa
   ↓
3a. Si NO hay sesión → Redirige a /login
3b. Si SÍ hay sesión → Permite acceso
   ↓
4. Usuario ingresa credenciales en formulario login
   ↓
5. Sistema valida credenciales contra diccionario USUARIOS
   ↓
6a. Si credenciales válidas → Crea sesión y redirige a index
6b. Si inválidas → Muestra error "Usuario o contraseña incorrectos"
   ↓
7. Usuario logueado navega por la aplicación
   ↓
8. Cada ruta CRUD valida:
   - ¿Usuario está en sesión?
   - ¿Usuario tiene permiso para esta acción?
   ↓
9a. Si permisos OK → Permite operación
9b. Si sin permiso → Muestra error "No tienes permiso"
   ↓
10. Usuario puede cerrar sesión con botón Logout
```

---

## 🛡️ SEGURIDAD IMPLEMENTADA

### En el Backend (`models.py`)
```python
def validar_usuario(usuario, password):
    # Verifica credenciales contra diccionario
    if usuario in USUARIOS:
        if USUARIOS[usuario]["password"] == password:
            return USUARIOS[usuario]
    return None

def tiene_permiso(usuario, permiso):
    # Verifica si usuario tiene permiso
    rol = USUARIOS[usuario]["rol"]
    permisos = ROLES[rol]["permisos"]
    return permiso in permisos
```

### En las Rutas (`app.py`)
```python
@permiso_requerido("find")  # Decorador que valida permisos
def artistas_list():
    # Ruta protegida
    pass
```

### En las Sesiones (Flask)
- Uso de sesiones encriptadas
- Token de sesión en cookies
- Logout limpia la sesión completamente

---

## 🎯 CÓMO USAR EL SISTEMA

### Paso 1: Acceder a la aplicación
```
http://127.0.0.1:5000
```

### Paso 2: Ingresa credenciales
Elige uno de los 3 usuarios disponibles:
- `ldaza` / `admin123` (Administrador)
- `sbarbosa` / `consulta123` (Consulta)
- `dandrade` / `operativo123` (Operativo)

### Paso 3: Usar según tu rol
- **Si eres Administrador:** Acceso completo a todo
- **Si eres Consulta:** Solo puedes ver datos
- **Si eres Operativo:** Puedes ver y crear datos

### Paso 4: Cerrar sesión
Haz clic en tu nombre (arriba derecha) → Cerrar Sesión

---

## 📋 LISTADO DE CAMBIOS

### Archivos Modificados
1. **models.py** - Agregadas funciones de autenticación y roles
2. **app.py** - Agregadas rutas de login/logout y decoradores de permisos
3. **base.html** - Agregado dropdown de usuario con información de rol
4. **index.html** - Agregada tarjeta informativa del rol del usuario

### Archivos Creados
1. **login.html** - Formulario de login con credenciales de prueba

---

## 🧪 PRUEBAS RECOMENDADAS

### Test 1: Login como Administrador
```
1. Acceder a http://127.0.0.1:5000
2. Usuario: ldaza, Contraseña: admin123
3. ✅ Deberías poder crear, editar y eliminar en todos los módulos
```

### Test 2: Login como Consulta
```
1. Acceder a http://127.0.0.1:5000
2. Usuario: sbarbosa, Contraseña: consulta123
3. ✅ Deberías poder solo consultar datos
4. ❌ Los botones crear, editar y eliminar deben estar deshabilitados o no permitir acción
```

### Test 3: Login como Operativo
```
1. Acceder a http://127.0.0.1:5000
2. Usuario: dandrade, Contraseña: operativo123
3. ✅ Deberías poder crear registros nuevos
4. ❌ Los botones editar y eliminar deben estar deshabilitados
```

### Test 4: Acceso no autorizado
```
1. Conecta como consulta (sbarbosa)
2. Intenta editar un registro
3. ❌ Deberías ver: "No tienes permiso para update"
```

### Test 5: Logout
```
1. Conéctate con cualquier usuario
2. Haz clic en tu nombre (arriba derecha)
3. Haz clic en "Cerrar Sesión"
4. ✅ Deberías volver al login
```

---

## 🔧 PERSONALIZACIÓN

### Agregar nuevo usuario
Edita `models.py`, sección `USUARIOS`:

```python
USUARIOS = {
    "mi_usuario": {
        "password": "mi_contraseña",
        "rol": "administrador",  # o "consulta" u "operativo"
        "nombre": "Mi Nombre"
    }
}
```

### Crear nuevo rol
Edita `models.py`, sección `ROLES`:

```python
ROLES = {
    "mi_rol": {
        "permisos": ["find", "insert"],  # Permisos que incluye
        "descripcion": "Mi rol personalizado"
    }
}
```

---

## 📊 RESUMEN

```
✅ Sistema de autenticación: IMPLEMENTADO
✅ 3 Roles predefinidos: CONFIGURADOS
✅ 4 Permisos (find, insert, update, remove): ACTIVOS
✅ Protección de rutas: APLICADA
✅ Información de usuario: VISIBLE EN NAVBAR
✅ Logout: FUNCIONAL
✅ Validación de credenciales: OPERATIVA
```

---

**Sistema de Autenticación Completado: 17/11/2025**  
**Versión: 1.0**  
**Estado:** ✅ OPERACIONAL
