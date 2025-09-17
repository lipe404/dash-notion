import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from config.settings import settings
import numpy as np


class ChartComponents:

    @staticmethod
    def sales_funnel_chart(df: pd.DataFrame):
        """Gráfico de funil de vendas"""
        try:
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

            # Criar funil com configuração mais simples
            fig = go.Figure()

            fig.add_trace(go.Funnel(
                y=ordered_labels,
                x=ordered_counts,
                textinfo="value+percent initial",
                marker=dict(
                    color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
                           "#FFEAA7", "#DDA0DD", "#98D8C8", "#F39C12", "#E74C3C"][:len(ordered_labels)]
                )
            ))

            fig.update_layout(
                title="Funil de Vendas por Status",
                height=600,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True, key="funnel_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de funil: {str(e)}")
            # Fallback: mostrar dados em tabela
            if not df.empty and "status" in df.columns:
                st.subheader("📊 Distribuição de Status (Tabela)")
                status_counts = df["status"].value_counts()
                st.dataframe(status_counts.to_frame("Quantidade"))

    @staticmethod
    def conversion_by_seller_chart(df: pd.DataFrame):
        """Gráfico de conversão por vendedor"""
        try:
            if df.empty or "vendedor" not in df.columns:
                st.warning(
                    "Dados insuficientes para gerar conversão por vendedor")
                return

            # Calcular conversão por vendedor
            seller_stats = df.groupby("vendedor").agg({
                "lead_id": "count",
                "status": lambda x: x.isin(settings.CONVERSION_STATUS).sum()
            }).rename(columns={"lead_id": "total_leads", "status": "fechados"})

            seller_stats["conversion_rate"] = (
                seller_stats["fechados"] / seller_stats["total_leads"] * 100
            ).round(2)

            # ✅ CORREÇÃO: Gerar cores baseadas nos valores
            # Criar uma escala de cores baseada na taxa de conversão
            max_rate = seller_stats["conversion_rate"].max()
            min_rate = seller_stats["conversion_rate"].min()

            # Normalizar valores para escala de 0-1
            if max_rate > min_rate:
                normalized_rates = (
                    seller_stats["conversion_rate"] - min_rate) / (max_rate - min_rate)
            else:
                normalized_rates = [0.5] * len(seller_stats)

            # Gerar cores usando uma paleta
            colors = []
            for rate in normalized_rates:
                # Escala de vermelho (baixo) para verde (alto)
                red = int(255 * (1 - rate))
                green = int(255 * rate)
                blue = 50
                colors.append(f'rgb({red},{green},{blue})')

            # Usar gráfico mais simples
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=seller_stats.index,
                y=seller_stats["conversion_rate"],
                text=seller_stats["conversion_rate"],
                texttemplate='%{text}%',
                textposition='outside',
                marker_color=colors  # ✅ Usar lista de cores específicas
            ))

            fig.update_layout(
                title="Taxa de Conversão por Vendedor (%)",
                xaxis_title="Vendedor",
                yaxis_title="Taxa de Conversão (%)",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="conversion_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de conversão: {str(e)}")
            # Fallback
            if not df.empty and "vendedor" in df.columns:
                st.subheader("📈 Taxa de Conversão (Tabela)")
                seller_stats = df.groupby("vendedor").agg({
                    "lead_id": "count",
                    "status": lambda x: x.isin(settings.CONVERSION_STATUS).sum()
                }).rename(columns={"lead_id": "total_leads", "status": "fechados"})
                seller_stats["conversion_rate"] = (
                    seller_stats["fechados"] /
                    seller_stats["total_leads"] * 100
                ).round(2)
                st.dataframe(seller_stats)

    @staticmethod
    def status_distribution_chart(df: pd.DataFrame):
        """Gráfico de distribuição de status"""
        try:
            if df.empty or "status" not in df.columns:
                st.warning("Dados de status não disponíveis")
                return

            # Distribuição por status
            status_counts = df["status"].value_counts()

            # ✅ CORREÇÃO: Usar cores predefinidas para o gráfico de pizza
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
                      '#DDA0DD', '#98D8C8', '#F39C12', '#E74C3C', '#A8E6CF']

            # Usar gráfico mais simples
            fig = go.Figure()

            fig.add_trace(go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3,
                # ✅ Cores específicas
                marker=dict(colors=colors[:len(status_counts)])
            ))

            fig.update_layout(
                title="Distribuição de Leads por Status",
                height=400,
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="status_pie_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de distribuição: {str(e)}")
            # Fallback
            if not df.empty and "status" in df.columns:
                st.subheader("📊 Distribuição de Status (Tabela)")
                status_counts = df["status"].value_counts()
                st.dataframe(status_counts.to_frame("Quantidade"))

    @staticmethod
    def leads_timeline_chart(df: pd.DataFrame):
        """Gráfico de timeline de leads"""
        try:
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

            # Usar gráfico mais simples
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=daily_leads["created_date"],
                y=daily_leads["count"],
                mode='lines+markers',
                name='Leads por dia',
                line=dict(color='#45B7D1', width=2),
                marker=dict(color='#FF6B6B', size=6)
            ))

            fig.update_layout(
                title="Leads Criados ao Longo do Tempo",
                xaxis_title="Data",
                yaxis_title="Número de Leads",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="timeline_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de timeline: {str(e)}")
            # Fallback
            if not df.empty and "created_time" in df.columns:
                st.subheader("📅 Timeline de Leads (Tabela)")
                df_copy = df.copy()
                df_copy["created_date"] = pd.to_datetime(
                    df_copy["created_time"]).dt.date
                daily_leads = df_copy.groupby(
                    "created_date").size().reset_index(name="count")
                st.dataframe(daily_leads)

    @staticmethod
    def seller_performance_chart(df: pd.DataFrame):
        """Gráfico de performance por vendedor"""
        try:
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

            # Usar gráfico mais simples
            fig = go.Figure()

            fig.add_trace(go.Bar(
                name='Total Leads',
                x=seller_stats["vendedor"],
                y=seller_stats["total_leads"],
                marker_color='#45B7D1'  # ✅ Cor específica
            ))

            fig.add_trace(go.Bar(
                name='Vendas',
                x=seller_stats["vendedor"],
                y=seller_stats["vendas"],
                marker_color='#4ECDC4'  # ✅ Cor específica
            ))

            fig.add_trace(go.Bar(
                name='Perdidos',
                x=seller_stats["vendedor"],
                y=seller_stats["perdidos"],
                marker_color='#FF6B6B'  # ✅ Cor específica
            ))

            fig.update_layout(
                title="Performance por Vendedor",
                xaxis_title="Vendedor",
                yaxis_title="Quantidade",
                barmode='group',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="performance_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de performance: {str(e)}")
            # Fallback
            if not df.empty and "vendedor" in df.columns:
                st.subheader("📊 Performance por Vendedor (Tabela)")
                seller_stats = df.groupby("vendedor").agg({
                    "lead_id": "count",
                    "status": [
                        lambda x: x.isin(settings.CONVERSION_STATUS).sum(),
                        lambda x: x.isin(settings.LOST_STATUS).sum()
                    ]
                }).round(2)
                seller_stats.columns = ["total_leads", "vendas", "perdidos"]
                st.dataframe(seller_stats)
