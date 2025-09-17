import os
from dotenv import load_dotenv
from notion_client import Client

# Carrega as variáveis de ambiente
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")


def test_status_extraction():
    print("🔍 TESTE ESPECÍFICO PARA CAMPOS DE STATUS")
    print("=" * 50)

    if not NOTION_TOKEN:
        print("❌ ERRO: NOTION_TOKEN não encontrado no .env")
        return

    print(f"✅ Token encontrado: {NOTION_TOKEN[:20]}...")

    try:
        client = Client(auth=NOTION_TOKEN)

        # Buscar todos os databases
        db_response = client.search(
            filter={
                "property": "object",
                "value": "database"
            }
        )

        all_databases = db_response.get("results", [])
        print(f"📊 Total de databases encontrados: {len(all_databases)}")

        for i, db in enumerate(all_databases):
            db_id = db.get("id", "N/A")
            db_title_prop = db.get("title", [])
            db_title = db_title_prop[0].get(
                "plain_text", "Sem título") if db_title_prop else "Sem título"

            print(f"\n🗄️ Database {i+1}: '{db_title}' (ID: {db_id})")

            try:
                # Buscar algumas entradas
                entries_response = client.databases.query(
                    database_id=db_id, page_size=3)
                entries = entries_response.get("results", [])

                if not entries:
                    print("   📝 Nenhuma entrada encontrada")
                    continue

                print(f"   📝 Analisando {len(entries)} entradas...")

                for j, entry in enumerate(entries):
                    print(f"\n   📄 Entrada {j+1}:")
                    properties = entry.get("properties", {})

                    status_found = False
                    for prop_name, prop_data in properties.items():
                        prop_type = prop_data.get("type", "unknown")

                        # Focar em propriedades que podem ser status
                        if "status" in prop_name.lower() or prop_type == "status":
                            status_found = True
                            print(f"      🎯 PROPRIEDADE DE STATUS ENCONTRADA!")
                            print(f"         Nome: '{prop_name}'")
                            print(f"         Tipo: '{prop_type}'")

                            # Extrair valor baseado no tipo
                            if prop_type == "status":
                                status_data = prop_data.get("status")
                                value = status_data.get(
                                    "name", "") if status_data else ""
                                print(f"         Valor extraído: '{value}'")
                                print(f"         Dados brutos: {status_data}")
                            elif prop_type == "select":
                                select_data = prop_data.get("select")
                                value = select_data.get(
                                    "name", "") if select_data else ""
                                print(f"         Valor extraído: '{value}'")
                                print(f"         Dados brutos: {select_data}")
                            else:
                                print(
                                    f"         ⚠️ Tipo não esperado para status: {prop_type}")

                    if not status_found:
                        print(
                            "      ❌ Nenhuma propriedade de status encontrada nesta entrada")
                        print("      📋 Propriedades disponíveis:")
                        for prop_name, prop_data in properties.items():
                            prop_type = prop_data.get("type", "unknown")
                            print(f"         - '{prop_name}': {prop_type}")

            except Exception as e:
                print(f"   ❌ Erro ao acessar database: {e}")

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")


if __name__ == "__main__":
    test_status_extraction()
