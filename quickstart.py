#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
⚡ QUICK START - Tienda Discos Vintage
Script para verificar que todo está listo y proporcionar instrucciones inmediatas
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")

def check_file(path, name):
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {name}: {path}")
    return exists

def check_env():
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    
    print(f"✅ MONGO_URI: {'Configurada' if mongo_uri else '❌ NO configurada'}")
    print(f"✅ DB_NAME: {db_name}")
    return bool(mongo_uri and db_name)

def main():
    print_section("🎵 TIENDA DISCOS VINTAGE - QUICK START")
    
    # Verificar archivos
    print_section("📁 Verificando Archivos")
    files_ok = all([
        check_file("!crud_musica/app.py", "app.py"),
        check_file("!crud_musica/models.py", "models.py"),
        check_file(".env", ".env"),
    ])
    
    # Verificar configuración
    print_section("⚙️  Verificando Configuración")
    env_ok = check_env()
    
    # Instrucciones
    print_section("🚀 CÓMO INICIAR")
    print("""
1. Abre PowerShell en esta carpeta

2. Activa el entorno virtual:
   .\.venv\Scripts\Activate.ps1

3. Navega a la carpeta de la app:
   cd !crud_musica

4. Inicia el servidor:
   python app.py

5. Abre en navegador:
   http://127.0.0.1:5000

6. ¡Listo! Ahora puedes:
   ✓ Crear artistas con IDs personalizados
   ✓ Gestionar clientes
   ✓ Controlar inventario
   ✓ Registrar ventas
    """)
    
    # Estado final
    print_section("✅ ESTADO")
    if files_ok and env_ok:
        print("✅ TODO LISTO PARA COMENZAR")
        print("\nDocumentación disponible:")
        print("  1. RESUMEN_IMPLEMENTACION.md")
        print("  2. GUIA_IDS_PERSONALIZADOS.md")
        print("  3. README_ESTADO_FINAL.md")
    else:
        print("⚠️  Revisa los errores arriba antes de iniciar")
    
    print(f"\n{'=' * 60}\n")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
