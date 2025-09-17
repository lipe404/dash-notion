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

        # ✅ USAR SESSION STATE PARA EVITAR DUPLICAÇÃO
        if 'df_loaded' not in st.session_state:
            st.session_state.df_loaded = None

        # Carregar dados para filtros apenas se necessário
        if st.session_state.df_loaded is None:
            st.session_state.df_loaded = self.load_data()

        df = st.session_state.df_loaded
        filters = {}

        if not df.empty:
            # ✅ FILTRO POR VENDEDOR
            vendedores = ["Todos"] + sorted(df["vendedor"].unique().tolist())
            selected_seller = st.sidebar.selectbox(
                "👤 Selecionar Vendedor",
                vendedores,
                key="main_seller_filter"  # ✅ Key única
            )
            filters["vendedor"] = selected_seller

            # ✅ FILTRO POR PERÍODO (opcional)
            if "created_time" in df.columns:
                df_copy = df.copy()
                df_copy["created_date"] = pd.to_datetime(
                    df_copy["created_time"]).dt.date

                min_date = df_copy["created_date"].min()
                max_date = df_copy["created_date"].max()

                if min_date and max_date:
                    date_range = st.sidebar.date_input(
                        "📅 Período",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="main_date_filter"  # ✅ Key única
                    )

                    if len(date_range) == 2:
                        filters["date_range"] = date_range

        # Botão para atualizar dados
        if st.sidebar.button("🔄 Atualizar Dados", type="primary", key="refresh_button"):
            st.cache_data.clear()
            st.session_state.df_loaded = None  # ✅ Limpar session state
            st.rerun()

        return filters

    def apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        """Aplica filtros ao DataFrame"""
        if df.empty:
            return df

        filtered_df = df.copy()

        # Filtro por vendedor
        if filters.get("vendedor") and filters["vendedor"] != "Todos":
            filtered_df = filtered_df[filtered_df["vendedor"]
                                      == filters["vendedor"]]

        # Filtro por data
        if filters.get("date_range") and len(filters["date_range"]) == 2:
            filtered_df["created_date"] = pd.to_datetime(
                filtered_df["created_time"]).dt.date
            start_date, end_date = filters["date_range"]
            filtered_df = filtered_df[
                (filtered_df["created_date"] >= start_date) &
                (filtered_df["created_date"] <= end_date)
            ]

        return filtered_df

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

        st.subheader("📊 Resumo dos Dados")

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

        # ✅ RENDERIZAR SIDEBAR AQUI (uma única vez)
        filters = self.render_sidebar()

        # Carregar dados originais
        with st.spinner("Carregando dados do Notion..."):
            if 'df_loaded' not in st.session_state or st.session_state.df_loaded is None:
                st.session_state.df_loaded = self.load_data()

            df_original = st.session_state.df_loaded

        if df_original.empty:
            st.error("❌ Nenhum dado encontrado. Verifique:")
            st.info("• Se o token do Notion está correto")
            st.info("• Se as tabelas têm dados com Nome e/ou Telefone preenchidos")
            st.info("• Se as colunas estão nomeadas corretamente")
            return

        # Aplicar filtros
        df = self.apply_filters(df_original, filters)

        # Mostrar informações
        """if filters.get("vendedor") and filters["vendedor"] != "Todos":
            st.success(
                f"✅ {len(df)} leads carregados para {filters['vendedor']}")
        else:
            st.success(f"✅ {len(df)} leads carregados com sucesso!")"""

        # Informações sobre qualidade dos dados
        self.render_data_quality_info(df)

        # Calcular métricas
        metrics = self.data_processor.calculate_conversion_metrics(df)

        # Renderizar cards de métricas
        self.render_metrics_cards(metrics)

        st.divider()

        # ✅ GRÁFICOS COM FILTROS APLICADOS
        col1, col2 = st.columns(2)

        with col1:
            # Passar vendedor selecionado para o funil
            selected_seller = filters.get("vendedor", "Todos")
            self.charts.sales_funnel_chart(df_original, selected_seller)

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
