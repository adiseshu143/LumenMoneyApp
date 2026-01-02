import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from dotenv import load_dotenv
import json
import hashlib

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Lumen Money", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'LumenMoney'
if 'user' not in st.session_state:
    st.session_state.user = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}  # Simple in-memory user database

st.markdown("""
<style>
    :root {
        --bg: #000000;
        --card: #000000;
        --primary: #7C6EF6;
        --primary-2: #EDEBFE;
        --text-strong: #FFFFFF;
        --text-muted: #E5E7EB;
        --border: #333333;
        --success: #22C55E;
        --danger: #EF4444;
    }
    
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        line-height: 1.55;
        letter-spacing: -0.01em;
    }

    html, body, .stApp, .stAppViewContainer, .main {
        background: #000000 !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg);
        color: var(--text-strong);
    }

    /* Hide Streamlit top deploy/menu bar */
    #MainMenu { display: none !important; }
    header [data-testid="stToolbar"] { display: none !important; }
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #333333;
        padding-top: 12px;
    }
    
    /* Sidebar collapse button */
    button[data-testid="stSidebarCollapseButton"] {
        color: #FFFFFF !important;
        background: #7C6EF6 !important;
        border: 2px solid #7C6EF6 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        cursor: pointer !important;
        min-width: 48px !important;
        min-height: 48px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        z-index: 999 !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    button[data-testid="stSidebarCollapseButton"] svg {
        stroke: #FFFFFF !important;
        fill: #FFFFFF !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    button[data-testid="stSidebarCollapseButton"]:hover {
        background: #6B5ED6 !important;
        border-color: #6B5ED6 !important;
        box-shadow: 0 6px 20px rgba(124, 110, 246, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    button[data-testid="stSidebarCollapseButton"]:active {
        background: #5a4fc6 !important;
        transform: translateY(0) !important;
    }
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: none;
        gap: 16px;
    }

    @media (max-width: 1024px) {
        .main .block-container {
            padding: 1.5rem 1.5rem;
        }
        .chart-card, .metric-card {
            padding: 20px;
        }
        .page-title {
            font-size: 26px;
        }
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem 1rem 2rem 1rem;
        }
        .chart-card, .metric-card {
            padding: 16px;
        }
        .chart-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
        }
        .page-title {
            font-size: 22px;
        }
        .page-subtitle {
            font-size: 13px;
        }
        .top-actions {
            gap: 10px;
        }
    }
    
    .metric-card {
        background: var(--card);
        border-radius: 16px;
        border: 1px solid var(--border);
        padding: 28px;
        box-shadow: 0 8px 24px rgba(124, 110, 246, 0.12);
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #7C6EF6, #A89FF7);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(124, 110, 246, 0.2);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    /* Back button styling */
    div[data-testid="column"] > div > div > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid var(--border) !important;
        padding: 0.75rem 1.25rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        font-size: 14px !important;
    }
    
    div[data-testid="column"] > div > div > button[kind="secondary"]:hover {
        background: #FFFFFF !important;
        border-color: var(--border) !important;
        color: #000000 !important;
        transform: none !important;
    }
    
    .chart-card {
        background: var(--card);
        border-radius: 16px;
        border: 1px solid var(--border);
        padding: 28px;
        box-shadow: 0 8px 24px rgba(124, 110, 246, 0.12);
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .chart-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(124, 110, 246, 0.2);
    }
    
    /* Header icon hover effects */
    .header-icon {
        color: #FFFFFF !important;
        transition: all 0.2s ease;
        filter: drop-shadow(0 0 8px rgba(255,255,255,0.6));
        display: inline-block !important;
        vertical-align: middle !important;
    }
    .header-icon:hover {
        color: var(--primary) !important;
        transform: scale(1.15);
        filter: drop-shadow(0 0 12px rgba(124, 110, 246, 0.8));
    }
    
    /* Icon container hover effects */
    [style*="display: flex"][style*="gap: 20px"] > div {
        transition: all 0.3s ease;
        border-radius: 8px;
    }
    
    [style*="display: flex"][style*="gap: 20px"] > div:hover i {
        color: var(--primary) !important;
        transform: scale(1.15);
    }
    
    /* Hide the actual profile button */
    button[key="profile_btn"] {
        opacity: 0;
        position: absolute;
        pointer-events: none;
        width: 0;
        height: 0;
    }
    
    .metric-title {
        color: var(--text-muted);
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: var(--text-strong);
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }
    
    .metric-change {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .positive {
        color: var(--success);
    }
    
    .negative {
        color: var(--danger);
    }
    
    .metric-subtext {
        color: #9CA3AF;
        font-size: 12px;
        margin-bottom: 12px;
        line-height: 1.6;
    }
    
    .metric-info {
        display: flex;
        align-items: center;
        gap: 16px;
        color: #9CA3AF;
        font-size: 12px;
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .chart-title {
        color: var(--text-strong);
        font-size: 18px;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 32px;
    }
    
    .page-title {
        color: #FFFFFF;
        font-size: 42px;
        font-weight: 900;
        margin-bottom: 12px;
        letter-spacing: -0.04em;
        text-shadow: 0 4px 16px rgba(124, 110, 246, 0.5);
        background: linear-gradient(135deg, #FFFFFF 0%, #A89FF7 50%, #7C6EF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: titleGlow 3s ease-in-out infinite;
    }
    
    @keyframes titleGlow {
        0%, 100% { text-shadow: 0 4px 16px rgba(124, 110, 246, 0.5); }
        50% { text-shadow: 0 4px 24px rgba(124, 110, 246, 0.8); }
    }
    
    .page-subtitle {
        color: #9CA3AF;
        font-size: 16px;
        font-weight: 500;
        letter-spacing: 0.01em;
    }
    
    .top-actions {
        display: flex;
        gap: 16px;
        align-items: center;
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, #FFFFFF 0%, #F9FAFB 100%);
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 14px 28px;
        color: #1F2937;
        font-size: 15px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        position: relative;
        overflow: hidden;
    }
    
    .btn-secondary::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(124, 110, 246, 0.1), transparent);
        transition: left 0.6s;
    }
    
    .btn-secondary:hover::before {
        left: 100%;
    }
    
    .btn-secondary:hover {
        background: linear-gradient(135deg, #F9FAFB 0%, #FFFFFF 100%);
        border-color: #7C6EF6;
        color: #7C6EF6;
        box-shadow: 0 8px 24px rgba(124, 110, 246, 0.3);
        transform: translateY(-3px);
    }
    
    /* Icon button styling */
    .stButton > button p {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Sidebar nav buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
        padding: 14px 18px !important;
        width: 100% !important;
        justify-content: flex-start !important;
        gap: 12px !important;
        transition: all 0.3s ease !important;
        text-align: left !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(124, 110, 246, 0.15) !important;
        border: 1px solid rgba(124, 110, 246, 0.3) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(124, 110, 246, 0.2) !important;
        transform: translateX(4px) !important;
        outline: none !important;
    }
    [data-testid="stSidebar"] .stButton > button:focus,
    [data-testid="stSidebar"] .stButton > button:active,
    [data-testid="stSidebar"] .stButton > button:focus-visible {
        background: rgba(124, 110, 246, 0.2) !important;
        border: 1px solid rgba(124, 110, 246, 0.4) !important;
        color: #FFFFFF !important;
        outline: none !important;
    }
    
    .stButton > button[data-testid="baseButton-secondary"] {
        font-family: 'Font Awesome 6 Free', 'Inter', sans-serif !important;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #7C6EF6 0%, #5a3fa8 100%);
        border: none;
        border-radius: 12px;
        padding: 14px 32px;
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 800;
        cursor: pointer;
        box-shadow: 0 8px 24px rgba(124, 110, 246, 0.5), 0 0 40px rgba(124, 110, 246, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
    
    .btn-primary:hover::before {
        left: 100%;
    }
    
    .btn-primary:hover {
        background: linear-gradient(135deg, #6B5ED6 0%, #4a2f98 100%);
        box-shadow: 0 12px 32px rgba(124, 110, 246, 0.6), 0 0 50px rgba(124, 110, 246, 0.3);
        transform: translateY(-3px) scale(1.02);
    }
    
    .btn-primary:active {
        transform: translateY(0);
        box-shadow: 0 6px 16px rgba(124, 110, 246, 0.4);
    }
    
    .stPlotlyChart {
        background: transparent !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
    }
    
    .currency-badge {
        background: #1a1a1a;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        color: #FFFFFF;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border: 1px solid #333333;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .currency-badge:hover {
        background: #252525;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(124, 110, 246, 0.3);
    }
    
    .profile-header {
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
        border-radius: 20px;
        border: 2px solid #3B82F6;
        padding: 40px;
        box-shadow: 0 0 30px rgba(59, 130, 246, 0.25), 0 8px 24px rgba(0, 0, 0, 0.4);
        margin-bottom: 24px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .profile-header:hover {
        transform: translateY(-4px);
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.4), 0 12px 32px rgba(0, 0, 0, 0.5);
    }
    
    .profile-avatar-large {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        border-radius: 50%;
        margin: 0 auto 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        font-weight: 700;
        color: white;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5), 0 8px 24px rgba(0, 0, 0, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.15);
    }
    
    .profile-name {
        color: var(--text-strong);
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    
    .profile-email {
        color: #60A5FA;
        font-size: 14px;
        margin-bottom: 20px;
        font-weight: 500;
    }
    
    .profile-stats {
        display: flex;
        justify-content: center;
        gap: 48px;
        margin-top: 24px;
        padding-top: 24px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .profile-stat {
        text-align: center;
        padding: 12px 8px;
        transition: all 0.3s ease;
    }
    
    .profile-stat:hover {
        transform: translateY(-2px);
    }
    
    .profile-stat-value {
        color: #3B82F6;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .profile-stat-label {
        color: #9CA3AF;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .profile-section {
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
        border-radius: 16px;
        border: 1.5px solid #374151;
        padding: 28px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 24px;
        transition: all 0.3s ease;
    }
    
    .profile-section:hover {
        transform: translateY(-4px);
        border-color: #3B82F6;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2), 0 4px 16px rgba(0, 0, 0, 0.4);
    }
    
    .section-title {
        color: var(--text-strong);
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .profile-field {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 0;
        border-bottom: 1px solid #374151;
        gap: 16px;
    }
    
    .profile-field:last-child {
        border-bottom: none;
    }
    
    .profile-field-label {
        color: #9CA3AF;
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .profile-field-value {
        color: var(--text-strong);
        font-size: 14px;
        font-weight: 700;
        text-align: right;
    }
    
    .edit-btn {
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        color: #FFFFFF;
        font-size: 12px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .edit-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
    }
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .edit-btn:hover {
        background: var(--primary-2);
        border-color: var(--primary);
        color: var(--primary);
        box-shadow: 0 6px 16px rgba(124,110,246,0.3);
        transform: translateY(-2px);
    }
    
    .preference-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px;
        background: linear-gradient(135deg, #111827 0%, #1F2937 100%);
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #374151;
        transition: all 0.3s ease;
    }
    
    .preference-item:hover {
        background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
        border-color: #3B82F6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    
    .preference-item:last-child {
        margin-bottom: 0;
    }
    
    .preference-label {
        color: var(--text-strong);
        font-size: 14px;
        font-weight: 700;
    }
    
    .preference-sublabel {
        color: #9CA3AF;
        font-size: 12px;
        margin-top: 2px;
        font-weight: 500;
    }
    
    .toggle-switch {
        width: 44px;
        height: 24px;
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        border-radius: 12px;
        position: relative;
        cursor: pointer;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.1), 0 2px 8px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .toggle-switch::after {
        content: '';
        position: absolute;
        width: 20px;
        height: 20px;
        background: #FFFFFF;
        border-radius: 50%;
        top: 2px;
        right: 2px;
        transition: all 0.2s;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    
    .badge-premium {
        background: linear-gradient(135deg, #F59E0B 0%, #F97316 100%);
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
    }
    
    .badge-premium:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.5);
    }
    
    .badge-verified {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: #FFFFFF;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    .badge-verified:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(16, 185, 129, 0.5);
    }
    
    /* Dot grid background canvas */
    #dotGridCanvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        pointer-events: none;
        background: #f5f5f5;
    }
</style>
""", unsafe_allow_html=True)

# Add interactive dot grid background
st.markdown("""
<canvas id="dotGridCanvas"></canvas>
<script>
(function() {
    const canvas = document.getElementById('dotGridCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let width = window.innerWidth;
    let height = window.innerHeight;
    
    canvas.width = width;
    canvas.height = height;
    
    // Dot grid settings
    const dotSpacing = 40;
    const dotRadius = 2;
    const maxDotRadius = 6;
    const glowDistance = 150;
    
    let mouseX = -1000;
    let mouseY = -1000;
    
    // Create dot grid
    const dots = [];
    for (let x = dotSpacing; x < width; x += dotSpacing) {
        for (let y = dotSpacing; y < height; y += dotSpacing) {
            dots.push({ x, y, baseRadius: dotRadius });
        }
    }
    
    // Mouse move handler
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });
    
    // Animation loop
    function animate() {
        ctx.fillStyle = '#f5f5f5';
        ctx.fillRect(0, 0, width, height);
        
        dots.forEach(dot => {
            const dx = mouseX - dot.x;
            const dy = mouseY - dot.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < glowDistance) {
                // Calculate glow effect
                const factor = 1 - (distance / glowDistance);
                const radius = dot.baseRadius + (maxDotRadius - dot.baseRadius) * factor;
                const opacity = 0.3 + 0.7 * factor;
                
                ctx.fillStyle = `rgba(0, 0, 0, ${opacity})`;
                ctx.beginPath();
                ctx.arc(dot.x, dot.y, radius, 0, Math.PI * 2);
                ctx.fill();
            } else {
                // Default dot
                ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
                ctx.beginPath();
                ctx.arc(dot.x, dot.y, dot.baseRadius, 0, Math.PI * 2);
                ctx.fill();
            }
        });
        
        requestAnimationFrame(animate);
    }
    
    // Handle window resize
    window.addEventListener('resize', () => {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        
        // Recreate dots
        dots.length = 0;
        for (let x = dotSpacing; x < width; x += dotSpacing) {
            for (let y = dotSpacing; y < height; y += dotSpacing) {
                dots.push({ x, y, baseRadius: dotRadius });
            }
        }
    });
    
    animate();
})();
</script>
""", unsafe_allow_html=True)

# ============= AUTHENTICATION LOGIC (Simple In-Memory for Hackathon) =============
def hash_password(password):
    """Hash password for simple security"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(email, password):
    """Login user with simple in-memory database"""
    try:
        email = email.lower().strip()
        if email not in st.session_state.users_db:
            return False, "Email not found. Please sign up first."
        
        stored_password = st.session_state.users_db[email]
        if stored_password == hash_password(password):
            st.session_state.user = {"email": email, "localId": hash_password(email)[:16]}
            st.session_state.user_email = email
            st.session_state.user_id = hash_password(email)[:16]
            return True, "Login successful!"
        else:
            return False, "Invalid email or password"
    except Exception as e:
        return False, f"Login error: {str(e)}"

def signup_user(email, password):
    """Sign up new user with simple in-memory database"""
    try:
        email = email.lower().strip()
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"
        
        # Check password length
        if len(password) < 6:
            return False, "Password should be at least 6 characters"
        
        # Check if email already exists
        if email in st.session_state.users_db:
            return False, "Email already exists. Please login instead."
        
        # Create new user
        st.session_state.users_db[email] = hash_password(password)
        st.session_state.user = {"email": email, "localId": hash_password(email)[:16]}
        st.session_state.user_email = email
        st.session_state.user_id = hash_password(email)[:16]
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Signup error: {str(e)}"

def logout_user():
    """Logout user"""
    st.session_state.user = None
    st.session_state.user_email = None
    st.session_state.user_id = None

# Check if user is logged in
if st.session_state.user is None:
    # Show login/signup page
    st.markdown("""
    <style>
        .auth-container {
            max-width: 450px;
            margin: 80px auto;
            padding: 40px;
            background: #111111;
            border-radius: 20px;
            border: 1px solid #333333;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }
        .auth-title {
            font-size: 32px;
            font-weight: 700;
            color: #FFFFFF;
            text-align: center;
            margin-bottom: 10px;
        }
        .auth-subtitle {
            font-size: 14px;
            color: #9CA3AF;
            text-align: center;
            margin-bottom: 30px;
        }
        .auth-input {
            width: 100%;
            padding: 14px 16px;
            margin-bottom: 16px;
            background: #000000;
            border: 1px solid #333333;
            border-radius: 10px;
            color: #FFFFFF;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        .auth-input:focus {
            outline: none;
            border-color: #7C6EF6;
        }
        .auth-button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #7C6EF6, #9D8EFF);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .auth-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(124, 110, 246, 0.4);
        }
        .auth-toggle {
            text-align: center;
            margin-top: 20px;
            color: #9CA3AF;
            font-size: 14px;
        }
        .auth-toggle-link {
            color: #7C6EF6;
            cursor: pointer;
            text-decoration: underline;
        }
        .stTextInput input {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: 1px solid #333333 !important;
            border-radius: 10px !important;
            padding: 14px 16px !important;
        }
        .stTextInput input:focus {
            border-color: #7C6EF6 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center content
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class="auth-container">
            <div class="auth-title">{"Welcome Back" if st.session_state.auth_mode == 'login' else "Create Account"}</div>
            <div class="auth-subtitle">{"Login to continue to LumenMoney" if st.session_state.auth_mode == 'login' else "Sign up to get started with LumenMoney"}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Email and password inputs
        email = st.text_input("Email", placeholder="Enter your email", key="auth_email", label_visibility="collapsed")
        st.markdown('<div style="margin-top: -10px;"></div>', unsafe_allow_html=True)
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="auth_password", label_visibility="collapsed")
        st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
        
        # Submit button
        if st.session_state.auth_mode == 'login':
            if st.button("🔐 Login", use_container_width=True, type="primary"):
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
            if st.button("✨ Sign Up", use_container_width=True, type="primary"):
                if email and password:
                    if len(password) < 6:
                        st.warning("Password should be at least 6 characters")
                    else:
                        success, message = signup_user(email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please enter both email and password")
        
        # Toggle between login and signup
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)
        if st.session_state.auth_mode == 'login':
            if st.button("Don't have an account? Sign Up", use_container_width=True):
                st.session_state.auth_mode = 'signup'
                st.rerun()
        else:
            if st.button("Already have an account? Login", use_container_width=True):
                st.session_state.auth_mode = 'login'
                st.rerun()
    
    st.stop()  # Stop execution here if not logged in

# ============= MAIN APPLICATION (Only shown when logged in) =============

# Responsive breakpoints - defaults to desktop layout
is_mobile = False
is_tablet = False
is_desktop = True
is_large = True

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 40px;">
        <div style="width: 40px; height: 40px; background: #111827; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
            <span style="color: white   ; font-weight: 700; font-size: 18px;">F</span>
        </div>
        <span style="font-size: 20px; font-weight: 700; color: #111827;">FinSet</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.button("📊 Dashboard", key="nav_dashboard", use_container_width=True)
    if st.session_state.get('nav_dashboard'):
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
    
    if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
        st.session_state.current_page = 'settings'
        st.rerun()
    
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 16px; color: #6B7280; font-size: 14px; font-weight: 500; cursor: pointer; border-radius: 8px;">
        ❓ Help
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 16px; color: #6B7280; font-size: 14px; font-weight: 500; cursor: pointer; border-radius: 8px;">
        🚪 Log out
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 16px; color: #6B7280; font-size: 14px; cursor: pointer;">
        ☀️ 🌙
    </div>
    """, unsafe_allow_html=True)

# Top bar with profile button (responsive spacing)
if is_mobile:
    top_col1, top_col2 = st.columns([1, 1])
elif is_tablet:
    top_col1, top_col2 = st.columns([5, 2])
else:
    top_col1, top_col2 = st.columns([6, 1])

with top_col1:
    if st.session_state.current_page == 'analytics':
        st.markdown("""
        <div>
            <div class="page-title">Analytics</div>
            <div class="page-subtitle">Detailed overview of your financial situation</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div>
            <div class="page-title">LumenMoney</div>
            <div class="page-subtitle">Manage your account settings and preferences</div>
        </div>
        """, unsafe_allow_html=True)

with top_col2:
    # Create icons row with proper spacing
    if is_mobile:
        st.markdown('''
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 16px; padding: 8px 0;">
            <div class="icon-circle icon-circle-search">
                <i class="fas fa-search header-icon" style="font-size: 17px;"></i>
            </div>
            <div class="icon-circle icon-circle-bell">
                <i class="fas fa-bell header-icon" style="font-size: 17px;"></i>
                <span class="notification-badge"></span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        btn_cols = st.columns([1, 1, 1, 1])
        with btn_cols[2]:
            if st.button("👤", key="profile_btn", help="View Profile"):
                st.session_state.current_page = 'profile'
                st.rerun()
        with btn_cols[3]:
            if st.button("🚪", key="logout_btn_mobile", help="Logout"):
                logout_user()
                st.rerun()
    else:
        st.markdown('''
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 16px; padding: 8px 0;">
            <div class="icon-circle icon-circle-search">
                <i class="fas fa-search header-icon" style="font-size: 17px;"></i>
            </div>
            <div class="icon-circle icon-circle-bell">
                <i class="fas fa-bell header-icon" style="font-size: 17px;"></i>
                <span class="notification-badge"></span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        btn_cols = st.columns([1, 1, 1, 1, 1])
        with btn_cols[3]:
            if st.button("👤", key="profile_btn", help="View Profile"):
                st.session_state.current_page = 'profile'
                st.rerun()
        with btn_cols[4]:
            if st.button("🚪", key="logout_btn", help="Logout"):
                logout_user()
                st.rerun()

# Add icon styling with circular backgrounds and animations
st.markdown("""
<style>
    /* Circular icon containers */
    .icon-circle {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        border: 2px solid rgba(255, 255, 255, 0.15);
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        vertical-align: middle;
    }
    
    .icon-circle-search {
        background: transparent;
        border-color: rgba(124, 110, 246, 0.2);
    }
    
    .icon-circle-bell {
        background: transparent;
        border-color: rgba(245, 158, 11, 0.2);
    }
    
    .icon-circle:hover {
        transform: translateY(-3px) scale(1.08);
        background: rgba(255, 255, 255, 0.1);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .icon-circle-search:hover {
        border-color: rgba(124, 110, 246, 0.5);
        background: rgba(124, 110, 246, 0.1);
    }
    
    .icon-circle-bell:hover {
        border-color: rgba(245, 158, 11, 0.5);
        background: rgba(245, 158, 11, 0.1);
    }
    
    .icon-circle .header-icon {
        color: #FFFFFF !important;
        filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.4));
        transition: all 0.3s ease;
    }
    
    .icon-circle:hover .header-icon {
        transform: scale(1.15);
        filter: drop-shadow(0 4px 10px rgba(255, 255, 255, 0.3));
    }
    
    /* Notification badge */
    .notification-badge {
        position: absolute;
        top: 2px;
        right: 2px;
        width: 12px;
        height: 12px;
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        border-radius: 50%;
        border: 2.5px solid #000000;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.8), 0 0 6px rgba(239, 68, 68, 1);
        animation: pulse-notification 2s infinite;
    }
    
    @keyframes pulse-notification {
        0%, 100% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.15);
            opacity: 0.85;
        }
    }
    
    /* Hide button container wrapper for profile and logout buttons */
    div:has(> button[key="profile_btn"]),
    div:has(> button[key="logout_btn"]),
    div:has(> button[key="logout_btn_mobile"]) {
        width: 44px !important;
        min-width: 44px !important;
        max-width: 44px !important;
    }
    
    button[key="profile_btn"], button[key="logout_btn"], button[key="logout_btn_mobile"] {
        background: transparent !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        max-width: 44px !important;
        max-height: 44px !important;
        padding: 0 !important;
        margin: 0 !important;
        border: 2px solid rgba(124, 110, 246, 0.2) !important;
        box-shadow: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 20px !important;
        line-height: 1 !important;
        backdrop-filter: blur(10px) !important;
        flex-shrink: 0 !important;
        overflow: hidden !important;
    }
    button[key="logout_btn"], button[key="logout_btn_mobile"] {
        border-color: rgba(239, 68, 68, 0.2) !important;
    }
    button[key="profile_btn"]:hover, button[key="logout_btn"]:hover, button[key="logout_btn_mobile"]:hover {
        transform: translateY(-3px) scale(1.08) !important;
        background: rgba(124, 110, 246, 0.1) !important;
        border-color: rgba(124, 110, 246, 0.5) !important;
        box-shadow: 0 4px 16px rgba(124, 110, 246, 0.2) !important;
    }
    button[key="logout_btn"]:hover, button[key="logout_btn_mobile"]:hover {
        background: rgba(239, 68, 68, 0.1) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
        box-shadow: 0 4px 16px rgba(239, 68, 68, 0.2) !important;
    }
    button[key="profile_btn"] p, button[key="logout_btn"] p, button[key="logout_btn_mobile"] p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    .header-icon:hover {
        color: var(--primary) !important;
        transform: scale(1.1);
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

# Conditional rendering based on current page
if st.session_state.current_page == 'profile':
    # Profile Page - Back Button
    if st.button("← Back to Dashboard", key="back_to_dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get user email from session
    user_email = st.session_state.get('user_email', 'user@example.com')
    
    # Extract name from email (before @ symbol) and format it
    user_name_part = user_email.split('@')[0]
    # Replace dots and underscores with spaces, capitalize each word
    user_display_name = user_name_part.replace('.', ' ').replace('_', ' ').title()
    
    # Get initials (first letter of each word, max 2)
    name_parts = user_display_name.split()
    if len(name_parts) >= 2:
        user_initials = (name_parts[0][0] + name_parts[1][0]).upper()
    else:
        user_initials = user_display_name[:2].upper() if len(user_display_name) >= 2 else user_display_name.upper()
    
    st.markdown(f"""
    <div class="profile-header">
        <div class="profile-avatar-large">{user_initials}</div>
        <div class="profile-name">{user_display_name}</div>
        <div class="profile-email">{user_email}</div>
        <div style="display: flex; gap: 8px; justify-content: center; margin-top: 12px;">
            <span class="badge badge-premium">Premium Member</span>
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
                <div class="profile-stat-label">Budget On Track</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if is_mobile:
        col1, col2 = st.columns(1)
    elif is_tablet:
        col1, col2 = st.columns([1, 1])
    else:
        col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="profile-section">
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
                <span class="profile-field-label">Email Address</span>
                <span class="profile-field-value">{user_email}</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Phone Number</span>
                <span class="profile-field-value">+91 (XXX) XXX-XXXX</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Date of Birth</span>
                <span class="profile-field-value">Not Set</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Location</span>
                <span class="profile-field-value">India</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="profile-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <span class="section-title">Financial Overview</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Primary Currency</span>
                <span class="profile-field-value">INR (₹)</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Member Since</span>
                <span class="profile-field-value">January 2023</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Total Transactions</span>
                <span class="profile-field-value">1,247</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Linked Accounts</span>
                <span class="profile-field-value">4 Bank Accounts</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="profile-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <span class="section-title">Preferences</span>
            </div>
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
                    <div class="preference-label">Transaction Notifications</div>
                    <div class="preference-sublabel">Real-time transaction alerts</div>
                </div>
                <div class="toggle-switch"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="profile-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <span class="section-title">Security</span>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Password</span>
                <button class="edit-btn">Change</button>
            </div>
            <div class="profile-field">
                <span class="profile-field-label">Two-Factor Authentication</span>
                <span style="color: #22C55E; font-size: 13px; font-weight: 600;">✓ Enabled</span>
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
    
    st.markdown("""
    <div class="profile-section">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="section-title" style="margin-bottom: 4px; display: block;">Subscription & Billing</span>
                <span style="color: #6B7280; font-size: 13px;">Your premium membership renews on February 15, 2026</span>
            </div>
            <div style="display: flex; gap: 12px; flex-wrap: wrap; justify-content: center;">
                <button class="edit-btn" style="width: auto; min-width: 180px;">Manage Subscription</button>
                <button class="btn-primary" style="width: auto; min-width: 160px;">Upgrade Plan</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    # Analytics Page (original content)
    # Action buttons
    if is_mobile:
        action_cols = st.columns(1)
        with action_cols[0]:
            st.markdown("""
            <div style="display: flex; gap: 12px; justify-content: center; margin-bottom: 20px; flex-wrap: wrap;">
                <button class="btn-secondary" style="width: 100%; max-width: 280px;">
                    <i class="fas fa-th-large" style="margin-right: 8px;"></i>Manage widgets
                </button>
                <button class="btn-primary" style="width: 100%; max-width: 280px;">
                    <i class="fas fa-plus-circle" style="margin-right: 8px;"></i>Add new widget
                </button>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; gap: 16px; justify-content: flex-end; margin-bottom: 32px; width: 100%;">
            <button class="btn-secondary">
                <i class="fas fa-th-large" style="margin-right: 10px;"></i>Manage widgets
            </button>
            <button class="btn-primary">
                <i class="fas fa-plus-circle" style="margin-right: 10px;"></i>Add new widget
            </button>
        </div>
        """, unsafe_allow_html=True)

    # Row 1: Metric cards - Always 3 columns on desktop/large screens
    metric_cols = st.columns(3, gap="large")

    with metric_cols[0]:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="metric-title">Total balance</span>
                <span class="currency-badge">USD 🔽</span>
            </div>
            <div class="metric-value">₹15,700<span style="color: #9CA3AF;">.00</span></div>
            <div class="metric-change positive">▲ 12.1%</div>
            <div class="metric-subtext">You have extra ₹1,700<br/>compared to last month</div>
            <div class="metric-info">
                <span>📊 50 transactions</span>
                <span>📑 15 categories</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with metric_cols[1]:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="metric-title">Income</span>
                <span class="currency-badge">USD 🔽</span>
            </div>
            <div class="metric-value">₹8,500<span style="color: #9CA3AF;">.00</span></div>
            <div class="metric-change positive">▲ 6.3%</div>
            <div class="metric-subtext">You earn extra ₹500<br/>compared to last month</div>
            <div class="metric-info">
                <span>📊 27 transactions</span>
                <span>📑 6 categories</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with metric_cols[2]:
        st.markdown("""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="metric-title">Expense</span>
                <span class="currency-badge">USD 🔽</span>
            </div>
            <div class="metric-value">₹6,222<span style="color: #9CA3AF;">.00</span></div>
            <div class="metric-change negative">▲ 2.4%</div>
            <div class="metric-subtext">You spent extra ₹1,222<br/>compared to last month</div>
            <div class="metric-info">
                <span>📊 23 transactions</span>
                <span>📑 9 categories</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

    # Row 2: Charts - Optimized layout
    chart_cols = st.columns([2, 1], gap="large")

    with chart_cols[0]:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 16px;">
            <span class="chart-title" style="flex-shrink: 0;">Total balance overview</span>
            <div style="display: flex; gap: 20px; align-items: center; flex-wrap: wrap;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 12px; height: 12px; background: #7C6EF6; border-radius: 50%; flex-shrink: 0;"></div>
                    <span style="font-size: 13px; color: #E5E7EB; white-space: nowrap;">This month</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 12px; height: 3px; background: #9CA3AF; border-top: 2px dashed #9CA3AF; flex-shrink: 0;"></div>
                    <span style="font-size: 13px; color: #E5E7EB; white-space: nowrap;">Some period last month</span>
                </div>
                <span class="currency-badge" style="flex-shrink: 0;">Total balance 🔽</span>
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
            line=dict(color='#9CA3AF', width=2, dash='dot'),
            hovertemplate='₹%{y:,.0f}<extra></extra>'
        ))
        
        fig1.add_trace(go.Scatter(
            x=days, y=this_month,
            mode='lines',
            name='This month',
            line=dict(color='#7C6EF6', width=3),
            fill='tozeroy',
            fillcolor='rgba(124, 110, 246, 0.15)',
            hovertemplate='₹%{y:,.0f}<extra></extra>'
        ))
        
        line_height = 240 if is_mobile else 260 if is_tablet else 280
        fig1.update_layout(
            height=line_height,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                tickfont=dict(size=11, color='#9CA3AF')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#F3F4F6',
                zeroline=False,
                tickfont=dict(size=11, color='#9CA3AF'),
                tickformat='₹,.0f'
            ),
            hovermode='x unified'
        )
        
    st.plotly_chart(fig1, width='stretch', config={'displayModeBar': False})
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_cols[1]:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="chart-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <span class="chart-title">Statistics</span>
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
                <span class="currency-badge">Expense 🔽</span>
                <span style="font-size: 13px; color: #E5E7EB; cursor: pointer; white-space: nowrap;">Details ›</span>
            </div>
        </div>
        <div style="text-align: center; color: #9CA3AF; font-size: 13px; margin-bottom: 16px; line-height: 1.5;">
            You have an increase of expenses in several<br/>categories this month
        </div>
        """, unsafe_allow_html=True)
    
    categories = ['Money transfer', 'Cafe & Restaurants', 'Rent', 'Education', 'Food & Groceries', 'Others']
    values = [1800, 1200, 2500, 400, 300, 22]
    # Better fintech color palette
    colors = ['#667eea', '#764ba2', '#10B981', '#14B8A6', '#60A5FA', '#E5E7EB']
    
    fig2 = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        hole=0.68,
        marker=dict(
            colors=colors,
            line=dict(color='white', width=2)
        ),
        textposition='outside',
        textinfo='label+percent',
        textfont=dict(size=10.5, color='#FFFFFF', family='Inter, Arial, sans-serif'),
        insidetextorientation='horizontal',
        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f} (%{percent})<extra></extra>',
        pull=[0.01, 0.01, 0.01, 0.01, 0.01, 0.01],
        automargin=True
    )])
    
    pie_height = 320 if is_mobile else 340 if is_tablet else 360
    pie_margin = dict(l=12, r=12, t=12, b=12) if is_mobile else (dict(l=20, r=20, t=16, b=16) if is_tablet else dict(l=20, r=20, t=20, b=20))
    fig2.update_layout(
        height=pie_height,
        margin=pie_margin,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(family='Inter, Arial, sans-serif', color='#1F2937'),
        annotations=[dict(
            text='<b style="font-size: 14px; color: #E5E7EB; letter-spacing: 0.5px;">This month expense</b><br><br><span style="font-size: 32px; font-weight: 700; color: #667eea; letter-spacing: -1px;">₹6,222</span><span style="color: #E5E7EB; font-size: 18px; font-weight: 400;">.00</span>',
            x=0.5, y=0.5,
            font=dict(size=12, color='#6B7280', family='Inter, Arial, sans-serif'),
            showarrow=False,
            align='center'
        )]
    )
    st.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})
    
    legend_columns = '1fr 1fr' if is_mobile else '1fr 1fr 1fr'
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: {legend_columns}; gap: 16px; font-size: 13px; margin-top: 16px; padding: 0 8px;">
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; transition: all 0.2s;">
            <div style="width: 12px; height: 12px; background: #667eea; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 8px rgba(102, 126, 234, 0.4);"></div>
            <div style="width: 12px; height: 12px; background: #764ba2; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 8px rgba(118, 75, 162, 0.4);"></div>
            <span style="color: #E5E7EB; font-weight: 500; font-size: 13px;">Cafe & Restaurants</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; transition: all 0.2s;">
            <div style="width: 12px; height: 12px; background: #10B981; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);"></div>
            <span style="color: #E5E7EB; font-weight: 500; font-size: 13px;">Rent</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; transition: all 0.2s;">
            <div style="width: 12px; height: 12px; background: #14B8A6; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 8px rgba(20, 184, 166, 0.4);"></div>
            <span style="color: #E5E7EB; font-weight: 500; font-size: 13px;">Education</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; transition: all 0.2s;">
            <div style="width: 12px; height: 12px; background: #60A5FA; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 8px rgba(96, 165, 250, 0.4);"></div>
            <span style="color: #E5E7EB; font-weight: 500; font-size: 13px;">Food & Groceries</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 8px; transition: all 0.2s;">
            <div style="width: 12px; height: 12px; background: #E5E7EB; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 4px rgba(229, 231, 235, 0.6);"></div>
            <span style="color: #E5E7EB; font-weight: 500; font-size: 13px;">Others</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# Row 3: Bar chart
st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.markdown("""
<div class="chart-header">
    <span class="chart-title">Comparing of budget and expence</span>
    <div style="display: flex; gap: 16px; align-items: center;">
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="width: 10px; height: 10px; background: #7C6EF6; border-radius: 50%;"></div>
            <span style="font-size: 13px; color: #6B7280;">Expense</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
            <div style="width: 10px; height: 10px; background: #EDEBFE; border-radius: 50%;"></div>
            <span style="font-size: 13px; color: #6B7280;">Budget</span>
        </div>
        <span class="currency-badge">This year 🔽</span>
    </div>
</div>
""", unsafe_allow_html=True)

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
expenses = [5800, 3500, 6200, 7200, 5500, 7800, 6800]
budgets = [6000, 4000, 6500, 7000, 6000, 7500, 7200]

fig3 = go.Figure()

fig3.add_trace(go.Bar(
    x=months,
    y=budgets,
    name='Budget',
    marker=dict(color='#EDEBFE', cornerradius=15),
    width=0.35,
    offset=-0.2,
    hovertemplate='₹%{y:,.0f}<extra></extra>'
))

fig3.add_trace(go.Bar(
    x=months,
    y=expenses,
    name='Expense',
    marker=dict(color='#7C6EF6', cornerradius=15),
    width=0.35,
    offset=0.2,
    hovertemplate='₹%{y:,.0f}<extra></extra>'
))

fig3.add_annotation(
    x='Feb',
    y=3500,
    text='<b>Exceeded<br>by 20% ₹500</b>',
    showarrow=True,
    arrowhead=2,
    arrowsize=1,
    arrowwidth=2,
    arrowcolor='#7C6EF6',
    ax=40,
    ay=-60,
    bgcolor='#FFFFFF',
    bordercolor='#E5E7EB',
    borderwidth=1,
    borderpad=8,
    font=dict(size=11, color='#111827')
)

fig3.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    showlegend=False,
    barmode='group',
    bargap=0.5,
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=11, color='#9CA3AF')
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='#F3F4F6',
        zeroline=False,
        tickfont=dict(size=11, color='#9CA3AF'),
        tickformat='₹,.0f'
    )
)

st.plotly_chart(fig3, width='stretch', config={'displayModeBar': False})

st.markdown('</div>', unsafe_allow_html=True)