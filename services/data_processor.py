import pandas as pd
from typing import List, Dict, Any
from services.notion_client import NotionClient


class DataProcessor:
    def __init__(self):
        self.notion_client = NotionClient()

    def get_all_sales_data(self) -> pd.DataFrame:
        """Coleta dados de vendas de todos os databases"""
        all_data = []

        # Buscar todos os databases
        databases = self.notion_client.get_all_databases()

        print(f"Encontrados {len(databases)} databases")

        for database in databases:
            database_id = database["id"]

            # Pegar título do database
            db_title_prop = database.get("title", [])
            db_title = db_title_prop[0].get(
                "plain_text", "Sem título") if db_title_prop else "Sem título"

            # Pegar informações do parent (página pai)
            parent_info = database.get("parent", {})
            parent_type = parent_info.get("type", "")

            # Se for um database de página, tentar pegar o nome da página
            vendedor_name = db_title
            if parent_type == "page_id":
                page_id = parent_info.get("page_id")
                try:
                    page_info = self.notion_client.client.pages.retrieve(
                        page_id=page_id)
                    page_title_prop = page_info.get(
                        "properties", {}).get("title", {})
                    if page_title_prop:
                        page_title = self.notion_client.extract_property_value(
                            page_title_prop)
                        if page_title:
                            vendedor_name = page_title
                except Exception as e:
                    print(
                        f"Erro ao buscar info da página {page_id} para vendedor: {e}")
                    pass

            print(
                f"Processando database: '{db_title}' - Vendedor: '{vendedor_name}'")

            # Buscar entradas do database
            entries = self.notion_client.get_database_entries(database_id)

            print(
                f"Processando {len(entries)} entradas para database '{db_title}'")

            for entry in entries:
                lead_data = self.extract_lead_data(
                    entry, vendedor_name, db_title)
                if lead_data:
                    all_data.append(lead_data)
                else:
                    # Adicione este log para entender por que um lead pode ser ignorado
                    print(
                        f"DEBUG: Lead ignorado: {entry.get('id', 'N/A')}. Possivelmente sem nome ou status.")

        print(f"Total de leads coletados: {len(all_data)}")
        # Para depuração: mostre os valores únicos de status após o processamento inicial
        if all_data:
            temp_df = pd.DataFrame(all_data)
            print(
                f"DEBUG: Valores únicos de status após extração: {temp_df['status'].unique()}")

        return pd.DataFrame(all_data)

    def extract_lead_data(self, entry: Dict[str, Any], vendedor: str, database_name: str) -> Dict[str, Any]:
        """Extrai dados de um lead individual"""
        properties = entry.get("properties", {})

        lead_data = {
            "vendedor": vendedor,
            "database": database_name,
            "lead_id": entry.get("id", ""),
            "created_time": entry.get("created_time", ""),
            "last_edited_time": entry.get("last_edited_time", ""),
            "data": "",
            "nome": "",
            "telefone": "",
            "curso": "",
            "status": ""
        }

        # Flag para verificar se encontramos uma propriedade de status
        found_status_prop = False

        # Mapear propriedades
        for prop_name, prop_data in properties.items():
            value = self.notion_client.extract_property_value(prop_data)
            prop_name_lower = prop_name.lower()
            prop_type = prop_data.get("type", "unknown")

            # DEBUG: Log detalhado para propriedades de status
            if any(keyword in prop_name_lower for keyword in ["status", "etapa", "stage"]):
                print(
                    f"DEBUG: Propriedade de status encontrada -> Nome: '{prop_name}', Tipo: '{prop_type}', Valor extraído: '{value}'")
                found_status_prop = True

            # Mapear baseado no nome da propriedade
            if any(keyword in prop_name_lower for keyword in ["data", "date"]):
                lead_data["data"] = value
            elif any(keyword in prop_name_lower for keyword in ["nome", "name", "cliente"]):
                lead_data["nome"] = value
            elif any(keyword in prop_name_lower for keyword in ["telefone", "phone", "tel", "fone"]):
                lead_data["telefone"] = value
            elif any(keyword in prop_name_lower for keyword in ["curso", "course", "produto"]):
                lead_data["curso"] = value
            elif any(keyword in prop_name_lower for keyword in ["status", "etapa", "stage"]):
                lead_data["status"] = value

            # Adicionar propriedade original também
            lead_data[f"prop_{prop_name.lower()}"] = value

        # Se não encontramos uma propriedade de status com os nomes esperados
        # e o status ainda está vazio, isso é um sinal de alerta
        if not found_status_prop and lead_data["status"] == "":
            print(
                f"ATENÇÃO: Não foi encontrada uma propriedade 'status' para o lead {lead_data['lead_id']} usando os termos de busca padrão (status, etapa, stage).")
            print(f"Por favor, verifique o nome da sua coluna de status no Notion. As propriedades encontradas foram:")
            for prop_name, prop_data in properties.items():
                value = self.notion_client.extract_property_value(prop_data)
                print(
                    f"  - '{prop_name}' (Tipo: {prop_data.get('type')}) -> Valor extraído: '{value}'")
            print("-" * 50)

            # Tente encontrar a primeira propriedade do tipo 'status' como fallback
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "status":
                    value = self.notion_client.extract_property_value(
                        prop_data)
                    if value:  # Se encontrou um valor para o status
                        print(
                            f"DEBUG: FALLBACK: Usando a propriedade '{prop_name}' (Tipo: {prop_data.get('type')}) como status: '{value}'")
                        lead_data["status"] = value
                        found_status_prop = True
                        break  # Pega a primeira que encontrar

        # Retornar se tiver pelo menos um nome ou status
        if lead_data["nome"] or lead_data["status"]:
            return lead_data

        return None

    def calculate_conversion_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas de conversão baseadas nos status específicos"""
        if df.empty:
            return {
                "total_leads": 0,
                "leads_fechados": 0,
                "leads_perdidos": 0,
                "conversion_rate": 0,
                "loss_rate": 0,
                "revenue_total": 0
            }

        total_leads = len(df)

        # Garante que a coluna status é string, para evitar erros com .str.contains
        df["status"] = df["status"].astype(str)

        # Status que indicam venda fechada
        leads_fechados = len(df[df["status"].str.contains(
            "VENDA|AGUARDANDO PAGAMENTO", case=False, na=False)])

        # Status que indicam leads perdidos
        leads_perdidos = len(df[df["status"].str.contains(
            "NÃO TEM INTERESSE|NÃO RESPONDE|NÃO OFERTAMOS", case=False, na=False)])

        conversion_rate = (leads_fechados / total_leads *
                           100) if total_leads > 0 else 0
        loss_rate = (leads_perdidos / total_leads *
                     100) if total_leads > 0 else 0

        return {
            "total_leads": total_leads,
            "leads_fechados": leads_fechados,
            "leads_perdidos": leads_perdidos,
            "conversion_rate": round(conversion_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "revenue_total": 0
        }
