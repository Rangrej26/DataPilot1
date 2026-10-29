"""
DataPilot AI - UI Components & Design System
Strict, reference-locked SaaS design system using exact color specifications:
- Sidebar: #222225
- Main workspace: #E8E8E8
- Content panels: #FFFFFF
- Primary text on light surfaces: #202124
- Secondary text on light surfaces: #62636B
- Primary accent: #D8F45B (lime: primary actions, active indicators)
- Secondary accent: #B9ADF5 (lavender: secondary highlights, selected traces)
- Borders: #D5D7DC
- Sidebar primary text: #FFFFFF
- Sidebar secondary text: #C6C6CC
- Dark button text on lime buttons: #202124
- State indicators: #10B981 (success), #F59E0B (warning), #EF4444 (error)
"""

from typing import Dict, List, Optional, Any
import datetime
try:
    import streamlit as st
except ImportError:
    st = None
import pandas as pd
import plotly.io as pio


def render_html(html_str: str):
    """
    Renders custom HTML in Streamlit safely.
    Strips leading and trailing whitespace from every line and removes blank lines,
    ensuring Markdown parsers NEVER mistakenly treat lines indented with 4+ spaces
    as <pre><code> blocks.
    """
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    clean_html = "\n".join(clean_lines)
    if st is not None:
        st.markdown(clean_html, unsafe_allow_html=True)


# Locked Color Palettes Configuration
# Sleek Enterprise Dark Color Palettes Configuration (Linear / Vercel / Supabase aesthetic)
THEMES = {
    "Professional SaaS": {
        "bg_primary": "#E8E8E8",
        "bg_secondary": "#FFFFFF",
        "bg_sidebar": "#222225",
        "border_color": "#D5D7DC",
        "text_primary": "#202124",
        "text_secondary": "#62636B",
        "text_body": "#202124",
        "sidebar_text_primary": "#FFFFFF",
        "sidebar_text_secondary": "#C6C6CC",
        "accent": "#D8F45B",
        "accent_hover": "#C8E645",
        "accent_lavender": "#B9ADF5",
        "accent_dark": "#222225",
        "card_shadow": "0 1px 3px rgba(0, 0, 0, 0.05)",
        "plotly_template": "plotly_white",
        "chart_colors": ["#222225", "#818CF8", "#B9ADF5", "#10B981", "#F59E0B", "#EF4444"]
    },
    "Professional Light": {
        "bg_primary": "#E8E8E8",
        "bg_secondary": "#FFFFFF",
        "bg_sidebar": "#222225",
        "border_color": "#D5D7DC",
        "text_primary": "#202124",
        "text_secondary": "#62636B",
        "text_body": "#202124",
        "sidebar_text_primary": "#FFFFFF",
        "sidebar_text_secondary": "#C6C6CC",
        "accent": "#D8F45B",
        "accent_hover": "#C8E645",
        "accent_lavender": "#B9ADF5",
        "accent_dark": "#222225",
        "card_shadow": "0 1px 3px rgba(0, 0, 0, 0.05)",
        "plotly_template": "plotly_white",
        "chart_colors": ["#222225", "#818CF8", "#B9ADF5", "#10B981", "#F59E0B", "#EF4444"]
    },
    "Enterprise Dark": {
        "bg_primary": "#131722",
        "bg_secondary": "#1E222D",
        "bg_sidebar": "#0E121A",
        "border_color": "#2E3440",
        "text_primary": "#FFFFFF",
        "text_secondary": "#94A3B8",
        "text_body": "#E2E8F0",
        "sidebar_text_primary": "#FFFFFF",
        "sidebar_text_secondary": "#94A3B8",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "accent_lavender": "#818CF8",
        "accent_dark": "#181B24",
        "card_shadow": "0 1px 3px rgba(0, 0, 0, 0.25)",
        "plotly_template": "plotly_dark",
        "chart_colors": ["#3B82F6", "#60A5FA", "#818CF8", "#34D399", "#F59E0B", "#94A3B8"]
    },
    "Obsidian Dark": {
        "bg_primary": "#0B0E14",
        "bg_secondary": "#151821",
        "bg_sidebar": "#0B0E14",
        "border_color": "#232834",
        "text_primary": "#FFFFFF",
        "text_secondary": "#94A3B8",
        "text_body": "#E2E8F0",
        "sidebar_text_primary": "#FFFFFF",
        "sidebar_text_secondary": "#94A3B8",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "accent_lavender": "#818CF8",
        "accent_dark": "#151821",
        "card_shadow": "0 1px 3px rgba(0, 0, 0, 0.3)",
        "plotly_template": "plotly_dark",
        "chart_colors": ["#3B82F6", "#60A5FA", "#818CF8", "#34D399", "#F59E0B", "#94A3B8"]
    },
    "Flux Bento": {
        "bg_primary": "#131722",
        "bg_secondary": "#1E222D",
        "bg_sidebar": "#0E121A",
        "border_color": "#2E3440",
        "text_primary": "#FFFFFF",
        "text_secondary": "#94A3B8",
        "text_body": "#E2E8F0",
        "sidebar_text_primary": "#FFFFFF",
        "sidebar_text_secondary": "#94A3B8",
        "accent": "#3B82F6",
        "accent_hover": "#2563EB",
        "accent_lavender": "#818CF8",
        "accent_dark": "#181B24",
        "card_shadow": "0 1px 3px rgba(0, 0, 0, 0.25)",
        "plotly_template": "plotly_dark",
        "chart_colors": ["#3B82F6", "#60A5FA", "#818CF8", "#34D399", "#F59E0B", "#94A3B8"]
    }
}


def load_custom_css():
    """
    Injects enterprise-grade dark SaaS styling (Linear / Vercel / Supabase aesthetic).
    Targets Streamlit internal CSS classes with crisp white headings (#FFFFFF),
    soft grey subheadings (#94A3B8), readable light slate body (#E2E8F0),
    dark slate container surfaces (#1E222D), subtle borders (#2E3440),
    and electric blue (#3B82F6) primary accents.
    """
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Typography & Base Application Surface */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
        text-rendering: optimizeLegibility !important;
        background-color: #131722 !important;
        color: #E2E8F0 !important;
    }

    /* Headings: Crisp White #FFFFFF */
    h1, h1 *, .stMarkdown h1, .stMarkdown h1 *, div[data-testid="stMarkdownContainer"] h1, div[data-testid="stMarkdownContainer"] h1 * {
        font-size: 28px !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em !important;
        margin-top: 0 !important;
        margin-bottom: 8px !important;
    }

    h2, h2 *, .stMarkdown h2, .stMarkdown h2 *, div[data-testid="stMarkdownContainer"] h2, div[data-testid="stMarkdownContainer"] h2 * {
        font-size: 20px !important;
        font-weight: 600 !important;
        line-height: 1.3 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.01em !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
    }

    h3, h3 *, .stMarkdown h3, .stMarkdown h3 *, div[data-testid="stMarkdownContainer"] h3, div[data-testid="stMarkdownContainer"] h3 * {
        font-size: 16px !important;
        font-weight: 600 !important;
        line-height: 1.35 !important;
        color: #FFFFFF !important;
        margin-top: 6px !important;
        margin-bottom: 4px !important;
    }

    h4, h4 *, .stMarkdown h4, .stMarkdown h4 *, div[data-testid="stMarkdownContainer"] h4, div[data-testid="stMarkdownContainer"] h4 * {
        font-size: 14.5px !important;
        font-weight: 600 !important;
        color: #FFFFFF !important;
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }

    /* Body Text: Readable light slate #E2E8F0 */
    p, li, .stMarkdown p {
        font-size: 14.5px !important;
        font-weight: 400 !important;
        line-height: 1.55 !important;
        color: #E2E8F0 !important;
    }

    /* Subheadings & Secondary text: Soft grey #94A3B8 */
    .text-secondary,
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
        font-size: 13.5px !important;
        color: #94A3B8 !important;
        line-height: 1.45 !important;
    }

    /* Form Widget Labels */
    label[data-testid="stWidgetLabel"],
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
        margin-bottom: 4px !important;
    }

    /* Application Viewport & Workspace Canvas */
    .stApp {
        background-color: #131722 !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
        height: 2rem !important;
        z-index: 99 !important;
    }

    header[data-testid="stHeader"] button {
        color: #94A3B8 !important;
    }

    .block-container {
        background-color: #131722 !important;
        padding: 1.5rem 2rem 2.5rem 2rem !important;
        margin-top: 0 !important;
        max-width: 1440px !important;
    }

    /* Left Sidebar - Sleek Dark Slate #0E121A */
    section[data-testid="stSidebar"] {
        background-color: #0E121A !important;
        border-right: 1px solid #2E3440 !important;
        padding-top: 1rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: #94A3B8 !important;
        font-size: 13.5px !important;
    }

    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] span {
        color: #FFFFFF !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        background-color: #181B24 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 6px !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #E2E8F0 !important;
        font-size: 13px !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: #2E3440 !important;
        margin: 12px 0 !important;
    }

    /* Sidebar Navigation Items */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        gap: 3px !important;
        padding: 2px 0 !important;
    }

    div[data-testid="stRadio"] label {
        background: transparent !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        margin: 0 !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        border: 1px solid transparent !important;
    }

    div[data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.04) !important;
    }

    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label span {
        color: #94A3B8 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    div[data-testid="stRadio"] label:hover p,
    div[data-testid="stRadio"] label:hover span {
        color: #FFFFFF !important;
    }

    /* Active Nav Item - Sleek Dark Pill with Electric Blue Indicator */
    div[data-testid="stRadio"] label:has(input:checked),
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #1E222D !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        border: 1px solid #2E3440 !important;
        border-left: 3px solid #3B82F6 !important;
    }

    div[data-testid="stRadio"] label:has(input:checked) p,
    div[data-testid="stRadio"] label:has(input:checked) span,
    div[data-testid="stRadio"] label[data-checked="true"] p,
    div[data-testid="stRadio"] label[data-checked="true"] span {
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stRadio"] label > div:first-child {
        display: none !important;
    }
    div[data-testid="stRadio"] [data-testid="stWidgetLabel"] {
        display: none !important;
    }

    /* Content Cards & Containers: #1E222D Surface, #2E3440 Border, 8px Radius */
    div[data-testid="stVerticalBlockBorderWrapper"],
    .content-card,
    .enterprise-card {
        background: #1E222D !important;
        border: 1px solid #2E3440 !important;
        border-radius: 8px !important;
        padding: 20px 22px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25) !important;
    }

    .content-card-secondary {
        background: #181B24 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 6px !important;
        padding: 12px 14px !important;
        margin-bottom: 10px !important;
    }

    /* Refined Translucent Badges */
    .badge-blue,
    .badge-primary,
    .badge-lime {
        background: rgba(59, 130, 246, 0.12) !important;
        color: #60A5FA !important;
        border: 1px solid rgba(59, 130, 246, 0.28) !important;
        border-radius: 9999px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 3px 10px !important;
        display: inline-flex !important;
        align-items: center !important;
        line-height: 1.3 !important;
    }

    .badge-blue *,
    .badge-lime * {
        color: #60A5FA !important;
        font-size: 12px !important;
    }

    .badge-neutral {
        background: rgba(148, 163, 184, 0.1) !important;
        color: #94A3B8 !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 9999px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 3px 10px !important;
        display: inline-flex !important;
        align-items: center !important;
        line-height: 1.3 !important;
    }

    .badge-neutral * {
        color: #94A3B8 !important;
        font-size: 12px !important;
    }

    .badge-success {
        background: rgba(16, 185, 129, 0.12) !important;
        color: #34D399 !important;
        border: 1px solid rgba(16, 185, 129, 0.28) !important;
        border-radius: 9999px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 3px 10px !important;
        display: inline-flex !important;
        align-items: center !important;
        line-height: 1.3 !important;
    }

    .badge-success * {
        color: #34D399 !important;
        font-size: 12px !important;
    }

    /* Primary Button: Electric Blue #3B82F6 */
    .stButton > button[kind="primary"],
    button[kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: #3B82F6 !important;
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        min-height: 38px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
        transition: background 0.15s ease, border-color 0.15s ease !important;
    }

    .stButton > button[kind="primary"]:hover,
    button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background: #2563EB !important;
        border-color: #2563EB !important;
        color: #FFFFFF !important;
    }

    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    button[kind="primary"] p,
    button[kind="primary"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Secondary Button: Subtle Dark Slate #1E222D */
    .stButton > button,
    button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background: #1E222D !important;
        color: #E2E8F0 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        min-height: 38px !important;
        transition: all 0.15s ease !important;
    }

    .stButton > button:hover,
    button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background: #252A37 !important;
        border-color: #3B4252 !important;
        color: #FFFFFF !important;
    }

    .stButton > button p,
    .stButton > button span,
    button[kind="secondary"] p,
    button[kind="secondary"] span {
        color: #E2E8F0 !important;
    }

    /* Form Controls & Inputs */
    input, select, textarea, div[data-baseweb="input"] > div, div[data-baseweb="select"] {
        background-color: #181B24 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        color: #E2E8F0 !important;
    }

    input:focus, textarea:focus, div[data-baseweb="input"]:focus-within > div {
        border-color: #3B82F6 !important;
    }

    input::placeholder, textarea::placeholder {
        color: #64748B !important;
        font-size: 13.5px !important;
    }

    /* File Upload Dropzone: #181B24 surface, #2E3440 dashed border, 8px radius */
    div[data-testid="stFileUploader"] {
        background: transparent !important;
        width: 100% !important;
    }

    div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] {
        color: #FFFFFF !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stFileUploader"] section,
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploadDropzone"] {
        background-color: #181B24 !important;
        border: 1.5px dashed #2E3440 !important;
        border-radius: 8px !important;
        padding: 2.25rem 1.5rem !important;
        min-height: 180px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stFileUploader"] section:hover,
    section[data-testid="stFileUploaderDropzone"]:hover,
    div[data-testid="stFileUploaderDropzone"]:hover {
        background-color: #1E222D !important;
        border-color: #3B82F6 !important;
    }

    /* Dropzone Icons & Text */
    div[data-testid="stFileUploader"] section svg,
    section[data-testid="stFileUploaderDropzone"] svg {
        color: #60A5FA !important;
        fill: #60A5FA !important;
        font-size: 32px !important;
        width: 32px !important;
        height: 32px !important;
    }

    div[data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: #E2E8F0 !important;
        font-size: 14.5px !important;
        font-weight: 500 !important;
    }

    div[data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: #94A3B8 !important;
        font-size: 13px !important;
    }

    /* Dropzone Browse Files Button */
    div[data-testid="stFileUploader"] section button,
    section[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploaderDropzone"] button {
        background-color: #1E222D !important;
        color: #E2E8F0 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 6px !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        padding: 7px 20px !important;
        min-height: 36px !important;
        margin-top: 10px !important;
        transition: all 0.15s ease !important;
    }

    div[data-testid="stFileUploader"] section button:hover,
    section[data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #252A37 !important;
        border-color: #3B82F6 !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stFileUploader"] section button p,
    div[data-testid="stFileUploader"] section button span {
        color: #E2E8F0 !important;
    }

    /* Uploaded File Item Container */
    div[data-testid="stFileUploaderFile"],
    li[data-testid="stFileUploaderFile"] {
        background-color: #181B24 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 6px !important;
        padding: 10px 14px !important;
        margin-top: 10px !important;
    }

    div[data-testid="stFileUploaderFile"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stFileUploaderFile"] span {
        color: #FFFFFF !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    div[data-testid="stFileUploaderFile"] small {
        color: #94A3B8 !important;
        font-size: 12.5px !important;
    }

    div[data-testid="stFileUploaderFile"] button {
        background: transparent !important;
        border: none !important;
        color: #94A3B8 !important;
    }

    div[data-testid="stFileUploaderFile"] button:hover {
        color: #EF4444 !important;
    }

    /* DataFrames & Tables */
    .stDataFrame, div[data-testid="stDataFrame"] {
        border: 1px solid #2E3440 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        background: #1E222D !important;
        font-size: 13.5px !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background: #1E222D !important;
        border: 1px solid #2E3440 !important;
        border-radius: 8px !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stExpander"] details summary p {
        font-size: 14.5px !important;
        font-weight: 500 !important;
        color: #E2E8F0 !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 500 !important;
        font-size: 14px !important;
        color: #94A3B8 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        background: #1E222D !important;
        border-bottom: 2px solid #3B82F6 !important;
    }

    /* Alerts with Accessible Contrast */
    div[data-testid="stAlert"] {
        background: #181B24 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
        color: #E2E8F0 !important;
    }

    div[data-testid="stAlert"] p {
        font-size: 14px !important;
        line-height: 1.5 !important;
        color: #E2E8F0 !important;
    }

    /* Stepper */
    .step-container {
        display: flex;
        align-items: center;
        background: #1E222D;
        border: 1px solid #2E3440;
        border-radius: 8px;
        padding: 8px 14px;
        margin-bottom: 20px;
        overflow-x: auto;
        gap: 6px;
    }

    .step-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 500;
        color: #94A3B8;
        white-space: nowrap;
        padding: 4px 8px;
        border-radius: 4px;
    }

    .step-item.active {
        color: #FFFFFF;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.12);
    }

    .step-item.completed {
        color: #34D399;
    }

    .step-circle {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        background: #181B24;
        border: 1px solid #2E3440;
        color: #94A3B8;
    }

    .step-item.active .step-circle {
        background: #3B82F6;
        color: #FFFFFF;
        border-color: #3B82F6;
        font-weight: 700;
    }

    .step-item.completed .step-circle {
        background: #10B981;
        color: #FFFFFF;
        border-color: #10B981;
    }

    .step-arrow {
        color: #475569;
        font-size: 12px;
    }

    /* KPI Cards */
    .kpi-card {
        background: #1E222D;
        border: 1px solid #2E3440;
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }

    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }

    .kpi-title {
        font-size: 13.5px;
        font-weight: 500;
        color: #94A3B8;
    }

    .kpi-icon {
        font-size: 16px;
        color: #94A3B8;
    }

    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1.2;
        margin-top: 4px;
    }

    .kpi-subtext {
        font-size: 12.5px;
        color: #94A3B8;
        margin-top: 4px;
    }

    .kpi-delta-pos {
        color: #34D399;
        font-weight: 600;
    }

    .kpi-delta-neg {
        color: #EF4444;
        font-weight: 600;
    }

    /* Code blocks */
    pre, code {
        font-family: 'JetBrains Mono', Consolas, monospace !important;
        font-size: 13px !important;
        background: #181B24 !important;
        border: 1px solid #2E3440 !important;
        border-radius: 6px !important;
        color: #E2E8F0 !important;
    }
    </style>
    """
    if st is not None:
        st.markdown(css, unsafe_allow_html=True)


def apply_theme_css(theme_name: str = "Enterprise Dark"):
    """
    Wrapper for load_custom_css to maintain backward compatibility.
    """
    load_custom_css()


# ---------------------------------------------------------------------------
# BRANDING, SIDEBAR & TOPBAR COMPONENTS
# ---------------------------------------------------------------------------

def render_datapilot_brand_logo():
    """Renders the top sidebar brand header matching sleek enterprise layout."""
    logo_html = """
    <div style="padding: 4px 6px 14px 6px; border-bottom: 1px solid #2E3440; margin-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 9px;">
            <div style="width: 26px; height: 26px; border-radius: 6px; background: #3B82F6; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px; color: #FFFFFF; box-shadow: 0 1px 3px rgba(59, 130, 246, 0.4);">
                DP
            </div>
            <div style="font-size: 17.5px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.3px;">
                DataPilot AI
            </div>
        </div>
        <div style="font-size: 12.5px; color: #94A3B8; margin-top: 5px; font-weight: 400;">Analyst Workspace</div>
        <div style="font-size: 11px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 3px; font-weight: 500;">M.Sc. Data Science Project</div>
    </div>
    """
    render_html(logo_html)


def render_flux_brand_logo():
    """Compatibility alias for render_datapilot_brand_logo."""
    render_datapilot_brand_logo()


def render_flux_sidebar_promo():
    """Clean sidebar status indicator."""
    pass


def render_datapilot_topbar(
    title: str = "Workspace Overview",
    subtitle: str = "Understand, clean, explore, and analyze your data in one workspace.",
    dataset_name: Optional[str] = None,
    row_count: Optional[int] = None,
    health_score: Optional[int] = None,
    date_str: Optional[str] = None
):
    """
    Renders the clean enterprise top bar with crisp white title, soft grey subtitle,
    and subtle status pill.
    """
    if dataset_name and dataset_name != "No dataset loaded":
        row_label = f"{row_count:,} rows" if row_count is not None else "Active"
        quality_label = f" • {health_score}% Quality" if health_score is not None else ""
        status_html = f"""
        <div style="display: inline-flex; align-items: center; gap: 7px; background: #1E222D; border: 1px solid #2E3440; border-radius: 9999px; padding: 6px 14px; font-size: 13px; color: #E2E8F0;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #10B981; display: inline-block;"></span>
            <span style="font-weight: 600; color: #FFFFFF;">{dataset_name}</span>
            <span style="color: #94A3B8;">({row_label}{quality_label})</span>
        </div>
        """
    else:
        status_html = """
        <div style="display: inline-flex; align-items: center; gap: 7px; background: #1E222D; border: 1px solid #2E3440; border-radius: 9999px; padding: 6px 14px; font-size: 13px; color: #94A3B8;">
            <span style="width: 8px; height: 8px; border-radius: 50%; background: #F59E0B; display: inline-block;"></span>
            <span style="font-weight: 500;">No Dataset Loaded</span>
        </div>
        """

    topbar_html = f"""
    <div style="margin-bottom: 20px; border-bottom: 1px solid #2E3440; padding-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em; line-height: 1.25;">
                    {title}
                </h1>
                <p style="margin: 6px 0 0 0; font-size: 14.5px; color: #94A3B8; line-height: 1.5; font-weight: 400;">
                    {subtitle}
                </p>
            </div>
            <div>
                {status_html}
            </div>
        </div>
    </div>
    """
    render_html(topbar_html)


def render_flux_topbar(
    title: str = "Workspace Overview",
    subtitle: str = "Understand, clean, explore, and analyze your data in one workspace.",
    date_str: str = "Today",
    filter_label: str = "Active Dataset ▾"
):
    """Compatibility wrapper that calls render_datapilot_topbar."""
    render_datapilot_topbar(title=title, subtitle=subtitle)


# ---------------------------------------------------------------------------
# WORKFLOW STEPPER & ANALYTICAL CARDS
# ---------------------------------------------------------------------------

def render_workflow_stepper(current_page: str):
    """
    Renders an interactive subtle progress stepper bar to visualize where the user is
    in the 8-stage data analysis lifecycle.
    """
    steps = [
        ("Upload", "Upload"),
        ("Explore", "Data Explorer"),
        ("Clean", "Smart Data Cleaning"),
        ("Chart Guide", "Chart Guide"),
        ("SQL", "SQL Assistant"),
        ("AI Analyst", "AI Data Analyst"),
        ("ML Lab", "Machine Learning Lab"),
        ("Reports", "Reports & Exports")
    ]
    
    current_idx = 0
    for idx, (label, p_name) in enumerate(steps):
        if p_name.lower() in current_page.lower() or label.lower() in current_page.lower():
            current_idx = idx
            break

    items_html = []
    for idx, (label, _) in enumerate(steps):
        if idx < current_idx:
            status = "completed"
            icon = "✓"
        elif idx == current_idx:
            status = "active"
            icon = str(idx + 1)
        else:
            status = "pending"
            icon = str(idx + 1)
            
        items_html.append(f"""
        <div class="step-item {status}">
            <div class="step-circle">{icon}</div>
            <span>{label}</span>
        </div>
        """)
        if idx < len(steps) - 1:
            items_html.append('<div class="step-arrow">→</div>')

    stepper_html = f'<div class="step-container">{"".join(items_html)}</div>'
    render_html(stepper_html)


def render_kpi_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_text: str = "",
    icon: str = "📈"
):
    """Renders a clean analytical KPI card with restrained borders and clear typography."""
    delta_html = ""
    if delta:
        is_pos = not str(delta).startswith("-")
        delta_class = "kpi-delta-pos" if is_pos else "kpi-delta-neg"
        arrow = "▲" if is_pos else "▼"
        delta_html = f'<span class="{delta_class}">{arrow} {delta}</span> {delta_text}'
    elif delta_text:
        delta_html = f'<span>{delta_text}</span>'

    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <span class="kpi-title">{title}</span>
            <span class="kpi-icon">{icon}</span>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{delta_html}</div>
    </div>
    """
    render_html(card_html)


def render_page_header(title: str, subtitle: str, badge: str = None, icon: str = None):
    """Renders a styled page header with crisp white title, soft grey subtitle and translucent blue badge."""
    badge_html = f'<span class="badge-blue" style="margin-left: 10px;">{badge}</span>' if badge else ""
    header_html = f"""
    <div style="margin-bottom: 20px; border-bottom: 1px solid #2E3440; padding-bottom: 14px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #FFFFFF; letter-spacing: -0.02em; line-height: 1.25;">{title}</h1>
            {badge_html}
        </div>
        <p style="margin: 6px 0 0 0; font-size: 14.5px; color: #94A3B8; line-height: 1.5; font-weight: 400;">{subtitle}</p>
    </div>
    """
    render_html(header_html)


# ---------------------------------------------------------------------------
# COMPATIBILITY WRAPPERS
# ---------------------------------------------------------------------------

def render_flux_bubble_card(*args, **kwargs):
    """Compatibility stub."""
    pass


def render_flux_kpi_card(
    title: str = "Metric",
    value: str = "100",
    unit: str = "",
    subtext_title: str = "Target",
    subtext_val: str = "100",
    icon: str = "📊"
):
    """Clean KPI card wrapper."""
    render_kpi_card(title=title, value=f"{value} {unit}".strip(), delta_text=f"{subtext_title}: {subtext_val}", icon=icon)


def render_flux_wellness_matrix_card(*args, **kwargs):
    """Compatibility stub."""
    pass


def render_flux_dark_card(*args, **kwargs):
    """Compatibility stub."""
    pass


def get_theme_colors(theme_name: str = "Professional SaaS") -> List[str]:
    """Returns the color list for Plotly charts matching current theme."""
    theme = THEMES.get(theme_name, THEMES["Professional SaaS"])
    return theme["chart_colors"]


def get_plotly_theme(theme_name: str = "Professional SaaS") -> str:
    """Returns the plotly layout template name for current theme."""
    theme = THEMES.get(theme_name, THEMES["Professional SaaS"])
    return theme["plotly_template"]
