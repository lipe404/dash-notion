import streamlit as st
import pandas as pd
from components.charts import ChartComponents
from services.data_processor import DataProcessor


class Dashboard:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.charts = ChartComponents()

    def render_sidebar(self):
        """Renderiza a barra lateral com filtros"""
        st.sidebar.header("🔍 Filtros")

        # Botão para atualizar dados
        if st.sidebar.button("🔄 Atualizar Dados", type="primary"):
            st.cache_data.clear()
            st.rerun()

        return {}

    def render_metrics_cards(self, metrics: dict):
        """Renderiza cards de métricas"""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="📊 Total de Leads",
                value=metrics.get("total_leads", 0)
            )

        with col2:
            st.metric(
                label="✅ Vendas Fechadas",
                value=metrics.get("leads_fechados", 0)
            )

        with col3:
            st.metric(
                label="📈 Taxa de Conversão",
                value=f"{metrics.get('conversion_rate', 0)}%"
            )

        with col4:
            st.metric(
                label="❌ Leads Perdidos",
                value=metrics.get("leads_perdidos", 0)
            )

    def render_data_quality_info(self, df: pd.DataFrame):
        """Renderiza informações sobre qualidade dos dados"""
        if df.empty:
            return

        st.subheader("📊 Qualidade dos Dados")

        col1, col2, col3 = st.columns(3)

        with col1:
            leads_com_nome = len(df[df["nome"].notna() & (df["nome"] != "")])
            st.metric("👤 Leads com Nome", leads_com_nome)

        with col2:
            leads_com_telefone = len(
                df[df["telefone"].notna() & (df["telefone"] != "")])
            st.metric("📞 Leads com Telefone", leads_com_telefone)

        with col3:
            leads_com_status = len(
                df[df["status"].notna() & (df["status"] != "")])
            st.metric("📋 Leads com Status", leads_com_status)

    def render_main_dashboard(self):
        """Renderiza o dashboard principal"""
        st.title("📊 Dashboard de Vendas - Notion CRM")

        # Carregar dados
        with st.spinner("Carregando dados do Notion..."):
            df = self.load_data()

        if df.empty:
            st.error("❌ Nenhum dado encontrado. Verifique:")
            st.info("• Se o token do Notion está correto")
            st.info("• Se as tabelas têm dados com Nome e/ou Telefone preenchidos")
            st.info("• Se as colunas estão nomeadas corretamente")
            return

        # Mostrar informações de debug
        st.success(f"✅ {len(df)} leads carregados com sucesso!")

        # Informações sobre qualidade dos dados
        self.render_data_quality_info(df)

        # Calcular métricas
        metrics = self.data_processor.calculate_conversion_metrics(df)

        # Renderizar cards de métricas
        self.render_metrics_cards(metrics)

        st.divider()

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            self.charts.sales_funnel_chart(df)

        with col2:
            self.charts.conversion_by_seller_chart(df)

        col3, col4 = st.columns(2)

        with col3:
            self.charts.status_distribution_chart(df)

        with col4:
            self.charts.seller_performance_chart(df)

        # Timeline
        self.charts.leads_timeline_chart(df)

        # Tabela de dados detalhados
        with st.expander("📋 Dados Detalhados"):
            st.dataframe(df, use_container_width=True)

    @st.cache_data
    def load_data(_self) -> pd.DataFrame:
        """Carrega dados do Notion com cache"""
        return _self.data_processor.get_all_sales_data()
