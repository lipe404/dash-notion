import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    WORKSPACE_ID = os.getenv("WORKSPACE_ID")

    # Configurações do dashboard
    PAGE_TITLE = "Dashboard de Vendas - Notion CRM"
    PAGE_ICON = "📊"
    LAYOUT = "wide"

    # Status de leads do seu CRM
    LEAD_STATUS = [
        "CONVERSANDO",
        "ABORDAGEM 1",
        "ABORDAGEM 2",
        "ABORDAGEM 3",
        "NÃO TEM INTERESSE",
        "NÃO RESPONDE +",
        "AGUARDANDO PAGAMENTO",
        "VENDA",
        "NÃO OFERTAMOS O CURSO"
    ]

    # Status de conversão
    CONVERSION_STATUS = ["VENDA", "AGUARDANDO PAGAMENTO"]
    LOST_STATUS = ["NÃO TEM INTERESSE",
                   "NÃO RESPONDE +", "NÃO OFERTAMOS O CURSO"]

    # ✅ CONFIGURAÇÕES DE FILTROS
    # Páginas específicas para excluir (nomes exatos)
    EXCLUDED_PAGES = [
        "CRM ANA LUÍSA NEVES (1)",
        "CRM ANA LUISA NEVES (1)",
    ]

    # Critérios de qualidade de dados
    MIN_CONTACT_DATA_PERCENTAGE = 30  # Mínimo de 30% dos leads com nome/telefone
    # Se tem menos de 50 leads, precisa de 50% de qualidade
    MIN_LEADS_FOR_LOW_QUALITY = 50


settings = Settings()
