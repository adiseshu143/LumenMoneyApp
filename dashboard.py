import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from dotenv import load_dotenv
import json
import hashlib

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="LumenMoney - Smart Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'
if 'user' not in st.session_state:
    st.session_state.user = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# ============= ENHANCED MODERN STYLING =============
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #12121a;
        --bg-card: #16161f;
        --bg-card-hover: #1c1c28;
        --accent-primary: #7c3aed;
        --accent-secondary: #a78bfa;
        --accent-gradient: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%);
        --accent-glow: rgba(124, 58, 237, 0.4);
        --text-primary: #ffffff;
        --text-secondary: #a1a1aa;
        --text-muted: #71717a;
        --border-color: rgba(255, 255, 255, 0.08);
        --border-hover: rgba(124, 58, 237, 0.5);
        --success: #22c55e;
        --success-bg: rgba(34, 197, 94, 0.15);
        --danger: #ef4444;
        --danger-bg: rgba(239, 68, 68, 0.15);
        --warning: #f59e0b;
        --info: #3b82f6;
        --glass-bg: rgba(22, 22, 31, 0.8);
        --glass-border: rgba(255, 255, 255, 0.1);
    }
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        box-sizing: border-box;
    }

    /* Main app styling */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-secondary);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem !important;
    }
    
    /* Sidebar navigation buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 12px !important;
        color: var(--text-secondary) !important;
        padding: 14px 20px !important;
        width: 100% !important;
        text-align: left !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 4px !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(124, 58, 237, 0.1) !important;
        border-color: var(--border-hover) !important;
        color: var(--text-primary) !important;
        transform: translateX(4px) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:active {
        background: rgba(124, 58, 237, 0.2) !important;
    }
    
    /* Main container */
    .main .block-container {
        padding: 2rem 3rem !important;
        max-width: 1600px !important;
    }
    
    /* Glass morphism card */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 28px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: var(--border-hover);
        box-shadow: 0 20px 40px rgba(124, 58, 237, 0.15),
                    0 0 60px rgba(124, 58, 237, 0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 28px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--accent-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(124, 58, 237, 0.03) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-6px) scale(1.01);
        border-color: var(--border-hover);
        box-shadow: 0 25px 50px rgba(124, 58, 237, 0.2),
                    0 0 80px rgba(124, 58, 237, 0.1);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-card:hover::after {
        opacity: 1;
    }
    
    .metric-label {
        color: var(--text-muted);
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 36px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -1px;
        margin-bottom: 8px;
        background: linear-gradient(135deg, #fff 0%, #a1a1aa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .metric-change {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }
    
    .metric-change.positive {
        background: var(--success-bg);
        color: var(--success);
    }
    
    .metric-change.negative {
        background: var(--danger-bg);
        color: var(--danger);
    }
    
    .metric-subtext {
        color: var(--text-muted);
        font-size: 13px;
        margin-top: 12px;
        line-height: 1.6;
    }
    
    .metric-footer {
        display: flex;
        gap: 20px;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid var(--border-color);
    }
    
    .metric-footer-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--text-muted);
        font-size: 12px;
    }
    
    /* Chart card */
    .chart-card {
        background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 28px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .chart-card:hover {
        border-color: var(--border-hover);
        box-shadow: 0 20px 40px rgba(124, 58, 237, 0.1);
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        flex-wrap: wrap;
        gap: 16px;
    }
    
    .chart-title {
        font-size: 18px;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    /* Currency badge */
    .currency-badge {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .currency-badge:hover {
        background: rgba(124, 58, 237, 0.1);
        border-color: var(--border-hover);
        color: var(--text-primary);
    }
    
    /* Page header */
    .page-header {
        margin-bottom: 40px;
    }
    
    .page-title {
        font-size: 42px;
        font-weight: 900;
        letter-spacing: -2px;
        margin-bottom: 8px;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 3s ease-in-out infinite;
        background-size: 200% auto;
    }
    
    @keyframes shimmer {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 100% center; }
    }
    
    .page-subtitle {
        color: var(--text-muted);
        font-size: 16px;
        font-weight: 400;
    }
    
    /* Buttons */
    .btn-primary {
        background: var(--accent-gradient);
        border: none;
        border-radius: 12px;
        padding: 14px 28px;
        color: white;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px var(--accent-glow);
        position: relative;
        overflow: hidden;
    }
    
    .btn-primary::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 30px var(--accent-glow);
    }
    
    .btn-primary:hover::before {
        left: 100%;
    }
    
    .btn-secondary {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 14px 28px;
        color: var(--text-primary);
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-secondary:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-hover);
        transform: translateY(-2px);
    }
    
    /* Profile styles */
    .profile-header {
        background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        padding: 48px;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-bottom: 32px;
    }
    
    .profile-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--accent-gradient);
    }
    
    .profile-avatar {
        width: 120px;
        height: 120px;
        background: var(--accent-gradient);
        border-radius: 50%;
        margin: 0 auto 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        font-weight: 800;
        color: white;
        box-shadow: 0 0 40px var(--accent-glow);
        position: relative;
    }
    
    .profile-avatar::after {
        content: '';
        position: absolute;
        inset: -4px;
        border-radius: 50%;
        border: 2px solid rgba(124, 58, 237, 0.3);
        animation: pulse-ring 2s ease-out infinite;
    }
    
    @keyframes pulse-ring {
        0% { transform: scale(1); opacity: 1; }
        100% { transform: scale(1.2); opacity: 0; }
    }
    
    .profile-name {
        font-size: 28px;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .profile-email {
        color: var(--accent-secondary);
        font-size: 14px;
        margin-bottom: 20px;
    }
    
    .profile-badges {
        display: flex;
        gap: 12px;
        justify-content: center;
        flex-wrap: wrap;
        margin-bottom: 32px;
    }
    
    .badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-premium {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
        color: #1a1a1a;
    }
    
    .badge-verified {
        background: linear-gradient(135deg, #22c55e 0%, #4ade80 100%);
        color: #1a1a1a;
    }
    
    .profile-stats {
        display: flex;
        justify-content: center;
        gap: 48px;
        padding-top: 32px;
        border-top: 1px solid var(--border-color);
    }
    
    .profile-stat {
        text-align: center;
    }
    
    .profile-stat-value {
        font-size: 28px;
        font-weight: 800;
        color: var(--accent-secondary);
    }
    
    .profile-stat-label {
        color: var(--text-muted);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
    
    .profile-section {
        background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 28px;
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }
    
    .profile-section:hover {
        border-color: var(--border-hover);
    }
    
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 24px;
    }
    
    .profile-field {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .profile-field:last-child {
        border-bottom: none;
    }
    
    .profile-field-label {
        color: var(--text-muted);
        font-size: 13px;
        font-weight: 500;
    }
    
    .profile-field-value {
        color: var(--text-primary);
        font-size: 14px;
        font-weight: 600;
    }
    
    .edit-btn {
        background: rgba(124, 58, 237, 0.1);
        border: 1px solid var(--border-hover);
        border-radius: 8px;
        padding: 8px 16px;
        color: var(--accent-secondary);
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .edit-btn:hover {
        background: rgba(124, 58, 237, 0.2);
        transform: translateY(-1px);
    }
    
    .preference-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 20px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .preference-item:hover {
        border-color: var(--border-hover);
        background: var(--bg-card-hover);
    }
    
    .preference-label {
        color: var(--text-primary);
        font-size: 14px;
        font-weight: 600;
    }
    
    .preference-sublabel {
        color: var(--text-muted);
        font-size: 12px;
        margin-top: 4px;
    }
    
    .toggle-switch {
        width: 48px;
        height: 26px;
        background: var(--accent-gradient);
        border-radius: 13px;
        position: relative;
        cursor: pointer;
        box-shadow: 0 2px 10px var(--accent-glow);
    }
    
    .toggle-switch::after {
        content: '';
        position: absolute;
        width: 22px;
        height: 22px;
        background: white;
        border-radius: 50%;
        top: 2px;
        right: 2px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Legend items */
    .legend-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 14px;
        border-radius: 10px;
        transition: all 0.2s ease;
    }
    
    .legend-item:hover {
        background: rgba(124, 58, 237, 0.1);
    }
    
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .legend-text {
        color: var(--text-secondary);
        font-size: 13px;
        font-weight: 500;
    }
    
    /* Icon buttons in header */
    .header-actions {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .icon-btn {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .icon-btn:hover {
        background: rgba(124, 58, 237, 0.1);
        border-color: var(--border-hover);
        transform: translateY(-2px);
    }
    
    .icon-btn i {
        color: var(--text-secondary);
        font-size: 16px;
        transition: color 0.3s ease;
    }
    
    .icon-btn:hover i {
        color: var(--accent-secondary);
    }
    
    .notification-dot {
        position: absolute;
        top: 8px;
        right: 8px;
        width: 10px;
        height: 10px;
        background: var(--danger);
        border-radius: 50%;
        border: 2px solid var(--bg-primary);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
    }
    
    /* Auth container styling */
    .auth-container {
        max-width: 420px;
        margin: 60px auto;
        padding: 48px;
        background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%);
        border: 1px solid var(--border-color);
        border-radius: 24px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
        position: relative;
        overflow: hidden;
    }
    
    .auth-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--accent-gradient);
    }
    
    .auth-title {
        font-size: 32px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 8px;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .auth-subtitle {
        color: var(--text-muted);
        text-align: center;
        font-size: 14px;
        margin-bottom: 32px;
    }
    
    .auth-mode-indicator {
        display: flex;
        gap: 8px;
        justify-content: center;
        margin-bottom: 32px;
    }
    
    .mode-badge {
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .mode-badge.active {
        background: var(--accent-gradient);
        border-color: transparent;
        color: white;
        box-shadow: 0 4px 20px var(--accent-glow);
    }
    
    .mode-badge.inactive {
        background: transparent;
        color: var(--text-muted);
    }
    
    .mode-badge.inactive:hover {
        border-color: var(--border-hover);
        color: var(--text-primary);
    }
    
    /* Form inputs */
    .stTextInput > div > div > input {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        padding: 14px 16px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--accent-glow) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: var(--text-muted) !important;
    }
    
    /* Primary button styling */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="baseButton-primary"] {
        background: var(--accent-gradient) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 28px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 20px var(--accent-glow) !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px var(--accent-glow) !important;
    }
    
    /* Secondary button */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="baseButton-secondary"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
    }
    
    /* Action buttons row */
    .action-buttons {
        display: flex;
        gap: 16px;
        justify-content: flex-end;
        margin-bottom: 32px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 1024px) {
        .main .block-container {
            padding: 1.5rem !important;
        }
        .page-title {
            font-size: 32px;
        }
        .metric-value {
            font-size: 28px;
        }
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem !important;
        }
        .page-title {
            font-size: 26px;
        }
        .metric-card, .chart-card {
            padding: 20px;
        }
        .profile-stats {
            flex-direction: column;
            gap: 24px;
        }
        .chart-header {
            flex-direction: column;
            align-items: flex-start;
        }
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-in {
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    /* Plotly chart adjustments */
    .stPlotlyChart {
        background: transparent !important;
    }
    
    /* Logo styling */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 40px;
        padding: 0 8px;
    }
    
    .logo-icon {
        width: 44px;
        height: 44px;
        background: var(--accent-gradient);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 800;
        color: white;
        box-shadow: 0 4px 15px var(--accent-glow);
    }
    
    .logo-text {
        font-size: 22px;
        font-weight: 800;
        color: var(--text-primary);
        letter-spacing: -0.5px;
    }
    
    /* Nav items */
    .nav-section-title {
        color: var(--text-muted);
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 16px 20px 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============= AUTHENTICATION FUNCTIONS =============
def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(email, password):
    """Login user"""
    try:
        email = email.lower().strip()
        if email not in st.session_state.users_db:
            return False, "Email not found. Please sign up first."
        
        stored_password = st.session_state.users_db[email]['password']
        if stored_password == hash_password(password):
            st.session_state.user = {
                "email": email, 
                "localId": hash_password(email)[:16],
                "name": st.session_state.users_db[email].get('name', '')
            }
            st.session_state.user_email = email
            st.session_state.user_id = hash_password(email)[:16]
            st.session_state.user_name = st.session_state.users_db[email].get('name', '')
            return True, "Login successful!"
        else:
            return False, "Invalid email or password"
    except Exception as e:
        return False, f"Login error: {str(e)}"

def signup_user(email, password, name=""):
    """Sign up new user"""
    try:
        email = email.lower().strip()
        name = name.strip()
        
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"
        
        if len(password) < 6:
            return False, "Password should be at least 6 characters"
        
        if email in st.session_state.users_db:
            return False, "Email already exists. Please login instead."
        
        st.session_state.users_db[email] = {
            'password': hash_password(password),
            'name': name
        }
        st.session_state.user = {"email": email, "localId": hash_password(email)[:16], "name": name}
        st.session_state.user_email = email
        st.session_state.user_id = hash_password(email)[:16]
        st.session_state.user_name = name
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Signup error: {str(e)}"

def logout_user():
    """Logout user"""
    st.session_state.user = None
    st.session_state.user_email = None
    st.session_state.user_id = None
    st.session_state.user_name = ""

# ============= AUTHENTICATION PAGE =============
if st.session_state.user is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="auth-mode-indicator">
            <div class="mode-badge {'active' if st.session_state.auth_mode == 'login' else 'inactive'}">🔐 Login</div>
            <div class="mode-badge {'active' if st.session_state.auth_mode == 'signup' else 'inactive'}">✨ Sign Up</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="auth-container">
            <div class="auth-title">{"Welcome Back" if st.session_state.auth_mode == 'login' else "Get Started"}</div>
            <div class="auth-subtitle">{"Sign in to access your financial dashboard" if st.session_state.auth_mode == 'login' else "Create your account to start managing your finances"}</div>
        </div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="Enter your email", key="auth_email", label_visibility="collapsed")
        
        if st.session_state.auth_mode == 'signup':
            name = st.text_input("Full Name", placeholder="Enter your full name", key="auth_name", label_visibility="collapsed")
        else:
            name = ""
        
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="auth_password", label_visibility="collapsed")
        
        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
        
        if st.session_state.auth_mode == 'login':
            if st.button("🔐 Sign In", use_container_width=True, type="primary"):
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both email and password")
        else:
            if st.button("✨ Create Account", use_container_width=True, type="primary"):
                if email and password:
                    if len(password) < 6:
                        st.warning("Password should be at least 6 characters")
                    else:
                        success, message = signup_user(email, password, name)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please fill in all required fields")
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        if st.session_state.auth_mode == 'login':
            st.markdown("<div style='text-align: center; color: var(--text-muted);'>Don't have an account?</div>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True, key="switch_signup"):
                st.session_state.auth_mode = 'signup'
                st.rerun()
        else:
            st.markdown("<div style='text-align: center; color: var(--text-muted);'>Already have an account?</div>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True, key="switch_login"):
                st.session_state.auth_mode = 'login'
                st.rerun()
    
    st.stop()

# ============= MAIN APPLICATION =============

# Sidebar Navigation
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <div class="logo-icon">L</div>
        <span class="logo-text">LumenMoney</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="nav-section-title">Main Menu</div>', unsafe_allow_html=True)
    
    if st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    if st.button("💳 Transactions", key="nav_transactions", use_container_width=True):
        st.session_state.current_page = 'transactions'
        st.rerun()
    
    if st.button("👛 Wallet", key="nav_wallet", use_container_width=True):
        st.session_state.current_page = 'wallet'
        st.rerun()
    
    if st.button("🎯 Goals", key="nav_goals", use_container_width=True):
        st.session_state.current_page = 'goals'
        st.rerun()
    
    if st.button("💰 Budget", key="nav_budget", use_container_width=True):
        st.session_state.current_page = 'budget'
        st.rerun()
    
    if st.button("📈 Analytics", key="nav_analytics", use_container_width=True):
        st.session_state.current_page = 'analytics'
        st.rerun()
    
    st.markdown('<div class="nav-section-title" style="margin-top: 24px;">Settings</div>', unsafe_allow_html=True)
    
    if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
        st.session_state.current_page = 'settings'
        st.rerun()
    
    if st.button("👤 Profile", key="nav_profile", use_container_width=True):
        st.session_state.current_page = 'profile'
        st.rerun()
    
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    
    if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
        logout_user()
        st.rerun()

# Main Content Area
top_col1, top_col2 = st.columns([6, 1])

with top_col1:
    page_titles = {
        'dashboard': ('LumenMoney', 'Your financial overview at a glance'),
        'transactions': ('Transactions', 'View and manage all your transactions'),
        'wallet': ('Wallet', 'Manage your digital wallets'),
        'goals': ('Goals', 'Track your financial goals'),
        'budget': ('Budget', 'Plan and monitor your budget'),
        'analytics': ('Analytics', 'Deep insights into your finances'),
        'settings': ('Settings', 'Customize your preferences'),
        'profile': ('Profile', 'Manage your account')
    }
    
    title, subtitle = page_titles.get(st.session_state.current_page, ('Dashboard', ''))
    
    st.markdown(f"""
    <div class="page-header">
        <h1 class="page-title">{title}</h1>
        <p class="page-subtitle">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

with top_col2:
    st.markdown("""
    <div class="header-actions">
        <div class="icon-btn">
            <i class="fas fa-search"></i>
        </div>
        <div class="icon-btn">
            <i class="fas fa-bell"></i>
            <span class="notification-dot"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============= PAGE CONTENT =============

if st.session_state.current_page == 'profile':
    # Profile Page
    user_email = st.session_state.get('user_email', 'user@example.com')
    stored_name = st.session_state.get('user_name', '')
    
    if stored_name:
        user_display_name = stored_name
        name_parts = user_display_name.split()
    else:
        user_name_part = user_email.split('@')[0]
        user_display_name = user_name_part.replace('.', ' ').replace('_', ' ').title()
        name_parts = user_display_name.split()
    
    if len(name_parts) >= 2:
        user_initials = (name_parts[0][0] + name_parts[1][0]).upper()
    else:
        user_initials = user_display_name[:2].upper() if len(user_display_name) >= 2 else user_display_name.upper()
    
    st.markdown(f"""
    <div class="profile-header animate-in">
        <div class="profile-avatar">{user_initials}</div>
        <div class="profile-name">{user_display_name}</div>
        <div class="profile-email">{user_email}</div>
        <div class="profile-badges">
            <span class="badge badge-premium">⭐ Premium</span>
            <span class="badge badge-verified">✓ Verified</span>
        </div>
        <div class="profile-stats">
            <div class="profile-stat">
                <div class="profile-stat-value">₹15,700</div>
                <div class="profile-stat-label">Total Balance</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-value">6</div>
                <div class="profile-stat-label">Active Goals</div>
            </div>
            <div class="profile-stat">
                <div class="profile-stat-value">89%</div>
                <div class="profile-stat-label">Budget Score</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="profile-section animate-in">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <span class="section-title">Personal Information</span>
                <button class="edit-btn">Edit</button>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">First Name</span>
                <span class="profile-field-value">{name_parts[0] if name_parts else 'Not Set'}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Last Name</span>
                <span class="profile-field-value">{name_parts[1] if len(name_parts) > 1 else 'Not Set'}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Email</span>
                <span class="profile-field-value">{user_email}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Phone</span>
                <span class="profile-field-value">+91 XXX XXX XXXX</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Location</span>
                <span class="profile-field-value">India</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="profile-section animate-in">
            <span class="section-title">Financial Overview</span>
            <div class="profile-field">
                <span class="profile-field-label">Primary Currency</span>
                <span class="profile-field-value">INR (₹)</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Member Since</span>
                <span class="profile-field-value">January 2024</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Total Transactions</span>
                <span class="profile-field-value">1,247</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Linked Accounts</span>
                <span class="profile-field-value">4 Accounts</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="profile-section animate-in">
            <span class="section-title">Preferences</span>
            <div class="preference-item">
                <div>
                    <div class="preference-label">Email Notifications</div>
                    <div class="preference-sublabel">Receive updates about your finances</div>
                </div>
                <div class="toggle-switch"></div>
            </div>
            <div class="preference-item">
                <div>
                    <div class="preference-label">Budget Alerts</div>
                    <div class="preference-sublabel">Get notified when exceeding budget</div>
                </div>
                <div class="toggle-switch"></div>
            </div>
            <div class="preference-item">
                <div>
                    <div class="preference-label">Goal Reminders</div>
                    <div class="preference-sublabel">Weekly progress updates</div>
                </div>
                <div class="toggle-switch"></div>
            </div>
            <div class="preference-item">
                <div>
                    <div class="preference-label">Transaction Alerts</div>
                    <div class="preference-sublabel">Real-time notifications</div>
                </div>
                <div class="toggle-switch"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="profile-section animate-in">
            <span class="section-title">Security</span>
            <div class="profile-field">
                <span class="profile-field-label">Password</span>
                <button class="edit-btn">Change</button>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Two-Factor Auth</span>
                <span style="color: #22c55e; font-weight: 600;">✓ Enabled</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Login Sessions</span>
                <button class="edit-btn">Manage</button>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Connected Devices</span>
                <span class="profile-field-value">3 Devices</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Dashboard / Analytics Page
    st.markdown("""
    <div class="action-buttons">
        <button class="btn-secondary">
            <i class="fas fa-th-large" style="margin-right: 8px;"></i>Manage Widgets
        </button>
        <button class="btn-primary">
            <i class="fas fa-plus" style="margin-right: 8px;"></i>Add Widget
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    # Metric Cards Row
    metric_cols = st.columns(3, gap="large")
    
    with metric_cols[0]:
        st.markdown("""
        <div class="metric-card animate-in">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span class="metric-label">Total Balance</span>
                <span class="currency-badge">INR ▾</span>
            </div>
            <div class="metric-value">₹15,700<span style="opacity: 0.5;">.00</span></div>
            <span class="metric-change positive">▲ 12.1% from last month</span>
            <div class="metric-subtext">You have ₹1,700 extra compared to last month</div>
            <div class="metric-footer">
                <span class="metric-footer-item">📊 50 transactions</span>
                <span class="metric-footer-item">📁 15 categories</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[1]:
        st.markdown("""
        <div class="metric-card animate-in" style="animation-delay: 0.1s;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span class="metric-label">Income</span>
                <span class="currency-badge">INR ▾</span>
            </div>
            <div class="metric-value">₹8,500<span style="opacity: 0.5;">.00</span></div>
            <span class="metric-change positive">▲ 6.3% from last month</span>
            <div class="metric-subtext">You earned ₹500 more compared to last month</div>
            <div class="metric-footer">
                <span class="metric-footer-item">📊 27 transactions</span>
                <span class="metric-footer-item">📁 6 categories</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[2]:
        st.markdown("""
        <div class="metric-card animate-in" style="animation-delay: 0.2s;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <span class="metric-label">Expense</span>
                <span class="currency-badge">INR ▾</span>
            </div>
            <div class="metric-value">₹6,222<span style="opacity: 0.5;">.00</span></div>
            <span class="metric-change negative">▲ 2.4% from last month</span>
            <div class="metric-subtext">You spent ₹1,222 more compared to last month</div>
            <div class="metric-footer">
                <span class="metric-footer-item">📊 23 transactions</span>
                <span class="metric-footer-item">📁 9 categories</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    
    # Charts Row
    chart_cols = st.columns([2, 1], gap="large")
    
    with chart_cols[0]:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="chart-header">
            <span class="chart-title">Balance Overview</span>
            <div style="display: flex; gap: 20px; align-items: center;">
                <div class="legend-item">
                    <div class="legend-dot" style="background: #7c3aed;"></div>
                    <span class="legend-text">This month</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot" style="background: #71717a; opacity: 0.5;"></div>
                    <span class="legend-text">Last month</span>
                </div>
                <span class="currency-badge">Total Balance ▾</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        days = ['1 Jul', '3 Jul', '5 Jul', '7 Jul', '9 Jul', '11 Jul', '13 Jul', '15 Jul', '17 Jul', '19 Jul']
        this_month = [14000, 13500, 15000, 14200, 15800, 14800, 16200, 15500, 16000, 15700]
        last_month = [13000, 12800, 13200, 13800, 13500, 14200, 14000, 14500, 14800, 15000]
        
        fig1 = go.Figure()
        
        fig1.add_trace(go.Scatter(
            x=days, y=last_month,
            mode='lines',
            name='Last month',
            line=dict(color='#71717a', width=2, dash='dot'),
            hovertemplate='₹%{y:,.0f}<extra></extra>'
        ))
        
        fig1.add_trace(go.Scatter(
            x=days, y=this_month,
            mode='lines',
            name='This month',
            line=dict(color='#7c3aed', width=3),
            fill='tozeroy',
            fillcolor='rgba(124, 58, 237, 0.1)',
            hovertemplate='₹%{y:,.0f}<extra></extra>'
        ))
        
        fig1.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=11, color='#71717a', family='Inter')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.05)',
                zeroline=False,
                tickfont=dict(size=11, color='#71717a', family='Inter'),
                tickformat='₹,.0f'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_cols[1]:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("""
        <div class="chart-header">
            <span class="chart-title">Expense Breakdown</span>
            <span class="currency-badge">Expense ▾</span>
        </div>
        <div style="text-align: center; color: #71717a; font-size: 13px; margin-bottom: 16px;">
            Expense distribution by category
        </div>
        """, unsafe_allow_html=True)
        
        categories = ['Rent', 'Food & Dining', 'Transport', 'Entertainment', 'Utilities', 'Others']
        values = [2500, 1800, 800, 600, 400, 122]
        colors = ['#7c3aed', '#a78bfa', '#c4b5fd', '#22c55e', '#3b82f6', '#71717a']
        
        fig2 = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=0.7,
            marker=dict(colors=colors, line=dict(color='#16161f', width=3)),
            textposition='outside',
            textinfo='percent',
            textfont=dict(size=11, color='#a1a1aa', family='Inter'),
            hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>',
            pull=[0.02, 0, 0, 0, 0, 0]
        )])
        
        fig2.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(
                text='<b style="font-size: 14px; color: #a1a1aa;">Total Expense</b><br><br><span style="font-size: 28px; font-weight: 800; color: #7c3aed;">₹6,222</span>',
                x=0.5, y=0.5,
                font=dict(size=12, color='#71717a', family='Inter'),
                showarrow=False,
                align='center'
            )]
        )
        
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        
        # Legend
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 0 8px;">
            <div class="legend-item"><div class="legend-dot" style="background: #7c3aed;"></div><span class="legend-text">Rent</span></div>
            <div class="legend-item"><div class="legend-dot" style="background: #a78bfa;"></div><span class="legend-text">Food & Dining</span></div>
            <div class="legend-item"><div class="legend-dot" style="background: #c4b5fd;"></div><span class="legend-text">Transport</span></div>
            <div class="legend-item"><div class="legend-dot" style="background: #22c55e;"></div><span class="legend-text">Entertainment</span></div>
            <div class="legend-item"><div class="legend-dot" style="background: #3b82f6;"></div><span class="legend-text">Utilities</span></div>
            <div class="legend-item"><div class="legend-dot" style="background: #71717a;"></div><span class="legend-text">Others</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
    
    # Budget Comparison Chart
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("""
    <div class="chart-header">
        <span class="chart-title">Budget vs Expense Comparison</span>
        <div style="display: flex; gap: 20px; align-items: center;">
            <div class="legend-item">
                <div class="legend-dot" style="background: #7c3aed;"></div>
                <span class="legend-text">Expense</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #c4b5fd;"></div>
                <span class="legend-text">Budget</span>
            </div>
            <span class="currency-badge">This Year ▾</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
    expenses = [5800, 3500, 6200, 7200, 5500, 7800, 6800]
    budgets = [6000, 4000, 6500, 7000, 6000, 7500, 7200]
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Bar(
        x=months, y=budgets,
        name='Budget',
        marker=dict(color='#c4b5fd', cornerradius=8),
        width=0.35,
        offset=-0.18,
        hovertemplate='Budget: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_trace(go.Bar(
        x=months, y=expenses,
        name='Expense',
        marker=dict(color='#7c3aed', cornerradius=8),
        width=0.35,
        offset=0.18,
        hovertemplate='Expense: ₹%{y:,.0f}<extra></extra>'
    ))
    
    fig3.add_annotation(
        x='Feb', y=3500,
        text='<b>Exceeded budget<br>by ₹500 (20%)</b>',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='#7c3aed',
        ax=50, ay=-50,
        bgcolor='#1c1c28',
        bordercolor='#7c3aed',
        borderwidth=1,
        borderpad=8,
        font=dict(size=11, color='#fff', family='Inter')
    )
    
    fig3.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        barmode='group',
        bargap=0.4,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=12, color='#71717a', family='Inter')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False,
            tickfont=dict(size=11, color='#71717a', family='Inter'),
            tickformat='₹,.0f'
        )
    )
    
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
