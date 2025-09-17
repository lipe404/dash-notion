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

    # ✅ FUNIL DE VENDAS ATUALIZADO - Ordem lógica do processo de vendas
    LEAD_STATUS = [
        "ABORDAGEM 1",           # Primeiro contato
        "ABORDAGEM 2",           # Segunda tentativa
        "ABORDAGEM 3",           # Terceira tentativa
        "CONVERSANDO",           # Em conversa ativa
        "INTERESSE EM GRADUAÇÃO",  # Demonstrou interesse específico
        "NEGOCIANDO",            # Em processo de negociação
        "AGUARDANDO FICHA",      # Aguardando documentação
        "AGUARDANDO PAGAMENTO",  # Venda quase fechada
        "VENDA",                 # Venda concluída
        # Status de saída/perda
        "NÃO RESPONDE +",
        "DESQUALIFICADO",
        "NÃO OFERTAMOS O CURSO",
        "NÃO TEM INTERESSE",
        "BLOQUEOU MEU NÚMERO",
        "SEM EXPERIÊNCIA",
        "NÃO TEMOS O CURSO",
        "REPETIDO"
    ]

    # ✅ STATUS DE CONVERSÃO ATUALIZADOS
    CONVERSION_STATUS = ["VENDA", "AGUARDANDO PAGAMENTO"]

    # ✅ STATUS DE PERDA ATUALIZADOS
    LOST_STATUS = [
        "NÃO TEM INTERESSE",
        "NÃO RESPONDE +",
        "NÃO OFERTAMOS O CURSO",
        "DESQUALIFICADO",
        "BLOQUEOU MEU NÚMERO",
        "SEM EXPERIÊNCIA",
        "NÃO TEMOS O CURSO",
        "REPETIDO"
    ]

    # ✅ STATUS EM PROGRESSO (para análise)
    IN_PROGRESS_STATUS = [
        "ABORDAGEM 1",
        "ABORDAGEM 2",
        "ABORDAGEM 3",
        "CONVERSANDO",
        "INTERESSE EM GRADUAÇÃO",
        "NEGOCIANDO",
        "AGUARDANDO FICHA"
    ]

    # ✅ CONFIGURAÇÕES DE FILTROS
    EXCLUDED_PAGES = [
        "CRM ANA LUÍSA NEVES (1)",
        "CRM ANA LUISA NEVES (1)",
    ]

    # Critérios de qualidade de dados
    MIN_CONTACT_DATA_PERCENTAGE = 30
    MIN_LEADS_FOR_LOW_QUALITY = 50


settings = Settings()
