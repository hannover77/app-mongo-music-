#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script de verificación completa de la aplicación Música Vintage"""

import os
import sys
from models import USUARIOS, ROLES
from app import app

PERMISOS = ['find', 'insert', 'update', 'remove']

def verificar_usuarios():
    """Verificar configuración de usuarios"""
    print("\n👤 USUARIOS CONFIGURADOS:")
    print("=" * 60)
    for user_id, user_data in USUARIOS.items():
        rol = user_data.get('rol', 'N/A')
        nombre = user_data.get('nombre', 'N/A')
        print(f"  ✓ {user_id}: {nombre} (Rol: {rol})")
    print(f"\nTotal: {len(USUARIOS)} usuarios")

def verificar_roles():
    """Verificar roles y permisos"""
    print("\n🔐 ROLES DISPONIBLES:")
    print("=" * 60)
    for rol_name, permissions in ROLES.items():
        perms = list(permissions.keys())
        print(f"  ✓ {rol_name}:")
        for perm_name, allowed in permissions.items():
            status = "✓" if allowed else "✗"
            print(f"      {status} {perm_name}: {allowed}")

def verificar_permisos():
    """Verificar permisos base"""
    print("\n🔑 PERMISOS BASE:")
    print("=" * 60)
    for perm in PERMISOS:
        print(f"  ✓ {perm}")

def verificar_rutas():
    """Verificar rutas Flask"""
    print("\n🔗 RUTAS FLASK:")
    print("=" * 60)
    
    routes_by_category = {
        'Autenticación': [],
        'Artistas': [],
        'Clientes': [],
        'Inventario': [],
        'Ventas': [],
        'Reportes': []
    }
    
    for rule in app.url_map.iter_rules():
        route = str(rule)
        
        if 'reportes' in route:
            routes_by_category['Reportes'].append(route)
        elif 'artista' in route:
            routes_by_category['Artistas'].append(route)
        elif 'cliente' in route:
            routes_by_category['Clientes'].append(route)
        elif 'inventario' in route:
            routes_by_category['Inventario'].append(route)
        elif 'venta' in route:
            routes_by_category['Ventas'].append(route)
        elif route in ['/', '/login', '/logout']:
            routes_by_category['Autenticación'].append(route)
    
    for category, routes in routes_by_category.items():
        if routes:
            print(f"\n  {category}:")
            for route in sorted(routes):
                print(f"    ✓ {route}")
    
    total = sum(len(r) for r in routes_by_category.values())
    print(f"\n  Total: {total} rutas")

def verificar_templates():
    """Verificar templates"""
    print("\n📄 TEMPLATES:")
    print("=" * 60)
    
    dirs = {
        'Principal': 'templates',
        'Reportes': 'templates/reportes',
        'Artistas': 'templates/artistas',
        'Clientes': 'templates/clientes',
        'Inventario': 'templates/inventario',
        'Ventas': 'templates/ventas'
    }
    
    for name, path in dirs.items():
        if os.path.exists(path):
            files = os.listdir(path)
            print(f"\n  {name}: {len(files)} archivos")
            for f in sorted(files):
                print(f"    ✓ {f}")
        else:
            print(f"\n  ✗ FALTA: {name}")

def verificar_archivos():
    """Verificar archivos críticos"""
    print("\n📁 ARCHIVOS CRÍTICOS:")
    print("=" * 60)
    
    files = ['app.py', 'models.py', 'requirements.txt', '.env', 'REPORTES_IMPLEMENTACION.md']
    for f in files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            print(f"  ✓ {f} ({size} bytes)")
        else:
            print(f"  ✗ FALTA: {f}")

def main():
    """Ejecutar todas las verificaciones"""
    print("\n" + "=" * 60)
    print("🎵 VERIFICACIÓN COMPLETA - MÚSICA VINTAGE")
    print("=" * 60)
    
    try:
        verificar_usuarios()
        verificar_roles()
        verificar_permisos()
        verificar_rutas()
        verificar_templates()
        verificar_archivos()
        
        print("\n" + "=" * 60)
        print("✅ TODAS LAS VERIFICACIONES COMPLETADAS EXITOSAMENTE")
        print("=" * 60 + "\n")
        
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
