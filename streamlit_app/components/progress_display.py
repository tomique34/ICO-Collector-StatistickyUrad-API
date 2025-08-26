#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Progress display komponenty pre ICO Collector Streamlit App
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

def render_live_progress_dashboard(stats: Dict[str, Any]):
    """
    Vykresli live progress dashboard s real-time metrikami.
    """
    if not stats:
        return
    
    # Hlavné metriky
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Spracované",
            f"{stats.get('processed_companies', 0)}",
            f"z {stats.get('total_companies', 0)}"
        )
    
    with col2:
        success_rate = stats.get('success_rate', 0)
        st.metric(
            "Úspešnosť",
            f"{success_rate:.1f}%",
            f"{stats.get('successful_matches', 0)} úspešných"
        )
    
    with col3:
        speed = stats.get('processing_speed', 0)
        st.metric(
            "Rýchlosť",
            f"{speed:.1f} firiem/min",
            "priemerne"
        )
    
    with col4:
        avg_time = stats.get('avg_time_per_company', 0)
        st.metric(
            "Čas/firmu",
            f"{avg_time:.2f}s",
            "priemerne"
        )
    
    # Progress bar s percentami
    if stats.get('total_companies', 0) > 0:
        progress = stats['processed_companies'] / stats['total_companies']
        st.progress(progress)
        st.write(f"**Pokrok:** {progress:.1%} dokončené")
    
    # Aktuálne spracovávaná firma
    if stats.get('current_company'):
        st.info(f"🔄 Aktuálne spracováva: **{stats['current_company']}**")

def create_real_time_chart(processing_data: List[Dict]):
    """
    Vytvorí real-time graf priebehu spracovania.
    """
    if not processing_data:
        return None
    
    df = pd.DataFrame(processing_data)
    
    # Graf rychlosti spracovania v čase
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['cumulative_processed'],
        mode='lines+markers',
        name='Spracované firmy',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['cumulative_successful'],
        mode='lines+markers',
        name='Úspešné zhody',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig.update_layout(
        title='Real-time priebeh spracovania',
        xaxis_title='Čas',
        yaxis_title='Počet firiem',
        height=400
    )
    
    return fig

def render_processing_insights(results: Dict[str, List]):
    """
    Vykresli insights a analýzy z výsledkov spracovania.
    """
    if not results:
        return
    
    st.subheader("📊 Analýza výsledkov")
    
    # Základné štatistiky
    total_companies = len(results.get('ICO', []))
    successful_matches = sum(1 for ico in results.get('ICO', []) if ico)
    
    # Graf úspešnosti podľa stratégie zhody
    if 'MatchStrategy' in results:
        strategies = pd.Series([s for s in results['MatchStrategy'] if s])
        strategy_success = {}
        
        for i, strategy in enumerate(results['MatchStrategy']):
            if strategy:
                ico = results['ICO'][i] if i < len(results['ICO']) else None
                if strategy not in strategy_success:
                    strategy_success[strategy] = {'total': 0, 'successful': 0}
                strategy_success[strategy]['total'] += 1
                if ico:
                    strategy_success[strategy]['successful'] += 1
        
        if strategy_success:
            strategy_df = pd.DataFrame([
                {
                    'Stratégia': strategy,
                    'Celkovo': data['total'],
                    'Úspešné': data['successful'],
                    'Úspešnosť (%)': (data['successful'] / data['total']) * 100
                }
                for strategy, data in strategy_success.items()
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_strategy = px.bar(
                    strategy_df,
                    x='Stratégia',
                    y='Úspešnosť (%)',
                    title='Úspešnosť podľa stratégie zhody',
                    color='Úspešnosť (%)',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_strategy, use_container_width=True)
            
            with col2:
                fig_volume = px.bar(
                    strategy_df,
                    x='Stratégia',
                    y='Celkovo',
                    title='Počet použití stratégií',
                    color='Celkovo',
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_volume, use_container_width=True)
    
    # Analýza čistenia názvov
    if 'CleanName' in results:
        original_names = []  # Tu by sme potrebovali pôvodné názvy
        clean_names = results['CleanName']
        
        # Štatistiky o čistení názvov
        cleaning_stats = {
            'Boli vyčistené': 0,
            'Neboli zmenené': 0
        }
        
        # Táto analýza by potrebovala porovnanie s pôvodnými názvami
        # Pre teraz zobrazíme len základné info
        st.write("**Štatistiky čistenia názvov:**")
        st.info("Všetky názvy firiem boli vyčistené od právnych foriem a diakritiky pre lepšie vyhľadávanie.")

def render_error_analysis(results: Dict[str, List]):
    """
    Vykresli analýzu chýb a problémových prípadov.
    """
    if not results or 'Notes' not in results:
        return
    
    st.subheader("🔍 Analýza problémov")
    
    # Analýza poznámok a chýb
    notes = [note for note in results['Notes'] if note]
    
    if notes:
        error_types = {}
        for note in notes:
            if 'Exception' in note:
                error_types['Technické chyby'] = error_types.get('Technické chyby', 0) + 1
            elif 'Not found' in note:
                error_types['Nenájdené'] = error_types.get('Nenájdené', 0) + 1
            elif 'without valid ICO' in note:
                error_types['Bez platného IČO'] = error_types.get('Bez platného IČO', 0) + 1
            else:
                error_types['Ostatné'] = error_types.get('Ostatné', 0) + 1
        
        if error_types:
            col1, col2 = st.columns(2)
            
            with col1:
                # Graf typov chýb
                fig_errors = px.pie(
                    values=list(error_types.values()),
                    names=list(error_types.keys()),
                    title='Rozdelenie typov problémov'
                )
                st.plotly_chart(fig_errors, use_container_width=True)
            
            with col2:
                # Tabuľka s detailmi
                error_df = pd.DataFrame([
                    {'Typ problému': k, 'Počet': v} 
                    for k, v in error_types.items()
                ])
                st.dataframe(error_df, use_container_width=True)

def render_performance_metrics(stats: Dict[str, Any]):
    """
    Vykresli výkonnostné metriky a trendy.
    """
    if not stats:
        return
    
    st.subheader("⚡ Výkonnostné metriky")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_time = stats.get('total_time', 0)
        if total_time > 0:
            hours = int(total_time // 3600)
            minutes = int((total_time % 3600) // 60)
            seconds = int(total_time % 60)
            
            if hours > 0:
                time_str = f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                time_str = f"{minutes}m {seconds}s"
            else:
                time_str = f"{seconds}s"
            
            st.metric("Celkový čas", time_str)
    
    with col2:
        avg_time = stats.get('avg_time_per_company', 0)
        st.metric("Priemer/firmu", f"{avg_time:.2f}s")
    
    with col3:
        speed = stats.get('processing_speed', 0)
        st.metric("Priemer/minútu", f"{speed:.1f} firiem")

def create_success_rate_gauge(success_rate: float):
    """
    Vytvorí gauge chart pre úspešnosť.
    """
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = success_rate,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Úspešnosť (%)"},
        delta = {'reference': 80},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

def render_time_estimation(stats: Dict[str, Any]):
    """
    Vykresli odhady času dokončenia.
    """
    if not stats or not stats.get('is_processing'):
        return
    
    processed = stats.get('processed_companies', 0)
    total = stats.get('total_companies', 0)
    speed = stats.get('processing_speed', 0)
    
    if processed > 0 and total > processed and speed > 0:
        remaining = total - processed
        eta_minutes = remaining / speed
        
        if eta_minutes > 60:
            eta_hours = eta_minutes / 60
            eta_str = f"{eta_hours:.1f} hodín"
        else:
            eta_str = f"{eta_minutes:.1f} minút"
        
        progress_percent = (processed / total) * 100
        
        st.info(f"📅 Odhadovaný čas dokončenia: **{eta_str}** (zostáva {remaining} firiem)")
        
        # Progress bar s percentami
        progress_bar = st.progress(progress_percent / 100)
        st.write(f"**{progress_percent:.1f}%** dokončené")

def create_processing_timeline_chart(processing_history: List[Dict]):
    """
    Vytvorí timeline chart priebehu spracovania.
    """
    if not processing_history:
        return None
    
    df = pd.DataFrame(processing_history)
    
    fig = go.Figure()
    
    # Kumulatívne spracované
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['processed'],
        fill='tonexty',
        mode='none',
        name='Spracované',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    # Úspešné
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['successful'],
        fill='tonexty',
        mode='none',
        name='Úspešné',
        fillcolor='rgba(44, 160, 44, 0.3)'
    ))
    
    fig.update_layout(
        title='Timeline priebehu spracovania',
        xaxis_title='Čas',
        yaxis_title='Kumulatívny počet',
        height=400,
        hovermode='x unified'
    )
    
    return fig