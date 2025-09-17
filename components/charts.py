import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from config.settings import settings
import numpy as np


class ChartComponents:

    @staticmethod
    def sales_funnel_chart(df: pd.DataFrame, selected_seller: str = "Todos"):
        """Gráfico de funil de vendas aprimorado com filtro por vendedor"""
        try:
            if df.empty or "status" not in df.columns:
                st.warning("Dados insuficientes para gerar o funil de vendas")
                return

            # ✅ APLICAR FILTRO POR VENDEDOR
            if selected_seller != "Todos":
                df_filtered = df[df["vendedor"] == selected_seller]
                title_suffix = f" - {selected_seller}"
            else:
                df_filtered = df.copy()
                title_suffix = " - Todos os Vendedores"

            if df_filtered.empty:
                st.warning(f"Nenhum dado encontrado para {selected_seller}")
                return

            # ✅ USAR ORDEM LÓGICA DO FUNIL
            status_order = settings.LEAD_STATUS
            status_counts = df_filtered["status"].value_counts()

            # Separar status em categorias para melhor visualização
            funnel_data = []
            colors = []

            for i, status in enumerate(status_order):
                if status in status_counts.index:
                    count = status_counts[status]
                    funnel_data.append(
                        {"status": status, "count": count, "order": i})

                    # ✅ CORES BASEADAS NA CATEGORIA DO STATUS
                    if status in settings.CONVERSION_STATUS:
                        colors.append("#4CAF50")  # Verde para vendas
                    elif status in settings.LOST_STATUS:
                        colors.append("#F44336")  # Vermelho para perdas
                    elif status in settings.IN_PROGRESS_STATUS:
                        colors.append("#2196F3")  # Azul para em progresso
                    else:
                        colors.append("#FF9800")  # Laranja para outros

            if not funnel_data:
                st.warning("Nenhum dado de status encontrado")
                return

            # Ordenar pela ordem do funil
            funnel_data.sort(key=lambda x: x["order"])

            labels = [item["status"] for item in funnel_data]
            values = [item["count"] for item in funnel_data]

            # ✅ CRIAR FUNIL APRIMORADO
            fig = go.Figure()

            fig.add_trace(go.Funnel(
                y=labels,
                x=values,
                textinfo="value+percent initial+percent previous",
                texttemplate='%{value}<br>%{percentInitial}<br>(%{percentPrevious} da anterior)',
                marker=dict(
                    color=colors,
                    line=dict(width=2, color="white")
                ),
                connector=dict(
                    line=dict(color="gray", dash="dot", width=2)
                )
            ))

            # ✅ LAYOUT APRIMORADO
            fig.update_layout(
                title=f"🎯 Funil de Vendas por Status{title_suffix}",
                height=700,
                showlegend=False,
                font=dict(size=12),
                margin=dict(l=20, r=20, t=60, b=20)
            )

            st.plotly_chart(fig, use_container_width=True,
                            key=f"funnel_chart_{selected_seller}")

            # ✅ MOSTRAR ESTATÍSTICAS DO FUNIL
            total_leads = sum(values)
            conversion_leads = sum(status_counts.get(status, 0)
                                   for status in settings.CONVERSION_STATUS)
            lost_leads = sum(status_counts.get(status, 0)
                             for status in settings.LOST_STATUS)
            in_progress_leads = sum(status_counts.get(status, 0)
                                    for status in settings.IN_PROGRESS_STATUS)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total no Funil", total_leads)
            with col2:
                st.metric("✅ Convertidos", conversion_leads,
                          f"{(conversion_leads/total_leads*100):.1f}%" if total_leads > 0 else "0%")
            with col3:
                st.metric("🔄 Em Progresso", in_progress_leads,
                          f"{(in_progress_leads/total_leads*100):.1f}%" if total_leads > 0 else "0%")
            with col4:
                st.metric("❌ Perdidos", lost_leads,
                          f"{(lost_leads/total_leads*100):.1f}%" if total_leads > 0 else "0%")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de funil: {str(e)}")
            # Fallback
            if not df.empty and "status" in df.columns:
                st.subheader("📊 Distribuição de Status (Tabela)")
                if selected_seller != "Todos":
                    df = df[df["vendedor"] == selected_seller]
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

            # ✅ CÁLCULO CORRIGIDO - Usar mesma lógica das KPIs
            seller_stats = df.groupby("vendedor").agg({
                "lead_id": "count",
                "status": lambda x: x.isin(settings.CONVERSION_STATUS).sum()
            }).rename(columns={"lead_id": "total_leads", "status": "fechados"})

            seller_stats["conversion_rate"] = (
                seller_stats["fechados"] / seller_stats["total_leads"] * 100
            ).round(2)

            # Gerar cores baseadas nos valores
            max_rate = seller_stats["conversion_rate"].max()
            min_rate = seller_stats["conversion_rate"].min()

            if max_rate > min_rate:
                normalized_rates = (
                    seller_stats["conversion_rate"] - min_rate) / (max_rate - min_rate)
            else:
                normalized_rates = [0.5] * len(seller_stats)

            colors = []
            for rate in normalized_rates:
                red = int(255 * (1 - rate))
                green = int(255 * rate)
                blue = 50
                colors.append(f'rgb({red},{green},{blue})')

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=seller_stats.index,
                y=seller_stats["conversion_rate"],
                text=[f'{rate}%<br>({closed}/{total})' for rate, closed, total in
                      zip(seller_stats["conversion_rate"], seller_stats["fechados"], seller_stats["total_leads"])],
                textposition='outside',
                marker_color=colors,
                hovertemplate='<b>%{x}</b><br>Taxa: %{y}%<br>Vendas: %{customdata[0]}<br>Total: %{customdata[1]}<extra></extra>',
                customdata=list(
                    zip(seller_stats["fechados"], seller_stats["total_leads"]))
            ))

            fig.update_layout(
                title="📈 Taxa de Conversão por Vendedor",
                xaxis_title="Vendedor",
                yaxis_title="Taxa de Conversão (%)",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="conversion_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de conversão: {str(e)}")

    @staticmethod
    def status_distribution_chart(df: pd.DataFrame):
        """Gráfico de distribuição de status"""
        try:
            if df.empty or "status" not in df.columns:
                st.warning("Dados de status não disponíveis")
                return

            status_counts = df["status"].value_counts()

            # ✅ CORES BASEADAS NA CATEGORIA
            colors = []
            for status in status_counts.index:
                if status in settings.CONVERSION_STATUS:
                    colors.append("#4CAF50")  # Verde
                elif status in settings.LOST_STATUS:
                    colors.append("#F44336")  # Vermelho
                elif status in settings.IN_PROGRESS_STATUS:
                    colors.append("#2196F3")  # Azul
                else:
                    colors.append("#FF9800")  # Laranja

            fig = go.Figure()

            fig.add_trace(go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+value+percent',
                textposition='auto'
            ))

            fig.update_layout(
                title="📊 Distribuição de Leads por Status",
                height=400,
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="status_pie_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de distribuição: {str(e)}")

    @staticmethod
    def leads_timeline_chart(df: pd.DataFrame):
        """Gráfico de timeline de leads"""
        try:
            if df.empty or "created_time" not in df.columns:
                st.warning("Dados de timeline não disponíveis")
                return

            df_copy = df.copy()
            df_copy["created_date"] = pd.to_datetime(
                df_copy["created_time"]).dt.date
            daily_leads = df_copy.groupby(
                "created_date").size().reset_index(name="count")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=daily_leads["created_date"],
                y=daily_leads["count"],
                mode='lines+markers',
                name='Leads por dia',
                line=dict(color='#45B7D1', width=2),
                marker=dict(color='#FF6B6B', size=6),
                fill='tonexty'
            ))

            fig.update_layout(
                title="📅 Leads Criados ao Longo do Tempo",
                xaxis_title="Data",
                yaxis_title="Número de Leads",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="timeline_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de timeline: {str(e)}")

    @staticmethod
    def seller_performance_chart(df: pd.DataFrame):
        """Gráfico de performance por vendedor"""
        try:
            if df.empty or "vendedor" not in df.columns:
                st.warning("Dados insuficientes para análise de performance")
                return

            # ✅ CÁLCULO CORRIGIDO - Usar mesma lógica das KPIs
            seller_stats = df.groupby("vendedor").agg({
                "lead_id": "count",
                "status": [
                    lambda x: x.isin(settings.CONVERSION_STATUS).sum(),
                    lambda x: x.isin(settings.LOST_STATUS).sum()
                ]
            }).round(2)

            seller_stats.columns = ["total_leads", "vendas", "perdidos"]
            seller_stats = seller_stats.reset_index()

            fig = go.Figure()

            fig.add_trace(go.Bar(
                name='Total Leads',
                x=seller_stats["vendedor"],
                y=seller_stats["total_leads"],
                marker_color='#45B7D1',
                text=seller_stats["total_leads"],
                textposition='inside'
            ))

            fig.add_trace(go.Bar(
                name='Vendas',
                x=seller_stats["vendedor"],
                y=seller_stats["vendas"],
                marker_color='#4CAF50',
                text=seller_stats["vendas"],
                textposition='inside'
            ))

            fig.add_trace(go.Bar(
                name='Perdidos',
                x=seller_stats["vendedor"],
                y=seller_stats["perdidos"],
                marker_color='#F44336',
                text=seller_stats["perdidos"],
                textposition='inside'
            ))

            fig.update_layout(
                title="📊 Performance por Vendedor",
                xaxis_title="Vendedor",
                yaxis_title="Quantidade",
                barmode='group',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True,
                            key="performance_chart")

        except Exception as e:
            st.error(f"Erro ao gerar gráfico de performance: {str(e)}")
