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


settings = Settings()
