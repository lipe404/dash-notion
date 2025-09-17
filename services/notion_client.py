from notion_client import Client
from config.settings import settings
import pandas as pd
from typing import List, Dict, Any


class NotionClient:
    def __init__(self):
        self.client = Client(auth=settings.NOTION_TOKEN)

    def get_all_databases(self) -> List[Dict[str, Any]]:
        """Busca todos os databases acessíveis"""
        try:
            response = self.client.search(
                filter={
                    "property": "object",
                    "value": "database"
                }
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Erro ao buscar databases: {e}")
            return []

    def get_database_entries(self, database_id: str) -> List[Dict[str, Any]]:
        """Busca todas as entradas de um database"""
        try:
            response = self.client.databases.query(database_id=database_id)
            return response.get("results", [])
        except Exception as e:
            print(f"Erro ao buscar entradas do database {database_id}: {e}")
            return []

    def get_database_info(self, database_id: str) -> Dict[str, Any]:
        """Busca informações de um database"""
        try:
            return self.client.databases.retrieve(database_id=database_id)
        except Exception as e:
            print(f"Erro ao buscar info do database {database_id}: {e}")
            return {}

    def extract_property_value(self, property_data: Dict[str, Any]) -> Any:
        """Extrai valor de uma propriedade do Notion com tratamento de erros"""
        if not property_data:
            return ""

        prop_type = property_data.get("type")

        try:
            if prop_type == "title":
                title_list = property_data.get("title", [])
                return title_list[0].get("plain_text", "") if title_list else ""

            elif prop_type == "rich_text":
                rich_text_list = property_data.get("rich_text", [])
                return rich_text_list[0].get("plain_text", "") if rich_text_list else ""

            elif prop_type == "select":
                select_data = property_data.get("select")
                return select_data.get("name", "") if select_data else ""

            elif prop_type == "status":  # ✅ ADICIONADO SUPORTE PARA TIPO "STATUS"
                status_data = property_data.get("status")
                return status_data.get("name", "") if status_data else ""

            elif prop_type == "multi_select":
                multi_select_list = property_data.get("multi_select", [])
                return [item.get("name", "") for item in multi_select_list]

            elif prop_type == "number":
                return property_data.get("number", 0) or 0

            elif prop_type == "date":
                date_data = property_data.get("date")
                return date_data.get("start", "") if date_data else ""

            elif prop_type == "people":
                people_list = property_data.get("people", [])
                return [person.get("name", "") for person in people_list]

            elif prop_type == "phone_number":
                return property_data.get("phone_number", "")

            elif prop_type == "url":
                return property_data.get("url", "")

            else:
                print(f"DEBUG: Tipo de propriedade não tratado: '{prop_type}'")
                return ""

        except (IndexError, KeyError, AttributeError) as e:
            print(f"Erro ao extrair propriedade {prop_type}: {e}")
            return ""
