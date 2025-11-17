#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para validar IDs personalizados en MongoDB
Prueba que los IDs se guardan correctamente en tienda_discos_vintage
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

def test_custom_ids():
    """Valida que los IDs personalizados se hayan guardado en MongoDB"""
    
    print("=" * 60)
    print("🧪 PRUEBA DE IDS PERSONALIZADOS - MongoDB")
    print("=" * 60)
    
    try:
        # Conectar a MongoDB
        mongo_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME", "tienda_discos_vintage")
        
        client = MongoClient(mongo_uri)
        db = client[db_name]
        
        print(f"\n✓ Conectado a: {db_name}")
        
        # Revisar cada colección
        collections = ["artistas", "clientes", "inventario", "ventas"]
        
        for col_name in collections:
            collection = db[col_name]
            count = collection.count_documents({})
            
            print(f"\n📊 Colección: {col_name}")
            print(f"   Total de documentos: {count}")
            
            # Mostrar últimos 3 documentos
            if count > 0:
                docs = list(collection.find().limit(3).sort("_id", -1))
                for i, doc in enumerate(docs, 1):
                    _id = doc.get("_id")
                    id_type = type(_id).__name__
                    
                    # Determinar si es custom o auto-generado
                    if isinstance(_id, str):
                        id_origen = "🔧 CUSTOM (String)"
                    elif isinstance(_id, ObjectId):
                        id_origen = "⚙️  AUTO-GENERADO (ObjectId)"
                    else:
                        id_origen = f"❓ TIPO: {id_type}"
                    
                    print(f"   [{i}] ID: {_id}")
                    print(f"       Origen: {id_origen}")
        
        client.close()
        
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA - Verifica MongoDB Atlas")
        print("=" * 60)
        print("\nAcciones a verificar manualmente:")
        print("1. Ve a MongoDB Atlas")
        print("2. Abre Database: 'tienda_discos_vintage'")
        print("3. Revisa cada colección para ver los IDs")
        print("4. Los IDs custom aparecerán como strings en campo _id")
        print("5. Los auto-generados aparecerán como ObjectId")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"   Tipo: {type(e).__name__}")

if __name__ == "__main__":
    test_custom_ids()
