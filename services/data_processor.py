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

            # ✅ FILTRO 1: Excluir páginas específicas duplicadas
            if self.is_duplicate_page(vendedor_name):
                print(f"🚫 PÁGINA DUPLICADA IGNORADA: '{vendedor_name}'")
                continue

            print(
                f"Processando database: '{db_title}' - Vendedor: '{vendedor_name}'")

            # Buscar TODAS as entradas do database (sem limitação)
            entries = self.notion_client.get_database_entries(database_id)

            print(
                f"Processando {len(entries)} entradas para database '{db_title}'")

            # Contadores para estatísticas
            leads_processados = 0
            leads_validos = 0

            # Lista temporária para validar qualidade dos dados
            temp_leads = []

            for entry in entries:
                leads_processados += 1
                lead_data = self.extract_lead_data(
                    entry, vendedor_name, db_title)

                if lead_data:
                    temp_leads.append(lead_data)

            # ✅ FILTRO 2: Verificar qualidade dos dados do database
            if self.is_low_quality_database(temp_leads, vendedor_name):
                print(
                    f"🚫 DATABASE COM BAIXA QUALIDADE IGNORADO: '{vendedor_name}' - {len(temp_leads)} leads")
                continue

            # Se passou nos filtros, adicionar os leads válidos
            for lead in temp_leads:
                leads_validos += 1
                all_data.append(lead)

            leads_sem_nome_telefone = leads_processados - leads_validos

            print(f"✅ Estatísticas do database '{db_title}':")
            print(f"  - Total processados: {leads_processados}")
            print(f"  - Leads válidos (com nome/telefone): {leads_validos}")
            print(
                f"  - Leads ignorados (sem nome/telefone): {leads_sem_nome_telefone}")

        print(f"RESUMO FINAL:")
        print(f"Total de leads coletados: {len(all_data)}")

        # Para depuração: mostre os valores únicos de status após o processamento inicial
        if all_data:
            temp_df = pd.DataFrame(all_data)
            print(
                f"DEBUG: Valores únicos de status após extração: {temp_df['status'].unique()}")
            print(f"DEBUG: Vendedores únicos: {temp_df['vendedor'].unique()}")

        return pd.DataFrame(all_data)

    def is_duplicate_page(self, vendedor_name: str) -> bool:
        """Verifica se é uma página duplicada que deve ser ignorada"""

        # Lista de páginas duplicadas específicas para ignorar
        duplicated_pages = [
            "CRM ANA LUÍSA NEVES (1)",
            "CRM ANA LUISA NEVES (1)",  # Variação sem acento
        ]

        # Verificar se o nome exato está na lista
        if vendedor_name in duplicated_pages:
            return True

        # Verificar padrões de duplicação (páginas com sufixos como (1), (2), etc.)
        import re
        duplicate_pattern = r'^(.+)\s+\(\d+\)$'
        if re.match(duplicate_pattern, vendedor_name):
            print(
                f"⚠️ POSSÍVEL DUPLICATA DETECTADA pelo padrão: '{vendedor_name}'")
            return True

        return False

    def safe_get_string(self, value) -> str:
        """Converte qualquer valor para string de forma segura"""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        return str(value)

    def is_low_quality_database(self, leads: List[Dict], vendedor_name: str) -> bool:
        """Verifica se o database tem baixa qualidade de dados"""

        if not leads:
            return True  # Database vazio

        total_leads = len(leads)

        # ✅ CORREÇÃO: Usar função segura para verificar strings
        leads_com_nome = sum(1 for lead in leads if self.safe_get_string(
            lead.get("nome", "")).strip())
        leads_com_telefone = sum(1 for lead in leads if self.safe_get_string(
            lead.get("telefone", "")).strip())
        leads_com_nome_ou_telefone = sum(1 for lead in leads if
                                         self.safe_get_string(lead.get("nome", "")).strip() or
                                         self.safe_get_string(lead.get("telefone", "")).strip())

        # Calcular percentuais de qualidade
        percentual_nome = (leads_com_nome / total_leads) * \
            100 if total_leads > 0 else 0
        percentual_telefone = (leads_com_telefone /
                               total_leads) * 100 if total_leads > 0 else 0
        percentual_contato = (leads_com_nome_ou_telefone /
                              total_leads) * 100 if total_leads > 0 else 0

        print(f"📊 Análise de qualidade para '{vendedor_name}':")
        print(f"  - Total de leads: {total_leads}")
        print(f"  - Com nome: {leads_com_nome} ({percentual_nome:.1f}%)")
        print(
            f"  - Com telefone: {leads_com_telefone} ({percentual_telefone:.1f}%)")
        print(
            f"  - Com nome OU telefone: {leads_com_nome_ou_telefone} ({percentual_contato:.1f}%)")

        # ✅ CRITÉRIOS DE BAIXA QUALIDADE:

        # 1. Se menos de 30% dos leads têm dados de contato
        if percentual_contato < 30:
            print(
                f"🚫 REJEITADO: Menos de 30% dos leads têm dados de contato ({percentual_contato:.1f}%)")
            return True

        # 2. Se é uma página específica conhecida como problemática
        if "ANA LUÍSA NEVES (1)" in vendedor_name or "ANA LUISA NEVES (1)" in vendedor_name:
            print(f"🚫 REJEITADO: Página específica na lista de exclusão")
            return True

        # 3. Se tem poucos leads e baixa qualidade
        if total_leads < 50 and percentual_contato < 50:
            print(
                f"🚫 REJEITADO: Poucos leads ({total_leads}) e baixa qualidade ({percentual_contato:.1f}%)")
            return True

        print(f"✅ APROVADO: Database passou nos critérios de qualidade")
        return False

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

        # Mapear propriedades
        for prop_name, prop_data in properties.items():
            value = self.notion_client.extract_property_value(prop_data)
            prop_name_lower = prop_name.lower()

            # ✅ CORREÇÃO: Converter valor para string segura
            safe_value = self.safe_get_string(value)

            # Mapear baseado no nome da propriedade
            if any(keyword in prop_name_lower for keyword in ["data", "date"]):
                lead_data["data"] = safe_value
            elif any(keyword in prop_name_lower for keyword in ["nome", "name", "cliente"]):
                lead_data["nome"] = safe_value
            elif any(keyword in prop_name_lower for keyword in ["telefone", "phone", "tel", "fone"]):
                lead_data["telefone"] = safe_value
            elif any(keyword in prop_name_lower for keyword in ["curso", "course", "produto"]):
                lead_data["curso"] = safe_value
            elif any(keyword in prop_name_lower for keyword in ["status", "etapa", "stage"]):
                lead_data["status"] = safe_value

            # Adicionar propriedade original também
            lead_data[f"prop_{prop_name.lower()}"] = safe_value

        # Se não encontrou status pelos nomes, tentar encontrar por tipo
        if not lead_data["status"]:
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "status":
                    value = self.notion_client.extract_property_value(
                        prop_data)
                    if value:
                        lead_data["status"] = self.safe_get_string(value)
                        break

        # ✅ VALIDAÇÃO CORRIGIDA: Só retornar se tiver Nome E/OU Telefone preenchidos
        nome_preenchido = lead_data["nome"] and lead_data["nome"].strip() != ""
        telefone_preenchido = lead_data["telefone"] and lead_data["telefone"].strip(
        ) != ""

        if nome_preenchido or telefone_preenchido:
            return lead_data

        # Lead ignorado por não ter nome nem telefone
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

        # ✅ CORREÇÃO: Usar a mesma lógica dos settings
        from config.settings import settings

        # Status que indicam venda fechada - usar lista exata dos settings
        leads_fechados = len(df[df["status"].isin(settings.CONVERSION_STATUS)])

        # Status que indicam leads perdidos - usar lista exata dos settings
        leads_perdidos = len(df[df["status"].isin(settings.LOST_STATUS)])

        conversion_rate = (leads_fechados / total_leads *
                        100) if total_leads > 0 else 0
        loss_rate = (leads_perdidos / total_leads * 100) if total_leads > 0 else 0

        return {
            "total_leads": total_leads,
            "leads_fechados": leads_fechados,
            "leads_perdidos": leads_perdidos,
            "conversion_rate": round(conversion_rate, 2),
            "loss_rate": round(loss_rate, 2),
            "revenue_total": 0
        }
