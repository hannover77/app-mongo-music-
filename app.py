import os
import re
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from bson import ObjectId
from models import (
    normalize_artista, normalize_cliente,
    normalize_inventario, normalize_venta, to_object_id,
    validar_usuario, obtener_rol, tiene_permiso
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")
# Seguridad: Configuraciones de sesión
app.config['SESSION_COOKIE_SECURE'] = False  # True en producción con HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Evita acceso desde JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protección contra CSRF

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME", "tienda_musica")]

# Funciones de Seguridad
def sanitize_input(value):
    """Sanitiza entradas para evitar inyecciones"""
    if not isinstance(value, str):
        return value
    # Remover caracteres especiales peligrosos
    value = value.strip()
    # Permitir solo letras, números, espacios, guiones y guiones bajos
    return re.sub(r'[<>&"\']', '', value)

def validate_email(email):
    """Valida formato de correo"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Colecciones
Artistas = db["artistas"]
Clientes = db["clientes"]
Inventario = db["inventario"]
Ventas = db["ventas"]

# ========== AUTENTICACIÓN ==========

def login_requerido(f):
    """Decorador que requiere login para acceder a una ruta"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            flash("Debes iniciar sesión", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def permiso_requerido(permiso):
    """Decorador que requiere un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "usuario" not in session:
                flash("Debes iniciar sesión", "error")
                return redirect(url_for("login"))
            
            usuario = session.get("usuario")
            if not tiene_permiso(usuario, permiso):
                flash(f"No tienes permiso para {permiso}", "error")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route("/login", methods=["GET", "POST"])
def login():
    """Ruta de login con validación segura"""
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "").strip()
        
        # Validación de entrada
        if not usuario or not password:
            flash("Usuario y contraseña son requeridos", "error")
            return render_template("login.html")
        
        if len(usuario) < 3 or len(usuario) > 50:
            flash("Usuario debe tener entre 3 y 50 caracteres", "error")
            return render_template("login.html")
        
        if len(password) < 6 or len(password) > 100:
            flash("Contraseña debe tener entre 6 y 100 caracteres", "error")
            return render_template("login.html")
        
        # Validar que el usuario solo contenga caracteres permitidos
        if not re.match(r'^[a-zA-Z0-9_-]+$', usuario):
            flash("Usuario solo puede contener letras, números, guiones y guiones bajos", "error")
            return render_template("login.html")
        
        # Validar credenciales
        resultado = validar_usuario(usuario, password)
        if resultado:
            session["usuario"] = usuario
            session["nombre"] = resultado.get("nombre", usuario)
            session["rol"] = resultado.get("rol", "")
            flash(f"✅ Bienvenido {resultado.get('nombre', usuario)}", "success")
            return redirect(url_for("index"))
        else:
            flash("❌ Usuario o contraseña incorrectos", "error")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Ruta de logout"""
    session.clear()
    flash("Has cerrado sesión", "info")
    return redirect(url_for("login"))

@app.route("/")
def index():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")


# ---------- ARTISTAS ----------
@app.route("/artistas")
@permiso_requerido("find")
def artistas_list():
    artistas = list(Artistas.find().sort("nombre", 1))
    return render_template("artistas/list.html", artistas=artistas)

@app.route("/artistas/nuevo", methods=["GET", "POST"])
@permiso_requerido("insert")
def artistas_new():
    if request.method == "POST":
        doc = normalize_artista(request.form)
        
        if not doc["nombre"]:
            flash("El nombre es obligatorio", "error")
            return redirect(url_for("artistas_new"))
        
        try:
            Artistas.insert_one(doc)
            id_creado = doc.get("_id", "")
            flash(f"Artista creado con ID: {id_creado}", "success")
            return redirect(url_for("artistas_list"))
        except Exception as e:
            flash(f"Error al crear artista: {str(e)}", "error")
            return redirect(url_for("artistas_new"))
    
    return render_template("artistas/form.html", item=None)

@app.route("/artistas/<id>")
@permiso_requerido("find")
def artistas_view(id):
    item = Artistas.find_one({"_id": ObjectId(id)})
    return render_template("artistas/view.html", item=item)

@app.route("/artistas/<id>/editar", methods=["GET", "POST"])
@permiso_requerido("update")
def artistas_edit(id):
    item = Artistas.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        doc = normalize_artista(request.form)
        Artistas.update_one({"_id": ObjectId(id)}, {"$set": doc})
        flash("Artista actualizado", "success")
        return redirect(url_for("artistas_list"))
    return render_template("artistas/form.html", item=item)

@app.route("/artistas/<id>/eliminar", methods=["POST"])
@permiso_requerido("remove")
def artistas_delete(id):
    Artistas.delete_one({"_id": ObjectId(id)})
    flash("Artista eliminado", "success")
    return redirect(url_for("artistas_list"))

# ---------- CLIENTES ----------
@app.route("/clientes")
@permiso_requerido("find")
def clientes_list():
    clientes = list(Clientes.find().sort("nombre", 1))
    return render_template("clientes/list.html", clientes=clientes)

@app.route("/clientes/nuevo", methods=["GET", "POST"])
@permiso_requerido("insert")
def clientes_new():
    if request.method == "POST":
        doc = normalize_cliente(request.form)
        
        if not doc["nombre"] or not doc["correo"]:
            flash("Nombre y correo son obligatorios", "error")
            return redirect(url_for("clientes_new"))
        
        try:
            Clientes.insert_one(doc)
            id_creado = doc.get("_id", "")
            flash(f"Cliente creado con ID: {id_creado}", "success")
            return redirect(url_for("clientes_list"))
        except Exception as e:
            flash(f"Error al crear cliente: {str(e)}", "error")
            return redirect(url_for("clientes_new"))
    
    return render_template("clientes/form.html", item=None)

@app.route("/clientes/<id>")
@permiso_requerido("find")
def clientes_view(id):
    item = Clientes.find_one({"_id": ObjectId(id)})
    return render_template("clientes/view.html", item=item)

@app.route("/clientes/<id>/editar", methods=["GET", "POST"])
@permiso_requerido("update")
def clientes_edit(id):
    item = Clientes.find_one({"_id": ObjectId(id)})
    if request.method == "POST":
        doc = normalize_cliente(request.form)
        Clientes.update_one({"_id": ObjectId(id)}, {"$set": doc})
        flash("Cliente actualizado", "success")
        return redirect(url_for("clientes_list"))
    return render_template("clientes/form.html", item=item)

@app.route("/clientes/<id>/eliminar", methods=["POST"])
@permiso_requerido("remove")
def clientes_delete(id):
    Clientes.delete_one({"_id": ObjectId(id)})
    flash("Cliente eliminado", "success")
    return redirect(url_for("clientes_list"))

# ---------- INVENTARIO ----------
@app.route("/inventario")
@permiso_requerido("find")
def inventario_list():
    items = list(Inventario.find().sort("album", 1))
    artistas = list(Artistas.find({}, {"_id": 1, "nombre": 1}))
    return render_template("inventario/list.html", inventario=items, artistas=artistas)

@app.route("/inventario/nuevo", methods=["GET", "POST"])
@permiso_requerido("insert")
def inventario_new():
    if request.method == "POST":
        doc = normalize_inventario(request.form)
        
        if not doc["artista_id"] or not doc["album"]:
            flash("Artista y álbum son obligatorios", "error")
            return redirect(url_for("inventario_new"))
        
        # No necesitamos guardar nombre_artista, $lookup lo traerá
        doc.pop("nombre_artista", None)
        
        try:
            Inventario.insert_one(doc)
            id_creado = doc.get("_id", "")
            flash(f"Producto creado con ID: {id_creado}", "success")
            return redirect(url_for("inventario_list"))
        except Exception as e:
            flash(f"Error al crear producto: {str(e)}", "error")
            return redirect(url_for("inventario_new"))
    
    artistas = list(Artistas.find().sort("nombre", 1))
    return render_template("inventario/form.html", item=None, artistas=artistas)

@app.route("/inventario/<id>")
@permiso_requerido("find")
def inventario_view(id):
    item = Inventario.find_one({"_id": ObjectId(id)})
    if item:
        artistas_dict = {str(a["_id"]): a["nombre"] for a in Artistas.find()}
        item["nombre_artista"] = artistas_dict.get(str(item.get("artista_id")), "N/A")
    return render_template("inventario/view.html", item=item)

@app.route("/inventario/<id>/editar", methods=["GET", "POST"])
@permiso_requerido("update")
def inventario_edit(id):
    if request.method == "POST":
        doc = normalize_inventario(request.form)
        Inventario.update_one({"_id": ObjectId(id)}, {"$set": doc})
        flash("Inventario actualizado", "success")
        return redirect(url_for("inventario_list"))

    item = Inventario.find_one({"_id": ObjectId(id)})
    if item:
        artistas_dict = {str(a["_id"]): a["nombre"] for a in Artistas.find()}
        item["nombre_artista"] = artistas_dict.get(str(item.get("artista_id")), "N/A")
    artistas = list(Artistas.find().sort("nombre", 1))
    return render_template("inventario/form.html", item=item, artistas=artistas)

@app.route("/inventario/<id>/eliminar", methods=["POST"])
@permiso_requerido("remove")
def inventario_delete(id):
    Inventario.delete_one({"_id": ObjectId(id)})
    flash("Inventario eliminado", "success")
    return redirect(url_for("inventario_list"))

# ---------- VENTAS ----------
@app.route("/ventas")
@permiso_requerido("find")
def ventas_list():
    """Lista de ventas optimizada con agregación $lookup"""
    pipeline = [
        { "$sort": { "fecha_venta": -1 } },
        {
            "$lookup": {
                "from": "clientes",
                "localField": "cliente_id",
                "foreignField": "_id",
                "as": "cliente_info"
            }
        },
        {
            "$lookup": {
                "from": "artistas",
                "localField": "artista_id",
                "foreignField": "_id",
                "as": "artista_info"
            }
        },
        { "$unwind": { "path": "$cliente_info", "preserveNullAndEmptyArrays": True } },
        { "$unwind": { "path": "$artista_info", "preserveNullAndEmptyArrays": True } },
        {
            "$project": {
                "_id": 1,
                "fecha_venta": 1,
                "album": 1,
                "cantidad": 1,
                "precio_unitario": 1,
                "nombre_cliente": { "$ifNull": ["$cliente_info.nombre", "N/A"] },
                "nombre_artista": { "$ifNull": ["$artista_info.nombre", "N/A"] },
                "total_venta": { "$multiply": ["$cantidad", "$precio_unitario"] }
            }
        }
    ]
    ventas = list(Ventas.aggregate(pipeline))
    return render_template("ventas/list.html", ventas=ventas)

@app.route("/ventas/nuevo", methods=["GET", "POST"])
@permiso_requerido("insert")
def ventas_new():
    if request.method == "POST":
        doc = normalize_venta(request.form)
        
        # Parse fecha ISO a datetime
        try:
            doc["fecha_venta"] = datetime.fromisoformat(doc["fecha_venta"].replace("Z",""))
        except Exception:
            flash("Fecha inválida. Usa formato ISO (YYYY-MM-DD).", "error")
            return redirect(url_for("ventas_new"))
        

        
        try:
            Ventas.insert_one(doc)
            id_creado = doc.get("_id", "")
            flash(f"Venta registrada con ID: {id_creado}", "success")
            return redirect(url_for("ventas_list"))
        except Exception as e:
            flash(f"Error al registrar venta: {str(e)}", "error")
            return redirect(url_for("ventas_new"))
    
    clientes = list(Clientes.find().sort("nombre", 1))
    artistas = list(Artistas.find().sort("nombre", 1))
    inv = list(Inventario.find().sort("album", 1))
    return render_template("ventas/form.html", item=None, clientes=clientes, artistas=artistas, inventario=inv)

@app.route("/ventas/<id>")
@permiso_requerido("find")
def ventas_view(id):
    item = Ventas.find_one({"_id": ObjectId(id)})
    if item:
        clientes_dict = {str(c["_id"]): c["nombre"] for c in Clientes.find()}
        artistas_dict = {str(a["_id"]): a["nombre"] for a in Artistas.find()}
        item["nombre_cliente"] = clientes_dict.get(str(item.get("cliente_id")), "N/A")
        item["nombre_artista"] = artistas_dict.get(str(item.get("artista_id")), "N/A")
    return render_template("ventas/view.html", item=item)

@app.route("/ventas/<id>/editar", methods=["GET", "POST"])
@permiso_requerido("update")
def ventas_edit(id):
    if request.method == "POST":
        doc = normalize_venta(request.form)
        try:
            doc["fecha_venta"] = datetime.fromisoformat(doc["fecha_venta"].replace("Z",""))
        except Exception:
            flash("Fecha inválida", "error")
            return redirect(url_for("ventas_edit", id=id))
        Ventas.update_one({"_id": ObjectId(id)}, {"$set": doc})
        flash("Venta actualizada", "success")
        return redirect(url_for("ventas_list"))
    
    item = Ventas.find_one({"_id": ObjectId(id)})
    if item:
        clientes_dict = {str(c["_id"]): c["nombre"] for c in Clientes.find()}
        artistas_dict = {str(a["_id"]): a["nombre"] for a in Artistas.find()}
        item["nombre_cliente"] = clientes_dict.get(str(item.get("cliente_id")), "N/A")
        item["nombre_artista"] = artistas_dict.get(str(item.get("artista_id")), "N/A")
    clientes = list(Clientes.find().sort("nombre", 1))
    artistas = list(Artistas.find().sort("nombre", 1))
    inv = list(Inventario.find().sort("album", 1))
    return render_template("ventas/form.html", item=item, clientes=clientes, artistas=artistas, inventario=inv)

@app.route("/ventas/<id>/eliminar", methods=["POST"])
@permiso_requerido("remove")
def ventas_delete(id):
    Ventas.delete_one({"_id": ObjectId(id)})
    flash("Venta eliminada", "success")
    return redirect(url_for("ventas_list"))

# ========== REPORTES CON AGREGACIONES ==========

@app.route("/reportes")
@permiso_requerido("find")
def reportes():
    """Página principal de reportes"""
    return render_template("reportes/index.html")

@app.route("/reportes/estadisticas")
@permiso_requerido("find")
def estadisticas():
    """Estadísticas generales usando $count y $sum"""
    
    # 1. $count: Contar total de registros
    total_artistas = Artistas.count_documents({})
    total_clientes = Clientes.count_documents({})
    total_productos = Inventario.count_documents({})
    total_ventas = Ventas.count_documents({})
    
    # 2. $sum con agregación: Ingresos totales por ventas
    ingresos_totales = list(Ventas.aggregate([
        {
            "$group": {
                "_id": None,
                "ingresos_totales": { "$sum": { "$multiply": ["$cantidad", "$precio_unitario"] } }
            }
        }
    ]))
    ingresos = ingresos_totales[0]["ingresos_totales"] if ingresos_totales else 0
    
    # 3. Stock total en inventario con $sum
    stock_total = list(Inventario.aggregate([
        {
            "$group": {
                "_id": None,
                "stock_total": { "$sum": "$stock" }
            }
        }
    ]))
    stock = stock_total[0]["stock_total"] if stock_total else 0
    
    estadisticas_dict = {
        "total_artistas": total_artistas,
        "total_clientes": total_clientes,
        "total_productos": total_productos,
        "total_ventas": total_ventas,
        "ingresos_totales": round(ingresos, 2),
        "stock_total": stock
    }
    
    return render_template("reportes/estadisticas.html", stats=estadisticas_dict)

@app.route("/reportes/ventas-por-artista")
@permiso_requerido("find")
def ventas_por_artista():
    """
    Reporte de ventas por artista usando agregaciones MongoDB
    """
    pipeline = [
        {
            "$match": {
                "cantidad": {"$gt": 0}
            }
        },
        {
            "$lookup": {
                "from": "artistas",
                "localField": "artista_id",
                "foreignField": "_id",
                "as": "artista"
            }
        },
        {
            "$unwind": {
                "path": "$artista",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$group": {
                "_id": "$artista_id",
                "artista_nombre": {"$first": "$artista.nombre"},
                "unidades_vendidas": {"$sum": "$cantidad"},
                "ingresos": {
                    "$sum": {"$multiply": ["$cantidad", "$precio_unitario"]}
                },
                "transacciones": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "artista": {"$ifNull": ["$artista_nombre", "Desconocido"]},
                "unidades": "$unidades_vendidas",
                "ingresos": {"$round": ["$ingresos", 2]},
                "transacciones": 1
            }
        },
        {
            "$sort": {"ingresos": -1}
        }
    ]

    reporte_list = list(Ventas.aggregate(pipeline))
    return render_template("reportes/ventas_por_artista.html", ventas=reporte_list)

@app.route("/reportes/inventario-bajo")
@permiso_requerido("find")
def inventario_bajo():
    """
    Productos con stock bajo usando agregaciones MongoDB
    """
    pipeline = [
        {
            "$match": {
                "stock": {"$lt": 5}
            }
        },
        {
            "$lookup": {
                "from": "artistas",
                "localField": "artista_id",
                "foreignField": "_id",
                "as": "artista"
            }
        },
        {
            "$unwind": {
                "path": "$artista",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 1,
                "nombre": "$album",
                "stock": 1,
                "precio_unitario": 1,
                "valor_total": {"$multiply": ["$stock", "$precio_unitario"]},
                "artista_nombre": {"$ifNull": ["$artista.nombre", "N/A"]}
            }
        },
        {
            "$sort": {"stock": 1}
        }
    ]

    productos = list(Inventario.aggregate(pipeline))
    return render_template("reportes/inventario_bajo.html", productos=productos)

@app.route("/reportes/clientes-activos")
@permiso_requerido("find")
def clientes_activos():
    """
    Clientes más activos usando agregaciones MongoDB
    """
    pipeline = [
        {
            "$match": {
                "cantidad": {"$gt": 0}
            }
        },
        {
            "$lookup": {
                "from": "clientes",
                "localField": "cliente_id",
                "foreignField": "_id",
                "as": "cliente"
            }
        },
        {
            "$unwind": {
                "path": "$cliente",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$group": {
                "_id": "$cliente_id",
                "cliente_nombre": {"$first": "$cliente.nombre"},
                "compras": {"$sum": 1},
                "cantidad_articulos": {"$sum": "$cantidad"},
                "gasto_total": {
                    "$sum": {"$multiply": ["$cantidad", "$precio_unitario"]}
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "cliente_id": "$_id",
                "cliente_nombre": {"$ifNull": ["$cliente_nombre", "Desconocido"]},
                "compras": 1,
                "cantidad_articulos": 1,
                "gasto_total": {"$round": ["$gasto_total", 2]}
            }
        },
        {
            "$sort": {"gasto_total": -1}
        }
    ]

    clientes_reporte = list(Ventas.aggregate(pipeline))
    return render_template("reportes/clientes_activos.html", clientes=clientes_reporte)

@app.route("/reportes/generos-populares")
@permiso_requerido("find")
def generos_populares():
    """
    Géneros musicales más vendidos usando agregaciones MongoDB
    """
    pipeline = [
        {
            "$match": {
                "genero": {"$ne": None, "$ne": ""}
            }
        },
        {
            "$group": {
                "_id": "$genero",
                "cantidad_productos": {"$sum": 1},
                "stock_disponible": {"$sum": "$stock"},
                "valor_total": {
                    "$sum": {"$multiply": ["$stock", "$precio_unitario"]}
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "genero": "$_id",
                "cantidad_productos": 1,
                "stock_disponible": 1,
                "valor_total": {"$round": ["$valor_total", 2]},
                "valor_promedio": {
                    "$round": [
                        {"$divide": ["$valor_total", "$cantidad_productos"]},
                        2
                    ]
                }
            }
        },
        {
            "$sort": {"valor_total": -1}
        }
    ]

    generos_reporte = list(Inventario.aggregate(pipeline))
    return render_template("reportes/generos_populares.html", generos=generos_reporte)

if __name__ == "__main__":
    app.run(debug=True)


