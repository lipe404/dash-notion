import streamlit as st
from config.settings import settings
from components.dashboard import Dashboard

# Configuração da página
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)


def main():
    # Verificar se o token está configurado
    if not settings.NOTION_TOKEN:
        st.error("❌ Token do Notion não configurado!")
        st.info("Configure o token no arquivo .env")
        st.stop()

    # Inicializar dashboard
    dashboard = Dashboard()

    # ✅ REMOVER ESTA LINHA - Não chamar render_sidebar aqui
    # filters = dashboard.render_sidebar()

    # Renderizar dashboard principal (que já inclui o sidebar)
    dashboard.render_main_dashboard()


if __name__ == "__main__":
    main()
