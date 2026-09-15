import json
from pathlib import Path
import importlib
import base64
import textwrap
from typing import Literal, cast

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from live_map import build_maplibre_html
from live_map_sdg import build_sdg_maplibre_html

ASSETS_DIR = Path(__file__).parent / "assets"




def get_base64_image(image_path: str) -> str:
    """Convert image to base64 for embedding in HTML"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


IframeWidth = int | Literal["stretch", "content"]


def render_html_iframe(html: str, *, height: int, width: IframeWidth = "stretch") -> None:
    """Render HTML in an iframe with proper UTF-8 encoding"""
    
    if not html.strip().startswith('<!DOCTYPE'):
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
{html}
</body>
</html>"""
    
    encoded = base64.b64encode(html.encode("utf-8")).decode("ascii")
    st.iframe(f"data:text/html;charset=utf-8;base64,{encoded}", height=height, width=width)


def scroll_to_recommendations() -> None:
    """Positionne la page sur le début du contenu après le rerun de l'onglet."""
    components.html(
        """
        <script>
        (() => {
            const scrollToStart = () => {
                const marker = window.parent.document.getElementById("recommendations-start");
                const main = window.parent.document.querySelector("section.stMain");
                if (!marker || !main) return;
                const topbarOffset = 70;
                const target = marker.getBoundingClientRect().top
                    - main.getBoundingClientRect().top
                    + main.scrollTop
                    - topbarOffset;
                main.scrollTo({ top: Math.max(0, target), behavior: "auto" });
            };
            requestAnimationFrame(() => requestAnimationFrame(scrollToStart));
        })();
        </script>
        """,
        height=0,
    )




DATA_DIR = Path(__file__).parent / "data"

SOURCE_LAND = "Source : Google Earth Engine | Trends.Earth v2.2.6 | UNCCD GPG 15.3.1 v2 (2021) | GPG Addendum (2025). Données satellites : MODIS MOD13Q1 (productivité), MODIS MCD12Q1 (couverture des terres), OpenLandMap (carbone organique du sol)."
SOURCE_LAND_BASELINE = "Source : Google Earth Engine | Trends.Earth v2.2.6 | UNCCD GPG 15.3.1 v2 (2021) | Période de référence 2001-2015."
SOURCE_DROUGHT = "Source : Google Earth Engine | CHIRPS (précipitations) | SPI-12 empirique | UNCCD GPG-SO3 (2021)."
SOURCE_LAND_DROUGHT = "Source : SDG 15.3.1 selon Google Earth Engine/Trends.Earth/UNCCD GPG | Sécheresse selon CHIRPS et SPI-12 empirique."
SOURCE_DVI = "Source : Google Earth Engine | Composite DVI reconstruit | UNCCD GPG-SO3 ."
SOURCE_MAP_BASE = "Fond de carte : OpenStreetMap contributors."


PALETTE = {
    
    "hcp_bordeaux": "#6B1F3A",      
    "hcp_gold": "#D4A74A",          
    "hcp_burgundy": "#4A1528",      
    "hcp_light_gold": "#E8C87A",    
    
    
    "bg": "#FAF9F7",                
    "card": "#FFFFFF",
    "surface": "#F5F2ED",           
    "ink": "#2D1B1F",               
    "muted": "#7B6B6E",             
    "line": "#E5DDD6",              
    
    
    "degraded": "#C1440E",          
    "stable": "#D4A74A",            
    "improved": "#4A7C59",          
    
    
    "accent": "#6B1F3A",            
    "accent2": "#D4A74A",           
    "navy": "#2D1B1F",
    
    
    "morocco_red": "#C1272D",
    "morocco_green": "#006233",
}


def icon_svg(name: str, color: str | None = None, size: int = 20) -> str:
    color = color or PALETTE["accent"]
    icons = {
        "earth": """
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="12" cy="12" r="9" stroke="{color}" stroke-width="1.8"/>
          <path d="M3 12H21M12 3C14.5 5.7 15.8 8.8 15.8 12C15.8 15.2 14.5 18.3 12 21C9.5 18.3 8.2 15.2 8.2 12C8.2 8.8 9.5 5.7 12 3Z" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """,
        "filter": """
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M4 6H20L14 12.8V18L10 20V12.8L4 6Z" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/>
        </svg>
        """,
        "alphabetical": """
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M3 7L7 17L11 7M5 13H9M14 7V17M14 7H19M14 17H19" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """,
        "alert": """
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="12" cy="12" r="9" stroke="{color}" stroke-width="2"/>
          <path d="M12 8V12M12 16H12.01" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        </svg>
        """,
        "success": """
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="12" cy="12" r="9" stroke="{color}" stroke-width="2"/>
          <path d="M9 12L11 14L15 10" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """,
    }
    return icons.get(name, icons["earth"]).format(size=size, color=color)


CUSTOM_CSS = f"""
<style>
    @keyframes sheen {{
        0% {{ transform: translateX(-120%); opacity: 0; }}
        28% {{ opacity: 0.38; }}
        100% {{ transform: translateX(160%); opacity: 0; }}
    }}
    @keyframes pulseGlow {{
        0%, 100% {{ box-shadow: 0 22px 60px rgba(107, 31, 58, 0.16); }}
        50% {{ box-shadow: 0 28px 72px rgba(212, 167, 74, 0.24); }}
    }}
    
    
    
    .hcp-topbar {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        height: 54px;
        background: linear-gradient(135deg, {PALETTE['hcp_burgundy']} 0%, {PALETTE['hcp_bordeaux']} 100%);
        border-bottom: 3px solid {PALETTE['hcp_gold']};
        box-shadow: 0 4px 24px rgba(107, 31, 58, 0.25);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 1.5rem;
        animation: fadeUp 500ms ease;
    }}
    .hcp-logo-container {{
        display: flex;
        align-items: center;
        gap: 1rem;
        cursor: pointer;
        transition: transform 0.3s ease;
    }}
    .hcp-logo-container:hover {{
        transform: scale(1.03);
    }}
    .hcp-logo {{
        height: 40px;
        width: auto;
        background: white;
        padding: 4px 10px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}
    .hcp-title {{
        color: white;
        font-family: 'Tajawal', 'Segoe UI', sans-serif;
        font-weight: 700;
        font-size: 0.98rem;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
        line-height: 1.3;
    }}
    .hcp-title-ar {{
        font-size: 0.82rem;
        color: {PALETTE['hcp_light_gold']};
        font-weight: 500;
        margin-bottom: 2px;
    }}
    .hcp-badges {{
        display: flex;
        gap: 0.9rem;
        align-items: center;
    }}
    .hcp-badge {{
        padding: 0;
        background: transparent;
        border: 0;
        border-radius: 0;
        color: {PALETTE['hcp_light_gold']};
        font-size: 0.76rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        cursor: default;
        user-select: text;
    }}
    .hcp-badge + .hcp-badge {{
        position: relative;
    }}
    .hcp-badge + .hcp-badge::before {{
        content: "";
        position: absolute;
        left: -0.6rem;
        top: 50%;
        width: 1px;
        height: 1rem;
        background: rgba(232, 200, 122, 0.45);
        transform: translateY(-50%);
    }}
    .morocco-flag {{
        width: 24px;
        height: 17px;
        border-radius: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }}
    
    
    .stApp {{
        padding-top: 54px;
        background:
            linear-gradient(135deg, rgba(107, 31, 58, 0.05), transparent 32rem),
            linear-gradient(225deg, rgba(212, 167, 74, 0.08), transparent 30rem),
            linear-gradient(180deg, #FFFFFF 0%, {PALETTE['bg']} 34%, {PALETTE['surface']} 100%);
    }}
    [data-testid="stAppViewContainer"] {{
        position: relative;
        z-index: 0;
    }}
    
    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0.8rem !important;
        padding-left: 1rem;
    }}
    
    [data-testid="stAppViewContainer"]:has(section[data-testid="stSidebar"][aria-expanded="false"]) {{
        margin-left: 0 !important;
    }}
    .block-container {{
        max-width: 1440px;
        padding-top: 0.5rem;
        padding-bottom: 4rem;
        position: relative;
        z-index: 0;
    }}
    h1, h2, h3, h4, h5 {{
        color: {PALETTE['ink']};
        font-family: 'Tajawal', 'Segoe UI', sans-serif;
        letter-spacing: 0;
    }}
    
    
    [data-testid="stMarkdownContainer"] h3 {{
        font-size: 1.45rem;
        font-weight: 700;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
        line-height: 1.3;
    }}
    [data-testid="stMarkdownContainer"] h4 {{
        font-size: 1.2rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
        line-height: 1.3;
    }}
    [data-testid="stMarkdownContainer"] h5 {{
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
        line-height: 1.3;
    }}
    p, span, label, div {{
        font-family: 'Tajawal', 'Segoe UI', sans-serif;
    }}
    div[data-testid="stMetric"] {{
        position: relative;
        overflow: visible;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.96));
        border: 1px solid {PALETTE['line']};
        border-radius: 12px;
        padding: 12px 14px 13px 14px;
        min-height: 82px;
        box-shadow: 0 10px 24px rgba(17, 24, 39, 0.07);
        animation: fadeUp 560ms ease both;
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        border-color: rgba(212, 167, 74, 0.45);
        box-shadow: 0 14px 30px rgba(107, 31, 58, 0.10);
    }}
    div[data-testid="stMetricLabel"] {{
        color: {PALETTE['muted']};
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    div[data-testid="stMetricValue"] {{
        color: {PALETTE['ink']};
        font-size: 1.18rem;
        font-weight: 800;
        word-wrap: break-word;
        overflow-wrap: break-word;
        word-break: break-word;
        white-space: normal !important;
        line-height: 1.22;
        max-width: 100%;
    }}
    section[data-testid="stSidebar"] {{
        position: relative;
        z-index: 0;
        zoom: 0.8;
        background:
            linear-gradient(180deg, rgba(107, 31, 58, 0.02) 0%, rgba(245, 242, 237, 0.98) 100%);
        border-right: 1px solid {PALETTE['line']};
    }}
    
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        display: none !important;
    }}
    
    
    
    [data-testid="collapsedControl"],
    [data-testid*="SidebarCollapsed"] {{
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        overflow: visible !important;
    }}

    
    [data-testid="stHeader"],
    [data-testid="stAppHeader"],
    [data-testid="stToolbar"],
    [data-testid="stAppToolbar"] {{
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        border: 0 !important;
    }}
    
    
    button[kind="header"],
    button[kind="headerNoPadding"],
    [data-testid="stExpandSidebarButton"] {{
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: fixed !important;
        left: 0.5rem !important;
        top: 62px !important;
        z-index: 999998 !important;
        background: transparent !important;
        background-color: transparent !important;
        border: 0 !important;
        box-shadow: none !important;
        padding: 0.4rem !important;
        min-width: unset !important;
        max-width: unset !important;
        width: auto !important;
        height: auto !important;
        margin: 0 !important;
    }}
    
    
    button[kind="header"] > *,
    button[kind="headerNoPadding"] > *,
    [data-testid="stExpandSidebarButton"] > * {{
        background: transparent !important;
        background-color: transparent !important;
    }}
    
    
    button[kind="header"]:hover,
    button[kind="headerNoPadding"]:hover,
    [data-testid="stExpandSidebarButton"]:hover {{
        background-color: rgba(107, 31, 58, 0.15) !important;
        border-radius: 8px !important;
    }}
    
    
    button[kind="header"] svg,
    button[kind="headerNoPadding"] svg,
    [data-testid="stExpandSidebarButton"] svg {{
        color: {PALETTE['hcp_bordeaux']} !important;
        opacity: 0.9 !important;
        width: 20px !important;
        height: 20px !important;
        display: block !important;
    }}
    
    button[kind="header"]:hover svg,
    button[kind="headerNoPadding"]:hover svg,
    [data-testid="stExpandSidebarButton"]:hover svg {{
        opacity: 1 !important;
        color: {PALETTE['hcp_gold']} !important;
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding: 0.5rem 1rem 0.5rem 1rem;
        overflow: visible;
    }}
    
    section[data-testid="stSidebar"] .block-container::-webkit-scrollbar {{
        display: none;
    }}
    [data-testid="stSidebarHeader"] {{
        min-height: 0 !important;
        height: auto !important;
        padding: 0.35rem 0.5rem 0 0.5rem !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{
        color: {PALETTE['ink']};
        font-size: 1.05rem;
        margin-bottom: 0.25rem;
    }}
    section[data-testid="stSidebar"] label {{
        color: {PALETTE['ink']};
        font-weight: 750;
        font-size: 0.82rem;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        border-radius: 12px;
        border-color: {PALETTE['line']};
        background: rgba(255,255,255,0.92);
        box-shadow: 0 8px 18px rgba(17, 24, 39, 0.05);
    }}
    section[data-testid="stSidebar"] div[data-baseweb="tag"] {{
        background: rgba(212, 167, 74, 0.12);
        color: {PALETTE['hcp_bordeaux']};
        border-radius: 9px;
        border: 1px solid rgba(212, 167, 74, 0.25);
    }}
    section[data-testid="stSidebar"] hr {{
        margin: 1rem 0;
        border-color: rgba(217, 226, 236, 0.75);
    }}
    .sidebar-panel {{
        position: relative;
        overflow: hidden;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 14px;
        border: 1px solid rgba(217, 226, 236, 0.90);
        background:
            linear-gradient(180deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92));
        box-shadow: 0 16px 34px rgba(17, 24, 39, 0.08);
        animation: fadeUp 520ms ease both;
    }}
    .sidebar-panel::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, {PALETTE['hcp_bordeaux']}, {PALETTE['hcp_gold']});
    }}
    .sidebar-kicker {{
        display: inline-flex;
        padding: 0.22rem 0.55rem;
        border-radius: 9px;
        background: rgba(212, 167, 74, 0.12);
        color: {PALETTE['hcp_bordeaux']};
        font-size: 0.70rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .sidebar-title {{
        margin: 0.55rem 0 0.25rem 0;
        color: {PALETTE['ink']};
        font-size: 1.12rem;
        line-height: 1.25;
        font-weight: 850;
    }}
    .sidebar-copy {{
        margin: 0;
        color: {PALETTE['muted']};
        font-size: 0.86rem;
        line-height: 1.48;
    }}
    .sidebar-stat-grid {{
        display: grid;
        gap: 0.55rem;
        margin-top: 0.7rem;
    }}
    .sidebar-stat {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.75rem;
        padding: 0.65rem 0.7rem;
        border-radius: 12px;
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(217, 226, 236, 0.88);
    }}
    .sidebar-stat span:first-child {{
        color: {PALETTE['muted']};
        font-size: 0.78rem;
        font-weight: 700;
    }}
    .sidebar-stat span:last-child {{
        color: {PALETTE['ink']};
        font-size: 0.9rem;
        font-weight: 850;
        text-align: right;
    }}
    .sidebar-hint {{
        margin-top: 0.8rem;
        padding: 0.72rem 0.78rem;
        border-radius: 12px;
        background: rgba(212, 167, 74, 0.08);
        border: 1px solid rgba(212, 167, 74, 0.20);
        color: {PALETTE['muted']};
        font-size: 0.82rem;
        line-height: 1.45;
    }}
    
    [data-testid="stTabs"] div:has(> [data-testid="stTab"]) {{
        gap: 6px;
        background: linear-gradient(135deg, 
            rgba(255,255,255,0.98) 0%, 
            rgba(250,249,247,0.96) 50%, 
            rgba(248,250,252,0.95) 100%);
        border: 1.5px solid rgba(229, 221, 214, 0.85);
        border-radius: 14px;
        padding: 6px 8px;
        box-shadow: 
            0 12px 32px rgba(17, 24, 39, 0.06),
            0 6px 16px rgba(107, 31, 58, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        position: relative;
        z-index: 2;
        backdrop-filter: blur(20px) saturate(180%);
    }}
    [data-testid="stTab"] {{
        position: relative;
        height: 46px;
        border-radius: 10px;
        color: {PALETTE['muted']};
        font-family: 'Poppins', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        font-weight: 600;
        line-height: 1.2;
        padding: 0 20px;
        margin: 0 !important;
        border: 1px solid transparent;
        transition: background 220ms ease, color 220ms ease, border-color 220ms ease;
        display: flex;
        align-items: center;
        justify-content: center;
        letter-spacing: 0.01em;
        text-transform: none;
        overflow: hidden;
        text-rendering: optimizeLegibility;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}
    [data-testid="stTab"]:hover {{
        background: rgba(212, 167, 74, 0.12);
        color: {PALETTE['ink']};
        border-color: rgba(212, 167, 74, 0.22);
    }}
    [data-testid="stTab"][aria-selected="true"] {{
        background: rgba(107, 31, 58, 0.09);
        color: {PALETTE['hcp_bordeaux']};
        font-weight: 700;
        border-color: rgba(107, 31, 58, 0.16);
        box-shadow: 
            0 3px 10px rgba(107, 31, 58, 0.10),
            inset 0 1px 0 rgba(255, 255, 255, 0.6);
    }}
    [data-testid="stTab"][aria-selected="true"]::after {{
        content: "";
        position: absolute;
        bottom: 4px;
        left: 14px;
        right: 14px;
        height: 3px;
        border-radius: 3px;
        background: linear-gradient(90deg, 
            {PALETTE['hcp_bordeaux']} 0%, 
            {PALETTE['hcp_gold']} 100%);
    }}
    [data-testid="stTabPanel"] {{
        animation: fadeUp 450ms cubic-bezier(0.4, 0, 0.2, 1) both;
        padding-top: 1.4rem;
    }}
    .hero-shell {{
        position: relative;
        overflow: hidden;
        z-index: 1;
        background:
            linear-gradient(120deg, rgba(107, 31, 58, 0.95), rgba(74, 21, 40, 0.92) 40%, rgba(193, 68, 14, 0.88)),
            url("https://images.unsplash.com/photo-1569163139394-de4798aa62b6?auto=format&fit=crop&w=1600&q=70");
        background-size: cover;
        background-position: center;
        color: white;
        border-radius: 18px;
        padding: 1.8rem 1.9rem 1.5rem 1.9rem;
        margin: 0.5rem 0 1.1rem 0;
        box-shadow: 0 24px 64px rgba(107, 31, 58, 0.28);
        animation: fadeUp 520ms ease both, pulseGlow 5.8s ease-in-out infinite;
        transition: margin-left 0.3s ease, max-width 0.3s ease;
    }}
    .hero-shell::after {{
        content: "";
        position: absolute;
        inset: 0;
        width: 42%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.26), transparent);
        animation: sheen 5s ease-in-out infinite;
        pointer-events: none;
    }}
    .hero-kicker {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0 0 0 0.72rem;
        border-left: 3px solid {PALETTE['hcp_light_gold']};
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.76rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 800;
        cursor: default;
        user-select: text;
    }}
    .hero-title {{
        margin: 0.55rem 0 0.35rem 0;
        font-size: 2.55rem;
        line-height: 1.08;
        font-weight: 800;
        letter-spacing: 0;
        color: white;
        max-width: 62rem;
    }}
    .hero-subtitle {{
        margin: 0;
        max-width: 68rem;
        color: rgba(255, 255, 255, 0.84);
        font-size: 1.02rem;
        line-height: 1.6;
    }}
    .hero-meta {{
        display: flex;
        flex-wrap: wrap;
        column-gap: 1.45rem;
        row-gap: 0.45rem;
        margin-top: 1rem;
    }}
    .hero-meta span {{
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0;
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.84rem;
        font-weight: 700;
        cursor: default;
        user-select: text;
    }}
    .hero-meta span + span::before {{
        content: "";
        position: absolute;
        left: -0.75rem;
        top: 50%;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: rgba(232, 200, 122, 0.85);
        transform: translateY(-50%);
    }}
    .section-eyebrow {{
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {PALETTE['hcp_bordeaux']};
        margin-bottom: 0.4rem;
    }}
    .card-note {{
        background: rgba(212, 167, 74, 0.08);
        border: 1px solid rgba(212, 167, 74, 0.2);
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        font-size: 0.85rem;
        line-height: 1.5;
        color: {PALETTE['muted']};
    }}
    .card-note strong {{
        color: {PALETTE['ink']};
    }}
    .insight-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        margin: 1rem 0 1.2rem 0;
    }}
    .insight-card {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, #FFFFFF, #F8FAFC);
        border: 1px solid {PALETTE['line']};
        border-radius: 14px;
        padding: 1.05rem 1.1rem;
        box-shadow: 0 16px 38px rgba(17, 24, 39, 0.07);
        animation: fadeUp 620ms ease both;
        transition: transform 180ms ease, box-shadow 180ms ease;
    }}
    .insight-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 24px 54px rgba(17, 24, 39, 0.12);
    }}
    .insight-card::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, {PALETTE['hcp_bordeaux']}, {PALETTE['hcp_gold']}, {PALETTE['degraded']});
    }}
    .insight-card .label {{
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {PALETTE['muted']};
        margin-bottom: 0.35rem;
    }}
    .insight-card h3 {{
        margin: 0;
        font-size: 1.15rem;
        line-height: 1.2;
    }}
    .insight-card p {{
        margin: 0.45rem 0 0 0;
        color: {PALETTE['muted']};
        font-size: 0.92rem;
        line-height: 1.5;
    }}
    .page-title {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 0.15rem;
        font-weight: 700;
        color: {PALETTE['ink']};
    }}
    .section-title {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.4rem 0 0.6rem 0;
        font-weight: 600;
        color: {PALETTE['ink']};
    }}
    .icon-inline {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
    }}
    .summary-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.7rem;
        border-radius: 10px;
        border: 1px solid {PALETTE['line']};
        background: rgba(255, 255, 255, 0.86);
        color: {PALETTE['muted']};
        font-size: 0.83rem;
        font-weight: 700;
        box-shadow: 0 8px 18px rgba(17, 24, 39, 0.05);
    }}
    .abbreviation-note {{
        margin-top: 1rem;
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background: rgba(212, 167, 74, 0.08);
        border: 1px solid rgba(212, 167, 74, 0.2);
        font-size: 0.82rem;
        line-height: 1.6;
        color: {PALETTE['muted']};
    }}
    .abbreviation-note strong {{
        color: {PALETTE['ink']};
        font-weight: 700;
    }}
    .abbreviation-list {{
        margin-top: 0.5rem;
        padding-left: 0;
        list-style: none;
    }}
    .abbreviation-list li {{
        margin-bottom: 0.3rem;
        padding-left: 1.2rem;
        position: relative;
    }}
    .abbreviation-list li::before {{
        content: "*";
        position: absolute;
        left: 0;
        color: {PALETTE['hcp_gold']};
        font-weight: bold;
        font-size: 1.1em;
    }}
    .download-button-spacer {{
        height: 0.75rem;
    }}
    .method-note {{
        box-sizing: border-box;
        width: 100%;
        max-width: 100%;
        margin: 0.5rem 0 0.75rem 0;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        border: 1px solid rgba(212, 167, 74, 0.2);
        background: rgba(212, 167, 74, 0.08);
        color: {PALETTE['muted']};
        font-size: 0.85rem;
        line-height: 1.55;
        overflow-wrap: anywhere;
        word-break: normal;
    }}
    .method-note strong {{
        color: {PALETTE['ink']};
    }}
    
    .dataframe {{
        width: 100%;
        border-collapse: collapse;
        font-family: 'Tajawal', 'Segoe UI', sans-serif;
        font-size: 0.9rem;
        margin: 1rem 0;
    }}
    .dataframe thead {{
        background: linear-gradient(135deg, {PALETTE['hcp_bordeaux']}, {PALETTE['hcp_gold']});
    }}
    .dataframe thead th {{
        color: white;
        font-weight: 700;
        padding: 0.8rem 1rem;
        text-align: left;
        border-bottom: 2px solid {PALETTE['hcp_gold']};
    }}
    .dataframe tbody tr {{
        border-bottom: 1px solid {PALETTE['line']};
        transition: background-color 0.2s ease;
    }}
    .dataframe tbody tr:hover {{
        background-color: rgba(212, 167, 74, 0.08);
    }}
    .dataframe tbody td {{
        padding: 0.7rem 1rem;
        color: {PALETTE['ink']};
    }}
    .dataframe tbody tr:nth-child(even) {{
        background-color: rgba(250, 249, 247, 0.5);
    }}
    .chart-source-note {{
        margin: 0.45rem 0 1rem 0.15rem;
        color: {PALETTE['muted']};
        font-size: 0.84rem;
        line-height: 1.45;
        font-style: italic;
    }}
    div[data-testid="stPlotlyChart"] {{
        border: 1px solid {PALETTE['line']};
        border-radius: 14px;
        overflow: hidden;
        background: #FFFFFF;
        box-shadow: 0 18px 42px rgba(17, 24, 39, 0.08);
        animation: fadeUp 580ms ease both;
        transition: transform 180ms ease, box-shadow 180ms ease;
    }}
    div[data-testid="stPlotlyChart"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 24px 56px rgba(17, 24, 39, 0.12);
    }}
    
    div[data-testid="stPlotlyChart"] .hoverlayer .legendtitletext {{
        font-size: 16px !important;
        font-weight: 800 !important;
        fill: {PALETTE['ink']} !important;
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid {PALETTE['line']};
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 14px 32px rgba(17, 24, 39, 0.07);
        animation: fadeUp 560ms ease both;
    }}
    .stSlider [data-baseweb="slider"] > div {{
        color: {PALETTE['hcp_bordeaux']};
    }}
    @media (max-width: 900px) {{
        .insight-grid {{
            grid-template-columns: 1fr;
        }}
        .hero-title {{
            font-size: 1.9rem;
        }}
        [data-testid="stTabs"] div:has(> [data-testid="stTab"]) {{
            overflow-x: auto;
        }}
    }}

    
    
    .hcp-footer {{
        margin-top: 2rem;
        border-top: 1px solid {PALETTE['line']};
        font-family: 'Inter', 'Tajawal', system-ui, sans-serif;
        content-visibility: auto;
        contain-intrinsic-size: 0 110px;
    }}

    
    .hcp-footer-sources {{
        display: flex;
        align-items: flex-start;
        gap: 0;
        padding: 1rem 0 0.9rem 0;
        flex-wrap: wrap;
        row-gap: 0.65rem;
    }}
    .hcp-footer-source-col {{
        flex: 1 1 160px;
        padding: 0 1rem;
    }}
    .hcp-footer-source-col:first-child {{
        padding-left: 0;
    }}
    .hcp-footer-divider {{
        width: 1px;
        align-self: stretch;
        background: {PALETTE['line']};
        flex-shrink: 0;
    }}
    .hcp-footer-source-label {{
        font-size: 0.67rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: {PALETTE['hcp_bordeaux']};
        margin-bottom: 0.22rem;
    }}
    .hcp-footer-source-value {{
        font-size: 0.76rem;
        color: {PALETTE['muted']};
        line-height: 1.5;
    }}

    
    .hcp-footer-bottom {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 0.65rem 0 3.5rem 0;
        border-top: 1px solid {PALETTE['line']};
    }}
    .hcp-footer-copyright {{
        font-size: 0.73rem;
        color: {PALETTE['muted']};
        font-weight: 500;
    }}
    .hcp-footer-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        align-items: center;
        justify-content: center;
    }}

    
    .hcp-footer-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0;
        background: none;
        border: none;
        border-radius: 0;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        cursor: default;
        user-select: none;
        pointer-events: none;
    }}
    .hcp-footer-badge svg {{
        opacity: 0.75;
        flex-shrink: 0;
    }}
    .hcp-footer-badge--bordeaux {{ color: {PALETTE['hcp_bordeaux']}; }}
    .hcp-footer-badge--gold     {{ color: #8A6418; }}
    .hcp-footer-badge--green    {{ color: {PALETTE['improved']}; }}
    .hcp-footer-badge--neutral  {{ color: {PALETTE['muted']}; }}

    
    .hcp-footer-badge + .hcp-footer-badge::before {{
        content: "·";
        margin-right: 0.3rem;
        color: {PALETTE['line']};
        font-weight: 400;
        pointer-events: none;
    }}

    .hcp-footer-version {{
        font-size: 0.71rem;
        font-family: 'Courier New', monospace;
        color: {PALETTE['muted']};
        opacity: 0.6;
        white-space: nowrap;
    }}

    @media (max-width: 900px) {{
        .hcp-footer-sources {{
            flex-direction: column;
            gap: 0.55rem;
        }}
        .hcp-footer-divider {{
            display: none;
        }}
        .hcp-footer-source-col {{
            padding: 0;
        }}
        .hcp-footer-bottom {{
            flex-direction: column;
            align-items: flex-start;
            gap: 0.45rem;
        }}
        .hcp-footer-badge + .hcp-footer-badge::before {{
            display: none;
        }}
    }}
</style>

"""




st.set_page_config(
    page_title="Dégradation des Terres & Sécheresse — Maroc",
    page_icon=str(ASSETS_DIR / "drought.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)



st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


_hcp_logo_b64 = get_base64_image('assets/hcp_logo.jpg')
_maroc_icon_b64 = get_base64_image('assets/maroc.png')


st.markdown(f"""
<div class="hcp-topbar">
    <div class="hcp-logo-container" onclick="window.location.reload();">
        <img src="data:image/png;base64,{_hcp_logo_b64}" class="hcp-logo" alt="HCP Logo">
        <div>
            <div class="hcp-title-ar">المندوبية السامية للتخطيط</div>
            <div class="hcp-title">HAUT-COMMISSARIAT AU PLAN</div>
        </div>
    </div>
    <div class="hcp-badges">
        <div class="hcp-badge">
            <img src="data:image/png;base64,{_maroc_icon_b64}" class="morocco-flag" alt="Maroc">
            Royaume du Maroc
        </div>
        <div class="hcp-badge">
            SDG 15.3.1
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

hero_placeholder = st.empty()
hero_placeholder.markdown(
    """
    <div class="hero-shell">
        <div class="hero-kicker">Maroc | SDG 15.3.1 | Analyse décisionnelle</div>
        <div class="hero-title">Dégradation des terres & vulnérabilité à la sécheresse</div>
        <div class="hero-meta">
            <span>Préparation des données...</span>
            <span>Référentiel: HCP / Trends.Earth / SDG 15.3.1</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

DROUGHT_COLORS = {
    "Aucune sécheresse": "#A9BFAE",
    "Légère": "#D8C79A",
    "Modérée": "#CE9B5C",
    "Sévère": "#B5654A",
    "Extrême": "#7A3B2E",
}

STATUS_EXP_COLORS = {
    "Dégradation persistante": "#7A3B2E",
    "Dégradation récente": "#B5654A",
    "Dégradation baseline": "#D9A28A",
    "Stabilité": "#B8A98A",
    "Amélioration baseline": "#B7C9AE",
    "Amélioration récente": "#7FA189",
    "Amélioration persistante": "#4C6B58",
}

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=PALETTE["card"],
        plot_bgcolor=PALETTE["card"],
        font=dict(color=PALETTE["ink"], family="Aptos, Segoe UI, sans-serif"),
        margin=dict(l=18, r=18, t=54, b=18),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=PALETTE["line"],
            font=dict(color=PALETTE["ink"], size=13),
        ),
        transition=dict(duration=450, easing="cubic-in-out"),
    )
)


def polish_chart(fig: go.Figure, height: int | None = None, show_source: bool = True, source_text: str | None = None) -> go.Figure:
    """
    Polit un graphique Plotly avec le style HCP et ajoute optionnellement une source.
    
    Args:
        fig: Figure Plotly à polir
        height: Hauteur du graphique en pixels
        show_source: Afficher la source sous le graphique
        source_text: Texte de source personnalisé (sinon utilise la source par défaut)
    """
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=height,
        hovermode="closest",
        bargap=0.22,
        showlegend=True,
        
        margin=dict(l=18, r=18, t=60, b=18),
        
        autosize=True,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(217, 226, 236, 0.70)",
        zeroline=False,
        linecolor=PALETTE["line"],
        tickfont=dict(color=PALETTE["muted"]),
        title_font=dict(color=PALETTE["muted"]),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(217, 226, 236, 0.70)",
        zeroline=False,
        linecolor=PALETTE["line"],
        tickfont=dict(color=PALETTE["muted"]),
        title_font=dict(color=PALETTE["muted"]),
        tickformat=".2f",  
        automargin=True,
    )
    
    
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            bordercolor=PALETTE["line"],
            font=dict(color=PALETTE["ink"], size=13),
            align="left",
        )
    )
    
    return fig


def format_int(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def format_pct_hover(fig: go.Figure, precision: int = 1) -> go.Figure:
    """
    Formate les tooltips pour afficher les pourcentages avec une précision définie.
    Par défaut: 1 décimale (61.4% au lieu de 61.3953616%)
    
    Args:
        fig: Figure Plotly à modifier
        precision: Nombre de décimales (0, 1, ou 2)
    
    Returns:
        Figure modifiée
    """
    hovertemplate = getattr(fig.data[0], "hovertemplate", None) if fig.data else None
    fig.update_traces(
        hovertemplate=hovertemplate.replace("%{y}", f"%{{y:.{precision}f}}")
        if hovertemplate
        else None
    )
    return fig


def format_pct(value: float, decimals: int = 2) -> str:
    """
    Formate un pourcentage avec le nombre de décimales spécifié.
    
    Args:
        value: Valeur à formater
        decimals: Nombre de décimales (défaut: 2)
    
    Returns:
        Chaîne formatée avec le symbole %
    """
    return f"{value:.{decimals}f}%"


def calculate_entropy_weights(data_df: pd.DataFrame, indicator_columns: list[str]) -> dict[str, float]:
    """
    Calcule les poids d'entropie pour un ensemble d'indicateurs selon la méthode scientifique validée.
    
    Basé sur: Umugwaneza et al. (2025) - Frontiers in Environmental Science
    "Integrated drought index for enhanced multi-factor assessment"
    
    Principe: Plus un indicateur varie entre régions, plus il contient d'information utile,
    donc plus son poids doit être élevé dans le score composite.
    
    Args:
        data_df: DataFrame contenant les données régionales
        indicator_columns: Liste des colonnes à pondérer (ex: ['degradation', 'drought'])
    
    Returns:
        dict: Dictionnaire {nom_indicateur: poids} avec somme des poids = 1.0
        
    Raises:
        ValueError: Si les données sont invalides ou si tous les indicateurs sont constants
    """
    try:
        
        if data_df.empty:
            
            return {col: 1.0 / len(indicator_columns) for col in indicator_columns}
        
        if len(data_df) < 2:
            
            return {col: 1.0 / len(indicator_columns) for col in indicator_columns}
        
        
        normalized = pd.DataFrame()
        for col in indicator_columns:
            if col not in data_df.columns:
                
                normalized[col] = 0
                continue
            
            values = data_df[col].fillna(0)  
            min_val = values.min()
            max_val = values.max()
            
            if max_val > min_val:
                
                normalized[col] = (values - min_val) / (max_val - min_val)
            else:
                
                normalized[col] = 0.5
        
        
        proportions = pd.DataFrame()
        for col in indicator_columns:
            col_sum = normalized[col].sum()
            if col_sum > 0:
                proportions[col] = normalized[col] / col_sum
            else:
                
                proportions[col] = 1.0 / len(data_df)
        
        
        n = len(data_df)  
        k = 1.0 / np.log(n) if n > 1 else 1.0
        
        entropies = {}
        for col in indicator_columns:
            
            p = proportions[col].replace(0, 1e-10)
            
            entropy = -k * (p * np.log(p)).sum()
            entropies[col] = entropy
        
        
        diversity = {col: 1.0 - ent for col, ent in entropies.items()}
        
        
        total_diversity = sum(diversity.values())
        
        if total_diversity > 0:
            weights = {col: div / total_diversity for col, div in diversity.items()}
        else:
            
            
            weights = {col: 1.0 / len(indicator_columns) for col in indicator_columns}
        
        
        weight_sum = sum(weights.values())
        if abs(weight_sum - 1.0) > 0.01:  
            
            weights = {col: w / weight_sum for col, w in weights.items()}
        
        return weights
        
    except Exception as e:
        
        print(f"Avertissement: Erreur dans le calcul d'entropie ({str(e)}). Utilisation de poids égaux.")
        return {col: 1.0 / len(indicator_columns) for col in indicator_columns}


def get_abbreviation_note(indicators: list[str] | None = None) -> str:
    """
    Génère une note HTML explicative pour les abréviations utilisées dans les graphiques.
    
    Args:
        indicators: Liste des indicateurs à expliquer (ex: ["SDG", "DVI", "GPG"])
                   Si None, retourne toutes les abréviations
    """
    abbreviations = {
        "SDG": "Sustainable Development Goals (Objectifs de développement durable)",
        "UNCCD": "United Nations Convention to Combat Desertification (Convention des Nations Unies sur la lutte contre la désertification)",
        "GPG": "Good Practice Guidance (Guide de bonnes pratiques)",
        "SO": "Strategic Objective (Objectif stratégique)",
        "DVI": "Drought Vulnerability Index (Indice de vulnérabilité à la sécheresse)",
        "NRT": "Near Real-Time (Quasi temps réel)",
        "ha": "hectare",
        "pp": "points de pourcentage",
    }
    
    
    if indicators is None:
        indicators = list(abbreviations.keys())
    
    
    filtered_abbr = {k: v for k, v in abbreviations.items() if k in indicators}
    
    if not filtered_abbr:
        return ""
    
    abbr_items = "".join([f"<li><strong>{abbr}</strong> : {meaning}</li>" for abbr, meaning in filtered_abbr.items()])
    
    return f"""
    <div class="abbreviation-note">
        <strong>Abréviations :</strong>
        <ul class="abbreviation-list">
            {abbr_items}
        </ul>
    </div>
    """


def to_csv_download_button(df: pd.DataFrame, filename: str, button_label: str, key: str) -> None:
    """Generate a CSV download button for a dataframe"""
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label=button_label,
        data=csv,
        file_name=filename,
        mime='text/csv',
        key=key,
        icon=":material/download:",
    )


def render_chart_source(source_text: str = SOURCE_LAND) -> None:
    st.markdown(f'<div class="chart-source-note">{source_text}</div>', unsafe_allow_html=True)


def render_footer() -> None:
    """Affiche le footer professionnel du dashboard avec design amélioré"""
    st.markdown("---")
    
    
    footer_html = f"""
    <div style="max-width: 1200px; margin: 2rem auto 0 auto; position: relative;">
        
        
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="
                display: inline-flex;
                align-items: center;
                gap: 0.6rem;
                padding: 0.5rem 1.2rem;
                background: linear-gradient(135deg, {PALETTE['hcp_bordeaux']}15, {PALETTE['hcp_bordeaux']}08);
                border: 1px solid {PALETTE['hcp_gold']}40;
                border-radius: 50px;
                margin-bottom: 1rem;
            ">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z" fill="{PALETTE['hcp_gold']}" stroke="{PALETTE['hcp_bordeaux']}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span style="
                    color: {PALETTE['hcp_bordeaux']};
                    font-size: 0.85rem;
                    font-weight: 700;
                    letter-spacing: 0.05em;
                    text-transform: uppercase;
                ">Source des données</span>
            </div>
        </div>
        
        
        <div style="
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.9));
            border: 1px solid {PALETTE['line']};
            border-left: 4px solid {PALETTE['hcp_gold']};
            border-radius: 16px;
            padding: 2rem 2.5rem;
            box-shadow: 0 8px 24px rgba(107, 31, 58, 0.08);
            margin-bottom: 2rem;
        ">
            
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <h3 style="
                    margin: 0;
                    color: {PALETTE['hcp_gold']};
                    font-size: 1.1rem;
                    font-weight: 800;
                    letter-spacing: 0.02em;
                ">Indicateur SDG 15.3.1 / UNCCD SO2 / UNCCD SO3</h3>
            </div>
            
            
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 1.5rem;
            ">
                
                <div style="
                    padding: 1.2rem;
                    background: rgba(107, 31, 58, 0.04);
                    border-radius: 12px;
                    border: 1px solid {PALETTE['hcp_bordeaux']}20;
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 0.6rem;
                        margin-bottom: 0.7rem;
                    ">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 2L2 7l10 5 10-5-10-5z" fill="{PALETTE['hcp_bordeaux']}" opacity="0.2"/>
                            <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="{PALETTE['hcp_bordeaux']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <strong style="
                            color: {PALETTE['hcp_bordeaux']};
                            font-size: 0.85rem;
                            font-weight: 700;
                        ">Méthodologie</strong>
                    </div>
                    <p style="
                        margin: 0;
                        color: {PALETTE['muted']};
                        font-size: 0.82rem;
                        line-height: 1.6;
                    ">
                        Trends.Earth v2.2.6<br>
                        UNCCD GPG 15.3.1 v2 (2021)<br>
                        GPG-SO3 (2021) · Addendum 2025
                    </p>
                </div>
                
                
                <div style="
                    padding: 1.2rem;
                    background: rgba(212, 167, 74, 0.08);
                    border-radius: 12px;
                    border: 1px solid {PALETTE['hcp_gold']}30;
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 0.6rem;
                        margin-bottom: 0.7rem;
                    ">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="10" stroke="{PALETTE['hcp_gold']}" stroke-width="2"/>
                            <path d="M12 6v6l4 2" stroke="{PALETTE['hcp_gold']}" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        <strong style="
                            color: {PALETTE['hcp_gold']};
                            font-size: 0.85rem;
                            font-weight: 700;
                        ">Période de référence</strong>
                    </div>
                    <p style="
                        margin: 0;
                        color: {PALETTE['muted']};
                        font-size: 0.82rem;
                        line-height: 1.6;
                    ">
                        2001–2015<br>
                        <span style="opacity: 0.7;">Baseline pour l'évaluation</span>
                    </p>
                </div>
                
                
                <div style="
                    padding: 1.2rem;
                    background: rgba(74, 124, 89, 0.08);
                    border-radius: 12px;
                    border: 1px solid {PALETTE['improved']}30;
                ">
                    <div style="
                        display: flex;
                        align-items: center;
                        gap: 0.6rem;
                        margin-bottom: 0.7rem;
                    ">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="{PALETTE['improved']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <strong style="
                            color: {PALETTE['improved']};
                            font-size: 0.85rem;
                            font-weight: 700;
                        ">Période de suivi</strong>
                    </div>
                    <p style="
                        margin: 0;
                        color: {PALETTE['muted']};
                        font-size: 0.82rem;
                        line-height: 1.6;
                    ">
                        2016–2025<br>
                        <span style="opacity: 0.7;">Monitoring actif</span>
                    </p>
                </div>
            </div>
            
            
            <div style="
                padding: 1rem 1.5rem;
                background: rgba(245, 242, 237, 0.5);
                border-radius: 10px;
                border: 1px solid {PALETTE['line']};
            ">
                <div style="
                    display: flex;
                    align-items: flex-start;
                    gap: 0.8rem;
                ">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="flex-shrink: 0; margin-top: 2px;">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" stroke="{PALETTE['muted']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96" stroke="{PALETTE['muted']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <line x1="12" y1="22.08" x2="12" y2="12" stroke="{PALETTE['muted']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <div style="flex: 1;">
                        <strong style="
                            color: {PALETTE['ink']};
                            font-size: 0.8rem;
                            display: block;
                            margin-bottom: 0.4rem;
                        ">Sources de Données géospatiales et climatiques :</strong>
                        <p style="
                            margin: 0;
                            color: {PALETTE['muted']};
                            font-size: 0.78rem;
                            line-height: 1.6;
                        ">
                            MODIS MOD13Q1 (productivité) · MODIS MCD12Q1 (couverture) · OpenLandMap (carbone du sol) · CHIRPS (sécheresse)
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            padding-top: 1.5rem;
            border-top: 1px solid {PALETTE['line']};
        ">
            
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: {PALETTE['muted']};
                font-size: 0.75rem;
            ">
                <span>© 2025 Haut-Commissariat au Plan (HCP)</span>
            </div>
            
            
            <div style="
                display: flex;
                gap: 0.8rem;
                flex-wrap: wrap;
                justify-content: center;
            ">
                <span style="
                    display: inline-flex;
                    align-items: center;
                    gap: 0.4rem;
                    padding: 0.3rem 0.7rem;
                    background: rgba(212, 167, 74, 0.12);
                    border: 1px solid {PALETTE['hcp_gold']}30;
                    border-radius: 20px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    color: {PALETTE['hcp_gold']};
                ">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.3"/>
                        <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Open Data
                </span>
                <span style="
                    display: inline-flex;
                    align-items: center;
                    gap: 0.4rem;
                    padding: 0.3rem 0.7rem;
                    background: rgba(74, 124, 89, 0.10);
                    border: 1px solid {PALETTE['improved']}30;
                    border-radius: 20px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    color: {PALETTE['improved']};
                ">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Validé UNCCD
                </span>
            </div>
            
            
            <div style="
                color: {PALETTE['muted']};
                font-size: 0.75rem;
                font-family: 'Courier New', monospace;
            ">
                v2.2.6
            </div>
        </div>
    </div>
    """
    
    st.markdown(footer_html, unsafe_allow_html=True)


def render_kpi_row(items: list[tuple[str, str, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)


def build_region_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary_source = df.copy()
    summary_source["class_key"] = summary_source["class"].replace(
        {
            "DÃ©gradÃ©": "Degraded",
            "AmÃ©liorÃ©": "Improved",
            "Dégradé": "Degraded",
            "Amélioré": "Improved",
        }
    )
    summary = (
        summary_source.pivot_table(index="region", columns="class_key", values="pct", aggfunc="sum", fill_value=0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    for column in ["Degraded", "Stable", "Improved"]:
        if column not in summary:
            summary[column] = 0.0
    summary["net_balance"] = summary["Improved"] - summary["Degraded"]
    return summary.sort_values("Degraded", ascending=False).reset_index(drop=True)


def build_drought_risk(df: pd.DataFrame, year: int) -> pd.DataFrame:
    current_year = df[df["year"] == year].copy()
    class_values = current_year["class"].astype(str).str.strip()
    drought_mask = class_values.isin(
        ["Mild", "Moderate", "Severe", "Extreme", "Légère", "Modérée", "Sévère", "Extrême"]
    )
    moderate_plus_mask = class_values.isin(
        ["Moderate", "Severe", "Extreme", "Modérée", "Sévère", "Extrême"]
    )
    severe_extreme_mask = class_values.isin(
        ["Severe", "Extreme", "Sévère", "Extrême"]
    )
    current_year["total_drought"] = current_year["pct"].where(drought_mask, 0)
    current_year["moderate_plus"] = current_year["pct"].where(moderate_plus_mask, 0)
    current_year["severe_extreme"] = current_year["pct"].where(
        severe_extreme_mask, 0
    )
    grouped = current_year.groupby("region", as_index=False).agg(
        total_drought=("total_drought", "sum"),
        moderate_plus=("moderate_plus", "sum"),
        severe_extreme=("severe_extreme", "sum")
    )
    return grouped.sort_values(by="severe_extreme", ascending=False).reset_index(
        drop=True
    )


def build_regional_choropleth_html(
    geojson: dict,
    map_df: pd.DataFrame,
    height_px: int = 420,
) -> str:
    values = map_df.set_index("region")[["pct", "area_ha"]].to_dict("index")

    def color_for_pct(value: float) -> str:
        if value <= 50:
            return "#D4A74A"
        return "#C1440E"

    features = []
    for feature in geojson.get("features", []):
        props = dict(feature.get("properties", {}))
        region = props.get("region")
        row = values.get(region)
        props["selected"] = row is not None
        props["pct_degraded"] = float(row["pct"]) if row is not None else None
        props["area_degraded"] = float(row["area_ha"]) if row is not None else None
        props["fill_color"] = color_for_pct(float(row["pct"])) if row is not None else "#E6E1D8"
        features.append(
            {
                "type": "Feature",
                "geometry": feature.get("geometry"),
                "properties": props,
            }
        )

    map_geojson = {"type": "FeatureCollection", "features": features}
    geojson_json = json.dumps(map_geojson, ensure_ascii=False)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">
        <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: {height_px}px;
                overflow: hidden;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            #regional-map {{
                position: relative;
                width: 100%;
                height: {height_px}px;
                border-radius: 14px;
                overflow: hidden;
                background: #E9EEF0;
                box-shadow: inset 0 0 0 1px rgba(45, 27, 31, 0.08);
            }}
            .maplibregl-ctrl-group {{
                border: 1px solid rgba(45, 27, 31, 0.14);
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 16px rgba(45, 27, 31, 0.14);
            }}
            .maplibregl-ctrl-group button {{
                width: 34px;
                height: 34px;
            }}
            .maplibregl-ctrl-scale {{
                border-color: #2D1B1F;
                color: #2D1B1F;
                background: rgba(255, 255, 255, 0.86);
                font-weight: 700;
            }}
            .map-legend {{
                position: absolute;
                left: 14px;
                top: 14px;
                z-index: 2;
                min-width: 170px;
                padding: 11px 13px;
                border: 1px solid rgba(45, 27, 31, 0.12);
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.94);
                box-shadow: 0 6px 18px rgba(45, 27, 31, 0.14);
                color: #2D1B1F;
                font-size: 12px;
            }}
            .legend-title {{
                margin-bottom: 7px;
                font-weight: 800;
            }}
            .legend-row {{
                display: flex;
                align-items: center;
                gap: 7px;
                line-height: 1.55;
            }}
            .legend-swatch {{
                width: 14px;
                height: 14px;
                border: 1px solid rgba(45, 27, 31, 0.18);
                border-radius: 3px;
            }}
            .popup-title {{
                color: #2D1B1F;
                font-weight: 800;
                margin-bottom: 4px;
            }}
            .popup-line {{
                color: #7B6B6E;
                font-size: 12px;
                line-height: 1.45;
            }}
            .map-error {{
                display: none;
                position: absolute;
                left: 50%;
                top: 50%;
                z-index: 3;
                transform: translate(-50%, -50%);
                max-width: 290px;
                padding: 12px 15px;
                border: 1px solid #C1440E;
                border-radius: 8px;
                background: rgba(255, 248, 244, 0.96);
                color: #7A2A0A;
                text-align: center;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div id="regional-map">
            <div class="map-legend">
                <div class="legend-title">% de terres dégradées</div>
                <div class="legend-row"><span class="legend-swatch" style="background:#D4A74A"></span>0 à 50 %</div>
                <div class="legend-row"><span class="legend-swatch" style="background:#C1440E"></span>50 à 100 %</div>
                <div class="legend-row"><span class="legend-swatch" style="background:#E6E1D8"></span>Non sélectionnée</div>
            </div>
            <div id="map-error" class="map-error">Les régions ne peuvent pas être affichées.</div>
        </div>
        <script>
            const geojson = {geojson_json};
            const map = new maplibregl.Map({{
                container: 'regional-map',
                style: {{
                    version: 8,
                    sources: {{
                        'osm': {{
                            type: 'raster',
                            tiles: [
                                'https://a.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
                                'https://b.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
                                'https://c.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png'
                            ],
                            tileSize: 256,
                            attribution: '© OpenStreetMap contributors'
                        }}
                    }},
                    layers: [
                        {{
                            id: 'background',
                            type: 'background',
                            paint: {{ 'background-color': '#E5E3DF' }}
                        }},
                        {{
                            id: 'osm-tiles',
                            type: 'raster',
                            source: 'osm',
                            paint: {{ 'raster-opacity': 1.0 }}
                        }}
                    ]
                }},
                center: [-8.0, 27.5],
                zoom: 4.0,
                minZoom: 4.0,
                maxZoom: 10,
                attributionControl: false,
                renderWorldCopies: false,
                maxBounds: [[-17.5, 20.5], [-0.8, 36.0]]
            }});

            map.addControl(new maplibregl.NavigationControl({{ showCompass: false }}), 'top-right');
            map.addControl(new maplibregl.ScaleControl({{ maxWidth: 140, unit: 'metric' }}), 'bottom-left');

            function collectCoords(geometry, coords) {{
                if (!geometry) return;
                if (geometry.type === 'Polygon') {{
                    geometry.coordinates.flat(1).forEach(coord => coords.push(coord));
                }} else if (geometry.type === 'MultiPolygon') {{
                    geometry.coordinates.flat(2).forEach(coord => coords.push(coord));
                }}
            }}

            map.on('load', () => {{
                if (!geojson.features || !geojson.features.length) {{
                    document.getElementById('map-error').style.display = 'block';
                    return;
                }}
                map.addSource('regions', {{ type: 'geojson', data: geojson }});
                map.addLayer({{
                    id: 'regions-fill',
                    type: 'fill',
                    source: 'regions',
                    paint: {{
                        'fill-color': ['coalesce', ['get', 'fill_color'], '#E6E1D8'],
                        'fill-opacity': ['case', ['get', 'selected'], 0.9, 0.22]
                    }}
                }});
                map.addLayer({{
                    id: 'regions-line',
                    type: 'line',
                    source: 'regions',
                    paint: {{
                        'line-color': '#4A3A3E',
                        'line-width': ['interpolate', ['linear'], ['zoom'], 4, 1.1, 7, 2.2],
                        'line-opacity': 0.82
                    }}
                }});

                const totalFeatures = geojson.features.length;
                const selectedFeatures = geojson.features.filter(f => f.properties.selected);
                
                if (selectedFeatures.length > 0 && selectedFeatures.length < totalFeatures) {{
                    const coords = [];
                    selectedFeatures.forEach(feature => {{
                        collectCoords(feature.geometry, coords);
                    }});
                    if (coords.length) {{
                        const bounds = coords.reduce(
                            (b, coord) => b.extend(coord),
                            new maplibregl.LngLatBounds(coords[0], coords[0])
                        );
                        map.fitBounds(bounds, {{ padding: 28, duration: 0 }});
                    }}
                }}
            }});

            const popup = new maplibregl.Popup({{ closeButton: false, closeOnClick: false }});
            map.on('mousemove', 'regions-fill', (event) => {{
                const props = event.features[0].properties;
                map.getCanvas().style.cursor = 'pointer';
                const pct = props.pct_degraded === null || props.pct_degraded === undefined
                    ? '-'
                    : `${{Number(props.pct_degraded).toFixed(1)}}%`;
                const area = props.area_degraded === null || props.area_degraded === undefined
                    ? '-'
                    : `${{Math.round(Number(props.area_degraded)).toLocaleString('fr-FR')}} ha`;
                popup
                    .setLngLat(event.lngLat)
                    .setHTML(`
                        <div class="popup-title">${{props.region || 'Région'}}</div>
                        <div class="popup-line">Terres dégradées: <b>${{pct}}</b></div>
                        <div class="popup-line">Superficie dégradée: <b>${{area}}</b></div>
                    `)
                    .addTo(map);
            }});
            map.on('mouseleave', 'regions-fill', () => {{
                map.getCanvas().style.cursor = '';
                popup.remove();
            }});
            map.on('error', (event) => {{
                if (event && event.error) {{
                    console.warn('Carte régionale:', event.error);
                    document.getElementById('map-error').style.display = 'block';
                }}
            }});
        </script>
    </body>
    </html>
    """





@st.cache_data(show_spinner=False)
def load_data():
    status = pd.read_csv(DATA_DIR / "status_by_region.csv")
    status_expanded = pd.read_csv(DATA_DIR / "status_expanded_by_region.csv")
    subind = pd.read_csv(DATA_DIR / "sdg1531_subindicators_by_region.csv")
    drought_land = pd.read_csv(DATA_DIR / "so3_1_drought_land_proportion.csv")
    dvi = pd.read_csv(DATA_DIR / "so3_3_dvi_rebuilt.csv")
    sdg_annual = pd.read_csv(DATA_DIR / "sdg1531_degradation_by_region_annual.csv")
    with open(DATA_DIR / "morocco_regions_12.geojson", encoding="utf-8") as f:
        geo = json.load(f)
    
    
    class_translation = {
        "Degraded": "Dégradé",
        "Stable": "Stable",
        "Improved": "Amélioré",
        "Persistent degradation": "Dégradation persistante",
        "Recent degradation": "Dégradation récente",
        "Baseline degradation": "Dégradation baseline",
        "Stability": "Stabilité",
        "Baseline improvement": "Amélioration baseline",
        "Recent improvement": "Amélioration récente",
        "Persistent improvement": "Amélioration persistante",
        "No drought": "Aucune sécheresse",
        "Mild": "Légère",
        "Moderate": "Modérée",
        "Severe": "Sévère",
        "Extreme": "Extrême",
        
        "Productivity": "Productivité",
        "Land cover": "Couverture des terres",
        "Soil organic carbon": "Carbone organique du sol",
    }
    
    
    if "class" in status.columns:
        status["class"] = status["class"].replace(class_translation)
    if "class" in status_expanded.columns:
        status_expanded["class"] = status_expanded["class"].replace(class_translation)
    if "class" in subind.columns:
        subind["class"] = subind["class"].replace(class_translation)
    if "class" in drought_land.columns:
        drought_land["class"] = drought_land["class"].replace(class_translation)
    
    
    
    def fill_missing_classes(df, group_cols):
        """Remplit les classes manquantes avec des valeurs 0 pour chaque groupe"""
        all_classes = ["Dégradé", "Stable", "Amélioré"]
        complete_data = []
        
        
        if isinstance(group_cols, str):
            group_cols = [group_cols]
        
        groups = df[group_cols].drop_duplicates()
        
        for _, group_vals in groups.iterrows():
            
            mask = pd.Series([True] * len(df))
            for col in group_cols:
                mask &= (df[col] == group_vals[col])
            group_data = df[mask]
            
            
            for class_name in all_classes:
                existing = group_data[group_data["class"] == class_name]
                if len(existing) > 0:
                    complete_data.append(existing.iloc[0].to_dict())
                else:
                    
                    class_code = {"Dégradé": -1, "Stable": 0, "Amélioré": 1}[class_name]
                    new_row = group_vals.to_dict()
                    new_row.update({
                        "class_code": class_code,
                        "class": class_name,
                        "area_ha": 0.0,
                        "pct": 0.0,
                    })
                    
                    if "indicator" in group_data.columns:
                        new_row["indicator"] = group_data["indicator"].iloc[0] if len(group_data) > 0 else "Statut"
                    complete_data.append(new_row)
        
        return pd.DataFrame(complete_data)
    
    
    status = fill_missing_classes(status, "region")
    subind = fill_missing_classes(subind, ["region", "indicator"])
    
    
    if "class" in sdg_annual.columns:
        sdg_annual["class"] = sdg_annual["class"].replace(class_translation)
    
    
    available_years = sorted(sdg_annual["year"].unique())
    if 2016 in available_years:
        st.warning("Attention: L'année 2016 est présente dans les données mais devrait être absente selon la méthodologie.")
    
    
    sdg_annual = fill_missing_classes(sdg_annual, ["region", "year"])
    
    return status, status_expanded, subind, drought_land, dvi, geo, sdg_annual


def load_sdg_sources():
    """Charger les sources de couche de statut SDG 15.3.1 (3 classes: Dégradé/Stable/Amélioré)."""
    path = Path(__file__).parent / "maplibre_sdg_sources.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


status, status_expanded, subind, drought_land, dvi, geo, sdg_annual = load_data()
sdg_sources = load_sdg_sources()

REGIONS = sorted(status["region"].unique())
YEARS = sorted(drought_land["year"].unique())
SDG_YEARS = sorted(sdg_annual["year"].unique())  




with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-panel">
            <div class="sidebar-kicker">Comité de pilotage</div>
            <div class="sidebar-title">Périmètre d'analyse</div>
            <p class="sidebar-copy">
            Ciblez les régions et l'année à analyser
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    selected_regions = st.multiselect(
        "Régions", options=REGIONS, default=REGIONS, key="region_filter"
    )
    selected_year = int(
        st.slider(
            "Année (sécheresse)",
            min_value=int(min(YEARS)),
            max_value=int(max(YEARS)),
            value=int(YEARS[-1]),
            step=1,
            key="year_filter",
        )
    )
    if not selected_regions:
        selected_regions = REGIONS

    st.markdown(
        f"""
        <div class="sidebar-panel">
            <div class="sidebar-kicker">Sélection active</div>
            <div class="sidebar-stat-grid">
                <div class="sidebar-stat">
                    <span>Régions</span>
                    <span>{len(selected_regions)} / {len(REGIONS)}</span>
                </div>
                <div class="sidebar-stat">
                    <span>Année sécheresse</span>
                    <span>{selected_year}</span>
                </div>
            </div>
            
        </div>
        """,
        unsafe_allow_html=True,
    )


status_f = status[status["region"].isin(selected_regions)]
status_expanded_f = status_expanded[status_expanded["region"].isin(selected_regions)]
drought_land_selected = drought_land[drought_land["region"].isin(selected_regions)]
drought_land_f = drought_land_selected[drought_land_selected["year"] == selected_year]

region_summary = build_region_summary(status_f)
drought_risk = build_drought_risk(drought_land_selected, selected_year)

degraded_area = status_f.loc[status_f["class"] == "Dégradé", "area_ha"].sum()
total_area = status_f["area_ha"].sum()
pct_degraded = (degraded_area / total_area * 100) if total_area else 0

improved_area = status_f.loc[status_f["class"] == "Amélioré", "area_ha"].sum()
pct_improved = (improved_area / total_area * 100) if total_area else 0

def drought_area_share(df: pd.DataFrame, classes: list[str]) -> float:
    denominator = df["area_ha"].sum()
    numerator = df.loc[df["class"].isin(classes), "area_ha"].sum()
    return (numerator / denominator * 100) if denominator else 0


pct_severe_drought = drought_area_share(drought_land_f, ["Sévère", "Extrême"])
pct_total_drought = drought_area_share(
    drought_land_f, ["Légère", "Modérée", "Sévère", "Extrême"]
)


persistent_deg = status_expanded_f[status_expanded_f["class"] == "Dégradation persistante"]["area_ha"].sum()
recent_deg = status_expanded_f[status_expanded_f["class"] == "Dégradation récente"]["area_ha"].sum()
pct_persistent = (persistent_deg / total_area * 100) if total_area else 0
pct_recent = (recent_deg / total_area * 100) if total_area else 0


if selected_year > min(YEARS):
    drought_prev_year = drought_land_selected[drought_land_selected["year"] == selected_year - 1]
    pct_severe_drought_prev = drought_area_share(drought_prev_year, ["Sévère", "Extrême"])
    drought_evolution = pct_severe_drought - pct_severe_drought_prev
    pct_total_drought_prev = drought_area_share(
        drought_prev_year, ["Légère", "Modérée", "Sévère", "Extrême"]
    )
    total_drought_evolution = pct_total_drought - pct_total_drought_prev
else:
    drought_evolution = 0
    total_drought_evolution = 0

top_degraded_region = region_summary.iloc[0]
top_resilience_region = region_summary.sort_values("net_balance", ascending=False).iloc[0]
top_drought_region = drought_risk.iloc[0]

hero_placeholder.markdown(
    f"""
    <div class="hero-shell">
        <div class="hero-kicker">Maroc | SDG 15.3.1 | Analyse décisionnelle</div>
        <div class="hero-title">Dégradation des terres & vulnérabilité à la sécheresse</div>
        <div class="hero-meta">
            <span>Régions actives: {len(selected_regions)} / {len(REGIONS)}</span>
            <span>Année sécheresse: {selected_year}</span>
            <span>Référentiel: HCP / Trends.Earth / SDG 15.3.1</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)




tab_synthese, tab_carte, tab_degradation, tab_secheresse, tab_dvi, tab_recommandations = st.tabs(
    [
        "Synthèse exécutive",
        "Carte régionale",
        "Dégradation",
        "Sécheresse",
        "Vulnérabilité (DVI)",
        "Recommandations",
    ],
    on_change="rerun",
)




st.markdown(
    f"""
    <div class="hcp-footer">
        <div class="hcp-footer-sources">
            <div class="hcp-footer-source-col">
                <div class="hcp-footer-source-label">Indicateur</div>
                <div class="hcp-footer-source-value">SDG 15.3.1 · UNCCD SO2 · SO3</div>
            </div>
            <div class="hcp-footer-divider"></div>
            <div class="hcp-footer-source-col">
                <div class="hcp-footer-source-label">Méthodologie</div>
                <div class="hcp-footer-source-value">Trends.Earth v2.2.6 · UNCCD GPG 15.3.1 v2 (2021) · GPG-SO3 · Addendum 2025</div>
            </div>
            <div class="hcp-footer-divider"></div>
            <div class="hcp-footer-source-col">
                <div class="hcp-footer-source-label">Données géospatiales et climatiques</div>
                <div class="hcp-footer-source-value">MODIS MOD13Q1 · MCD12Q1 · OpenLandMap · CHIRPS</div>
            </div>
            <div class="hcp-footer-divider"></div>
            <div class="hcp-footer-source-col">
                <div class="hcp-footer-source-label">Périodes</div>
                <div class="hcp-footer-source-value">Référence 2001–2015 · Suivi 2016–2025</div>
            </div>
        </div>
        <div class="hcp-footer-bottom">
            <div class="hcp-footer-copyright">
                © 2026 Haut-Commissariat au Plan (HCP) — Royaume du Maroc
            </div>
            <div class="hcp-footer-badges">
                <span class="hcp-footer-badge hcp-footer-badge--gold"><svg width="11" height="11" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg> Open Data</span>
                <span class="hcp-footer-badge hcp-footer-badge--neutral">Neutralité dégradation des terres (LDN)</span>
            </div>
            <div class="hcp-footer-version">v2.2.6</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if tab_synthese.open:
    with tab_synthese:
        st.markdown("### Synthèse exécutive")
        
        
        render_kpi_row(
            [
                (
                    "Terres dégradées",
                    f"{pct_degraded:.2f}%",
                    "Part de la superficie totale classée « Dégradée » sur l'ensemble des régions sélectionnées. Une valeur élevée signale un besoin d'intervention prioritaire.",
                ),
                (
                    "Terres améliorées",
                    f"{pct_improved:.2f}%",
                    "Part de la superficie totale classée « Améliorée » sur l'ensemble des régions sélectionnées. Reflète l'efficacité des actions de restauration engagées.",
                ),
                (
                    "Superficie en sécheresse",
                    f"{pct_total_drought:.2f}%",
                    f"Part de la superficie sélectionnée exposée à au moins un épisode de sécheresse (toutes classes confondues) en {selected_year}.",
                ),
            ]
        )
        
        
        st.markdown("#### Signaux d'alerte")
        render_kpi_row(
            [
                (
                    "Dégradation persistante",
                    f"{pct_persistent:.2f}%",
                    "Superficie où la dégradation est continue sur toute la période de suivi (2016-2025). Ces zones sont les plus difficiles à restaurer et doivent être traitées en priorité absolue.",
                ),
                (
                    "Dégradation récente",
                    f"{pct_recent:.2f}%",
                    "Superficie dont la dégradation est apparue uniquement dans la période récente. Ce signal d'accélération indique des pressions nouvelles qui méritent une intervention rapide avant aggravation.",
                ),
                (
                    "Régions en sécheresse sévère",
                    f"{int((drought_risk['severe_extreme'] > 0).sum())} / {len(selected_regions)}",
                    f"Nombre de régions présentant au moins une portion de territoire en sécheresse sévère ou extrême en {selected_year}. Indicateur de stress hydrique immédiat.",
                ),
            ]
        )
        st.markdown(
            f"""
            <div class="insight-grid">
                <div class="insight-card">
                    <div class="label">Région la plus dégradée</div>
                    <h3>{top_degraded_region['region']}</h3>
                    <p>{format_pct(float(top_degraded_region['Degraded']))} des terres y sont classées dégradées — priorité d'intervention n°1 sur le périmètre sélectionné.</p>
                </div>
                <div class="insight-card">
                    <div class="label">Meilleur bilan net</div>
                    <h3>{top_resilience_region['region']}</h3>
                    <p>Le solde amélioration − dégradation y est le plus favorable : {format_pct(float(top_resilience_region['net_balance']))}. Bonne pratique à documenter et à répliquer.</p>
                </div>
                <div class="insight-card">
                    <div class="label">Pression climatique maximale</div>
                    <h3>{top_drought_region['region']}</h3>
                    <p>La part de superficie en sécheresse sévère ou extrême y atteint {format_pct(float(top_drought_region['severe_extreme']))} en {selected_year}. Intervention hydrique urgente requise.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        synth_col_1, synth_col_2 = st.columns([1, 1.2])
    
        with synth_col_1:
            st.markdown("##### Répartition des terres par statut")
            
            status_totals = status_f.groupby("class", as_index=False)["area_ha"].sum()
            
            total_area = status_totals["area_ha"].sum()
            status_totals["pct"] = (status_totals["area_ha"] / total_area) * 100
            
            
            status_totals = (
                status_totals.set_index("class")
                .reindex(["Dégradé", "Stable", "Amélioré"])
                .fillna({"area_ha": 0, "pct": 0})
                .reset_index()
            )
            
            fig_status_mix = px.pie(
                status_totals,
                names="class",
                values="pct",
                hole=0.6,
                color="class",
                color_discrete_map={"Dégradé": PALETTE["degraded"], "Stable": PALETTE["stable"], "Amélioré": PALETTE["improved"]},
            )
            
            hovertext_status = [
                (
                    f"<b>{row['class']}</b><br>"
                    f"pourcentage: {float(row['pct']):.1f}%<br>"
                    f"superficie:&nbsp;{format_int(float(row['area_ha'])).replace(' ', '&nbsp;')}&nbsp;ha"
                )
                for _, row in status_totals.iterrows()
            ]
    
            fig_status_mix.update_traces(
                hovertext=hovertext_status,
                textinfo="percent",
                textposition="inside",
                insidetextorientation="radial",
                sort=False,
                marker=dict(line=dict(color="white", width=2)),
                textfont=dict(size=14, color="white"),
                hovertemplate="%{hovertext}<extra></extra>"
            )
            polish_chart(fig_status_mix, height=390, show_source=False)
            fig_status_mix.update_layout(legend_title="")
            st.plotly_chart(fig_status_mix, width="stretch", config={
                'displayModeBar': True,
                'displaylogo': False,
                'modeBarButtonsToRemove': [],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': f'statut_global_{selected_year}',
                    'height': 800,
                    'width': 1200,
                    'scale': 2
                }
            })
            render_chart_source(SOURCE_LAND)
            
            
            status_mix_export = status_totals.rename(
                columns={
                    "class": "Statut",
                    "area_ha": "Superficie (ha)",
                    "pct": "Pourcentage (%)",
                }
            )
            to_csv_download_button(
                status_mix_export[["Statut", "Superficie (ha)", "Pourcentage (%)"]],
                f"statut_global_sdg_{selected_year}.csv",
                "Télécharger en CSV",
                "download_status_mix"
            )
            
        with synth_col_2:
            st.markdown("##### Régions prioritaires")
            priority = region_summary.sort_values("Degraded", ascending=False).head(5).copy()
            priority = priority.rename(
                columns={
                    "region": "Région",
                    "Degraded": "Dégradé",
                    "Stable": "Stable",
                    "Improved": "Amélioré",
                }
            )
            priority = priority[["Région", "Dégradé", "Amélioré", "Stable"]]
            for column in ["Dégradé", "Stable", "Amélioré"]:
                priority[column] = priority[column].map(format_pct)
            st.dataframe(priority, width="stretch", hide_index=True)
            render_chart_source(SOURCE_LAND)
            
            
            priority_export = region_summary.sort_values("Degraded", ascending=False).head(5).copy()
            priority_export = priority_export.rename(
                columns={
                    "region": "Région",
                    "Degraded": "Dégradé (%)",
                    "Stable": "Stable (%)",
                    "Improved": "Amélioré (%)",
                    "net_balance": "Solde net (%)",
                }
            )[["Région", "Dégradé (%)", "Amélioré (%)", "Stable (%)", "Solde net (%)"]]
            to_csv_download_button(
                priority_export,
                f"regions_prioritaires_{selected_year}.csv",
                "Télécharger en CSV",
                "download_priority_regions"
            )
            
            st.markdown(
                '<div class="card-note"><strong>Lecture :</strong> Le classement présente les régions où la part de terres dégradées est la plus élevée, afin d’orienter les priorités d’action.</div>',
                unsafe_allow_html=True,
            )
    
        st.markdown(f"##### Sécheresse sévère et extrême par région — {selected_year}")
        drought_priority = drought_risk.sort_values("severe_extreme", ascending=True)
        drought_priority = drought_priority.copy()
        drought_priority["severe_extreme_label"] = drought_priority["severe_extreme"].map(
            lambda value: f"{value:.4f}%" if abs(value) < 0.1 else f"{value:.1f}%"
        )
        fig_drought_priority = px.bar(
            drought_priority,
            x="severe_extreme",
            y="region",
            orientation="h",
            color="severe_extreme",
            color_continuous_scale=[PALETTE["stable"], PALETTE["accent2"], PALETTE["degraded"]],
            labels={"severe_extreme": "% sévère/extrême", "region": ""},
        )
        polish_chart(fig_drought_priority, height=max(360, len(drought_priority) * 36 + 90), show_source=False)
        fig_drought_priority.update_traces(
            customdata=drought_priority[["severe_extreme_label"]],
            text=drought_priority["severe_extreme_label"],
            textposition="outside",
            hovertemplate="% sévère/extrême: %{customdata[0]}<extra></extra>",
        )
        zero_drought_priority = drought_priority[drought_priority["severe_extreme"] == 0]
        if not zero_drought_priority.empty:
            fig_drought_priority.add_trace(
                go.Scatter(
                    x=[0] * len(zero_drought_priority),
                    y=zero_drought_priority["region"],
                    mode="markers",
                    marker=dict(
                        symbol="circle",
                        size=9,
                        color=PALETTE["muted"],
                        line=dict(color="#FFFFFF", width=1.5),
                    ),
                    customdata=zero_drought_priority[["severe_extreme_label"]],
                    hovertemplate="% sévère/extrême: %{customdata[0]}<extra></extra>",
                    showlegend=False,
                )
            )
        max_severe_extreme = float(drought_priority["severe_extreme"].max()) if not drought_priority.empty else 0
        fig_drought_priority.update_layout(
            coloraxis_showscale=False,
            margin=dict(l=18, r=18, t=0, b=18),
            yaxis=dict(autorange="reversed"),
            xaxis=dict(
                ticksuffix="%",
                range=[0, max(max_severe_extreme * 1.18, 0.1)],
            ),
            uniformtext_minsize=9,
            uniformtext_mode="show",
        )
        st.plotly_chart(fig_drought_priority, width="stretch")
        render_chart_source(SOURCE_DROUGHT)
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        drought_priority_export = drought_priority.copy()
        drought_priority_export = drought_priority_export.rename(
            columns={
                "region": "Région",
                "severe_extreme": "Sécheresse sévère/extrême (%)",
            }
        )[["Région", "Sécheresse sévère/extrême (%)"]]
        to_csv_download_button(
            drought_priority_export,
            f"secheresse_prioritaire_{selected_year}.csv",
            "Télécharger en CSV",
            "download_drought_priority"
        )
    
    


if tab_carte.open:
    with tab_carte:
        st.markdown("## Répartition régionale des terres dégradées")
        map_status = status_f.copy()
        map_status["class_map"] = map_status["class"].replace(
            {
                "Degraded": "Dégradé",
                "Improved": "Amélioré",
                "Dégradé": "Dégradé",
                "Amélioré": "Amélioré",
            }
        )
        
        
        region_status = (
            map_status.sort_values(by="pct", ascending=False)
            .groupby("region", as_index=False)
            .first()
            [["region", "class_map", "pct"]]
            .rename(columns={"class_map": "status_class"})
        )
        
        
        map_df = map_status[map_status["class_map"] == "Dégradé"][["region", "pct", "area_ha"]]
        
        
        total_mapped_area = status_f["area_ha"].sum()
        pct_degraded_mapped = (map_df["area_ha"].sum() / total_mapped_area * 100) if total_mapped_area else 0
        avg_degradation = pct_degraded_mapped
        std_degradation = map_df["pct"].std() if not map_df.empty else 0
        std_degradation = 0 if pd.isna(std_degradation) else std_degradation
        regions_high_risk = int((map_df["pct"] >= 70).sum())
        
        
        top_degraded_map = map_df.sort_values(by="pct", ascending=False).iloc[0] if not map_df.empty else None
        top_degraded_name = str(top_degraded_map["region"]) if top_degraded_map is not None else "-"
        top_degraded_pct = float(top_degraded_map["pct"]) if top_degraded_map is not None else 0.0
        
        
        priority_restore_ha = float(map_df[map_df["pct"] >= 70]["area_ha"].sum()) if not map_df.empty else 0.0
        
        
        stable_area_ha_map = float(status_f.loc[status_f["class"] == "Stable", "area_ha"].sum())
        improved_area_ha_map = float(status_f.loc[status_f["class"] == "Amélioré", "area_ha"].sum())
        top_improved_map = (
            status_f[status_f["class"] == "Amélioré"]
            .groupby("region", as_index=False)
            .agg(pct=("pct", "sum"))
            .sort_values(by="pct", ascending=False)
            .iloc[0] if not status_f[status_f["class"] == "Amélioré"].empty else None
        )
    
        render_kpi_row(
            [
                (
                    "Superficie dégradée",
                    f"{format_int(float(map_df['area_ha'].sum()))} ha" if not map_df.empty else "-",
                    "Somme des superficies dégradées sur les régions sélectionnées",
                ),
                (
                    "Superficie stable",
                    f"{format_int(stable_area_ha_map)} ha",
                    "Superficie dont le statut n'a pas évolué — potentiel à protéger pour éviter la dégradation",
                ),
                (
                    "Régions à haut risque",
                    f"{regions_high_risk}",
                    "Nombre de régions avec ≥ 70% de terres dégradées",
                ),
            ]
        )
        
        render_kpi_row(
            [
                (
                    "Superficie prioritaire à restaurer",
                    f"{format_int(priority_restore_ha)} ha" if priority_restore_ha > 0 else "0 ha",
                    f"Superficie dégradée dans les {regions_high_risk} région(s) à ≥ 70% — intervention urgente requise",
                ),
                (
                    "Région la plus dégradée",
                    f"{top_degraded_name} ({top_degraded_pct:.0f}%)" if top_degraded_map is not None else "-",
                    "Région avec la part de terres dégradées la plus élevée — à prioriser sur la carte",
                ),
                (
                    "Région la plus améliorée",
                    f"{top_improved_map['region']} ({top_improved_map['pct']:.0f}%)" if top_improved_map is not None else "-",
                    "Région avec le taux de terres améliorées le plus élevé — bonnes pratiques à répliquer",
                ),
            ]
        )
        
        col_map, col_side = st.columns([2, 1])
        
        with col_map:
            st.markdown("### Carte interactive : Statut dominant par région")
            
            geo_regions = [
                feature.get("properties", {}).get("region")
                for feature in geo.get("features", [])
            ]
            
            
            map_plot_df = pd.DataFrame({
                "region": geo_regions
            })
            
            
            map_plot_df = map_plot_df.merge(
                region_status, 
                on="region", 
                how="left",
                suffixes=("", "_status")
            )
            
            
            map_plot_df["status_class"] = map_plot_df["status_class"].fillna("Non sélectionnée")
            map_plot_df["pct"] = map_plot_df["pct"].fillna(0)
            
            
            def build_status_map_html(geojson_data, status_df, height_px=540):
                """Construit une carte interactive MapLibre avec statut dominant par région"""
                
                
                status_colors = {
                    "Dégradé": PALETTE["degraded"],
                    "Stable": PALETTE["stable"],
                    "Amélioré": PALETTE["improved"],
                    "Non sélectionnée": "#E6E1D8"
                }
                
                
                features = []
                for feature in geojson_data.get("features", []):
                    props = dict(feature.get("properties", {}))
                    region = props.get("region")
                    
                    
                    region_data = status_df[status_df["region"] == region]
                    if not region_data.empty:
                        status_class = region_data.iloc[0]["status_class"]
                        pct = float(region_data.iloc[0]["pct"])
                        props["status"] = status_class
                        props["pct"] = pct
                        props["fill_color"] = status_colors.get(status_class, "#E6E1D8")
                    else:
                        props["status"] = "Non sélectionnée"
                        props["pct"] = 0
                        props["fill_color"] = "#E6E1D8"
                    
                    features.append({
                        "type": "Feature",
                        "geometry": feature.get("geometry"),
                        "properties": props
                    })
                
                map_geojson = {"type": "FeatureCollection", "features": features}
                geojson_json = json.dumps(map_geojson, ensure_ascii=False)
                
                return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet">
                    <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
                    <style>
                        html, body {{
                            margin: 0;
                            padding: 0;
                            width: 100%;
                            height: {height_px}px;
                            overflow: hidden;
                            font-family: 'Segoe UI', Arial, sans-serif;
                        }}
                        #status-map {{
                            position: relative;
                            width: 100%;
                            height: {height_px}px;
                            border-radius: 14px;
                            overflow: hidden;
                            background: #FFFFFF;
                            box-shadow: inset 0 0 0 1px rgba(45, 27, 31, 0.08);
                        }}
                        .maplibregl-ctrl-group {{
                            border: 1px solid rgba(45, 27, 31, 0.14);
                            border-radius: 10px;
                            overflow: hidden;
                            box-shadow: 0 5px 16px rgba(45, 27, 31, 0.14);
                        }}
                        .maplibregl-ctrl-group button {{
                            width: 34px;
                            height: 34px;
                        }}
                        .maplibregl-ctrl-scale {{
                            border: 2px solid {PALETTE['hcp_bordeaux']};
                            color: {PALETTE['ink']};
                            background: rgba(255, 255, 255, 0.95);
                            font-weight: 700;
                            font-size: 11px;
                            padding: 4px 8px;
                            border-radius: 6px;
                            box-shadow: 0 2px 8px rgba(107, 31, 58, 0.15);
                        }}
                        .map-legend {{
                            position: absolute;
                            left: 14px;
                            top: 14px;
                            z-index: 2;
                            min-width: 180px;
                            padding: 12px 14px;
                            border: 1.5px solid {PALETTE['hcp_bordeaux']};
                            border-radius: 12px;
                            background: rgba(255, 255, 255, 0.96);
                            box-shadow: 0 8px 20px rgba(107, 31, 58, 0.18);
                            color: {PALETTE['ink']};
                            font-size: 12px;
                        }}
                        .legend-title {{
                            margin-bottom: 8px;
                            font-weight: 800;
                            font-size: 13px;
                            color: {PALETTE['hcp_bordeaux']};
                            border-bottom: 1px solid {PALETTE['line']};
                            padding-bottom: 6px;
                        }}
                        .legend-row {{
                            display: flex;
                            align-items: center;
                            gap: 8px;
                            line-height: 1.6;
                            margin-bottom: 4px;
                        }}
                        .legend-swatch {{
                            width: 16px;
                            height: 16px;
                            border: 1px solid rgba(45, 27, 31, 0.25);
                            border-radius: 3px;
                            flex-shrink: 0;
                        }}
                        .popup-title {{
                            color: {PALETTE['ink']};
                            font-weight: 800;
                            margin-bottom: 6px;
                            font-size: 13px;
                            border-bottom: 1px solid {PALETTE['line']};
                            padding-bottom: 4px;
                        }}
                        .popup-line {{
                            color: {PALETTE['muted']};
                            font-size: 12px;
                            line-height: 1.5;
                            margin-bottom: 3px;
                        }}
                        .popup-line strong {{
                            color: {PALETTE['ink']};
                            font-weight: 700;
                        }}
                    </style>
                </head>
                <body>
                    <div id="status-map">
                        <div class="map-legend">
                            <div class="legend-title">Statut dominant</div>
                            <div class="legend-row">
                                <span class="legend-swatch" style="background:{PALETTE['degraded']}"></span>
                                <span>Dégradé</span>
                            </div>
                            <div class="legend-row">
                                <span class="legend-swatch" style="background:{PALETTE['stable']}"></span>
                                <span>Stable</span>
                            </div>
                            <div class="legend-row">
                                <span class="legend-swatch" style="background:{PALETTE['improved']}"></span>
                                <span>Amélioré</span>
                            </div>
                            <div class="legend-row">
                                <span class="legend-swatch" style="background:#E6E1D8"></span>
                                <span>Non sélectionnée</span>
                            </div>
                        </div>
                    </div>
                    <script>
                        const geojson = {geojson_json};
                        
                        const map = new maplibregl.Map({{
                            container: 'status-map',
                            style: {{
                                version: 8,
                                sources: {{}},
                                layers: [
                                    {{
                                        id: 'background',
                                        type: 'background',
                                        paint: {{ 'background-color': '#FFFFFF' }}
                                    }}
                                ]
                            }},
                            center: [-8.0, 27.5],
                            zoom: 3.5,
                            minZoom: 1.5,
                            maxZoom: 10,
                            attributionControl: false,
                            renderWorldCopies: false
                        }});
    
                        map.addControl(new maplibregl.NavigationControl({{ showCompass: false }}), 'top-right');
                        
                        map.addControl(
                            new maplibregl.ScaleControl({{ 
                                maxWidth: 150, 
                                unit: 'metric' 
                            }}), 
                            'bottom-left'
                        );
    
                        const mapContainer = document.getElementById('status-map');
                        const resizeObserver = new ResizeObserver(() => map.resize());
                        resizeObserver.observe(mapContainer);
                        window.addEventListener('resize', () => map.resize());
    
                        map.on('load', () => {{
                            map.resize();
                            map.addSource('regions', {{
                                type: 'geojson',
                                data: geojson
                            }});
    
                            map.addLayer({{
                                id: 'regions-fill',
                                type: 'fill',
                                source: 'regions',
                                paint: {{
                                    'fill-color': ['get', 'fill_color'],
                                    'fill-opacity': 0.75
                                }}
                            }});
    
                            map.addLayer({{
                                id: 'regions-outline',
                                type: 'line',
                                source: 'regions',
                                paint: {{
                                    'line-color': '#2C1B1F',
                                    'line-width': [
                                        'interpolate', ['linear'], ['zoom'],
                                        4, 1.8,
                                        7, 3.0
                                    ],
                                    'line-opacity': 0.9
                                }}
                            }});
    
                            const coords = [];
                            geojson.features.forEach(feature => {{
                                const geom = feature.geometry;
                                if (!geom) return;
                                if (geom.type === 'Polygon') {{
                                    geom.coordinates.forEach(ring => ring.forEach(coord => coords.push(coord)));
                                }} else if (geom.type === 'MultiPolygon') {{
                                    geom.coordinates.forEach(polygon => polygon.forEach(ring => ring.forEach(coord => coords.push(coord))));
                                }}
                            }});
    
                            if (coords.length > 0) {{
                                const bounds = coords.reduce(
                                    (b, coord) => b.extend(coord),
                                    new maplibregl.LngLatBounds(coords[0], coords[0])
                                );
                                map.fitBounds(bounds, {{
                                    padding: 24,
                                    maxZoom: 4.0,
                                    duration: 0
                                }});
                            }}
                        }});
    
                        const popup = new maplibregl.Popup({{
                            closeButton: false,
                            closeOnClick: false
                        }});
    
                        map.on('mousemove', 'regions-fill', (e) => {{
                            map.getCanvas().style.cursor = 'pointer';
                            const props = e.features[0].properties;
                            const pct = props.pct ? `${{props.pct.toFixed(1)}}%` : 'N/A';
                            
                            popup
                                .setLngLat(e.lngLat)
                                .setHTML(`
                                    <div style="padding: 8px; min-width: 180px;">
                                        <div class="popup-title">${{props.region}}</div>
                                        <div class="popup-line">
                                            <strong>Statut:</strong> ${{props.status}}
                                        </div>
                                        <div class="popup-line">
                                            <strong>Part du statut:</strong> ${{pct}}
                                        </div>
                                    </div>
                                `)
                                .addTo(map);
                        }});
    
                        map.on('mouseleave', 'regions-fill', () => {{
                            map.getCanvas().style.cursor = '';
                            popup.remove();
                        }});
                    </script>
                </body>
                </html>
                """
            
            
            map_html = build_status_map_html(geo, map_plot_df, height_px=540)
            render_html_iframe(map_html, height=540)
            
            
            st.markdown(
                f"""
                <div style="
                    margin: 0.45rem 0.15rem 1rem 0.15rem;
                    padding: 0.5rem 0.9rem;
                    background: rgba(23,32,51,0.04);
                    border-radius: 8px;
                    font-size: 0.71rem;
                    color: {PALETTE['muted']};
                    line-height: 1.5;
                ">
                    <strong style="color: {PALETTE['ink']};">Source :</strong> 
                    Google Earth Engine | Trends.Earth v2.2.6 | UNCCD GPG 15.3.1 v2 (2021) | GPG Addendum (2025) | 
                    Données géospatiales et climatiques : MODIS MOD13Q1, MODIS MCD12Q1, OpenLandMap | 
                    Fond de carte : OpenStreetMap contributors
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            
            map_export = map_plot_df[["region", "status_class", "pct"]].copy()
            map_export = map_export.rename(
                columns={
                    "region": "Région",
                    "status_class": "Statut dominant",
                    "pct": "Pourcentage du statut (%)",
                }
            )
            st.markdown('<div class="download-button-spacer"></div>', unsafe_allow_html=True)
            to_csv_download_button(
                map_export,
                f"carte_statut_dominant_regions_{selected_year}.csv",
                "Télécharger en CSV",
                "download_map_status"
            )
            
        with col_side:
            st.markdown("### Classement des régions")
            rank = map_df.sort_values(by="pct", ascending=False).reset_index(drop=True)
            fig_rank = px.bar(
                rank,
                x="pct",
                y="region",
                orientation="h",
                color="pct",
                color_continuous_scale=[PALETTE["stable"], PALETTE["degraded"]],
                labels={"pct": "% dégradé", "region": ""},
            )
            fig_rank.update_layout(
                template=PLOTLY_TEMPLATE,
                height=520,
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                margin=dict(l=18, r=18, t=4, b=18),
            )
            fig_rank.update_traces(
                hovertemplate="% d" + "\u00e9" + "grad" + "\u00e9" + ": %{x:.1f}%<extra></extra>"
            )
            polish_chart(fig_rank, height=520, show_source=False)
            st.plotly_chart(fig_rank, width="stretch")
            render_chart_source(SOURCE_LAND)
            
            
            rank_export = rank.rename(
                columns={
                    "region": "Région",
                    "pct": "Dégradation (%)",
                    "area_ha": "Superficie dégradée (ha)",
                }
            )
            st.markdown('<div class="download-button-spacer"></div>', unsafe_allow_html=True)
            to_csv_download_button(
                rank_export,
                f"classement_regions_degradation_{selected_year}.csv",
                "Télécharger en CSV",
                "download_region_rank"
            )
    
        st.markdown("### Lecture décisionnelle du territoire")
        indicator_labels = {
            "Productivity": "Productivité",
            "Land cover": "Couverture des terres",
            "Soil organic carbon": "Carbone organique du sol",
        }
        exposure_df = (
            region_summary[["region", "Degraded"]]
            .merge(drought_risk, on="region", how="left")
            .merge(map_df[["region", "area_ha"]], on="region", how="left")
            .fillna({"severe_extreme": 0, "area_ha": 0})
            .sort_values("Degraded", ascending=False)
            .head(8)
        )
        exposure_long = exposure_df.melt(
            id_vars=["region", "area_ha"],
            value_vars=["Degraded", "severe_extreme"],
            var_name="Indicateur",
            value_name="pct",
        )
        exposure_long["Indicateur"] = exposure_long["Indicateur"].map(
            {
                "Degraded": "Terres dégradées",
                "severe_extreme": f"Sécheresse sévère/extrême {selected_year}",
            }
        )
        
        exposure_long["pct_label"] = exposure_long.apply(
            lambda row: f"{float(row['pct']):.3f}%"
            if str(row["Indicateur"]).startswith("Sécheresse") and float(row["pct"]) < 1.0
            else f"{float(row['pct']):.1f}%",
            axis=1,
        )
    
        diagnostic_regions = map_df.sort_values(by="pct", ascending=False).head(6)["region"].tolist()
        causes_df = subind[
            (subind["region"].isin(diagnostic_regions))
            & (subind["indicator"].isin(indicator_labels))
            & (subind["class"] == "Dégradé")
        ].copy()
        causes_df["indicator_label"] = causes_df["indicator"].map(indicator_labels)
        causes_y_max = float(causes_df["pct"].max()) if not causes_df.empty else 0.0
        causes_y_max = max(100.0, causes_y_max * 1.12)
    
        diagnostic_left, diagnostic_right = st.columns([1, 1])
    
        with diagnostic_left:
            st.markdown(f"##### Exposition comparée: dégradation et sécheresse {selected_year}")
            fig_exposure = px.bar(
                exposure_long,
                x="pct",
                y="region",
                color="Indicateur",
                orientation="h",
                barmode="group",
                text="pct_label",
                custom_data=["pct_label"],
                color_discrete_map={
                    "Terres dégradées": PALETTE["degraded"],
                    f"Sécheresse sévère/extrême {selected_year}": PALETTE["accent2"],
                },
                category_orders={"region": exposure_df["region"].tolist()},
                labels={"pct": "% de la superficie", "region": "", "Indicateur": ""},
            )
            fig_exposure.update_traces(
                texttemplate="%{text}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate="<b>%{y}</b><br>%{fullData.name}: %{customdata[0]}<extra></extra>",
            )
            
            
            _max_pct = float(exposure_long["pct"].max()) if not exposure_long.empty else 100.0
            _x_max = max(_max_pct * 1.20, 110.0)
            polish_chart(fig_exposure, height=max(380, len(exposure_df) * 44 + 100), show_source=False)
            fig_exposure.update_layout(
                xaxis=dict(range=[0, _x_max], ticksuffix="%"),
                yaxis=dict(autorange="reversed"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
                uniformtext_minsize=9,
                uniformtext_mode="show",
            )
            st.plotly_chart(fig_exposure, width="stretch")
            render_chart_source(SOURCE_LAND_DROUGHT)
            
            
            exposure_export = exposure_df.copy()
            exposure_export = exposure_export.rename(
                columns={
                    "region": "Région",
                    "Degraded": "Terres dégradées (%)",
                    "severe_extreme": "Sécheresse sévère/extrême (%)",
                    "area_ha": "Superficie dégradée (ha)",
                }
            )
            st.markdown('<div class="download-button-spacer"></div>', unsafe_allow_html=True)
            to_csv_download_button(
                exposure_export[["Région", "Terres dégradées (%)", "Sécheresse sévère/extrême (%)", "Superficie dégradée (ha)"]],
                f"exposition_comparee_{selected_year}.csv",
                "Télécharger en CSV",
                "download_exposure_comparison"
            )
    
        with diagnostic_right:
            st.markdown("##### Causes dominantes dans les régions prioritaires")
            fig_causes = px.bar(
                causes_df,
                x="region",
                y="pct",
                color="indicator_label",
                barmode="group",
                color_discrete_sequence=[PALETTE["degraded"], PALETTE["hcp_gold"], PALETTE["improved"]],
                labels={"pct": "% dégradé", "region": "", "indicator_label": "Sous-indicateur"},
            )
            fig_causes.update_traces(
                hovertemplate="<b>%{fullData.name}</b><br>% dégradé: %{y:.1f}%<extra></extra>"
            )
            polish_chart(fig_causes, height=390, show_source=False)
            fig_causes.update_layout(
                xaxis_tickangle=-30,
                legend_title="",
                yaxis=dict(range=[0, causes_y_max]),
            )
            st.plotly_chart(fig_causes, width="stretch")
            render_chart_source(SOURCE_LAND)
            
            
            causes_export = causes_df.rename(
                columns={
                    "region": "Région",
                    "indicator": "Sous-indicateur (code)",
                    "indicator_label": "Sous-indicateur",
                    "class": "Statut",
                    "pct": "Dégradation (%)",
                    "area_ha": "Superficie (ha)",
                }
            )
            cols_causes = [c for c in ["Région", "Sous-indicateur", "Dégradation (%)", "Superficie (ha)"] if c in causes_export.columns]
            st.markdown('<div class="download-button-spacer"></div>', unsafe_allow_html=True)
            to_csv_download_button(
                causes_export[cols_causes],
                f"causes_dominantes_regions_prioritaires_{selected_year}.csv",
                "Télécharger en CSV",
                "download_causes_dominantes"
            )
    
    


if tab_degradation.open:
    with tab_degradation:
        indicator_labels = {
            "Productivity": "Productivité",
            "Land cover": "Couverture des terres",
            "Soil organic carbon": "Carbone organique du sol",
        }
        indicators = [
            indicator
            for indicator in indicator_labels
            if indicator in set(subind["indicator"].unique())
        ]
        status_color_map = {
            "Dégradé": PALETTE["degraded"],
            "Stable": PALETTE["stable"],
            "Amélioré": PALETTE["improved"],
        }
    
        degraded_regions = (
            status_f[status_f["class"] == "Dégradé"][["region", "pct", "area_ha"]]
            .copy()
            .sort_values(by="pct", ascending=False)
        )
        severe_regions_count = int((degraded_regions["pct"] >= 70).sum())
        
        
        baseline_degraded = subind[
            (subind["indicator"] == "SDG 15.3.1 baseline")
            & (subind["class"] == "Dégradé")
            & (subind["region"].isin(selected_regions))
        ]["area_ha"].sum()
        current_degraded = status_f[status_f["class"] == "Dégradé"]["area_ha"].sum()
        
        
        degradation_increase_ha = float(current_degraded - baseline_degraded)
        
        
        sub_degraded_summary = subind[
            (subind["indicator"].isin(indicators))
            & (subind["region"].isin(selected_regions))
            & (subind["class"] == "Dégradé")
        ].groupby("indicator")["area_ha"].sum()
        worst_indicator = str(sub_degraded_summary.idxmax()) if len(sub_degraded_summary) > 0 else "-"
        worst_indicator_label = indicator_labels.get(worst_indicator, worst_indicator) if worst_indicator != "-" else "-"
        worst_indicator_share = (
            float(sub_degraded_summary.max() / sub_degraded_summary.sum() * 100)
            if len(sub_degraded_summary) > 0 and sub_degraded_summary.sum() > 0
            else 0.0
        )
        
        
        stable_area_ha_deg = float(status_f.loc[status_f["class"] == "Stable", "area_ha"].sum())
        pct_stable_deg = (stable_area_ha_deg / total_area * 100) if total_area else 0
        
        
        
        regions_degraded_count = int(degraded_regions["region"].nunique())
        improved_area_ha = float(status_f.loc[status_f["class"] == "Amélioré", "area_ha"].sum())
    
        render_kpi_row(
            [
                (
                    "% terres stables",
                    format_pct(float(pct_stable_deg)),
                    "Part de la superficie dont le statut n'a pas évolué — à protéger pour éviter toute bascule vers la dégradation",
                ),
                (
                    "Régions touchées",
                    f"{regions_degraded_count}",
                    "Nombre de régions comptant au moins une part de terres dégradées, quelle que soit l'intensité",
                ),
                (
                    "Indice de récupération",
                    f"{(improved_area_ha / float(degraded_regions['area_ha'].sum()) * 100):.1f}%" if not degraded_regions.empty and degraded_regions['area_ha'].sum() > 0 else "-",
                    f"Pour chaque hectare de terre dégradée, combien d'hectares ont été améliorés ? "
                    f"Ici {(improved_area_ha / float(degraded_regions['area_ha'].sum()) * 100):.1f}% signifie que seulement "
                    f"{(improved_area_ha / float(degraded_regions['area_ha'].sum()) * 100):.1f} ha sont améliorés pour 100 ha dégradés. "
                    f"Objectif à atteindre : 100% (autant d'amélioration que de dégradation) ou plus.",
                ),
            ]
        )
        
        
        render_kpi_row(
            [
                (
                    "Évolution vs baseline",
                    f"{degradation_increase_ha:+,.0f} ha".replace(",", " "),
                    "Différence de superficie dégradée entre aujourd'hui et la période de référence (2001-2015). Une valeur positive signifie plus de terres dégradées qu'à la baseline.",
                ),
                (
                    "Sous-indicateur critique",
                    worst_indicator_label,
                    "Sous-indicateur contribuant le plus à la dégradation totale (en superficie)",
                ),
                (
                    "Part du sous-indicateur critique",
                    f"{worst_indicator_share:.0f}%" if worst_indicator != "-" else "-",
                    "Part de la superficie dégradée expliquée par le sous-indicateur le plus critique — oriente la priorité de remise en état",
                ),
            ]
        )
    
        
        
        
        st.markdown("##### Baseline SDG 15.3.1 (période de référence 2001-2015)")
        baseline_f = subind[
            (subind["indicator"] == "SDG 15.3.1 baseline")
            & (subind["region"].isin(selected_regions))
        ]
        fig_baseline_status = px.bar(
            baseline_f,
            x="region",
            y="pct",
            color="class",
            color_discrete_map=status_color_map,
            category_orders={"class": ["Dégradé", "Stable", "Amélioré"]},
            labels={"pct": "% de la superficie", "region": "", "class": "Statut"},
        )
        fig_baseline_status.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>% de la superficie: %{y:.1f}%<extra></extra>"
        )
        polish_chart(fig_baseline_status, height=430, show_source=False)
        fig_baseline_status.update_layout(xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_baseline_status, width="stretch")
        render_chart_source(SOURCE_LAND_BASELINE)
        baseline_export = baseline_f.copy()
        baseline_export = baseline_export.rename(
            columns={
                "region": "Région",
                "class": "Statut",
                "pct": "Pourcentage (%)",
                "area_ha": "Superficie (ha)",
            }
        )
        to_csv_download_button(
            baseline_export[["Région", "Statut", "Pourcentage (%)", "Superficie (ha)"]],
            "statut_sdg_baseline_2001_2015.csv",
            "Télécharger en CSV",
            "download_baseline_status"
        )
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Comparaison Baseline (2001-2015) vs Année sélectionnée — % Terres dégradées par région")
    
        st.markdown(
            f"""
            <div class="method-note">
                <strong>Lecture :</strong> Chaque paire de barres compare, pour chaque région, le pourcentage de terres
                dégradées calculé sur la <strong>période de référence 2001-2015</strong> (Baseline) et celui de
                l'<strong>année sélectionnée</strong>. La valeur affichée au-dessus de chaque paire indique <strong>l'évolution
                en points de pourcentage</strong> (différence entre l'année sélectionnée et la baseline). Une barre rouge signifie 
                que la dégradation a augmenté par rapport à la baseline ; une barre verte qu'elle a diminué. 
                La comparaison porte sur le pourcentage de superficie (et non sur les hectares bruts) pour rester comparable 
                entre régions de tailles différentes.
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown(
            f"""
            <div class="abbreviation-note">
                <strong>Note d'interprétation :</strong> L'évolution (différence) mesure le changement observé entre 
                la période de référence et l'année sélectionnée :
                <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                    <li><strong>Valeur négative (ex : -1.6 pp)</strong> : Le pourcentage de terres dégradées a <strong>diminué</strong>, 
                    indiquant une amélioration de l'état des terres.</li>
                    <li><strong>Valeur positive (ex : +7.3 pp)</strong> : Le pourcentage de terres dégradées a <strong>augmenté</strong>, 
                    signalant une détérioration de l'état des terres.</li>
                    <li><strong>pp</strong> = points de pourcentage (unité de mesure des différences de pourcentages).</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
        
        baseline_compare_year = st.selectbox(
            "Année à comparer avec la baseline",
            options=SDG_YEARS,
            index=len(SDG_YEARS) - 1,  
            key="baseline_compare_year_selector",
        )
    
        
        baseline_degraded = (
            subind[
                (subind["indicator"] == "SDG 15.3.1 baseline")
                & (subind["class"] == "Dégradé")
                & (subind["region"].isin(selected_regions))
            ][["region", "pct"]]
            .rename(columns={"pct": "pct_baseline"})
        )
    
        
        annual_degraded = (
            sdg_annual[
                (sdg_annual["year"] == baseline_compare_year)
                & (sdg_annual["class"] == "Dégradé")
                & (sdg_annual["region"].isin(selected_regions))
            ][["region", "pct"]]
            .rename(columns={"pct": "pct_annual"})
        )
    
        
        compare_df = baseline_degraded.merge(annual_degraded, on="region", how="inner")
    
        
        baseline_regions = set(baseline_degraded["region"])
        annual_regions = set(annual_degraded["region"])
        missing_in_annual = baseline_regions - annual_regions
        missing_in_baseline = annual_regions - baseline_regions
        for r in sorted(missing_in_annual):
            print(f"[WARN] Région absente des données annuelles {baseline_compare_year}, exclue du graphique : {r}")
        for r in sorted(missing_in_baseline):
            print(f"[WARN] Région absente de la baseline, exclue du graphique : {r}")
    
        if compare_df.empty:
            st.warning(
                f"Aucune donnée commune entre la baseline et l'année {baseline_compare_year} "
                "pour les régions sélectionnées. Vérifiez les filtres."
            )
        else:
            
            compare_df["delta"] = compare_df["pct_annual"] - compare_df["pct_baseline"]
            
            
            increase_icon_path = ASSETS_DIR / "up.png"
            decrease_icon_path = ASSETS_DIR / "down.png"
            increase_icon_b64 = get_base64_image(str(increase_icon_path))
            decrease_icon_b64 = get_base64_image(str(decrease_icon_path))
            
            def format_delta_with_icon(d):
                if d > 0:
                    return f'<img src="data:image/png;base64,{increase_icon_b64}" width="14" height="14" style="vertical-align: middle;"/> +{d:.1f} pp'
                elif d < 0:
                    return f'<img src="data:image/png;base64,{decrease_icon_b64}" width="14" height="14" style="vertical-align: middle;"/> {d:.1f} pp'
                else:
                    return "= 0 pp"
            
            compare_df["delta_label"] = compare_df["delta"].map(format_delta_with_icon)
            compare_df["delta_label_plain"] = compare_df["delta"].map(
                lambda d: f"+{d:.1f} pp" if d > 0 else (f"{d:.1f} pp" if d < 0 else "= 0 pp")
            )
            compare_df["bar_color_annual"] = compare_df["delta"].map(
                lambda d: PALETTE["degraded"] if d > 0 else PALETTE["improved"]
            )
    
            
            compare_df = compare_df.sort_values("pct_baseline", ascending=False).reset_index(drop=True)
    
            
            fig_baseline_compare = go.Figure()
    
            
            fig_baseline_compare.add_trace(
                go.Bar(
                    name="Baseline (2001-2015)",
                    x=compare_df["region"],
                    y=compare_df["pct_baseline"],
                    marker_color=PALETTE["hcp_gold"],
                    marker_line=dict(color=PALETTE["hcp_bordeaux"], width=1),
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Baseline (2001-2015) : %{y:.1f}%<extra></extra>"
                    ),
                )
            )
    
            
            fig_baseline_compare.add_trace(
                go.Bar(
                    name=f"Année {baseline_compare_year}",
                    x=compare_df["region"],
                    y=compare_df["pct_annual"],
                    marker_color=compare_df["bar_color_annual"].tolist(),
                    marker_line=dict(color="rgba(0,0,0,0.12)", width=1),
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        f"Année {baseline_compare_year} : " + "%{y:.1f}%<br>"
                        "Évolution vs baseline : %{customdata}<extra></extra>"
                    ),
                    customdata=compare_df["delta_label_plain"].tolist(),
                )
            )
    
            
            for i, row in compare_df.iterrows():
                delta_color = (
                    PALETTE["degraded"] if row["delta"] > 0
                    else PALETTE["improved"] if row["delta"] < 0
                    else PALETTE["muted"]
                )
                y_anchor = max(row["pct_baseline"], row["pct_annual"]) + 2.5
                
                
                if row["delta"] > 0:
                    icon_source = f'data:image/png;base64,{increase_icon_b64}'
                    text_label = f'+{row["delta"]:.1f} pp'
                elif row["delta"] < 0:
                    icon_source = f'data:image/png;base64,{decrease_icon_b64}'
                    text_label = f'{row["delta"]:.1f} pp'
                else:
                    icon_source = None
                    text_label = '= 0 pp'
                
                
                if icon_source:
                    
                    fig_baseline_compare.add_layout_image(
                        dict(
                            source=icon_source,
                            xref="x",
                            yref="y",
                            x=i,  
                            y=y_anchor,
                            sizex=0.15,  
                            sizey=2.5,
                            xanchor="right",
                            yanchor="bottom",
                        )
                    )
                    
                    
                    fig_baseline_compare.add_annotation(
                        x=i,
                        y=y_anchor,
                        text=text_label,
                        showarrow=False,
                        font=dict(size=10, color=delta_color, family="Tajawal, Segoe UI, sans-serif"),
                        xanchor="left",
                        yanchor="bottom",
                        xshift=2,  
                    )
                else:
                    
                    fig_baseline_compare.add_annotation(
                        x=i,
                        y=y_anchor,
                        text=text_label,
                        showarrow=False,
                        font=dict(size=10, color=delta_color, family="Tajawal, Segoe UI, sans-serif"),
                        xanchor="center",
                        yanchor="bottom",
                    )
    
    
    
            
            
            fig_baseline_compare.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='markers',
                    marker=dict(size=10, color=PALETTE["degraded"], symbol='square'),
                    showlegend=True,
                    name=f"Année {baseline_compare_year} — dégradation en hausse vs baseline",
                    hoverinfo='skip'
                )
            )
            
            
            fig_baseline_compare.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='markers',
                    marker=dict(size=10, color=PALETTE["improved"], symbol='square'),
                    showlegend=True,
                    name=f"Année {baseline_compare_year} — dégradation en baisse vs baseline",
                    hoverinfo='skip'
                )
            )
    
            
            y_max = max(compare_df["pct_baseline"].max(), compare_df["pct_annual"].max()) + 14
            polish_chart(fig_baseline_compare, height=max(480, len(compare_df) * 36 + 160), show_source=False)
            fig_baseline_compare.update_layout(
                barmode="group",
                bargap=0.20,
                bargroupgap=0.08,
                xaxis=dict(
                    tickangle=-35,
                    title="",
                ),
                yaxis=dict(
                    title="% terres dégradées",
                    ticksuffix="%",
                    range=[0, min(y_max, 115)],
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.04,
                    xanchor="left",
                    x=0,
                    font=dict(size=11),
                ),
            )
    
            st.plotly_chart(fig_baseline_compare, width='stretch')
            render_chart_source(SOURCE_LAND_BASELINE)
    
            
            excluded = sorted(missing_in_annual | missing_in_baseline)
            if excluded:
                st.markdown(
                    f'<div class="card-note">'
                    f'<strong>Régions exclues</strong> (données manquantes dans un des deux fichiers) : '
                    f'{", ".join(excluded)}. Vérifier la cohérence des sources.</div>',
                    unsafe_allow_html=True,
                )
    
            
            with st.expander("Tableau détaillé des valeurs"):
                table_compare = compare_df[["region", "pct_baseline", "pct_annual", "delta"]].copy()
                table_compare.columns = [
                    "Région",
                    "Baseline 2001-2015 (%)",
                    f"Année {baseline_compare_year} (%)",
                    "Évolution (pp)",
                ]
                table_compare["Baseline 2001-2015 (%)"] = table_compare["Baseline 2001-2015 (%)"].map(
                    lambda v: f"{v:.2f}"
                )
                table_compare[f"Année {baseline_compare_year} (%)"] = table_compare[
                    f"Année {baseline_compare_year} (%)"
                ].map(lambda v: f"{v:.2f}")
                table_compare["Évolution (pp)"] = table_compare["Évolution (pp)"].map(lambda v: f"{v:+.2f}")
                
                
                def get_evolution_html(delta):
                    if delta > 0:
                        return f'<img src="data:image/png;base64,{increase_icon_b64}" width="16" height="16" style="vertical-align: middle;"/> Détérioration'
                    elif delta < 0:
                        return f'<img src="data:image/png;base64,{decrease_icon_b64}" width="16" height="16" style="vertical-align: middle;"/> Amélioration'
                    else:
                        return "Stable"
                
                table_compare["Tendance"] = compare_df["delta"].map(get_evolution_html)
                
                
                html_table = table_compare.to_html(escape=False, index=False)
                st.markdown(html_table, unsafe_allow_html=True)
    
            
            export_compare = compare_df[["region", "pct_baseline", "pct_annual", "delta"]].copy()
            export_compare.columns = [
                "Région",
                "Baseline 2001-2015 (%)",
                f"Année {baseline_compare_year} (%)",
                "Évolution (pp)",
            ]
            to_csv_download_button(
                export_compare,
                f"comparaison_baseline_vs_{baseline_compare_year}.csv",
                "Télécharger en CSV",
                "download_baseline_compare",
            )
    
        st.markdown("---")
    
        
        
        
        
        st.markdown("##### Statut SDG 15.3.1 actuel")
        fig_current_status = px.bar(
            status_f,
            x="region",
            y="pct",
            color="class",
            color_discrete_map=status_color_map,
            category_orders={"class": ["Dégradé", "Stable", "Amélioré"]},
            labels={"pct": "% de la superficie", "region": "", "class": "Statut"},
        )
        fig_current_status.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>% de la superficie: %{y:.1f}%<extra></extra>"
        )
        polish_chart(fig_current_status, height=430, show_source=False)
        fig_current_status.update_layout(xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_current_status, width="stretch")
        render_chart_source(SOURCE_LAND)
        status_current_export = status_f.copy()
        status_current_export = status_current_export.rename(
            columns={
                "region": "Région",
                "class": "Statut",
                "pct": "Pourcentage (%)",
                "area_ha": "Superficie (ha)",
            }
        )
        to_csv_download_button(
            status_current_export[["Région", "Statut", "Pourcentage (%)", "Superficie (ha)"]],
            f"statut_sdg_actuel_{selected_year}.csv",
            "Télécharger en CSV",
            "download_current_status"
        )
    
        
        
        
        
        st.markdown("---")
        st.markdown("### Analyse temporelle de la dégradation (2017-2025)")
    
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(193, 68, 14, 0.08), rgba(193, 68, 14, 0.03));
                border: 1px solid rgba(193, 68, 14, 0.2);
                border-radius: 12px;
                padding: 1.2rem 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 12px rgba(193, 68, 14, 0.08);
            ">
                <div style="display: flex; align-items: flex-start; gap: 0.9rem;">
                    <div style="flex: 1;">
                        <strong style="color: {PALETTE['ink']}; font-size: 0.95rem;">Suivi annuel de la dégradation des terres :</strong>
                        <span style="color: {PALETTE['muted']}; font-size: 0.9rem; line-height: 1.6;">
                            Cette section présente l'évolution annuelle de l'indicateur SDG 15.3.1 par région sur la période 2017-2025.
                            Les graphiques utilisent le <strong style="color: {PALETTE['ink']};">pourcentage de terres dégradées</strong> (et non la superficie brute) 
                            pour permettre la comparaison entre régions de tailles différentes. 
                            <strong style="color: {PALETTE['degraded']};">Note méthodologique :</strong> Les données 2017-2019 reposent sur une fenêtre statistique 
                            plus courte que 2022-2025 (trajectoire cumulative + fenêtre d'état glissante de 3 ans), ce qui peut affecter la comparabilité directe.
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        
        sdg_annual_f = sdg_annual[sdg_annual["region"].isin(selected_regions)].copy()
        
        
        sdg_degraded = sdg_annual_f[sdg_annual_f["class"] == "Dégradé"].copy()
        
        
        
        if len(SDG_YEARS) >= 2:
            first_year = min(SDG_YEARS)
            last_year = max(SDG_YEARS)
            
            
            first_year_data = sdg_annual_f[sdg_annual_f["year"] == first_year]
            last_year_data = sdg_annual_f[sdg_annual_f["year"] == last_year]
            
            first_year_degraded = first_year_data[first_year_data["class"] == "Dégradé"]["area_ha"].sum()
            first_year_total = first_year_data["area_ha"].sum()
            first_year_pct = (first_year_degraded / first_year_total * 100) if first_year_total > 0 else 0
            
            last_year_degraded = last_year_data[last_year_data["class"] == "Dégradé"]["area_ha"].sum()
            last_year_total = last_year_data["area_ha"].sum()
            last_year_pct = (last_year_degraded / last_year_total * 100) if last_year_total > 0 else 0
            
            variation_total = last_year_pct - first_year_pct
            variation_annuelle = variation_total / (last_year - first_year)
            
            
            region_variations = []
            for region in selected_regions:
                region_first = sdg_degraded[(sdg_degraded["region"] == region) & (sdg_degraded["year"] == first_year)]["pct"].values
                region_last = sdg_degraded[(sdg_degraded["region"] == region) & (sdg_degraded["year"] == last_year)]["pct"].values
                if len(region_first) > 0 and len(region_last) > 0:
                    variation = float(region_last[0]) - float(region_first[0])
                    region_variations.append({"region": region, "variation": variation})
            
            region_variations_df = pd.DataFrame(region_variations).sort_values("variation", ascending=False)
            worst_region = region_variations_df.iloc[0] if len(region_variations_df) > 0 else None
            best_region = region_variations_df.iloc[-1] if len(region_variations_df) > 0 else None
            
            
            regions_worsening = len(region_variations_df[region_variations_df["variation"] > 0])
            regions_improving = len(region_variations_df[region_variations_df["variation"] < 0])
        else:
            variation_annuelle = 0
            variation_total = 0
            worst_region = None
            best_region = None
            regions_worsening = 0
            regions_improving = 0
            first_year = 2017
            last_year = 2025
        
        
        render_kpi_row([
            (
                f"Variation {first_year}-{last_year}",
                f"{variation_total:+.1f} pp",
                f"Évolution du pourcentage national de terres dégradées entre {first_year} et {last_year}. « pp » = points de pourcentage (différence entre deux pourcentages)."
            ),
            (
                "Variation annuelle moyenne",
                f"{variation_annuelle:+.2f} pp/an",
                "Vitesse moyenne d'évolution de la dégradation sur la période. Une valeur positive indique une aggravation, négative une amélioration."
            ),
            (
                "Régions en aggravation",
                f"{regions_worsening} / {len(selected_regions)}",
                f"Nombre de régions où le % de terres dégradées a augmenté entre {first_year} et {last_year}"
            ),
        ])
        
        
        render_kpi_row([
            (
                "Région la plus aggravée",
                f"{worst_region['region']}" if worst_region is not None else "-",
                f"Région avec la plus forte augmentation du % de dégradation : {worst_region['variation']:+.1f} pp" if worst_region is not None else "Aucune donnée"
            ),
            (
                "Région la plus améliorée",
                f"{best_region['region']}" if best_region is not None else "-",
                f"Région avec la plus forte baisse du % de dégradation : {best_region['variation']:+.1f} pp" if best_region is not None else "Aucune donnée"
            ),
            (
                "Régions en amélioration",
                f"{regions_improving} / {len(selected_regions)}",
                f"Nombre de régions où le % de terres dégradées a diminué entre {first_year} et {last_year}"
            ),
        ])
        
        
        
        
        
        st.markdown("##### Évolution du pourcentage de terres dégradées par région (2017-2025)")
        
        
        _all_regions_selected = len(selected_regions) == len(REGIONS)
        _national_label = (
            "NATIONAL (pondéré)"
            if _all_regions_selected
            else f"SÉLECTION ({len(selected_regions)} rég., pondéré)"
        )
    
        
        national_trend = []
        for year in SDG_YEARS:
            year_data = sdg_annual_f[sdg_annual_f["year"] == year]
            degraded_ha = year_data[year_data["class"] == "Dégradé"]["area_ha"].sum()
            total_ha = year_data["area_ha"].sum()
            pct_national = (degraded_ha / total_ha * 100) if total_ha > 0 else 0
            national_trend.append({"year": year, "pct": pct_national})
        national_df = pd.DataFrame(national_trend)
        national_method_note = f"""
                <div class="card-note">
                    <strong>Note de lecture :</strong>
                    La courbe <em>{_national_label}</em> indique la part de terres dégradées
                    dans l'ensemble des régions affichées, calculée par pondération surfacique
                    (superficie dégradée totale / superficie totale × 100).
                    Lorsque toutes les régions sont sélectionnées, elle représente l'agrégat national.
                    Lorsqu'un filtre régional est appliqué, elle représente uniquement le périmètre sélectionné.
                </div>
                """
        
        
        col_opts1, col_opts2, col_opts3 = st.columns([1.2, 1.5, 1.8])
        with col_opts1:
            show_national = st.checkbox(" Courbe nationale", value=True, key="show_national_trend")
        with col_opts2:
            view_mode = st.radio(
                "**Vue**",
                options=["Toutes les régions", "Une région par graphique"],
                index=0,
                key="view_mode_temporal",
                horizontal=True,
            )
        with col_opts3:
            if view_mode == "Toutes les régions":
                
                sort_options = {
                    "Alphabétique (A → Z)": "Les régions sont classées de A à Z dans la légende. Utile pour retrouver rapidement une région par son nom.",
                    "Par criticité (Pire → Meilleur)": "Les régions les PLUS DÉGRADÉES en 2025 apparaissent EN HAUT de la légende (ex: Casablanca 92%). Permet d'identifier rapidement les priorités d'intervention.",
                    "Par amélioration (Meilleur → Pire)": "Les régions les MOINS DÉGRADÉES en 2025 apparaissent EN HAUT de la légende (ex: Dakhla 14%). Permet de voir les success stories et bonnes pratiques en premier.",
                    "Par évolution (Détérioration croissante)": "Les régions où la dégradation a le PLUS AUGMENTÉ entre 2017 et 2025 apparaissent EN HAUT (ex: +68 pp). Identifie les zones en détérioration rapide nécessitant une action urgente."
                }
                
                
                st.markdown(
                    f"""<div style="display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.3rem;">
                        <span class="icon-inline">{icon_svg("filter", PALETTE["accent"], 16)}</span>
                        <span style="font-weight: 600; font-size: 0.875rem;">Ordre de priorité dans la légende</span>
                    </div>""",
                    unsafe_allow_html=True
                )
                
                
                sort_icons_svg = {
                    "Alphabétique (A → Z)": icon_svg("alphabetical", PALETTE["ink"], 14),
                    "Par criticité (Pire → Meilleur)": icon_svg("alert", PALETTE["degraded"], 14),
                    "Par amélioration (Meilleur → Pire)": icon_svg("success", PALETTE["improved"], 14),
                    "Par évolution (Détérioration croissante)": icon_svg("trending", PALETTE["hcp_gold"], 14)
                }
                
                
                def format_option(option):
                    return f'<span style="display: inline-flex; align-items: center; gap: 0.3rem;">{sort_icons_svg[option]}<span>{option}</span></span>'
                
                sort_order = st.selectbox(
                    "Ordre de priorité",  
                    options=list(sort_options.keys()),
                    index=0,
                    key="sort_order_regions",
                    help="Choisissez l'ordre d'affichage des régions dans la légende pour faciliter l'analyse selon vos priorités.",
                    label_visibility="collapsed"
                )
                
        
        
        
        if view_mode == "Une région par graphique":
            st.markdown(
                f"""
                <div style="
                    background: rgba(74, 124, 89, 0.08);
                    border: 1px solid rgba(74, 124, 89, 0.2);
                    border-radius: 8px;
                    padding: 0.6rem 0.9rem;
                    margin-bottom: 1rem;
                    font-size: 0.85rem;
                    color: {PALETTE['muted']};
                ">
                    <strong style="color: {PALETTE['ink']};">Note de lecture :</strong> 
                    Chaque région est présentée dans un graphique distinct afin de faciliter
                    la lecture des trajectoires temporelles. La courbe pondérée fournit un repère
                    comparatif commun pour le périmètre régional sélectionné.
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            
            fig_facets = px.line(
                sdg_degraded,
                x="year",
                y="pct",
                color="region",
                facet_col="region",
                facet_col_wrap=3,  
                markers=True,
                labels={"pct": "% dégradé", "year": "Année", "region": ""},
                color_discrete_sequence=px.colors.qualitative.Bold,
            )
            
            
            fig_facets.update_traces(
                line=dict(width=3),
                marker=dict(size=8, line=dict(color="#FFFFFF", width=1.5)),
                showlegend=False,  
                hovertemplate="%{y:.1f}% dégradé<extra></extra>",
            )
            
            
            if show_national:
                for i in range(len(selected_regions)):
                    fig_facets.add_trace(
                        go.Scatter(
                            x=national_df["year"],
                            y=national_df["pct"],
                            mode="lines",
                            name=_national_label,
                            line=dict(color=PALETTE["degraded"], width=2, dash="dash"),
                            showlegend=(i == 0),  
                            hovertemplate=f"{_national_label}: %{{y:.1f}}% dégradé<extra></extra>",
                        ),
                        row=(i // 3) + 1,
                        col=(i % 3) + 1,
                    )
            
            
            fig_facets.update_xaxes(
                tickmode="array",
                tickvals=SDG_YEARS,
                tickformat="d",
                tickangle=-45,
                title_text="",
            )
            fig_facets.update_yaxes(
                ticksuffix="%",
                range=[0, 100],
                title_text="",
            )
            
            
            n_rows = (len(selected_regions) + 2) // 3
            fig_height = max(400, n_rows * 220)
            
            polish_chart(fig_facets, height=fig_height, show_source=False)
            fig_facets.update_layout(
                margin=dict(t=30, b=20),
                hovermode="closest",
                hoverlabel=dict(
                    bgcolor="#FFFFFF",
                    bordercolor=PALETTE["line"],
                    font=dict(color=PALETTE["ink"], size=10),
                ),
            )
            
            
            for annotation in fig_facets.layout.annotations:
                annotation.text = annotation.text.replace("region=", "")
                annotation.font.size = 11
                annotation.font.weight = 700
            
            st.plotly_chart(fig_facets, width='stretch')
            render_chart_source(SOURCE_LAND)
            st.markdown(national_method_note, unsafe_allow_html=True)
        
        
        
        
        else:
            
            if sort_order == "Par criticité (Pire → Meilleur)":
                last_year_vals = sdg_degraded[sdg_degraded["year"] == last_year].sort_values("pct", ascending=False)
                region_order = last_year_vals["region"].tolist()
            elif sort_order == "Par amélioration (Meilleur → Pire)":
                last_year_vals = sdg_degraded[sdg_degraded["year"] == last_year].sort_values("pct", ascending=True)
                region_order = last_year_vals["region"].tolist()
            elif sort_order == "Par évolution (Détérioration croissante)":
                if len(region_variations_df) > 0:
                    region_order = region_variations_df.sort_values("variation", ascending=False)["region"].tolist()
                else:
                    region_order = sorted(selected_regions)
            else:  
                region_order = sorted(selected_regions)
            
            
            color_palette = [
                "#E63946", "#F77F00", "#FCBF49", "#06A77D", "#118AB2",
                "#073B4C", "#A4036F", "#7209B7", "#560BAD", "#3A0CA3",
                "#F72585", "#B5179E"
            ]
            
            
            
            fixed_region_order = sorted(selected_regions)
            color_map = {region: color_palette[i % len(color_palette)] for i, region in enumerate(fixed_region_order)}
            
            
            sdg_sorted = sdg_degraded.copy()
            sdg_sorted["region"] = pd.Categorical(sdg_sorted["region"], categories=region_order, ordered=True)
            sdg_sorted = sdg_sorted.sort_values(["region", "year"])
            
            fig_temporal = go.Figure()
            
            
            for region in region_order:
                region_data = sdg_sorted[sdg_sorted["region"] == region]
                fig_temporal.add_trace(
                    go.Scatter(
                        x=region_data["year"],
                        y=region_data["pct"],
                        mode="lines+markers",
                        name=region,
                        line=dict(width=2.8, color=color_map[region]),
                        marker=dict(size=7, color=color_map[region], line=dict(color="#FFFFFF", width=1.2)),
                        hovertemplate="<b>{region}</b>: %{{y:.1f}}% dégradé<extra></extra>".format(region=region),
                        customdata=region_data[["year"]],
                    )
                )
            
            
            if show_national:
                fig_temporal.add_trace(
                    go.Scatter(
                        x=national_df["year"],
                        y=national_df["pct"],
                        mode="lines+markers",
                        name=f"<b>{_national_label}</b>",
                        line=dict(color=PALETTE["degraded"], width=4, dash="dash"),
                        marker=dict(size=10, color=PALETTE["degraded"], line=dict(color="#FFFFFF", width=2)),
                        hovertemplate=f"<b>{_national_label}</b>: %{{y:.1f}}% dégradé<extra></extra>",
                    )
                )
            
            polish_chart(fig_temporal, height=550, show_source=False)
            fig_temporal.update_layout(
                xaxis=dict(
                    tickmode="array",
                    tickvals=SDG_YEARS,
                    tickformat="d",
                    title="Année",
                    gridcolor="rgba(200,200,200,0.3)",
                    
                    showspikes=True,
                    spikemode="across",
                    spikesnap="cursor",
                    spikedash="solid",
                    spikecolor=PALETTE["hcp_bordeaux"],
                    spikethickness=1,
                ),
                yaxis=dict(
                    ticksuffix="%",
                    range=[0, max(100, sdg_degraded["pct"].max() * 1.05)],
                    title="% terres dégradées",
                    gridcolor="rgba(200,200,200,0.3)",
                ),
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=0.98,
                    xanchor="left",
                    x=1.01,
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor=PALETTE["line"],
                    borderwidth=1.5,
                    font=dict(size=11),
                ),
                hovermode="x unified",
                
                margin=dict(l=18, r=18, t=80, b=18),
                hoverlabel=dict(
                    bgcolor="#FFFFFF",
                    bordercolor=PALETTE["line"],
                    font=dict(color=PALETTE["ink"], size=12),
                    align="left",
                    namelength=-1,
                ),
                
                hoverdistance=100,
            )
    
            try:
                fig_temporal.update_layout(xaxis_unifiedhovertitle_text="<b>Année %{x}</b>")
            except ValueError:
                fig_temporal.update_xaxes(hoverformat="d")
            
            
            fig_temporal.update_traces(
                hoverlabel=dict(
                    bgcolor="#FFFFFF",
                    bordercolor=PALETTE["line"],
                    font=dict(color=PALETTE["ink"], size=12),
                    align="left",
                    namelength=-1,
                )
            )
            
            st.plotly_chart(fig_temporal, width='stretch')
            render_chart_source(SOURCE_LAND)
            
            st.markdown(national_method_note, unsafe_allow_html=True)
        
        
        temporal_export = sdg_degraded[["region", "year", "pct"]].rename(columns={
            "region": "Région",
            "year": "Année",
            "pct": "Pourcentage dégradé (%)",
        })
        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
        to_csv_download_button(
            temporal_export,
            f"evolution_temporelle_degradation_{first_year}_{last_year}.csv",
            "Télécharger les données temporelles",
            "download_temporal_data"
        )
        
        
        
        
        
        st.markdown("##### Carte de chaleur : intensité de la dégradation par région et année")
        
        
        heatmap_data = sdg_degraded.pivot_table(
            index="region",
            columns="year",
            values="pct",
            aggfunc="first"
        ).fillna(0)
        
        
        heatmap_data["avg"] = heatmap_data.mean(axis=1)
        heatmap_data = heatmap_data.sort_values("avg", ascending=False).drop("avg", axis=1)
        
        fig_heatmap = px.imshow(
            heatmap_data,
            color_continuous_scale=[
                PALETTE["stable"],
                PALETTE["accent2"],
                PALETTE["degraded"],
                "#8B0000"  
            ],
            aspect="auto",
            labels=dict(x="Année", y="Région", color="% dégradé"),
            zmin=0,
            zmax=100,
        )
        
        fig_heatmap.update_traces(
            hovertemplate="<b>%{y}</b><br>Année: %{x}<br>% dégradé: %{z:.1f}%<extra></extra>",
            text=heatmap_data.values,
            texttemplate="%{z:.0f}%",
            textfont=dict(size=10),
        )
        
        all_years = list(heatmap_data.columns)
        polish_chart(fig_heatmap, height=max(420, len(heatmap_data) * 35 + 100), show_source=False)
        fig_heatmap.update_layout(
            coloraxis_colorbar=dict(title="% dégradé", ticksuffix="%"),
            xaxis=dict(
                side="top",
                tickangle=0,
                tickmode="array",
                tickvals=all_years,
                ticktext=[str(y) for y in all_years],
            ),
            yaxis=dict(autorange="reversed"),
        )
        
        st.plotly_chart(fig_heatmap, width='stretch')
        render_chart_source(SOURCE_LAND)
        
        st.markdown(
            f"""
            <div class="card-note">
                <strong>Lecture :</strong> Les couleurs chaudes (rouge) indiquent un pourcentage élevé de terres dégradées. 
                Cette visualisation permet d'identifier rapidement les régions et les années les plus critiques. 
                Les régions sont triées par ordre décroissant de dégradation moyenne sur la période.
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        
        heatmap_export = heatmap_data.reset_index().rename(columns={"region": "Région"})
        to_csv_download_button(
            heatmap_export,
            f"heatmap_degradation_{first_year}_{last_year}.csv",
            "Télécharger la heatmap",
            "download_heatmap_data"
        )
        
        
        
        
        
        st.markdown("##### Classement des régions par tendance de dégradation")
        
        col_trend_left, col_trend_right = st.columns([1.5, 1])
        
        with col_trend_left:
            
            if len(region_variations_df) > 0:
                trend_data = region_variations_df.copy()
                trend_data = trend_data.sort_values("variation", ascending=True)
                
                
                trend_data["color"] = trend_data["variation"].apply(
                    lambda x: PALETTE["improved"] if x < 0 else PALETTE["degraded"]
                )
                
                fig_trend = px.bar(
                    trend_data,
                    x="variation",
                    y="region",
                    orientation="h",
                    color="variation",
                    color_continuous_scale=[
                        PALETTE["improved"],
                        PALETTE["stable"],
                        PALETTE["accent2"],
                        PALETTE["degraded"]
                    ],
                    labels={"variation": f"Variation {first_year}-{last_year} (pp)", "region": ""},
                )
                
                fig_trend.update_traces(
                    hovertemplate="<b>%{y}</b><br>Variation: %{x:+.1f} pp<extra></extra>",
                )
                
                polish_chart(fig_trend, height=max(400, len(trend_data) * 32 + 90), show_source=False)
                fig_trend.update_layout(
                    coloraxis_showscale=False,
                    xaxis=dict(
                        title=f"Variation {first_year}-{last_year} (points de pourcentage)",
                        ticksuffix=" pp",
                        zeroline=True,
                    ),
                    yaxis=dict(autorange="reversed"),
                )
                
                
                fig_trend.add_vline(
                    x=0,
                    line_width=2,
                    line_dash="dash",
                    line_color=PALETTE["muted"],
                    annotation_text="Pas de changement",
                    annotation_position="top",
                )
                
                st.plotly_chart(fig_trend, width='stretch')
                render_chart_source(SOURCE_LAND)
                
                st.markdown(
                    f"""
                    <div class="card-note">
                        <strong>Lecture :</strong> Les barres vers la droite (rouge) indiquent une aggravation de la dégradation 
                        (le % de terres dégradées a augmenté). Les barres vers la gauche (vert) indiquent une amélioration 
                        (le % de terres dégradées a diminué). L'unité « pp » signifie « points de pourcentage ».
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                
                trend_export = trend_data[["region", "variation"]].rename(columns={
                    "region": "Région",
                    "variation": f"Variation {first_year}-{last_year} (pp)",
                })
                to_csv_download_button(
                    trend_export,
                    f"tendances_degradation_{first_year}_{last_year}.csv",
                    "Télécharger les tendances",
                    "download_trend_data"
                )
            else:
                st.info("Données insuffisantes pour calculer les tendances")
        
        with col_trend_right:
            st.markdown("##### Synthèse des tendances")
            
            if len(region_variations_df) > 0:
                
                strong_worsening = len(trend_data[trend_data["variation"] > 10])
                moderate_worsening = len(trend_data[(trend_data["variation"] > 0) & (trend_data["variation"] <= 10)])
                stable = len(trend_data[(trend_data["variation"] >= -5) & (trend_data["variation"] <= 5)])
                moderate_improving = len(trend_data[(trend_data["variation"] < 0) & (trend_data["variation"] >= -10)])
                strong_improving = len(trend_data[trend_data["variation"] < -10])
                
                
                
                
                
                
                
                
                
                
                
                _tc = {
                    "strong_worsening":   PALETTE["degraded"],   
                    "moderate_worsening": "#C97535",             
                    "stable":             PALETTE["stable"],     
                    "moderate_improving": "#7A9E6E",             
                    "strong_improving":   PALETTE["improved"],   
                }
                
                def _dot(color: str) -> str:
                    """Pastille colorée inline accessible (role=img + aria-label)."""
                    return (
                        f'<span role="img" aria-label="indicateur" style="'
                        f'display:inline-block;width:11px;height:11px;'
                        f'border-radius:50%;background:{color};'
                        f'flex-shrink:0;margin-right:0.45rem;'
                        f'border:1px solid rgba(0,0,0,0.12);"></span>'
                    )
                
                def _row(dot_color: str, label: str, count: int, count_color: str, extra_style: str = "") -> str:
                    return (
                        f'<div style="display:flex;justify-content:space-between;'
                        f'align-items:center;margin-bottom:0.5rem;{extra_style}">'
                        f'<span style="display:flex;align-items:center;color:{PALETTE["muted"]};">'
                        f'{_dot(dot_color)}{label}</span>'
                        f'<strong style="color:{count_color};">{count}</strong>'
                        f'</div>'
                    )
                
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #FFFFFF, #F8FAFC);
                        border: 1px solid {PALETTE['line']};
                        border-radius: 10px;
                        padding: 1rem;
                        margin-bottom: 1rem;
                    ">
                        <div style="font-size: 0.85rem; line-height: 1.8;">
                            {_row(_tc['strong_worsening'],   "Forte aggravation (&gt;+10 pp)",                         strong_worsening,  _tc['strong_worsening'])}
                            {_row(_tc['moderate_worsening'], "Aggravation mod&eacute;r&eacute;e (0 &agrave; +10 pp)",  moderate_worsening, _tc['moderate_worsening'])}
                            {_row(_tc['stable'],              "Stable (-5 &agrave; +5 pp)",                             stable,            PALETTE['ink'],
                                  f"padding:0.3rem 0;border-top:1px solid {PALETTE['line']};border-bottom:1px solid {PALETTE['line']};")}
                            {_row(_tc['moderate_improving'], "Am&eacute;lioration mod&eacute;r&eacute;e (-10 &agrave; 0 pp)", moderate_improving, _tc['moderate_improving'])}
                            {_row(_tc['strong_improving'],   "Forte am&eacute;lioration (&lt;-10 pp)",                  strong_improving,  _tc['strong_improving'])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                
                if strong_worsening + moderate_worsening > len(selected_regions) / 2:
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(193, 68, 14, 0.10), rgba(193, 68, 14, 0.05));
                            border: 1px solid {PALETTE['degraded']};
                            border-radius: 8px;
                            padding: 0.8rem;
                            margin-top: 1rem;
                        ">
                            <div style="display: flex; align-items: center; gap: 0.6rem;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="{PALETTE['degraded']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;">
                                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                    <line x1="12" y1="9" x2="12" y2="13"/>
                                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                                </svg>
                                <div style="flex: 1;">
                                    <strong style="color: {PALETTE['degraded']}; font-size: 0.9rem;">Alerte :</strong>
                                    <span style="color: {PALETTE['ink']}; font-size: 0.85rem; display: block; margin-top: 0.2rem;">
                                        Plus de la moitié des régions sélectionnées montrent une aggravation de la dégradation. 
                                        Une intervention prioritaire est nécessaire.
                                    </span>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Types de dégradation par région")
        degradation_types = status_expanded_f[
            status_expanded_f["class"].isin(["Dégradation persistante", "Dégradation récente", "Dégradation baseline"])
        ].copy()
    
        if not degradation_types.empty:
            fig_deg_types = px.bar(
                degradation_types,
                x="region",
                y="pct",
                color="class",
                color_discrete_map={
                    "Dégradation persistante": "#7A3B2E",
                    "Dégradation récente": "#B5654A",
                    "Dégradation baseline": "#D9A28A",
                },
                category_orders={"class": ["Dégradation persistante", "Dégradation récente", "Dégradation baseline"]},
                labels={"pct": "% de la superficie", "region": "", "class": "Type"},
            )
            fig_deg_types.update_traces(
                hovertemplate="<b>%{fullData.name}</b><br>% de la superficie: %{y:.1f}%<extra></extra>"
            )
            polish_chart(fig_deg_types, height=430, show_source=False)
            fig_deg_types.update_layout(xaxis_tickangle=-35, legend_title="")
            st.plotly_chart(fig_deg_types, width="stretch")
            render_chart_source(SOURCE_LAND)
            deg_types_export = degradation_types.rename(
                columns={
                    "region": "Région",
                    "class": "Type de dégradation",
                    "pct": "Pourcentage (%)",
                    "area_ha": "Superficie (ha)",
                }
            )
            cols_deg = [c for c in ["Région", "Type de dégradation", "Pourcentage (%)", "Superficie (ha)"] if c in deg_types_export.columns]
            to_csv_download_button(
                deg_types_export[cols_deg],
                f"types_degradation_{selected_year}.csv",
                "Télécharger en CSV",
                "download_deg_types"
            )
            st.markdown(
                '<div class="card-note">'
                '<strong>Interprétation :</strong> La dégradation <em>persistante</em> indique une détérioration continue sur toute la période. '
                'La dégradation <em>récente</em> montre une détérioration dans la période de suivi uniquement. '
                'La dégradation <em>baseline</em> était présente dès la période de référence.'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("Aucune donnée de dégradation détaillée disponible pour la sélection actuelle.")
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Sous-indicateurs SDG 15.3.1")
        sel_ind = st.selectbox(
            "Choisir un sous-indicateur",
            indicators,
            format_func=lambda indicator: indicator_labels.get(indicator) or str(indicator),
        )
        sel_ind_label = indicator_labels.get(sel_ind, sel_ind)
        st.markdown(f"##### Répartition selon {sel_ind_label}")
        sub_f = subind[
            (subind["indicator"] == sel_ind)
            & (subind["region"].isin(selected_regions))
        ]
        fig_sub_indicator = px.bar(
            sub_f,
            x="region",
            y="pct",
            color="class",
            color_discrete_map=status_color_map,
            category_orders={"class": ["Dégradé", "Stable", "Amélioré"]},
            labels={"pct": "% de la superficie", "region": "", "class": "Classe"},
        )
        fig_sub_indicator.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>% de la superficie: %{y:.1f}%<extra></extra>"
        )
        polish_chart(fig_sub_indicator, height=430, show_source=False)
        fig_sub_indicator.update_layout(xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_sub_indicator, width="stretch")
        render_chart_source(SOURCE_LAND)
        sub_indicator_export = sub_f.rename(
            columns={
                "region": "Région",
                "indicator": "Sous-indicateur",
                "class": "Statut",
                "pct": "Pourcentage (%)",
                "area_ha": "Superficie (ha)",
            }
        )
        cols_sub = [c for c in ["Région", "Sous-indicateur", "Statut", "Pourcentage (%)", "Superficie (ha)"] if c in sub_indicator_export.columns]
        to_csv_download_button(
            sub_indicator_export[cols_sub],
            f"sous_indicateur_{sel_ind.replace(' ', '_')}_{selected_year}.csv",
            "Télécharger en CSV",
            "download_sub_indicator"
        )
    
        
        
        
        
        st.markdown("##### Diagnostic des causes par sous-indicateur")
        sub_degraded = subind[
            (subind["indicator"].isin(indicators))
            & (subind["region"].isin(selected_regions))
            & (subind["class"] == "Dégradé")
        ].copy()
        sub_degraded["indicator_label"] = sub_degraded["indicator"].map(indicator_labels)
        heatmap_causes_data = (
            sub_degraded.pivot_table(
                index="region",
                columns="indicator_label",
                values="pct",
                aggfunc="sum",
                fill_value=0,
            )
            .reindex(degraded_regions["region"])
            .rename_axis(None, axis=1)
        )
        heatmap_causes_data = heatmap_causes_data[[indicator_labels[indicator] for indicator in indicators]]
        fig_heatmap_causes = px.imshow(
            heatmap_causes_data,
            color_continuous_scale=[PALETTE["stable"], PALETTE["accent2"], PALETTE["degraded"]],
            aspect="auto",
            labels=dict(x="", y="", color="% dégradé"),
            zmin=0,
            zmax=100,
        )
        fig_heatmap_causes.update_traces(
            hovertemplate="% dégradé: %{z:.1f}%<extra></extra>"
        )
        polish_chart(fig_heatmap_causes, height=max(420, len(heatmap_causes_data) * 32 + 90), show_source=False)
        fig_heatmap_causes.update_layout(coloraxis_colorbar=dict(title="% dégradé"))
        st.plotly_chart(fig_heatmap_causes, width="stretch")
        render_chart_source(SOURCE_LAND)
        heatmap_causes_export = heatmap_causes_data.reset_index().rename(columns={"index": "Région"})
        to_csv_download_button(
            heatmap_causes_export,
            f"heatmap_causes_degradation_{selected_year}.csv",
            "Télécharger en CSV",
            "download_heatmap_causes"
        )
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Table de priorité")
        priority_table = degraded_regions.copy()
        priority_table["Priorité"] = priority_table["pct"].map(
            lambda value: "Très élevée"
            if value >= 70
            else "Élevée"
            if value >= 50
            else "Moyenne"
            if value >= 30
            else "Faible"
        )
        priority_table = priority_table.rename(
            columns={
                "region": "Région",
                "pct": "% dégradé",
                "area_ha": "Superficie dégradée (ha)",
            }
        )
        priority_table["% dégradé"] = priority_table["% dégradé"].map(format_pct)
        priority_table["Superficie dégradée (ha)"] = priority_table["Superficie dégradée (ha)"].map(format_int)
        st.dataframe(
            priority_table[["Région", "% dégradé", "Superficie dégradée (ha)", "Priorité"]],
            width="stretch",
            hide_index=True,
        )
        render_chart_source(SOURCE_LAND)
        priority_table_export = degraded_regions.copy()
        priority_table_export["Priorité"] = priority_table_export["pct"].map(
            lambda value: "Très élevée"
            if value >= 70
            else "Élevée"
            if value >= 50
            else "Moyenne"
            if value >= 30
            else "Faible"
        )
        priority_table_export = priority_table_export.rename(
            columns={
                "region": "Région",
                "pct": "Dégradation (%)",
                "area_ha": "Superficie dégradée (ha)",
            }
        )
        to_csv_download_button(
            priority_table_export[["Région", "Dégradation (%)", "Superficie dégradée (ha)", "Priorité"]],
            f"table_priorite_degradation_{selected_year}.csv",
            "Télécharger en CSV",
            "download_priority_table"
        )
    
    


if tab_secheresse.open:
    with tab_secheresse:
        drought_current = drought_land_f.copy()
        severe_extreme_area = drought_current.loc[
            drought_current["class"].isin(["Sévère", "Extrême"]), "area_ha"
        ].sum()
        drought_total_area = drought_current["area_ha"].sum()
        severe_extreme_area_pct = (
            severe_extreme_area / drought_total_area * 100 if drought_total_area else 0
        )
        
        
        no_drought_area = drought_current.loc[drought_current["class"] == "Aucune sécheresse", "area_ha"].sum()
        no_drought_pct = (no_drought_area / drought_total_area * 100) if drought_total_area else 0
        
        
        regions_severe_extreme = drought_current[drought_current["class"].isin(["Sévère", "Extrême"])]["region"].nunique()
        regions_no_drought = drought_current[drought_current["pct"].groupby(drought_current["region"]).transform("sum") == 100]["region"].nunique() if not drought_current.empty else 0
        
        
        if selected_year >= min(YEARS) + 2:
            last_3_years = drought_land_selected[drought_land_selected["year"].isin([selected_year-2, selected_year-1, selected_year])]
            severe_extreme_trend = last_3_years.groupby("year").apply(
                lambda year_df: drought_area_share(year_df, ["Sévère", "Extrême"])
            )
            if len(severe_extreme_trend) >= 2:
                trend_direction = "↗" if severe_extreme_trend.iloc[-1] > severe_extreme_trend.iloc[0] else "↘"
                trend_change = severe_extreme_trend.iloc[-1] - severe_extreme_trend.iloc[0]
            else:
                trend_direction = "→"
                trend_change = 0
        else:
            trend_direction = "→"
            trend_change = 0
        
        
        moderate_plus_area = drought_current.loc[
            drought_current["class"].isin(["Modérée", "Sévère", "Extrême"]), "area_ha"
        ].sum()
    
        render_kpi_row(
            [
                (
                    "Superficie modérée à extrême",
                    f"{format_int(float(moderate_plus_area))} ha",
                    f"Superficie en sécheresse modérée, sévère ou extrême en {selected_year} — périmètre d'intervention élargi",
                ),
                (
                    "Superficie sévère/extrême",
                    f"{format_int(float(severe_extreme_area))} ha",
                    f"Superficie touchée par une sécheresse sévère ou extrême en {selected_year}",
                ),
                (
                    "Sécheresse sévère/extrême",
                    format_pct(float(severe_extreme_area_pct)),
                    "Part de la superficie sélectionnée en classes sévère ou extrême",
                ),
            ]
        )
        
        
        no_drought_by_region = (
            drought_current[drought_current["class"] == "Aucune sécheresse"]
            .groupby("region", as_index=False)
            .agg(pct=("pct", "sum"))
            .sort_values(by="pct", ascending=False)
        )
        best_drought_region = str(no_drought_by_region.iloc[0]["region"]) if not no_drought_by_region.empty else "-"
        best_drought_pct = float(no_drought_by_region.iloc[0]["pct"]) if not no_drought_by_region.empty else 0.0
    
        
        render_kpi_row(
            [
                (
                    "Tendance 3 ans",
                    f"{trend_direction} {trend_change:+.1f}pp",
                    (
                        f"Variation de la part de superficie en sécheresse sévère/extrême entre {selected_year-2} et {selected_year}. "
                        "« pp » veut dire « point de pourcentage » : c'est simplement la différence entre deux pourcentages. "
                        "Par exemple, passer de 40% à 30% fait -10 pp (et non -10%). "
                        "Ici, une valeur négative (↘) veut dire que la sécheresse sévère a reculé depuis 3 ans ; "
                        "une valeur positive (↗) veut dire qu'elle a progressé."
                        if selected_year >= min(YEARS) + 2 else "Pas assez de données (il faut au moins 3 années de sécheresse sélectionnées)"
                    ),
                ),
                (
                    "Sans sécheresse",
                    format_pct(float(no_drought_pct)),
                    "Part de la superficie en classe sans sécheresse",
                ),
                (
                    "Région la moins exposée",
                    best_drought_region,
                    f"{format_pct(best_drought_pct)} de superficie sans sécheresse en {selected_year} — modèle de résilience climatique",
                ),
            ]
        )
        
        
        
        
        st.markdown(f"##### Évolution temporelle ({min(YEARS)}–{max(YEARS)})")
        dl_evol = drought_land[drought_land["region"].isin(selected_regions)]
        drought_year_totals = dl_evol.groupby("year", as_index=False).agg(total_area_ha=("area_ha", "sum"))
        evol = (
            dl_evol.groupby(["year", "class"], as_index=False)["area_ha"].sum()
            .merge(drought_year_totals, on="year", how="left")
        )
        evol["pct"] = (evol["area_ha"] / evol["total_area_ha"] * 100).where(
            evol["total_area_ha"] > 0, 0
        )
        fig_evol = px.line(
            evol,
            x="year",
            y="pct",
            color="class",
            markers=True,
            color_discrete_map=DROUGHT_COLORS,
            category_orders={"class": ["Aucune sécheresse", "Légère", "Modérée", "Sévère", "Extrême"]},
            labels={"pct": "% de la superficie", "year": "Année", "class": "Niveau"},
        )
        fig_evol.update_traces(
            line=dict(width=2.6),
            marker=dict(size=7, line=dict(color="#FFFFFF", width=1.2)),
            hovertemplate="<b>%{fullData.name}</b><br>Année: %{x:.0f}<br>% de la superficie: %{y:.1f}%<extra></extra>",
        )
        polish_chart(fig_evol, height=420, show_source=False)
        fig_evol.update_layout(
            legend_title="",
            xaxis=dict(tickmode="array", tickvals=YEARS, tickformat="d"),
            yaxis=dict(range=[0, 100], ticksuffix="%"),
        )
        st.plotly_chart(fig_evol, width="stretch")
        render_chart_source(SOURCE_DROUGHT)
        evol_export = pd.DataFrame(
            {
                "Année": evol["year"],
                "Niveau de sécheresse": evol["class"],
                "Pourcentage (%)": evol["pct"],
            }
        )
        to_csv_download_button(
            evol_export,
            f"evolution_secheresse_{min(YEARS)}_{max(YEARS)}.csv",
            "Télécharger en CSV",
            "download_drought_evolution"
        )
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Carte de chaleur : sécheresse sévère/extrême par région et année")
        dl_all = drought_land[drought_land["region"].isin(selected_regions)]
        dl_severe = (
            dl_all[dl_all["class"].isin(["Sévère", "Extrême"])]
            .groupby(["region", "year"], as_index=False)["pct"]
            .sum()
        )
        
        all_years_drought = sorted(dl_all["year"].unique())
        all_regions_drought = sorted(dl_all["region"].unique())
        drought_heatmap_full = (
            pd.MultiIndex.from_product([all_regions_drought, all_years_drought], names=["region", "year"])
            .to_frame(index=False)
            .merge(dl_severe, on=["region", "year"], how="left")
            .fillna({"pct": 0.0})
        )
        drought_heatmap_pivot = drought_heatmap_full.pivot(index="region", columns="year", values="pct")
        
        drought_heatmap_pivot["avg"] = drought_heatmap_pivot.mean(axis=1)
        drought_heatmap_pivot = drought_heatmap_pivot.sort_values("avg", ascending=False).drop("avg", axis=1)
        fig_drought_heatmap = px.imshow(
            drought_heatmap_pivot,
            color_continuous_scale=[
                PALETTE["stable"],
                PALETTE["accent2"],
                DROUGHT_COLORS["Sévère"],
                DROUGHT_COLORS["Extrême"],
            ],
            aspect="auto",
            labels=dict(x="Année", y="Région", color="% sévère/extrême"),
            zmin=0,
            zmax=100,
        )
        fig_drought_heatmap.update_traces(
            hovertemplate="<b>%{y}</b><br>Année : %{x}<br>% sévère/extrême : %{z:.1f}%<extra></extra>",
            texttemplate="%{z:.0f}%",
            textfont=dict(size=10),
        )
        _drought_hm_years = list(drought_heatmap_pivot.columns)
        polish_chart(fig_drought_heatmap, height=max(420, len(drought_heatmap_pivot) * 35 + 100), show_source=False)
        fig_drought_heatmap.update_layout(
            coloraxis_colorbar=dict(title="% sévère/<br>extrême", ticksuffix="%"),
            xaxis=dict(
                side="top",
                tickangle=0,
                tickmode="array",
                tickvals=_drought_hm_years,
                ticktext=[str(y) for y in _drought_hm_years],
            ),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_drought_heatmap, width='stretch')
        render_chart_source(SOURCE_DROUGHT)
        st.markdown(
            '<div class="card-note">'
            '<strong>Lecture :</strong> Les couleurs chaudes indiquent les années et régions où la sécheresse '
            'sévère et extrême a été la plus intense. Les régions sont triées par intensité moyenne décroissante '
            'sur toute la période.'
            '</div>',
            unsafe_allow_html=True,
        )
        drought_hm_export = drought_heatmap_pivot.reset_index().rename(columns={"region": "Région"})
        to_csv_download_button(
            drought_hm_export,
            f"heatmap_secheresse_severe_{min(YEARS)}_{max(YEARS)}.csv",
            "Télécharger en CSV",
            "download_drought_heatmap"
        )
    
        
        
        
        
        st.markdown("---")
        st.markdown(f"##### Exposition à la sécheresse par région — {selected_year}")
        fig_drought = px.bar(
            drought_land_f,
            x="region",
            y="pct",
            color="class",
            color_discrete_map=DROUGHT_COLORS,
            category_orders={"class": ["Aucune sécheresse", "Légère", "Modérée", "Sévère", "Extrême"]},
            labels={"pct": "% de la superficie", "region": "", "class": "Niveau"},
        )
        fig_drought.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>% de la superficie: %{y}<extra></extra>"
        )
        polish_chart(fig_drought, height=460, show_source=False)
        fig_drought.update_layout(xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_drought, width="stretch")
        render_chart_source(SOURCE_DROUGHT)
        drought_current_export = drought_land_f.copy()
        drought_current_export = drought_current_export.rename(
            columns={
                "region": "Région",
                "year": "Année",
                "class": "Niveau de sécheresse",
                "pct": "Pourcentage (%)",
                "area_ha": "Superficie (ha)",
            }
        )
        to_csv_download_button(
            drought_current_export[["Région", "Année", "Niveau de sécheresse", "Pourcentage (%)", "Superficie (ha)"]],
            f"exposition_secheresse_{selected_year}.csv",
            "Télécharger en CSV",
            "download_drought_current"
        )
    
        
        
        
        
        st.markdown(f"##### Classement des régions par sécheresse sévère/extrême — {selected_year}")
        severe_rank = (
            drought_land_f[drought_land_f["class"].isin(["Sévère", "Extrême"])]
            .groupby("region", as_index=False)
            .agg(pct=("pct", "sum"))
            .sort_values("pct", ascending=True)
        )
        
        all_sel_regions_df = pd.DataFrame({"region": list(selected_regions)})
        severe_rank = all_sel_regions_df.merge(severe_rank, on="region", how="left").fillna({"pct": 0.0})
        severe_rank = severe_rank.sort_values("pct", ascending=True).reset_index(drop=True)
        severe_rank["pct_label"] = severe_rank["pct"].map(
            lambda v: f"{v:.4f}%" if 0 < v < 0.1 else f"{v:.1f}%"
        )
        fig_severe_rank = px.bar(
            severe_rank,
            x="pct",
            y="region",
            orientation="h",
            color="pct",
            color_continuous_scale=[PALETTE["stable"], PALETTE["accent2"], DROUGHT_COLORS["Sévère"], DROUGHT_COLORS["Extrême"]],
            labels={"pct": "% sévère/extrême", "region": ""},
        )
        fig_severe_rank.update_traces(
            text=severe_rank["pct_label"],
            textposition="outside",
            customdata=severe_rank[["pct_label"]],
            hovertemplate="<b>%{y}</b><br>% sévère/extrême : %{customdata[0]}<extra></extra>",
        )
        _max_severe = float(severe_rank["pct"].max()) if not severe_rank.empty else 0
        polish_chart(fig_severe_rank, height=max(360, len(severe_rank) * 36 + 90), show_source=False)
        fig_severe_rank.update_layout(
            coloraxis_showscale=False,
            xaxis=dict(
                ticksuffix="%",
                range=[0, max(_max_severe * 1.20, 1)],
            ),
            yaxis=dict(autorange="reversed"),
            showlegend=False,
            uniformtext_minsize=9,
            uniformtext_mode="show",
        )
        st.plotly_chart(fig_severe_rank, width="stretch")
        render_chart_source(SOURCE_DROUGHT)
        severe_rank_export = severe_rank[["region", "pct"]].rename(
            columns={"region": "Région", "pct": "Sécheresse sévère/extrême (%)"}
        )
        severe_rank_export["Année"] = selected_year
        to_csv_download_button(
            severe_rank_export[["Région", "Année", "Sécheresse sévère/extrême (%)"]],
            f"classement_secheresse_severe_{selected_year}.csv",
            "Télécharger en CSV",
            "download_severe_rank"
        )
    
        
        
        
        
        st.markdown("---")
        st.markdown(f"##### Détail par classe de sécheresse — {selected_year}")
        drought_class_order = ["Aucune sécheresse", "Légère", "Modérée", "Sévère", "Extrême"]
        available_drought_classes = [
            class_name
            for class_name in drought_class_order
            if class_name in drought_current["class"].unique()
        ]
        if available_drought_classes:
            selected_drought_class = st.selectbox(
                "Classe de sécheresse",
                available_drought_classes,
                index=0,
                key="drought_class_region_filter",
            )
            drought_class_region = cast(pd.DataFrame, (
                drought_current[drought_current["class"] == selected_drought_class]
                .groupby("region", as_index=False)
                .agg({"pct": "sum"})
            ))
            drought_class_region = drought_class_region.sort_values(by="pct", ascending=True)
            drought_class_region["pct_label"] = drought_class_region["pct"].map(
                lambda value: f"{value:.4f}%" if 0 < abs(value) < 0.1 else f"{value:.1f}%"
            )
            fig_drought_class = px.bar(
                drought_class_region,
                x="pct",
                y="region",
                orientation="h",
                color_discrete_sequence=[DROUGHT_COLORS.get(selected_drought_class, PALETTE["accent2"])],
                labels={"pct": "% de la superficie", "region": ""},
            )
            fig_drought_class.update_traces(
                text=drought_class_region["pct_label"],
                textposition="outside",
                customdata=drought_class_region[["pct_label"]],
                hovertemplate="% de la superficie: %{customdata[0]}<extra></extra>",
            )
            max_drought_class_pct = float(drought_class_region["pct"].max()) if not drought_class_region.empty else 0
            polish_chart(fig_drought_class, height=max(360, len(drought_class_region) * 36 + 90), show_source=False)
            fig_drought_class.update_layout(
                xaxis=dict(
                    ticksuffix="%",
                    range=[0, max(max_drought_class_pct * 1.18, 1)],
                ),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
                uniformtext_minsize=9,
                uniformtext_mode="show",
            )
            st.plotly_chart(fig_drought_class, width="stretch")
            render_chart_source(SOURCE_DROUGHT)
            drought_class_export = drought_class_region.rename(
                columns={"region": "Région", "pct": f"{selected_drought_class} (%)"}
            )[["Région", f"{selected_drought_class} (%)"]]
            drought_class_export["Année"] = selected_year
            drought_class_export["Classe de sécheresse"] = selected_drought_class
            to_csv_download_button(
                drought_class_export[["Région", "Année", "Classe de sécheresse", f"{selected_drought_class} (%)"]],
                f"secheresse_{selected_drought_class.replace(' ', '_')}_{selected_year}.csv",
                "Télécharger en CSV",
                "download_drought_class"
            )
        else:
            st.info("Aucune donnée de sécheresse disponible pour la sélection actuelle.")
    
    


if tab_dvi.open:
    with tab_dvi:
        st.markdown("### Indice de Vulnérabilité à la Sécheresse (DVI) — Positionnement du Maroc par rapport aux pays de référence")
        st.caption("Composite reconstruit (social, économique, infrastructurel) — indicateur SO3-3")
        country_names = {
            "DZA": "Algérie",
            "EGY": "Égypte",
            "ESP": "Espagne",
            "MAR": "Maroc",
            "MRT": "Mauritanie",
            "PRT": "Portugal",
            "TUN": "Tunisie",
        }
        dvi = dvi.copy()
        dvi["pays"] = dvi["iso3"].map(country_names).fillna(dvi["iso3"])
        mar_dvi = dvi[dvi["iso3"] == "MAR"].iloc[0] if "MAR" in set(dvi["iso3"]) else None
        dvi_rank = (
            int(dvi.sort_values("DVI", ascending=False).reset_index(drop=True).query("iso3 == 'MAR'").index[0]) + 1
            if mar_dvi is not None
            else None
        )
        strongest_component = (
            mar_dvi[["social", "economic", "infrastructural"]].astype(float).idxmax()
            if mar_dvi is not None
            else "-"
        )
        weakest_component = (
            mar_dvi[["social", "economic", "infrastructural"]].astype(float).idxmin()
            if mar_dvi is not None
            else "-"
        )
        component_labels = {
            "social": "Social",
            "economic": "Économique",
            "infrastructural": "Infrastructurel",
        }
        
        
        avg_dvi = dvi["DVI"].mean()
        dvi_gap = (float(mar_dvi["DVI"]) - avg_dvi) if mar_dvi is not None else 0
        best_country = dvi.sort_values("DVI").iloc[0] if not dvi.empty else None
        worst_country = dvi.sort_values("DVI", ascending=False).iloc[0] if not dvi.empty else None
        
        render_kpi_row(
            [
                (
                    "DVI Maroc",
                    f"{float(mar_dvi['DVI']):.3f}" if mar_dvi is not None else "-",
                    "Indice composite de vulnérabilité à la sécheresse pour MAR",
                ),
                (
                    "Rang Maroc",
                    f"{dvi_rank} / {len(dvi)}" if dvi_rank is not None else "-",
                    "Classement décroissant parmi les pays de comparaison",
                ),
                (
                    "Composante dominante",
                    component_labels.get(str(strongest_component), "-"),
                    "Dimension qui contribue le plus au DVI du Maroc",
                ),
            ]
        )
        
        
        render_kpi_row(
            [
                (
                    "Score composante critique",
                    f"{float(mar_dvi[strongest_component]):.2f} / 1.0" if mar_dvi is not None else "-",
                    (
                        f"Score de vulnérabilité {component_labels.get(str(strongest_component), strongest_component)} — "
                        f"plus proche de 1.0 = vulnérabilité maximale"
                        if mar_dvi is not None else "Score de la composante la plus vulnérable"
                    ),
                ),
                (
                    "Atout relatif",
                    component_labels.get(str(weakest_component), "-"),
                    f"Composante où le Maroc est le moins vulnérable (score {float(mar_dvi[weakest_component]):.2f}/1.0) — levier à valoriser" if mar_dvi is not None else "Composante la moins vulnérable",
                ),
                (
                    "Meilleur pays",
                    f"{best_country['pays']} ({best_country['DVI']:.3f})" if best_country is not None else "-",
                    "Pays avec la vulnérabilité la plus faible — référence à atteindre",
                ),
            ]
        )
    
        if mar_dvi is not None:
            st.markdown(
                f"""
                <div class="card-note">
                    <strong>Executive Summary :</strong>
                    Le Maroc affiche un DVI de <strong>{float(mar_dvi['DVI']):.3f}</strong>
                    et se classe <strong>{dvi_rank} / {len(dvi)}</strong> parmi les pays de référence.
                    La vulnérabilité est principalement portée par la composante
                    <strong>{component_labels.get(str(strongest_component), "-")}</strong>.
                    La composante <strong>{component_labels.get(str(weakest_component), "-")}</strong>
                    constitue le meilleur levier relatif à préserver.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="card-note">
                    <strong>Executive Summary :</strong>
                    Les données DVI du Maroc ne sont pas disponibles dans le fichier chargé.
                </div>
                """,
                unsafe_allow_html=True,
            )
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Classement DVI global")
        dvi_sorted = dvi.sort_values("DVI", ascending=True)
        fig_dvi = px.bar(
            dvi_sorted,
            x="DVI",
            y="pays",
            orientation="h",
            color="DVI",
            color_continuous_scale=[PALETTE["stable"], PALETTE["accent2"], PALETTE["degraded"]],
            labels={"DVI": "Indice DVI (0–1)", "pays": "Pays"},
            hover_name="pays",
            hover_data={"DVI": ":.3f", "pays": False},
        )
        fig_dvi.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Indice DVI: %{x:.3f}<extra></extra>"
        )
        polish_chart(fig_dvi, height=380, show_source=False)
        fig_dvi.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_dvi, width="stretch")
        render_chart_source(SOURCE_DVI)
        dvi_export = dvi_sorted[["pays", "DVI", "social", "economic", "infrastructural"]].copy()
        dvi_export = dvi_export.rename(
            columns={
                "pays": "Pays",
                "DVI": "Indice DVI",
                "social": "Composante sociale",
                "economic": "Composante économique",
                "infrastructural": "Composante infrastructurelle",
            }
        )
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Composantes du DVI")
        dvi_components = dvi.melt(
            id_vars=["iso3", "pays", "DVI"],
            value_vars=["social", "economic", "infrastructural"],
            var_name="composante",
            value_name="valeur",
        )
        dvi_components["composante"] = dvi_components["composante"].map(
            {"social": "Social", "economic": "Économique", "infrastructural": "Infrastructurel"}
        )
        country_order = dvi_sorted["pays"].tolist()
        component_order = ["Social", "Économique", "Infrastructurel"]
        components_matrix = (
            dvi_components.pivot_table(
                index="pays",
                columns="composante",
                values="valeur",
                aggfunc="mean",
            )
            .reindex(country_order)
            .reindex(columns=component_order)
        )
        fig_components = px.imshow(
            components_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=[PALETTE["improved"], PALETTE["stable"], PALETTE["degraded"]],
            zmin=0,
            zmax=1,
            labels=dict(x="Composante", y="Pays", color="Valeur"),
        )
        fig_components.update_traces(
            hovertemplate="<b>%{y}</b><br>%{x}: %{z:.3f}<extra></extra>",
            texttemplate="%{z:.2f}",
            textfont=dict(size=13, color=PALETTE["ink"]),
        )
        polish_chart(fig_components, height=max(360, len(components_matrix) * 42 + 120), show_source=False)
        fig_components.update_layout(
            coloraxis_colorbar=dict(title="Vulnérabilité<br>0-1"),
            xaxis=dict(side="top"),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig_components, width="stretch")
        render_chart_source(SOURCE_DVI)
        components_export = components_matrix.reset_index().rename(columns={"pays": "Pays"})
    
        
        
        
        
        st.markdown("---")
        gap_export = None
        if mar_dvi is not None and best_country is not None:
            reference_name = str(best_country["pays"])
            st.markdown(f"##### Écart du Maroc avec {reference_name}, pays le moins vulnérable")
            gap_components = pd.DataFrame(
                [
                    {
                        "Composante": label,
                        "Écart": float(mar_dvi[column]) - float(best_country[column]),
                        "Maroc": float(mar_dvi[column]),
                        reference_name: float(best_country[column]),
                    }
                    for column, label in component_labels.items()
                ]
            )
            gap_components["Écart"] = gap_components["Écart"].round(3)
            gap_components["Maroc"] = gap_components["Maroc"].round(3)
            gap_components[reference_name] = gap_components[reference_name].round(3)
            gap_components["Écart affiché"] = gap_components["Écart"].map(lambda value: f"{value:+.3f}")
            fig_gap = px.bar(
                gap_components,
                x="Écart",
                y="Composante",
                text="Écart affiché",
                orientation="h",
                color="Écart",
                color_continuous_scale=[PALETTE["improved"], PALETTE["stable"], PALETTE["degraded"]],
                range_color=[-1, 1],
                labels={"Écart": "Écart de vulnérabilité"},
            )
            fig_gap.update_traces(
                customdata=gap_components[["Maroc", reference_name]],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Écart Maroc - référence: %{x:+.3f}<br>"
                    "Maroc: %{customdata[0]:.3f}<br>"
                    f"{reference_name}: %{{customdata[1]:.3f}}"
                    "<extra></extra>"
                ),
            )
            polish_chart(fig_gap, height=320, show_source=False)
            fig_gap.add_vline(
                x=0,
                line_width=1.5,
                line_dash="dash",
                line_color=PALETTE["muted"],
            )
            fig_gap.update_layout(
                coloraxis_showscale=False,
                xaxis=dict(
                    zeroline=True,
                    title=f"Écart par rapport à {reference_name} (Maroc - référence)",
                ),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_gap, width="stretch")
            render_chart_source(SOURCE_DVI)
            gap_export = gap_components[["Composante", "Maroc", reference_name, "Écart"]].copy()
            gap_export = gap_export.rename(columns={
                "Composante": "Composante DVI",
                "Maroc": "Maroc (score)",
                reference_name: f"{reference_name} (score)",
                "Écart": "Écart (Maroc - référence)",
            })
            gap_filename = f"ecart_dvi_maroc_vs_{reference_name.lower().replace(' ', '_')}.csv"
    
        
        
        
        
        st.markdown("---")
        st.markdown("##### Classement des pays par composante")
        st.markdown(
            f"""
            <div class="method-note">
                <strong>Lecture :</strong> Le rang 1 correspond au pays <em>le moins vulnérable</em> sur cette composante.
                Plus le rang est élevé, plus la vulnérabilité est forte. Le Maroc est mis en évidence.
            </div>
            """,
            unsafe_allow_html=True,
        )
    
        
        _rank_df = dvi[["pays", "social", "economic", "infrastructural", "DVI"]].copy()
        for col in ["social", "economic", "infrastructural", "DVI"]:
            _rank_df[f"rang_{col}"] = _rank_df[col].rank(method="min", ascending=True).astype(int)
    
        
        _rank_rows = []
        for pays_row in _rank_df.sort_values("rang_DVI").itertuples():
            _rank_rows.append({
                "Pays": pays_row.pays,
                "Social (rang / score)":           f"{pays_row.rang_social} ({pays_row.social:.2f})",
                "Économique (rang / score)":       f"{pays_row.rang_economic} ({pays_row.economic:.2f})",
                "Infrastructurel (rang / score)":  f"{pays_row.rang_infrastructural} ({pays_row.infrastructural:.2f})",
                "DVI global (rang / score)":       f"{pays_row.rang_DVI} ({pays_row.DVI:.3f})",
            })
        _rank_display = pd.DataFrame(_rank_rows)
    
        
        st.dataframe(
            _rank_display,
            hide_index=True,
            width='stretch',
            column_config={
                "Pays":                           st.column_config.TextColumn("Pays", width="medium"),
                "Social (rang / score)":          st.column_config.TextColumn("Social", width="medium"),
                "Économique (rang / score)":      st.column_config.TextColumn("Économique", width="medium"),
                "Infrastructurel (rang / score)": st.column_config.TextColumn("Infrastructurel", width="medium"),
                "DVI global (rang / score)":      st.column_config.TextColumn("DVI global", width="medium"),
            },
        )
        render_chart_source(SOURCE_DVI)
        st.markdown(
            f"""
            <div class="card-note">
                <strong>Interprétation pour le Maroc :</strong>
                La composante avec le rang le plus élevé est la priorité d'action la plus urgente.
                Un rang faible (proche de 1) indique un levier relatif à préserver.
            </div>
            """,
            unsafe_allow_html=True,
        )
        _rank_export = _rank_df[["pays", "social", "rang_social", "economic", "rang_economic",
                                  "infrastructural", "rang_infrastructural", "DVI", "rang_DVI"]].copy()
        _rank_export.columns = [
            "Pays", "Score Social", "Rang Social",
            "Score Économique", "Rang Économique",
            "Score Infrastructurel", "Rang Infrastructurel",
            "Score DVI", "Rang DVI global",
        ]
        st.markdown("---")
        st.markdown("##### Méthodologie et source")
        st.markdown(
            f"""
            <div class="method-note">
                <strong>Note méthodologique :</strong>
                Le DVI est un indice composite compris entre 0 et 1 qui synthétise trois dimensions
                de vulnérabilité à la sécheresse : sociale, économique et infrastructurelle.
                Une valeur plus élevée indique une vulnérabilité plus forte.
                <br><strong>{SOURCE_DVI}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
        st.markdown("##### Téléchargements")
        to_csv_download_button(
            dvi_export,
            "comparaison_dvi_pays.csv",
            "Télécharger le classement DVI global (CSV)",
            "download_dvi_comparison"
        )
        to_csv_download_button(
            components_export,
            "composantes_dvi_pays.csv",
            "Télécharger les composantes DVI (CSV)",
            "download_dvi_components"
        )
        if gap_export is not None:
            to_csv_download_button(
                gap_export,
                gap_filename,
                "Télécharger l'écart Maroc vs référence (CSV)",
                "download_dvi_gap"
            )
        to_csv_download_button(
            _rank_export,
            "dvi_rangs_par_composante.csv",
            "Télécharger les rangs par composante (CSV)",
            "download_dvi_ranks"
        )
    
    


if tab_recommandations.open:
    with tab_recommandations:
        st.markdown('<div id="recommendations-start"></div>', unsafe_allow_html=True)
        scroll_to_recommendations()

        
        st.markdown(
            f"""
            <style>
            .recommendations-main-title {{
                font-size: 2.2rem !important;
                font-weight: 900 !important;
                color: {PALETTE['ink']} !important;
                margin: 1.5rem 0 1rem 0 !important;
                padding-bottom: 0.5rem !important;
                border-bottom: 3px solid {PALETTE['hcp_gold']} !important;
                letter-spacing: 0 !important;
            }}
            
            .recommendations-section-title {{
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-size: 1.3rem !important;
                font-weight: 700 !important;
                color: {PALETTE['ink']} !important;
                margin: 2.5rem 0 1.2rem 0 !important;
                padding: 0 !important;
                background: none !important;
                border: none !important;
                border-top: 1px solid {PALETTE['line']} !important;
                padding-top: 1.4rem !important;
                letter-spacing: -0.01em !important;
            }}
            
            .recommendations-section-title::before {{
                content: "";
                display: inline-block;
                width: 3px;
                height: 1.3em;
                border-radius: 2px;
                background: linear-gradient(180deg, {PALETTE['hcp_gold']}, {PALETTE['hcp_bordeaux']});
                flex: 0 0 auto;
                align-self: center;
            }}
    
            .recommendations-subtitle {{
                font-size: 1.1rem !important;
                font-weight: 700 !important;
                color: {PALETTE['muted']} !important;
                margin: 1.2rem 0 0.7rem 0 !important;
                text-transform: none !important;
                letter-spacing: 0 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        
        def rec_title(text: str, level: str = "section") -> None:
            class_name = {
                "main": "recommendations-main-title",
                "section": "recommendations-section-title",
                "sub": "recommendations-subtitle",
            }[level]
            tag = "h3" if level == "main" else "h4" if level == "section" else "h5"
            st.markdown(f'<{tag} class="{class_name}">{text}</{tag}>', unsafe_allow_html=True)
    
        rec_title("Recommandations stratégiques pour l'action", "main")
        
        
        
        
        
        
        critical_regions = region_summary[region_summary["Degraded"] >= 70]["region"].tolist()
        high_risk_regions = region_summary[(region_summary["Degraded"] >= 50) & (region_summary["Degraded"] < 70)]["region"].tolist()
        resilient_regions = region_summary[region_summary["net_balance"] > 0]["region"].tolist()
        
        
        subind_analysis = subind[
            (subind["region"].isin(selected_regions))
            & (subind["indicator"].isin(["Productivité", "Couverture des terres", "Carbone organique du sol"]))
            & (subind["class"] == "Dégradé")
        ].groupby("indicator")["area_ha"].sum().sort_values(ascending=False)
        
        
        drought_critical = drought_risk[drought_risk["severe_extreme"] > 5]["region"].tolist()
        
        
        
        priority_data = []
        for _, row in region_summary.iterrows():
            region = row["region"]
            drought_score = drought_risk[drought_risk["region"] == region]["total_drought"].values[0] if region in drought_risk["region"].values else 0
            priority_data.append({
                "region": region,
                "degradation": row["Degraded"],
                "drought": drought_score
            })
        
        priority_input_df = pd.DataFrame(priority_data)
        
        
        
        entropy_weights = calculate_entropy_weights(
            priority_input_df, 
            ['degradation', 'drought']
        )
        
        
        priority_scores = []
        for _, row in priority_input_df.iterrows():
            combined_score = (
                row["degradation"] * entropy_weights['degradation'] + 
                row["drought"] * entropy_weights['drought']
            )
            priority_scores.append({
                "region": row["region"],
                "degradation": row["degradation"],
                "drought": row["drought"],
                "priority_score": combined_score
            })
        
        priority_df = pd.DataFrame(priority_scores).sort_values("priority_score", ascending=False)
        
        
        
        
        
        st.markdown(
            f"""
            <div style="background: {PALETTE['card']}; border: 1px solid {PALETTE['line']}; border-radius: 14px; margin-bottom: 1.2rem; box-shadow: 0 10px 28px rgba(107, 31, 58, 0.10); position: relative; overflow: hidden;">
                <div style="background: linear-gradient(120deg, {PALETTE['hcp_bordeaux']} 0%, {PALETTE['hcp_burgundy']} 100%); padding: 0.85rem 1.3rem; display: flex; align-items: center; gap: 0.5rem; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: -20px; right: -10px; width: 90px; height: 90px; background: radial-gradient(circle, {PALETTE['hcp_gold']}30, transparent 70%); border-radius: 50%;"></div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="{PALETTE['hcp_light_gold']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span style="color: {PALETTE['hcp_light_gold']}; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;">Analyse contextuelle</span>
                </div>
                <div style="padding: 1.1rem 1.3rem 1rem 1.3rem;">
                <h3 style="margin: 0 0 0.7rem 0; color: {PALETTE['ink']}; font-size: 1.4rem; font-weight: 800; line-height: 1.2; display: flex; align-items: center; gap: 0.6rem;">
                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 42px; height: 42px; background: linear-gradient(135deg, {PALETTE['hcp_bordeaux']}, {PALETTE['hcp_burgundy']}); color: {PALETTE['hcp_light_gold']}; font-size: 1.2rem; font-weight: 900; border-radius: 50%; box-shadow: 0 3px 10px rgba(107, 31, 58, 0.25);">{len(selected_regions)}</span>
                    <span>région{'s' if len(selected_regions) > 1 else ''} analysée{'s' if len(selected_regions) > 1 else ''}</span>
                </h3>
                <p style="margin: 0; color: {PALETTE['muted']}; font-size: 0.88rem; line-height: 1.5; max-width: 90%;">
                    Basé sur les données <strong style="color: {PALETTE['ink']};">SDG 15.3.1</strong> (dégradation des terres) 
                    et l'exposition à la sécheresse en <strong style="color: {PALETTE['ink']};">{selected_year}</strong>, 
                    ce module génère des recommandations ciblées et hiérarchisées pour orienter l'action publique 
                    vers les territoires et les leviers les plus critiques.
                </p>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0; margin-top: 1rem; padding-top: 0.9rem; border-top: 1px solid {PALETTE['line']}; font-size: 0.78rem; color: {PALETTE['muted']};">
                    <span style="display: inline-flex; align-items: center; gap: 0.4rem; padding-right: 1rem;">
                        <span style="display: inline-block; width: 6px; height: 6px; background: {PALETTE['hcp_gold']}; border-radius: 50%; flex-shrink: 0;"></span>
                        <strong style="color: {PALETTE['ink']};">Année :</strong>&nbsp;{selected_year}
                    </span>
                    <span style="width: 1px; height: 14px; background: {PALETTE['line']}; margin-right: 1rem; display: inline-block;"></span>
                    <span style="display: inline-flex; align-items: center; gap: 0.4rem; padding-right: 1rem;">
                        <span style="display: inline-block; width: 6px; height: 6px; background: {PALETTE['hcp_gold']}; border-radius: 50%; flex-shrink: 0;"></span>
                        <strong style="color: {PALETTE['ink']};">Référentiel :</strong>&nbsp;UNCCD GPG 15.3.1
                    </span>
                    <span style="width: 1px; height: 14px; background: {PALETTE['line']}; margin-right: 1rem; display: inline-block;"></span>
                    <span style="display: inline-flex; align-items: center; gap: 0.4rem;">
                        <span style="display: inline-block; width: 6px; height: 6px; background: {PALETTE['hcp_gold']}; border-radius: 50%; flex-shrink: 0;"></span>
                        <strong style="color: {PALETTE['ink']};">Mode :</strong>&nbsp;Génération dynamique
                    </span>
                </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown(
            f"""
            <div style="background: {PALETTE['card']}; border: 1px solid {PALETTE['line']}; border-radius: 14px; margin-bottom: 1.2rem; box-shadow: 0 10px 28px rgba(74, 124, 89, 0.10); position: relative; overflow: hidden;">
                <div style="background: linear-gradient(120deg, #2F5A3D 0%, {PALETTE['improved']} 100%); padding: 0.85rem 1.3rem; display: flex; align-items: center; gap: 0.5rem; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: -20px; right: -10px; width: 90px; height: 90px; background: radial-gradient(circle, rgba(255,255,255,0.12), transparent 70%); border-radius: 50%;"></div>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="rgba(255,255,255,0.9)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    <span style="color: rgba(255,255,255,0.92); font-size: 0.74rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;">Méthodologie scientifique</span>
                </div>
                <div style="padding: 1.1rem 1.3rem 1rem 1.3rem; position: relative; overflow: hidden;">
                <div style="position: absolute; top: -25px; right: -20px; width: 110px; height: 110px; background: radial-gradient(circle, rgba(74, 124, 89, 0.08), transparent 70%); border-radius: 50%;"></div>
                <h3 style="margin: 0 0 0.7rem 0; color: {PALETTE['ink']}; font-size: 1.4rem; font-weight: 800; line-height: 1.2; display: flex; align-items: center; gap: 0.6rem;">
                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; background: linear-gradient(135deg, {PALETTE['improved']}, #2F5A3D); color: white; font-size: 1.2rem; font-weight: 900; border-radius: 50%; box-shadow: 0 3px 10px rgba(74, 124, 89, 0.25);"><svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg></span>
                    <span>Score de priorité calculé par méthode d'entropie</span>
                </h3>
                <p style="margin: 0 0 0.8rem 0; color: {PALETTE['muted']}; font-size: 0.88rem; line-height: 1.5; max-width: 90%;">
                    Le <strong style="color: {PALETTE['ink']};">score de priorité</strong> combinant dégradation des terres et exposition à la sécheresse 
                    est calculé selon la <strong style="color: {PALETTE['ink']};">méthode d'entropie</strong>, une approche documentée 
                    qui attribue des poids objectifs basés sur la <strong style="color: {PALETTE['ink']};">variabilité informationnelle</strong> de chaque indicateur.
                </p>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 0; margin-top: 1rem; padding-top: 0.9rem; border-top: 1px solid {PALETTE['line']}; font-size: 0.78rem; color: {PALETTE['muted']};">
                    <span style="display: inline-flex; align-items: center; gap: 0.4rem; padding-right: 1rem;">
                        <span style="display: inline-block; width: 6px; height: 6px; background: {PALETTE['improved']}; border-radius: 50%; flex-shrink: 0;"></span>
                        <strong style="color: {PALETTE['ink']};">Poids dégradation :</strong>&nbsp;{entropy_weights['degradation']:.1%}
                    </span>
                    <span style="width: 1px; height: 14px; background: {PALETTE['line']}; margin-right: 1rem; display: inline-block;"></span>
                    <span style="display: inline-flex; align-items: center; gap: 0.4rem; padding-right: 1rem;">
                        <span style="display: inline-block; width: 6px; height: 6px; background: {PALETTE['improved']}; border-radius: 50%; flex-shrink: 0;"></span>
                        <strong style="color: {PALETTE['ink']};">Poids sécheresse :</strong>&nbsp;{entropy_weights['drought']:.1%}
                    </span>
                    <span style="width: 1px; height: 14px; background: {PALETTE['line']}; margin-right: 1rem; display: inline-block;"></span>
                    <span style="display: inline-flex; align-items: center; gap: 0.4rem;">
                        <span style="display: inline-block; width: 6px; height: 6px; background: {PALETTE['improved']}; border-radius: 50%; flex-shrink: 0;"></span>
                        <strong style="color: {PALETTE['ink']};">Méthode :</strong>&nbsp;Entropie objective
                    </span>
                </div>
                </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        
        render_kpi_row([
            ("Régions critiques", f"{len(critical_regions)}", "Régions où 70% ou plus de la surface est dégradée. Ce sont les zones les plus touchées : elles doivent être traitées en priorité absolue (mesures d'urgence, financement immédiat)."),
            ("Régions à risque élevé", f"{len(high_risk_regions)}", "Régions dont 50% à 70% de la surface est dégradée. La situation n'est pas encore critique, mais risque de s'aggraver sans action rapide : c'est le moment d'intervenir de façon préventive."),
            ("Régions résilientes", f"{len(resilient_regions)}", "Régions où la surface améliorée dépasse la surface dégradée (bilan net positif). Elles montrent que des actions ou des conditions locales fonctionnent bien et peuvent servir de modèle pour les autres régions."),
        ])
        
        rec_title("Priorisation territoriale")
    
        col_priority1, col_priority2 = st.columns([1.2, 1])
        
        with col_priority1:
            rec_title("Matrice de priorisation : Dégradation × Sécheresse", "sub")
            
            
            fig_scatter = px.scatter(
                priority_df,
                x="degradation",
                y="drought",
                size="priority_score",
                color="priority_score",
                hover_name="region",
                custom_data=["region", "degradation", "drought", "priority_score"],
                size_max=35,
                color_continuous_scale=[PALETTE["improved"], PALETTE["stable"], PALETTE["accent2"], PALETTE["degraded"]],
                labels={
                    "degradation": "Dégradation (%)",
                    "drought": f"Sécheresse totale {selected_year} (%)",
                    "priority_score": "Score de priorité"
                }
            )
            
            
            fig_scatter.update_yaxes(title_text=f"Secheresse totale {selected_year} (%)")
            fig_scatter.update_traces(
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "Degradation: %{customdata[1]:.1f}%<br>"
                    f"Secheresse totale {selected_year}: "
                    "%{customdata[2]:.1f}%<br>"
                    "Score de priorite: %{customdata[3]:.1f}"
                    "<extra></extra>"
                )
            )
            fig_scatter.add_shape(
                type="rect",
                x0=70, x1=100, y0=5, y1=100,
                fillcolor=PALETTE["degraded"],
                opacity=0.1,
                line=dict(width=0),
            )
            fig_scatter.add_annotation(
                x=85, y=50,
                text="URGENCE MAXIMALE",
                showarrow=False,
                font=dict(size=10, color=PALETTE["degraded"], weight="bold"),
                opacity=0.6
            )
            
            polish_chart(fig_scatter, height=420, show_source=False)
            fig_scatter.update_layout(coloraxis_showscale=True)
            st.plotly_chart(fig_scatter, width="stretch")
            
            st.markdown(
                '<div class="card-note">'
                '<strong>Lecture:</strong> Les régions en haut à droite (forte dégradation + forte sécheresse) nécessitent '
                'une intervention urgente avec approche intégrée. La taille des bulles représente le score de priorité combiné.'
                '</div>',
                unsafe_allow_html=True,
            )
        
        with col_priority2:
            rec_title("Top 4 régions prioritaires", "sub")
            
            top_priority = priority_df.head(4).copy()
            top_priority["priority_label"] = top_priority.apply(
                lambda row: "Urgence maximale" if row["degradation"] >= 70 and row["drought"] > 5
                else "Urgence élevée" if row["degradation"] >= 70
                else "Priorité élevée" if row["degradation"] >= 50
                else "Priorité modérée",
                axis=1
            )
            
            for idx, row in top_priority.iterrows():
                urgency_color = (
                    PALETTE["degraded"] if "maximale" in row["priority_label"]
                    else PALETTE["accent"] if "élevée" in row["priority_label"]
                    else PALETTE["accent2"]
                )
                
                
                if "maximale" in row["priority_label"]:
                    urgency_icon = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>"""
                elif "élevée" in row["priority_label"]:
                    urgency_icon = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>"""
                else:
                    urgency_icon = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>"""
                
                
                card_html = textwrap.dedent(f"""
                    <div style="
                        position: relative;
                        background: linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%);
                        border: 1px solid {PALETTE['line']};
                        border-radius: 10px;
                        padding: 0.7rem 0.8rem;
                        margin-bottom: 0.6rem;
                        box-shadow: 0 3px 10px rgba(17, 24, 39, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
                        transition: transform 0.2s ease, box-shadow 0.2s ease;
                        overflow: hidden;
                    ">
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 3px;
                            background: linear-gradient(90deg, {urgency_color}, {urgency_color}CC);
                        "></div>
                        
                        <div style="display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.5rem;">
                            <div style="
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                min-width: 34px;
                                height: 34px;
                                background: linear-gradient(135deg, {urgency_color}18, {urgency_color}08);
                                border: 2px solid {urgency_color}35;
                                border-radius: 50%;
                                font-size: 16px;
                            ">{urgency_icon}</div>
                            
                            <div style="flex: 1; min-width: 0;">
                                <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.4rem; margin-bottom: 0.3rem;">
                                    <strong style="
                                        color: {PALETTE['ink']};
                                        font-size: 0.9rem;
                                        font-weight: 700;
                                        white-space: nowrap;
                                        overflow: hidden;
                                        text-overflow: ellipsis;
                                    ">{row['region']}</strong>
                                    <span style="
                                        background: linear-gradient(135deg, {urgency_color}22, {urgency_color}15);
                                        color: {urgency_color};
                                        padding: 0.15rem 0.5rem;
                                        border-radius: 6px;
                                        font-size: 0.65rem;
                                        font-weight: 800;
                                        text-transform: uppercase;
                                        letter-spacing: 0.02em;
                                        white-space: nowrap;
                                        border: 1px solid {urgency_color}30;
                                    ">{row['priority_label'].replace('Urgence ', '').replace('Priorité ', '')}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div style="
                            display: grid;
                            grid-template-columns: repeat(3, 1fr);
                            gap: 0.5rem;
                            padding: 0.5rem 0.6rem;
                            background: rgba(248, 250, 252, 0.5);
                            border-radius: 7px;
                            border: 1px solid {PALETTE['line']}80;
                        ">
                            <div style="text-align: center;">
                                <div style="font-size: 0.62rem; color: {PALETTE['muted']}; text-transform: uppercase; font-weight: 600; margin-bottom: 0.15rem;">Dégradation</div>
                                <div style="font-size: 1rem; font-weight: 800; color: {PALETTE['degraded']};">{row['degradation']:.1f}%</div>
                            </div>
                            <div style="text-align: center; border-left: 1px solid {PALETTE['line']}; border-right: 1px solid {PALETTE['line']};">
                                <div style="font-size: 0.62rem; color: {PALETTE['muted']}; text-transform: uppercase; font-weight: 600; margin-bottom: 0.15rem;">Sécheresse</div>
                                <div style="font-size: 1rem; font-weight: 800; color: {PALETTE['accent2']};">{row['drought']:.2f}%</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 0.62rem; color: {PALETTE['muted']}; text-transform: uppercase; font-weight: 600; margin-bottom: 0.15rem;">Score</div>
                                <div style="font-size: 1rem; font-weight: 800; color: {PALETTE['ink']};">{row['priority_score']:.1f}</div>
                            </div>
                        </div>
                    </div>
                """)
                card_html = "\n".join(
                    line.strip() for line in card_html.splitlines() if line.strip()
                )
                
                st.markdown(card_html, unsafe_allow_html=True)
            
            
            st.markdown('<div class="download-button-spacer"></div>', unsafe_allow_html=True)
            priority_export = priority_df.rename(columns={
                "region": "Région",
                "degradation": "Dégradation (%)",
                "drought": "Sécheresse totale (%)",
                "priority_score": "Score de priorité combiné"
            })
            priority_export.columns = [
                "Region",
                "Degradation (%)",
                "Secheresse totale (%)",
                "Score de priorite combine",
            ]
            to_csv_download_button(
                priority_export,
                f"priorisation_territoriale_{selected_year}.csv",
                "Télécharger la priorisation complète",
                "download_priority_matrix"
            )
        
        
        
        
        
        st.markdown("---")
        rec_title("Recommandations par type de dégradation")
        
        
        recommendations_db = {
            "Productivité": {
                "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4A7C59" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 20s4-6 4-11c0-3.31-1.34-6-3-6S5 5.69 5 9c0 2.93 1.17 5.37 2 7"/><path d="M11 9C11 9 14 6 17 7c3 1 4 4 4 4s-3 1-6 0"/><line x1="11" y1="20" x2="11" y2="9"/></svg>""",
                "title": "Restauration de la productivité des terres",
                "actions_court_terme": [
                    "Promouvoir l'agriculture de conservation (semis direct, couverture végétale permanente)",
                    "Intensifier les programmes de régénération naturelle assistée (RNA)",
                    "Distribuer des semences adaptées aux conditions locales (variétés résistantes à la sécheresse)",
                    "Renforcer les systèmes d'irrigation goutte-à-goutte et micro-aspersion"
                ],
                "actions_moyen_terme": [
                    "Établir des centres de démonstration d'agroforesterie productive",
                    "Mettre en place des systèmes de rotation cultures-jachères améliorées",
                    "Développer les filières de valorisation des plantes aromatiques et médicinales (PAM)",
                    "Créer des banques de semences paysannes résilientes"
                ],
                "actions_long_terme": [
                    "Restaurer 30% des parcours dégradés via sylvopastoralisme",
                    "Développer des chaînes de valeur durables (certifications bio, commerce équitable)",
                    "Investir dans la recherche agricole adaptée au climat aride/semi-aride",
                    "Intégrer la gestion durable des terres dans les plans d'aménagement territoriaux"
                ],
                "indicateurs_suivi": [
                    "Rendement agricole moyen (quintal/ha)",
                    "Biomasse végétale (NDVI annuel moyen)",
                    "Taux d'adoption des pratiques durables (%)",
                    "Revenus agricoles des ménages ruraux"
                ]
            },
            "Couverture des terres": {
                "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4A7C59" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L6 12h4v8h4v-8h4L12 2z"/></svg>""",
                "title": "Protection et restauration de la couverture végétale",
                "actions_court_terme": [
                    "Interdire l'exploitation forestière non autorisée dans les zones critiques",
                    "Lancer des campagnes de reboisement participatif (1 million d'arbres/région)",
                    "Installer des pare-feu et tours de surveillance anti-incendie",
                    "Réglementer l'urbanisation dans les zones à haute valeur écologique"
                ],
                "actions_moyen_terme": [
                    "Établir des corridors écologiques entre aires protégées",
                    "Promouvoir l'agroforesterie (arbres fruitiers, arganiers, oliviers)",
                    "Créer des pépinières communautaires d'essences locales",
                    "Restaurer les écosystèmes dégradés (zones humides, steppes, forêts)"
                ],
                "actions_long_terme": [
                    "Atteindre 15% de couverture forestière nationale (objectif 2030)",
                    "Établir un système de paiement pour services écosystémiques (PSE)",
                    "Développer des zones de conservation communautaire",
                    "Intégrer la biodiversité dans les stratégies de développement régional"
                ],
                "indicateurs_suivi": [
                    "Taux de couverture végétale (%)",
                    "Superficie reboisée annuelle (ha)",
                    "Nombre d'espèces endémiques protégées",
                    "Taux de survie des plantations (%)"
                ]
            },
            "Carbone organique du sol": {
                "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#8B6914" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="14" rx="8" ry="4"/><path d="M4 14c0 3.3 3.58 6 8 6s8-2.7 8-6"/><path d="M12 10V4"/><path d="M9 7l3-3 3 3"/></svg>""",
                "title": "Restauration de la fertilité et du carbone des sols",
                "actions_court_terme": [
                    "Interdire le brûlage des résidus agricoles",
                    "Promouvoir le compostage à la ferme (formation + équipement)",
                    "Distribuer des biofertilisants et stimulateurs microbiens",
                    "Réduire le labour profond (adopter techniques sans labour)"
                ],
                "actions_moyen_terme": [
                    "Créer des unités de production de compost de qualité",
                    "Promouvoir les cultures de légumineuses fixatrices d'azote",
                    "Développer l'agriculture de précision (gestion spatiale de la fertilisation)",
                    "Établir un réseau de surveillance de la santé des sols"
                ],
                "actions_long_terme": [
                    "Séquestrer 2 tonnes CO2e/ha/an via agriculture régénérative",
                    "Intégrer les sols dans les stratégies nationales d'atténuation climatique",
                    "Valoriser les crédits carbone des pratiques durables",
                    "Restaurer les sols salinisés et pollués (phytoremédiation)"
                ],
                "indicateurs_suivi": [
                    "Teneur en carbone organique du sol (t/ha)",
                    "pH et salinité des sols",
                    "Activité biologique (biomasse microbienne)",
                    "Rendement en matière organique (t/ha)"
                ]
            }
        }
        
        
        if len(subind_analysis) > 0:
            for indicator in subind_analysis.index[:3]:  
                if indicator in recommendations_db:
                    rec = recommendations_db[indicator]
                    area_affected = subind_analysis[indicator]
                    pct_affected = (area_affected / total_area * 100) if total_area > 0 else 0
                    
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(248,250,252,0.95));
                            border: 1px solid {PALETTE['line']};
                            border-radius: 14px;
                            padding: 1.2rem 1.4rem;
                            margin-bottom: 1.2rem;
                            box-shadow: 0 12px 28px rgba(17, 24, 39, 0.08);
                            min-height: 110px;
                            display: flex;
                            align-items: center;
                        ">
                            <div style="display: flex; align-items: center; gap: 0.8rem; width: 100%;">
                                <span style="font-size: 2rem; flex-shrink: 0;">{rec['icon']}</span>
                                <div style="flex: 1;">
                                    <h4 style="margin: 0; color: {PALETTE['ink']}; font-size: 1.05rem;">{rec['title']}</h4>
                                    <p style="margin: 0.2rem 0 0 0; color: {PALETTE['muted']}; font-size: 0.85rem;">
                                        {format_int(float(area_affected))} ha affectés ({pct_affected:.1f}% du territoire sélectionné)
                                    </p>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    
                    col_ct, col_mt, col_lt = st.columns(3)
                    
                    with col_ct:
                        st.markdown("**Court terme (0-2 ans)**")
                        for action in rec["actions_court_terme"]:
                            st.markdown(f"• {action}")
                    
                    with col_mt:
                        st.markdown("**Moyen terme (2-5 ans)**")
                        for action in rec["actions_moyen_terme"]:
                            st.markdown(f"• {action}")
                    
                    with col_lt:
                        st.markdown("**Long terme (5-10 ans)**")
                        for action in rec["actions_long_terme"]:
                            st.markdown(f"• {action}")
                    
                    with st.expander(f"Indicateurs de suivi — {indicator}"):
                        for idx, indic in enumerate(rec["indicateurs_suivi"], 1):
                            st.markdown(f"{idx}. {indic}")
                    
                    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        
        
        
        
        
        st.markdown("---")
        rec_title("Adaptation au changement climatique et gestion de la sécheresse")
        
        if pct_severe_drought > 0.1 or len(drought_critical) > 0:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.03));
                    border: 1px solid rgba(245, 158, 11, 0.2);
                    border-radius: 12px;
                    padding: 1.2rem 1.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.08);
                ">
                    <div style="display: flex; align-items: flex-start; gap: 0.9rem;">
                        <span style="display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;background:rgba(245,158,11,0.15);border-radius:10px;flex-shrink:0;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg></span>
                        <div style="flex: 1;">
                            <strong style="color: {PALETTE['ink']}; font-size: 0.95rem;">Contexte climatique:</strong>
                            <span style="color: {PALETTE['muted']}; font-size: 0.9rem; line-height: 1.6;">
                                En {selected_year}, {len(drought_critical) if drought_critical else 'certaines'} 
                                région{'s' if len(drought_critical) != 1 else ''} {'connaissent' if len(drought_critical) != 1 else 'connaît'} une sécheresse sévère ou extrême.
                                Une approche intégrée eau-sol-végétation est nécessaire pour renforcer la résilience climatique.
                            </span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        
        drought_cards_html = f"""
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #FFFFFF, #F8FAFC); border: 1px solid {PALETTE['line']}; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(14, 165, 233, 0.1); min-height: 520px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.2rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(14, 165, 233, 0.15);">
                    <div style="display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: linear-gradient(135deg, rgba(14, 165, 233, 0.15), rgba(14, 165, 233, 0.08)); border-radius: 12px; flex-shrink: 0;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#0EA5E9" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg></div>
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem; font-weight: 700; line-height: 1.3;">Gestion intégrée des ressources en eau</strong>
                </div>
                <div style="flex: 1; font-size: 0.9rem; line-height: 1.8; color: {PALETTE['muted']};">
                    • Moderniser les réseaux d'irrigation (réduction pertes 30→10%)<br><br>
                    • Développer la réutilisation des eaux usées épurées en agriculture<br><br>
                    • Construire des bassins de rétention collinaires (2-5 ha)<br><br>
                    • Promouvoir les techniques d'irrigation économe (goutte-à-goutte subventionné)<br><br>
                    • Établir des plans de gestion participative des nappes phréatiques
                </div>
            </div>
            <div style="background: linear-gradient(135deg, #FFFFFF, #F8FAFC); border: 1px solid {PALETTE['line']}; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.1); min-height: 520px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.2rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(16, 185, 129, 0.15);">
                    <div style="display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08)); border-radius: 12px; flex-shrink: 0;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22V11"/><path d="M12 11C12 11 7.5 9 7.5 4.5c0 0 2.5-.5 4.5 2 2-2.5 4.5-2 4.5-2C16.5 9 12 11 12 11z"/><path d="M12 15c-2.5 0-5 1.5-5 4"/><line x1="4" y1="22" x2="20" y2="22"/></svg></div>
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem; font-weight: 700; line-height: 1.3;">Cultures et pratiques résilientes</strong>
                </div>
                <div style="flex: 1; font-size: 0.9rem; line-height: 1.8; color: {PALETTE['muted']};">
                    • Promouvoir les cultures tolérantes à la sécheresse (quinoa, légumineuses locales)<br><br>
                    • Généraliser le paillage et techniques de conservation de l'humidité<br><br>
                    • Adapter le calendrier agricole (semis précoces, variétés à cycle court)<br><br>
                    • Diversifier les sources de revenus (élevage adapté, apiculture)<br><br>
                    • Créer des banques fourragères stratégiques régionales
                </div>
            </div>
            <div style="background: linear-gradient(135deg, #FFFFFF, #F8FAFC); border: 1px solid {PALETTE['line']}; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(245, 158, 11, 0.1); min-height: 520px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.2rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(245, 158, 11, 0.15);">
                    <div style="display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.08)); border-radius: 12px; flex-shrink: 0;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/><path d="M2 8c0-1.1.2-2.2.6-3.2"/><path d="M21.4 4.8A10 10 0 0 1 22 8"/></svg></div>
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem; font-weight: 700; line-height: 1.3;">Systèmes d'alerte précoce et gouvernance</strong>
                </div>
                <div style="flex: 1; font-size: 0.9rem; line-height: 1.8; color: {PALETTE['muted']};">
                    • Déployer un système d'alerte sécheresse temps réel (données satellitaires + stations)<br><br>
                    • Former les agriculteurs à l'interprétation des bulletins agro-météo<br><br>
                    • Établir des comités locaux de gestion des crises hydriques<br><br>
                    • Développer des assurances climatiques indicielles<br><br>
                    • Intégrer les savoirs locaux dans la planification climatique
                </div>
            </div>
        </div>
        """
        st.markdown(drought_cards_html, unsafe_allow_html=True)
        
        
        
        
        
        st.markdown("---")
        rec_title("Mesures transversales et habilitantes")
        
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        
        
        import base64 as _b64
        with open("assets/financial-profit.png", "rb") as _f:
            _financial_icon_b64 = _b64.b64encode(_f.read()).decode()
        _financial_icon_img = f'<img src="data:image/png;base64,{_financial_icon_b64}" width="28" height="28" style="display:block;filter:sepia(1) saturate(3) hue-rotate(5deg) brightness(0.85);" />'
    
        
        transversal_cards_html = f"""
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 1.5rem;">
            <div style="background: linear-gradient(135deg, #FFFFFF, #F8FAFC); border: 1px solid {PALETTE['line']}; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(107, 31, 58, 0.08); min-height: 420px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.2rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(107, 31, 58, 0.12);">
                    <div style="display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: linear-gradient(135deg, rgba(107, 31, 58, 0.12), rgba(107, 31, 58, 0.06)); border-radius: 12px; flex-shrink: 0;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6B1F3A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg></div>
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem; font-weight: 700; line-height: 1.3;">Gouvernance et institutionnel</strong>
                </div>
                <div style="flex: 1; font-size: 0.9rem; line-height: 1.8; color: {PALETTE['muted']};">
                    • Créer une Task Force Régionale LDN (neutralité dégradation)<br><br>
                    • Intégrer la LDN dans les Plans de Développement Régionaux<br><br>
                    • Harmoniser les politiques sectorielles (agriculture, forêt, eau, énergie)<br><br>
                    • Renforcer les capacités des collectivités territoriales<br><br>
                    • Établir un Observatoire Régional de la Dégradation des Terres
                </div>
            </div>
            <div style="background: linear-gradient(135deg, #FFFFFF, #F8FAFC); border: 1px solid {PALETTE['line']}; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(74, 124, 89, 0.1); min-height: 420px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.2rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(74, 124, 89, 0.15);">
                    <div style="display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: linear-gradient(135deg, rgba(74, 124, 89, 0.15), rgba(74, 124, 89, 0.08)); border-radius: 12px; flex-shrink: 0;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#4A7C59" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg></div>
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem; font-weight: 700; line-height: 1.3;">Sensibilisation et renforcement des capacités</strong>
                </div>
                <div style="flex: 1; font-size: 0.9rem; line-height: 1.8; color: {PALETTE['muted']};">
                    • Former 10,000 agriculteurs/an aux pratiques durables<br><br>
                    • Intégrer la gestion durable des terres dans les curricula scolaires<br><br>
                    • Lancer des campagnes de sensibilisation (médias, mosquées, marchés)<br><br>
                    • Créer des fermes-écoles de démonstration<br><br>
                    • Établir un réseau de Champions de la Terre (leaders locaux)
                </div>
            </div>
            <div style="background: linear-gradient(135deg, #FFFFFF, #F8FAFC); border: 1px solid {PALETTE['line']}; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(212, 167, 74, 0.1); min-height: 420px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.2rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(212, 167, 74, 0.15);">
                    <div style="display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: linear-gradient(135deg, rgba(212, 167, 74, 0.15), rgba(212, 167, 74, 0.08)); border-radius: 12px; flex-shrink: 0;">{_financial_icon_img}</div>
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem; font-weight: 700; line-height: 1.3;">Financement et incitations</strong>
                </div>
                <div style="flex: 1; font-size: 0.9rem; line-height: 1.8; color: {PALETTE['muted']};">
                    • Créer un Fonds Régional de Restauration des Terres<br><br>
                    • Subventionner les pratiques durables (50-80% coûts investissement)<br><br>
                    • Développer des mécanismes de paiement pour services écosystémiques<br><br>
                    • Mobiliser la finance climat (Fonds Vert Climat, GEF)<br><br>
                    • Faciliter l'accès au microcrédit vert pour petits exploitants
                </div>
            </div>
            <div style="background: linear-gradient(135deg, #FFFFFF, #F8FAFC); border: 1px solid {PALETTE['line']}; border-radius: 14px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1); min-height: 420px; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.2rem; padding-bottom: 1rem; border-bottom: 2px solid rgba(59, 130, 246, 0.15);">
                    <div style="display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.08)); border-radius: 12px; flex-shrink: 0;"><svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/><line x1="3" y1="20" x2="21" y2="20"/></svg></div>
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem; font-weight: 700; line-height: 1.3;">Suivi-évaluation et recherche</strong>
                </div>
                <div style="flex: 1; font-size: 0.9rem; line-height: 1.8; color: {PALETTE['muted']};">
                    • Établir un système de Monitoring & Evaluation (M&E) robuste<br><br>
                    • Développer des indicateurs SMART par région<br><br>
                    • Promouvoir la recherche-action participative<br><br>
                    • Créer des partenariats université-terrain<br><br>
                    • Publier un rapport annuel de progrès LDN
                </div>
            </div>
        </div>
        """
        st.markdown(transversal_cards_html, unsafe_allow_html=True)
        
        
        
        
        
        st.markdown("---")
        rec_title("Plans d'action régionalisés")
        
        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, rgba(245, 158, 11, 0.06), rgba(245, 158, 11, 0.02));
                border: 1px solid rgba(245, 158, 11, 0.2);
                border-radius: 12px;
                padding: 1.2rem 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 12px rgba(245, 158, 11, 0.08);
            ">
                <div style="display: flex; align-items: flex-start; gap: 0.9rem;">
                    <span style="display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;width:36px;height:36px;"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/></svg></span>
                    <div style="flex: 1;">
                        <strong style="color: {PALETTE['ink']}; font-size: 0.95rem;">Méthodologie :</strong>
                        <span style="color: {PALETTE['muted']}; font-size: 0.9rem; line-height: 1.6;">
                            Les recommandations ci-dessous sont générées automatiquement en fonction 
                            du niveau de dégradation, de l'exposition à la sécheresse, et des sous-indicateurs critiques de chaque région.
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        
        selected_region_rec = st.selectbox(
            "Sélectionner une région pour voir son plan d'action détaillé:",
            selected_regions,
            key="region_recommendation_selector"
        )
        
        if selected_region_rec:
            
            region_data = region_summary[region_summary["region"] == selected_region_rec].iloc[0]
            region_drought = drought_risk[drought_risk["region"] == selected_region_rec].iloc[0] if selected_region_rec in drought_risk["region"].values else {"total_drought": 0, "moderate_plus": 0, "severe_extreme": 0}
            region_subind = subind.loc[
                (subind["region"] == selected_region_rec)
                & (subind["indicator"].isin(["Productivité", "Couverture des terres", "Carbone organique du sol"]))
                & (subind["class"] == "Dégradé")
                , :
            ]
            
            
            if region_data["Degraded"] >= 70:
                urgency = "CRITIQUE"
                urgency_color = PALETTE["degraded"]
            elif region_data["Degraded"] >= 50:
                urgency = "ÉLEVÉE"
                urgency_color = PALETTE["accent"]
            else:
                urgency = "MODÉRÉE"
                urgency_color = PALETTE["accent2"]
            
            
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, {urgency_color}15, {urgency_color}08);
                    border: 2px solid {urgency_color};
                    border-radius: 14px;
                    padding: 1.2rem 1.5rem;
                    margin: 1rem 0 1.5rem 0;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                        <div>
                            <h3 style="margin: 0; color: {PALETTE['ink']}; font-size: 1.4rem;">{selected_region_rec}</h3>
                        </div>
                        <div style="
                            display: inline-flex;
                            align-items: center;
                            gap: 0.45rem;
                            color: {urgency_color};
                            font-weight: 700;
                            font-size: 0.92rem;
                            letter-spacing: 0.07em;
                            text-transform: uppercase;
                        ">
                            <span style="display: inline-block; width: 8px; height: 8px; background: {urgency_color}; border-radius: 50%; flex-shrink: 0;"></span>
                            URGENCE {urgency}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            
            col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
            with col_kpi1:
                st.metric("Dégradation", f"{region_data['Degraded']:.1f}%")
            with col_kpi2:
                st.metric("Amélioration", f"{region_data['Improved']:.1f}%")
            with col_kpi3:
                st.metric("Sécheresse sévère/extrême", f"{region_drought['severe_extreme']:.2f}%")
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            
            
            st.markdown(
                f"""
                <div style="margin: 1.5rem 0 1rem 0;">
                    <strong style="color: {PALETTE['ink']}; font-size: 1.05rem;">Actions prioritaires recommandées (12-24 mois)</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            priority_actions = []
            
            
            if region_data["Degraded"] >= 70:
                priority_actions.append("Déclarer la région en zone d'intervention prioritaire LDN")
                priority_actions.append("Mobiliser un financement d'urgence (5-10 M DH)")
                priority_actions.append("Créer une Task Force dédiée avec mandat exécutif")
            
            
            if not region_subind.empty:
                worst_subind = region_subind.loc[region_subind["area_ha"].idxmax(), "indicator"]
                if worst_subind == "Productivité":
                    priority_actions.append(f"Lancer un programme de restauration de la productivité (semences, irrigation, RNA)")
                elif worst_subind == "Couverture des terres":
                    priority_actions.append(f"Initier un programme de reboisement intensif (500,000 arbres/an)")
                elif worst_subind == "Carbone organique du sol":
                    priority_actions.append(f"Promouvoir l'agriculture de conservation et le compostage à grande échelle")
            
            
            if region_drought["severe_extreme"] > 20:
                priority_actions.append(f"Établir un plan de gestion de crise hydrique (restrictions + aides d'urgence)")
                priority_actions.append(f"Distribuer des semences de cultures résistantes à la sécheresse")
            elif region_drought["moderate_plus"] > 20:
                priority_actions.append(f"Renforcer les infrastructures de mobilisation des eaux (barrages collinaires)")
            
            
            if region_data["net_balance"] > 0:
                priority_actions.append(f"Documenter et diffuser les bonnes pratiques locales vers autres régions")
    
            
            if not priority_actions:
                priority_actions.extend([
                    "Réaliser un diagnostic terrain rapide pour confirmer les pressions locales",
                    "Mettre en place un suivi trimestriel des indicateurs de dégradation et de sécheresse",
                    "Préparer un portefeuille d'actions préventives à faible coût avec les acteurs régionaux",
                ])
            
            
            for idx, action in enumerate(priority_actions, 1):
                st.markdown(f"{idx}. {action}")
            
            
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="margin: 1rem 0;">
                    <strong style="color: {PALETTE['ink']}; font-size: 1rem;">Estimation indicative du coût des interventions</strong>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            
            degraded_area_region = status_f[
                (status_f["region"] == selected_region_rec) & (status_f["class"] == "Dégradé")
            ]["area_ha"].sum()
            
            
            budget_min = degraded_area_region * 500 / 1000000  
            budget_max = degraded_area_region * 2000 / 1000000  
            
            col_budget1, col_budget2, col_budget3 = st.columns(3)
            col_budget1.metric("Estimation basse", f"{budget_min:.1f} M DH", help="Actions légères (sensibilisation, formation)")
            col_budget2.metric("Estimation moyenne", f"{(budget_min+budget_max)/2:.1f} M DH", help="Mix actions (semences, équipement, reboisement)")
            col_budget3.metric("Estimation haute", f"{budget_max:.1f} M DH", help="Actions lourdes (infrastructures, restauration intensive)")
            
            
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(74, 124, 89, 0.08), rgba(74, 124, 89, 0.03));
                    border: 1px solid rgba(74, 124, 89, 0.2);
                    border-radius: 12px;
                    padding: 1.2rem 1.5rem;
                    margin-top: 1rem;
                    box-shadow: 0 4px 12px rgba(74, 124, 89, 0.08);
                ">
                    <div style="display: flex; align-items: flex-start; gap: 0.9rem;">
                        <span style="display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;width:36px;height:36px;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{PALETTE['improved']}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                        </span>
                        <div style="flex: 1;">
                            <strong style="color: {PALETTE['ink']}; font-size: 0.95rem;">Méthode d’estimation budgétaire</strong>
                            <div style="color: {PALETTE['muted']}; font-size: 0.88rem; line-height: 1.6; margin-top: 0.5rem;">
                                <p style="margin: 0 0 0.7rem 0;">
                                    Pour obtenir une estimation, la superficie dégradée est multipliée par le montant nécessaire pour traiter un hectare.
                                </p>
                                <p style="margin: 0 0 0.7rem 0;">
                                    <strong style="color: {PALETTE['ink']};">Superficie dégradée de la région sélectionnée : {format_int(float(degraded_area_region))} ha</strong>
                                </p>
                                <ul style="margin: 0 0 0.7rem 0; padding-left: 1.5rem;">
                                    <li><strong>Scénario bas :</strong> 500 DH pour traiter un hectare.</li>
                                    <li><strong>Scénario moyen :</strong> valeur située entre les deux scénarios.</li>
                                    <li><strong>Scénario haut :</strong> 2 000 DH pour traiter un hectare.</li>
                                </ul>
                                <p style="margin: 0;"><strong style="color: {PALETTE['ink']};">Ces montants donnent un ordre de grandeur du financement nécessaire selon différents niveaux d’intervention.</strong></p>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            
            st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
            
            
            col_icon, col_title = st.columns([0.06, 0.94], gap="small")
            with col_icon:
                st.image("assets/Parties prenantes.png", width=35)
            with col_title:
                st.markdown(
                    f"""
                    <h4 style="margin: 0; padding: 0; color: {PALETTE['ink']};">Parties prenantes clés à mobiliser</h4>
                    """,
                    unsafe_allow_html=True
                )
            
            stakeholders_col1, stakeholders_col2 = st.columns(2)
            
            with stakeholders_col1:
                st.markdown("""
                **Institutions publiques:**
                • Ministère de l'Agriculture
                • Agence Nationale des Eaux et Forêts
                • Agence du Bassin Hydraulique
                • Collectivités territoriales
                • Direction Régionale du HCP
                """)
            
            with stakeholders_col2:
                st.markdown("""
                **Acteurs non-gouvernementaux:**
                • Associations d'agriculteurs et coopératives
                • ONG environnementales locales
                • Chambres d'Agriculture
                • Institutions de recherche (INRA, Universités)
                • Secteur privé (agro-industries)
                """)
        
        
        
        
        
        st.markdown("---")
        rec_title("Références et ressources")
        
        _refs_html = (
            f'<div style="background:linear-gradient(135deg,rgba(245,158,11,0.06),rgba(245,158,11,0.02));border:1px solid rgba(245,158,11,0.22);border-radius:12px;padding:1.3rem 1.5rem;margin:0.5rem 0 1rem 0;">'
            f'<div style="display:flex;gap:0.8rem;align-items:flex-start;">'
            f'<span style="display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:0.1rem;width:28px;height:28px;"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/><path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/></svg></span>'
            f'<div style="font-size:0.875rem;color:{PALETTE["ink"]};line-height:1.65;">'
            f'<strong>Références et ressources clés :</strong>'
            f'<ul style="margin:0.45rem 0 0.9rem 0;padding-left:1.3rem;">'
            f'<li><a href="https://library.unccd.int/Details/fullCatalogue/1531" target="_blank" style="color:{PALETTE["hcp_bordeaux"]};"><strong>UNCCD Good Practice Guidance for SDG Indicator 15.3.1</strong></a> — Cadre méthodologique officiel pour l\'évaluation de la proportion des terres dégradées, basé sur les sous-indicateurs de couverture terrestre, productivité des terres et carbone organique du sol.</li>'
            f'<li><a href="https://www.trends.earth/" target="_blank" style="color:{PALETTE["hcp_bordeaux"]};"><strong>Trends.Earth</strong></a> — Plateforme open-source utilisée pour l\'analyse géospatiale de la dégradation des terres et le suivi de l\'indicateur ODD 15.3.1 (<a href="https://plugins.qgis.org/plugins/LDMP/" target="_blank" style="color:{PALETTE["hcp_bordeaux"]};">plugin QGIS</a>).</li>'
            f'<li><strong>Méthode de pondération par entropie</strong> — Approche objective de pondération fondée sur la variabilité de l\'information contenue dans les indicateurs.</li>'
            f'<li><a href="https://www.unccd.int/" target="_blank" style="color:{PALETTE["hcp_bordeaux"]};"><strong>UNCCD</strong></a> — Source institutionnelle de référence sur la neutralité en matière de dégradation des terres.</li>'
            f'</ul>'
            f'</div></div></div>'
        )
        st.markdown(_refs_html, unsafe_allow_html=True)
        
        
        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        
        recommendations_summary = pd.DataFrame([
            {"Région": reg, 
             "Niveau d'urgence": "CRITIQUE" if region_summary[region_summary["region"]==reg]["Degraded"].values[0] >= 70
                                else "ÉLEVÉE" if region_summary[region_summary["region"]==reg]["Degraded"].values[0] >= 50
                                else "MODÉRÉE",
             "Dégradation (%)": region_summary[region_summary['region']==reg]['Degraded'].values[0],
             "Sécheresse totale (%)": drought_risk[drought_risk['region']==reg]['total_drought'].values[0] if reg in drought_risk["region"].values else 0,
             "Score priorité": priority_df[priority_df['region']==reg]['priority_score'].values[0]}
            for reg in selected_regions
        ])
        
        to_csv_download_button(
            recommendations_summary,
            f"rapport_recommandations_{selected_year}.csv",
            "Télécharger le rapport de recommandations complet (CSV)",
            "download_recommendations_report"
        )
    
