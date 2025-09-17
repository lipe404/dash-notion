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
        """Busca TODAS as entradas de um database (sem limitação de 100)"""
        all_entries = []
        has_more = True
        next_cursor = None

        print(
            f"DEBUG: Iniciando busca de entradas para database {database_id}")

        try:
            while has_more:
                # Preparar parâmetros da query
                query_params = {
                    "database_id": database_id,
                    "page_size": 100  # Máximo por página
                }

                # Adicionar cursor se não for a primeira página
                if next_cursor:
                    query_params["start_cursor"] = next_cursor

                # Fazer a query
                response = self.client.databases.query(**query_params)

                # Adicionar resultados à lista
                page_results = response.get("results", [])
                all_entries.extend(page_results)

                # Verificar se há mais páginas
                has_more = response.get("has_more", False)
                next_cursor = response.get("next_cursor")

                print(
                    f"DEBUG: Página processada - {len(page_results)} entradas. Total acumulado: {len(all_entries)}. Há mais páginas: {has_more}")

        except Exception as e:
            print(f"Erro ao buscar entradas do database {database_id}: {e}")
            return []

        print(
            f"DEBUG: Busca finalizada - Total de {len(all_entries)} entradas encontradas para database {database_id}")
        return all_entries

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

            elif prop_type == "status":
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
