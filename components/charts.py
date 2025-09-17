import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from config.settings import settings


class ChartComponents:

    @staticmethod
    def sales_funnel_chart(df: pd.DataFrame):
        """Gráfico de funil de vendas"""
        if df.empty or "status" not in df.columns:
            st.warning("Dados insuficientes para gerar o funil de vendas")
            return

        # Contar leads por status na ordem do funil
        status_order = settings.LEAD_STATUS
        status_counts = df["status"].value_counts()

        # Reordenar conforme a ordem do funil
        ordered_counts = []
        ordered_labels = []

        for status in status_order:
            if status in status_counts.index:
                ordered_counts.append(status_counts[status])
                ordered_labels.append(status)

        if not ordered_counts:
            st.warning("Nenhum dado de status encontrado")
            return

        # Criar funil
        fig = go.Figure(go.Funnel(
            y=ordered_labels,
            x=ordered_counts,
            textinfo="value+percent initial",
            marker_color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
                          "#FFEAA7", "#DDA0DD", "#98D8C8", "#F39C12", "#E74C3C"]
        ))

        fig.update_layout(
            title="Funil de Vendas por Status",
            height=600
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def conversion_by_seller_chart(df: pd.DataFrame):
        """Gráfico de conversão por vendedor"""
        if df.empty or "vendedor" not in df.columns:
            st.warning("Dados insuficientes para gerar conversão por vendedor")
            return

        # Calcular conversão por vendedor
        seller_stats = df.groupby("vendedor").agg({
            "lead_id": "count",
            "status": lambda x: x.isin(settings.CONVERSION_STATUS).sum()
        }).rename(columns={"lead_id": "total_leads", "status": "fechados"})

        seller_stats["conversion_rate"] = (
            seller_stats["fechados"] / seller_stats["total_leads"] * 100
        ).round(2)

        fig = px.bar(
            x=seller_stats.index,
            y=seller_stats["conversion_rate"],
            title="Taxa de Conversão por Vendedor (%)",
            labels={"x": "Vendedor", "y": "Taxa de Conversão (%)"},
            color=seller_stats["conversion_rate"],
            color_continuous_scale="Viridis",
            text=seller_stats["conversion_rate"]
        )

        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def status_distribution_chart(df: pd.DataFrame):
        """Gráfico de distribuição de status"""
        if df.empty or "status" not in df.columns:
            st.warning("Dados de status não disponíveis")
            return

        # Distribuição por status
        status_counts = df["status"].value_counts()

        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribuição de Leads por Status"
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def leads_timeline_chart(df: pd.DataFrame):
        """Gráfico de timeline de leads"""
        if df.empty or "created_time" not in df.columns:
            st.warning("Dados de timeline não disponíveis")
            return

        # Converter para datetime
        df_copy = df.copy()
        df_copy["created_date"] = pd.to_datetime(
            df_copy["created_time"]).dt.date

        # Contar leads por data
        daily_leads = df_copy.groupby(
            "created_date").size().reset_index(name="count")

        fig = px.line(
            daily_leads,
            x="created_date",
            y="count",
            title="Leads Criados ao Longo do Tempo",
            labels={"created_date": "Data", "count": "Número de Leads"}
        )

        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def seller_performance_chart(df: pd.DataFrame):
        """Gráfico de performance por vendedor"""
        if df.empty or "vendedor" not in df.columns:
            st.warning("Dados insuficientes para análise de performance")
            return

        # Estatísticas por vendedor
        seller_stats = df.groupby("vendedor").agg({
            "lead_id": "count",
            "status": [
                lambda x: x.isin(settings.CONVERSION_STATUS).sum(),
                lambda x: x.isin(settings.LOST_STATUS).sum()
            ]
        }).round(2)

        # Flatten column names
        seller_stats.columns = ["total_leads", "vendas", "perdidos"]
        seller_stats = seller_stats.reset_index()

        fig = px.bar(
            seller_stats,
            x="vendedor",
            y=["total_leads", "vendas", "perdidos"],
            title="Performance por Vendedor",
            labels={"value": "Quantidade", "variable": "Tipo"},
            barmode="group"
        )

        st.plotly_chart(fig, use_container_width=True)
