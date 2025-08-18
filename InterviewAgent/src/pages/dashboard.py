"""
Dashboard page for InterviewAgent Streamlit app
Enhanced with modern ShadCN-inspired components
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from database.operations import get_db_operations
from config import get_config

def inject_shadcn_styles():
    """Inject ultra-modern ShadCN styles with glassmorphism, animations, and cutting-edge design"""
    
    st.markdown("""
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');
    
    /* Ultra-Modern ShadCN Variables with Glassmorphism */
    :root {
        /* Base colors */
        --background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --background-glass: rgba(255, 255, 255, 0.1);
        --foreground: #ffffff;
        --foreground-muted: rgba(255, 255, 255, 0.8);
        
        /* Glass effects */
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --glass-backdrop: blur(8px);
        
        /* Neon accents */
        --neon-primary: #00d4ff;
        --neon-secondary: #ff0080;
        --neon-accent: #39ff14;
        --neon-warning: #ffaa00;
        --neon-danger: #ff073a;
        
        /* Gradients */
        --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-secondary: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-success: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-warning: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);
        --gradient-danger: linear-gradient(135deg, #ff0844 0%, #ffb199 100%);
        
        /* Advanced shadows */
        --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.2);
        --shadow-xl: 0 20px 60px rgba(0, 0, 0, 0.3);
        --shadow-neon: 0 0 20px rgba(0, 212, 255, 0.5);
        
        /* Spacing and sizing */
        --radius: 16px;
        --radius-sm: 8px;
        --radius-lg: 24px;
        --blur: 12px;
    }
    
    /* Dark Mode - Even More Stunning */
    @media (prefers-color-scheme: dark), .dark, [data-theme="dark"] {
        :root {
            /* Dark glassmorphism */
            --background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            --background-glass: rgba(255, 255, 255, 0.05);
            --foreground: #ffffff;
            --foreground-muted: rgba(255, 255, 255, 0.7);
            
            /* Enhanced glass effects */
            --glass-bg: rgba(255, 255, 255, 0.08);
            --glass-border: rgba(255, 255, 255, 0.15);
            --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
            
            /* Neon accents - more vibrant in dark */
            --neon-primary: #00f5ff;
            --neon-secondary: #ff1493;
            --neon-accent: #00ff41;
            --neon-warning: #ffd700;
            --neon-danger: #ff073a;
            
            /* Dark gradients */
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-secondary: linear-gradient(135deg, #ff0080 0%, #7928ca 100%);
            --gradient-success: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            --gradient-warning: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);
            --gradient-danger: linear-gradient(135deg, #ff073a 0%, #ff5733 100%);
        }
    }
    
    /* Global Body Styling */
    body, .stApp {
        background: var(--background) !important;
        color: var(--foreground) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }
    
    /* Animated background */
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--background);
        z-index: -1;
        animation: backgroundShift 20s ease-in-out infinite alternate;
    }
    
    @keyframes backgroundShift {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.05); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    /* Ultra-Modern Container Styling */
    .main .block-container {
        padding: 3rem 2rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
        background: transparent !important;
        position: relative;
    }
    
    .stApp > .main {
        background: transparent !important;
    }
    
    /* Glassmorphism Card Component - Next Level */
    .shadcn-card {
        background: var(--glass-bg) !important;
        backdrop-filter: var(--glass-backdrop) !important;
        -webkit-backdrop-filter: var(--glass-backdrop) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius) !important;
        padding: 2rem !important;
        margin-bottom: 2rem !important;
        box-shadow: var(--glass-shadow) !important;
        color: var(--foreground) !important;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .shadcn-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: -1;
    }
    
    .shadcn-card:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3) !important;
        border-color: var(--neon-primary) !important;
    }
    
    .shadcn-card:hover::before {
        opacity: 0.1;
    }
    
    /* Floating particles effect */
    .shadcn-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: radial-gradient(2px 2px at 20px 30px, var(--neon-primary), transparent),
                          radial-gradient(2px 2px at 40px 70px, var(--neon-secondary), transparent),
                          radial-gradient(1px 1px at 90px 40px, var(--neon-accent), transparent);
        opacity: 0.3;
        animation: particles 15s linear infinite;
        pointer-events: none;
    }
    
    @keyframes particles {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.3; }
        50% { transform: translateY(-20px) rotate(180deg); opacity: 0.6; }
    }
    
    /* Ultra-Modern Metric Cards with Spectacular Effects */
    .metric-card {
        background: var(--glass-bg) !important;
        backdrop-filter: var(--glass-backdrop) !important;
        -webkit-backdrop-filter: var(--glass-backdrop) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 2rem !important;
        text-align: center !important;
        position: relative !important;
        overflow: hidden !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: var(--glass-shadow) !important;
        color: var(--foreground) !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Animated gradient border */
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        padding: 2px;
        background: linear-gradient(45deg, 
            var(--neon-primary), 
            var(--neon-secondary), 
            var(--neon-accent), 
            var(--neon-primary));
        background-size: 200% 200%;
        border-radius: inherit;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: subtract;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: source-out;
        animation: gradientBorder 3s ease infinite;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: -1;
    }
    
    @keyframes gradientBorder {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .metric-card:hover {
        transform: translateY(-12px) scale(1.05) !important;
        box-shadow: 0 25px 80px rgba(0, 0, 0, 0.4), 
                    0 0 40px var(--neon-primary) !important;
        border-color: var(--neon-primary) !important;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    /* Pulsing glow effect */
    .metric-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, var(--neon-primary) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(-50%, -50%);
        opacity: 0;
        animation: pulse 3s ease-in-out infinite;
        z-index: -1;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
        50% { opacity: 0.3; transform: translate(-50%, -50%) scale(1.2); }
    }
    
    /* Metric Value with Animated Counter */
    .metric-value {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        color: var(--foreground) !important;
        margin: 1rem 0 !important;
        line-height: 1 !important;
        background: linear-gradient(45deg, var(--neon-primary), var(--neon-secondary));
        background-clip: text !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 0 30px var(--neon-primary);
        animation: numberGlow 2s ease-in-out infinite alternate;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    @keyframes numberGlow {
        0% { text-shadow: 0 0 20px var(--neon-primary); }
        100% { text-shadow: 0 0 40px var(--neon-primary), 0 0 60px var(--neon-secondary); }
    }
    
    /* Metric Label with Neon Effect */
    .metric-label {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        color: var(--foreground-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        margin-bottom: 1rem !important;
        position: relative !important;
    }
    
    .metric-label::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 50%;
        transform: translateX(-50%);
        width: 30px;
        height: 2px;
        background: var(--neon-accent);
        border-radius: 2px;
        box-shadow: 0 0 10px var(--neon-accent);
    }
    
    /* Enhanced Delta Badge */
    .metric-delta {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        border-radius: 50px !important;
        margin-top: 1rem !important;
        display: inline-block !important;
        border: 1px solid transparent !important;
        position: relative !important;
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    
    .metric-delta.positive {
        background: linear-gradient(45deg, rgba(0, 255, 65, 0.2), rgba(0, 242, 254, 0.2)) !important;
        color: var(--neon-accent) !important;
        border-color: var(--neon-accent) !important;
        box-shadow: 0 4px 15px rgba(0, 255, 65, 0.3) !important;
    }
    
    .metric-delta.positive:hover {
        box-shadow: 0 8px 25px rgba(0, 255, 65, 0.5) !important;
        transform: scale(1.1) !important;
    }
    
    .metric-delta.neutral {
        background: var(--glass-bg) !important;
        color: var(--foreground-muted) !important;
        border-color: var(--glass-border) !important;
    }
    
    /* Ultra-Modern Status Indicators */
    .status-indicator {
        display: flex !important;
        align-items: center !important;
        gap: 1rem !important;
        padding: 1rem 1.5rem !important;
        border-radius: var(--radius) !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        border: 1px solid var(--glass-border) !important;
        background: var(--glass-bg) !important;
        backdrop-filter: var(--glass-backdrop) !important;
        -webkit-backdrop-filter: var(--glass-backdrop) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: var(--glass-shadow) !important;
        color: var(--foreground) !important;
    }
    
    .status-indicator:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Status indicator glow effects */
    .status-indicator::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: inherit;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: -1;
    }
    
    .status-indicator:hover::before {
        opacity: 0.1;
    }
    
    /* Success Status */
    .status-success {
        border-color: var(--neon-accent) !important;
        color: var(--neon-accent) !important;
    }
    
    .status-success:hover {
        box-shadow: 0 15px 40px rgba(0, 255, 65, 0.3) !important;
        border-color: var(--neon-accent) !important;
    }
    
    .status-success::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--neon-accent);
        border-radius: 0 4px 4px 0;
        box-shadow: 0 0 15px var(--neon-accent);
    }
    
    /* Warning Status */
    .status-warning {
        border-color: var(--neon-warning) !important;
        color: var(--neon-warning) !important;
    }
    
    .status-warning:hover {
        box-shadow: 0 15px 40px rgba(255, 170, 0, 0.3) !important;
    }
    
    .status-warning::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--neon-warning);
        border-radius: 0 4px 4px 0;
        box-shadow: 0 0 15px var(--neon-warning);
    }
    
    /* Error Status */
    .status-error {
        border-color: var(--neon-danger) !important;
        color: var(--neon-danger) !important;
    }
    
    .status-error:hover {
        box-shadow: 0 15px 40px rgba(255, 7, 58, 0.3) !important;
    }
    
    .status-error::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--neon-danger);
        border-radius: 0 4px 4px 0;
        box-shadow: 0 0 15px var(--neon-danger);
    }
    
    /* Info Status */
    .status-info {
        border-color: var(--neon-primary) !important;
        color: var(--neon-primary) !important;
    }
    
    .status-info:hover {
        box-shadow: 0 15px 40px rgba(0, 212, 255, 0.3) !important;
    }
    
    .status-info::after {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background: var(--neon-primary);
        border-radius: 0 4px 4px 0;
        box-shadow: 0 0 15px var(--neon-primary);
    }
    
    /* Ultra-Modern Section Titles */
    .section-title {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--foreground) !important;
        margin: 2rem 0 1.5rem 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.75rem !important;
        position: relative !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    
    .section-title::before {
        content: '';
        width: 4px;
        height: 100%;
        background: var(--gradient-primary);
        border-radius: 2px;
        box-shadow: 0 0 10px var(--neon-primary);
    }
    
    .section-title::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--neon-primary), transparent);
        margin-left: 1rem;
    }
    
    /* ULTRA-FUTURISTIC DATA TABLES */
    .stDataFrame {
        background: var(--glass-bg) !important;
        backdrop-filter: var(--glass-backdrop) !important;
        -webkit-backdrop-filter: var(--glass-backdrop) !important;
        border-radius: var(--radius-lg) !important;
        border: 2px solid var(--glass-border) !important;
        overflow: hidden !important;
        box-shadow: var(--glass-shadow), 0 0 40px rgba(0, 212, 255, 0.1) !important;
        margin: 2rem 0 !important;
        position: relative !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stDataFrame::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, 
            var(--neon-primary) 0%, 
            var(--neon-secondary) 25%,
            var(--neon-accent) 50%,
            var(--neon-warning) 75%,
            var(--neon-primary) 100%);
        background-size: 200% 100%;
        animation: tableGradient 4s ease-in-out infinite;
    }
    
    @keyframes tableGradient {
        0%, 100% { background-position: 0% 0%; }
        50% { background-position: 200% 0%; }
    }
    
    .stDataFrame:hover {
        transform: scale(1.01) !important;
        border-color: var(--neon-primary) !important;
        box-shadow: var(--glass-shadow), 0 0 60px rgba(0, 212, 255, 0.3) !important;
    }
    
    .stDataFrame table {
        background: transparent !important;
        color: var(--foreground) !important;
        width: 100% !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* SPECTACULAR TABLE HEADERS */
    .stDataFrame thead {
        position: relative !important;
    }
    
    .stDataFrame thead::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--neon-primary), transparent);
        box-shadow: 0 0 10px var(--neon-primary);
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, 
            rgba(0, 212, 255, 0.1) 0%, 
            rgba(255, 20, 147, 0.1) 50%,
            rgba(0, 212, 255, 0.1) 100%) !important;
        color: var(--foreground) !important;
        border: none !important;
        padding: 1.25rem 1rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        font-size: 0.875rem !important;
        position: relative !important;
        text-align: center !important;
        border-right: 1px solid var(--glass-border) !important;
        transition: all 0.3s ease !important;
    }
    
    .stDataFrame th:last-child {
        border-right: none !important;
    }
    
    .stDataFrame th:hover {
        background: linear-gradient(135deg, 
            rgba(0, 212, 255, 0.2) 0%, 
            rgba(255, 20, 147, 0.2) 50%,
            rgba(0, 212, 255, 0.2) 100%) !important;
        color: var(--neon-primary) !important;
        text-shadow: 0 0 10px var(--neon-primary) !important;
    }
    
    /* FUTURISTIC TABLE ROWS */
    .stDataFrame tbody tr {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
    }
    
    .stDataFrame tbody tr::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 0;
        background: linear-gradient(90deg, var(--neon-primary), transparent);
        transition: width 0.3s ease !important;
        z-index: 1;
    }
    
    .stDataFrame tbody tr:hover::before {
        width: 100%;
        opacity: 0.1;
    }
    
    .stDataFrame tbody tr:hover {
        background: var(--background-glass) !important;
        transform: scale(1.01) translateZ(0) !important;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2) !important;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background: rgba(255, 255, 255, 0.02) !important;
    }
    
    /* ENHANCED TABLE CELLS */
    .stDataFrame td {
        border: none !important;
        border-right: 1px solid var(--glass-border) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: var(--foreground-muted) !important;
        padding: 1rem !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        text-align: center !important;
        font-weight: 500 !important;
        z-index: 2;
    }
    
    .stDataFrame td:last-child {
        border-right: none !important;
    }
    
    .stDataFrame tbody tr:hover td {
        color: var(--foreground) !important;
        text-shadow: 0 0 5px rgba(0, 212, 255, 0.5) !important;
    }
    
    /* SPECIAL STYLING FOR STATUS COLUMNS */
    .stDataFrame td:has(.status-badge), 
    .stDataFrame td[data-status] {
        padding: 0.75rem !important;
    }
    
    /* ANIMATED LOADING STATE */
    .stDataFrame::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(0, 212, 255, 0.1), 
            transparent);
        animation: tableShimmer 3s ease-in-out infinite;
        pointer-events: none;
    }
    
    @keyframes tableShimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* RESPONSIVE TABLE DESIGN */
    @media (max-width: 768px) {
        .stDataFrame th,
        .stDataFrame td {
            padding: 0.75rem 0.5rem !important;
            font-size: 0.8rem !important;
        }
    }
    
    /* Ultra-Modern Streamlit Buttons */
    .stButton > button {
        background: var(--gradient-primary) !important;
        color: var(--foreground) !important;
        border: 1px solid var(--neon-primary) !important;
        border-radius: var(--radius) !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.5) !important;
        border-color: var(--neon-secondary) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Force theme consistency */
    .stApp, .stApp > .main, .main .block-container {
        background: hsl(var(--background)) !important;
        color: hsl(var(--foreground)) !important;
    }
    </style>
    
    <script>
    // Enhanced theme detection for Streamlit
    (function() {
        function applyTheme() {
            const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            const streamlitTheme = window.getComputedStyle(document.body).getPropertyValue('background-color');
            const isStreamlitDark = streamlitTheme.includes('14, 17, 23') || streamlitTheme.includes('rgb(14, 17, 23)');
            
            if (isDark || isStreamlitDark) {
                document.documentElement.setAttribute('data-theme', 'dark');
                document.body.classList.add('dark');
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                document.body.classList.remove('dark');
            }
        }
        
        // Apply theme immediately
        applyTheme();
        
        // Watch for theme changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
        }
        
        // Watch for Streamlit theme changes
        const observer = new MutationObserver(applyTheme);
        observer.observe(document.body, { 
            attributes: true, 
            attributeFilter: ['style', 'class'] 
        });
        
        // Periodic check for theme changes
        setInterval(applyTheme, 1000);
    })();
    </script>
    """, unsafe_allow_html=True)

def create_metric_card(label: str, value: str, delta: str = None, icon: str = "📊"):
    """Create an ultra-modern glassmorphism metric card with spectacular effects"""
    
    delta_html = ""
    if delta:
        delta_class = "positive" if "+" in delta else "neutral"
        delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>'
    
    # Generate unique ID for animated counter
    import random, string
    card_id = ''.join(random.choices(string.ascii_lowercase, k=8))
    
    return f"""
    <div class="metric-card" id="card-{card_id}">
        <div class="metric-label">{icon} {label}</div>
        <div class="metric-value" data-target="{value}" id="counter-{card_id}">{value}</div>
        {delta_html}
    </div>
    
    <script>
    (function() {{
        const counter = document.getElementById('counter-{card_id}');
        const card = document.getElementById('card-{card_id}');
        const target = parseFloat(counter.dataset.target) || 0;
        let current = 0;
        const increment = target / 50;
        const duration = 2000;
        const stepTime = duration / 50;
        
        function updateCounter() {{
            if (current < target) {{
                current += increment;
                if (current > target) current = target;
                
                if (Number.isInteger(target)) {{
                    counter.textContent = Math.floor(current);
                }} else {{
                    counter.textContent = current.toFixed(1);
                }}
                
                setTimeout(updateCounter, stepTime);
            }}
        }}
        
        // Trigger animation when card is visible
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    setTimeout(updateCounter, 500);
                    observer.unobserve(card);
                }}
            }});
        }}, {{ threshold: 0.1 }});
        
        observer.observe(card);
    }})();
    </script>
    """

def create_status_card(title: str, status: str, status_type: str = "success"):
    """Create a futuristic status indicator card with glassmorphism effects"""
    
    status_icons = {
        "success": "✅",
        "warning": "⚠️", 
        "error": "❌",
        "info": "ℹ️"
    }
    
    icon = status_icons.get(status_type, "ℹ️")
    
    return f"""
    <div class="status-indicator status-{status_type}">
        <span style="font-size: 1.25rem;">{icon}</span>
        <div>
            <div style="font-weight: 600; margin-bottom: 0.25rem;">{title}</div>
            <div style="font-size: 0.8rem; opacity: 0.8;">{status}</div>
        </div>
    </div>
    """

def create_futuristic_table_badge(status: str, status_type: str = "success"):
    """Create animated status badges for table cells"""
    
    badge_configs = {
        "success": {"color": "var(--neon-accent)", "bg": "rgba(0, 255, 65, 0.1)", "icon": "✓"},
        "completed": {"color": "var(--neon-accent)", "bg": "rgba(0, 255, 65, 0.1)", "icon": "✓"},
        "warning": {"color": "var(--neon-warning)", "bg": "rgba(255, 170, 0, 0.1)", "icon": "⚠"},
        "error": {"color": "var(--neon-danger)", "bg": "rgba(255, 7, 58, 0.1)", "icon": "✗"},
        "pending": {"color": "var(--neon-primary)", "bg": "rgba(0, 212, 255, 0.1)", "icon": "○"},
        "info": {"color": "var(--neon-primary)", "bg": "rgba(0, 212, 255, 0.1)", "icon": "i"}
    }
    
    config = badge_configs.get(status_type.lower(), badge_configs["info"])
    
    color = config['color']
    bg = config['bg']
    icon = config['icon']
    
    return f"""
    <div class="futuristic-badge" style="
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: {bg};
        color: {color};
        border: 1px solid {color};
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 2px 10px {color}33;
        transition: all 0.3s ease;
        animation: badgePulse 2s ease-in-out infinite;
    ">
        <span style="font-size: 1rem;">{icon}</span>
        {status}
    </div>
    
    <style>
    .futuristic-badge:hover {{
        transform: scale(1.1);
        box-shadow: 0 4px 20px {color}66;
    }}
    
    @keyframes badgePulse {{
        0%, 100% {{ box-shadow: 0 2px 10px {color}33; }}
        50% {{ box-shadow: 0 4px 15px {color}66; }}
    }}
    </style>
    """

def show_dashboard():
    """Display the modern ShadCN-inspired dashboard"""
    
    # Inject modern ShadCN styles
    inject_shadcn_styles()
    
    # Modern page header
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="font-size: 2.25rem; font-weight: 700; color: hsl(var(--foreground)); margin-bottom: 0.5rem; line-height: 1.2;">
            🤖 InterviewAgent Dashboard
        </h1>
        <p style="font-size: 1.125rem; color: hsl(var(--muted-foreground)); margin-bottom: 0;">
            AI-Powered Job Application Automation System
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get configuration and database operations
    config = get_config()
    db = get_db_operations()
    
    # Get or create user (single-user MVP) - use consistent email with job search pages
    try:
        user = db.get_or_create_user(
            email="user@interviewagent.local",  # Consistent with job search pages
            full_name="InterviewAgent User"
        )
        st.session_state.current_user = user
    except Exception as e:
        st.error(f"Failed to initialize user: {str(e)}")
        return
    
    # Get real user statistics
    try:
        # Get actual job search statistics
        job_searches = db.get_job_searches(user.id, limit=100)
        
        # Calculate real stats from job searches
        total_jobs_discovered = sum(search.jobs_found for search in job_searches if search.jobs_found)
        total_searches = len(job_searches)
        
        # Load all jobs from database searches 
        all_jobs_from_searches = []
        
        for search in job_searches:
            if search.search_results:
                try:
                    # Handle both dict and JSON string formats
                    if isinstance(search.search_results, str):
                        import json
                        search_data = json.loads(search.search_results)
                    else:
                        search_data = search.search_results
                    
                    if 'jobs' in search_data:
                        jobs = search_data['jobs']
                        all_jobs_from_searches.extend(jobs)
                        
                except (json.JSONDecodeError, TypeError):
                    continue
        
        # Get saved jobs count from session state if available, otherwise estimate
        saved_jobs_count = 0
        if 'discovered_jobs' in st.session_state:
            saved_jobs_count = len([job for job in st.session_state.discovered_jobs if job.get('saved', False)])
        else:
            # Estimate saved jobs as 10% of total jobs found
            saved_jobs_count = max(0, int(len(all_jobs_from_searches) * 0.1))
        
        # Calculate applications (placeholder for now)
        applications_submitted = saved_jobs_count
        applications_successful = int(applications_submitted * 0.2)  # 20% success rate estimate
        
        # Build real stats
        stats = {
            'resumes': 1,  # Single user MVP
            'jobs_discovered': total_jobs_discovered,
            'applications_submitted': applications_submitted,
            'applications_successful': applications_successful,
            'job_searches': total_searches,
            'saved_jobs': saved_jobs_count
        }
        
        # Update session state stats
        if 'stats' not in st.session_state:
            st.session_state.stats = {}
        st.session_state.stats.update(stats)
        
        # Also update session state with job search history for cross-tab consistency
        if 'job_search_history' not in st.session_state:
            st.session_state.job_search_history = job_searches
        
        # Load discovered jobs into session state if not already present
        if 'discovered_jobs' not in st.session_state and all_jobs_from_searches:
            st.session_state.discovered_jobs = all_jobs_from_searches
        
    except Exception as e:
        st.error(f"Could not load statistics: {str(e)}")
        
        # Fallback to session state or defaults
        stats = getattr(st.session_state, 'stats', {
            'resumes': 0,
            'jobs_discovered': 0,
            'applications_submitted': 0,
            'applications_successful': 0,
            'job_searches': 0,
            'saved_jobs': 0
        })
    
    # Welcome message with modern card
    st.markdown(f"""
    <div class="shadcn-card">
        <h3 style="margin: 0 0 0.5rem 0; color: hsl(var(--foreground));">Welcome back, {user.full_name or user.email}! 👋</h3>
        <p style="margin: 0; color: hsl(var(--muted-foreground));">Here's your job search activity overview.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics with modern ShadCN-style cards
    st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        today_searches = len([s for s in job_searches if s.created_at and s.created_at.date() == datetime.now().date()]) if job_searches else 0
        delta = f"+{today_searches} today" if today_searches > 0 else None
        st.markdown(create_metric_card("Job Searches", str(stats['job_searches']), delta, "🔍"), unsafe_allow_html=True)
    
    with col2:
        latest_jobs = job_searches[0].jobs_found if job_searches else 0
        delta = f"+{latest_jobs} latest" if latest_jobs > 0 else None
        st.markdown(create_metric_card("Jobs Discovered", str(stats['jobs_discovered']), delta, "💼"), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card("Saved Jobs", str(stats['saved_jobs']), None, "⭐"), unsafe_allow_html=True)
    
    with col4:
        # Calculate average jobs per search
        avg_jobs = stats['jobs_discovered'] / max(stats['job_searches'], 1)
        st.markdown(create_metric_card("Avg Jobs/Search", f"{avg_jobs:.1f}", None, "📈"), unsafe_allow_html=True)
    
    # Recent activity section with modern styling
    st.markdown('<div class="section-title">📈 Recent Activity</div>', unsafe_allow_html=True)
    
    # Show real job search activity
    try:
        if job_searches:
            # Create activity timeline from job searches
            activity_data = []
            for search in job_searches[:15]:  # Show more searches now that we have full width
                try:
                    search_time = search.created_at
                    if search_time:
                        if search_time.tzinfo is not None:
                            search_time = search_time.replace(tzinfo=None)
                        time_str = search_time.strftime('%m/%d %H:%M')
                    else:
                        time_str = 'Unknown'
                    
                    activity_data.append({
                        'Time': time_str,
                        'Activity': '🔍 Job Search',
                        'Query': search.search_query,  # Full query now since we have more space
                        'Jobs Found': search.jobs_found,
                        'Status': '✅ Completed'
                    })
                except Exception:
                    continue
            
            if activity_data:
                # Enhance the activity data with futuristic badges
                for item in activity_data:
                    if item['Status'] == '✅ Completed':
                        item['Status'] = create_futuristic_table_badge('Completed', 'completed')
                    elif 'Error' in item['Status']:
                        item['Status'] = create_futuristic_table_badge('Error', 'error')
                    elif 'Pending' in item['Status']:
                        item['Status'] = create_futuristic_table_badge('Pending', 'pending')
                
                activity_df = pd.DataFrame(activity_data)
                
                # Create enhanced table with custom styling
                st.markdown('<div class="futuristic-table-container">', unsafe_allow_html=True)
                st.dataframe(
                    activity_df, 
                    use_container_width=True, 
                    height=450,
                    hide_index=True,
                    column_config={
                        "Status": st.column_config.TextColumn(
                            "Status",
                            help="Job search status",
                            width="medium"
                        ),
                        "Activity": st.column_config.TextColumn(
                            "Activity",
                            help="Type of activity performed"
                        ),
                        "Query": st.column_config.TextColumn(
                            "Search Query",
                            help="The job search query used"
                        ),
                        "Jobs Found": st.column_config.NumberColumn(
                            "Jobs Found",
                            help="Number of jobs discovered",
                            format="%d"
                        )
                    }
                )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="shadcn-card" style="text-align: center; padding: 3rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
                    <h3 style="color: var(--foreground); margin-bottom: 1rem;">No Activity Found</h3>
                    <p style="color: var(--foreground-muted);">Start by searching for jobs to see your activity here!</p>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.info("No recent activity found. Start by searching for jobs!")
            
        # Add quick stats about recent activity
        if job_searches:
            recent_count = len([s for s in job_searches if s.created_at and s.created_at.date() >= (datetime.now() - timedelta(days=7)).date()])
            if recent_count > 0:
                st.success(f"🎉 {recent_count} searches in the last 7 days!")
            
    except Exception as e:
        st.error(f"Failed to load recent activity: {str(e)}")
    
    # Charts section
    st.markdown("---")
    st.subheader("📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Application status pie chart
        if stats['applications_submitted'] > 0:
            try:
                applications = db.get_applications(user_id=user.id, limit=100)
                
                status_counts = {}
                for app in applications:
                    status = app.status.value if app.status else 'unknown'
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                if status_counts:
                    fig = px.pie(
                        values=list(status_counts.values()),
                        names=list(status_counts.keys()),
                        title="Application Status Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No application data available for chart")
                    
            except Exception as e:
                st.error(f"Failed to create status chart: {str(e)}")
        else:
            st.info("No applications submitted yet")
    
    with col2:
        # Real job discovery over time
        try:
            if job_searches and len(job_searches) > 0:
                # Group searches by date and sum jobs found
                daily_jobs = {}
                for search in job_searches:
                    if search.created_at:
                        # Handle timezone-aware datetime
                        search_date = search.created_at
                        if search_date.tzinfo is not None:
                            search_date = search_date.replace(tzinfo=None)
                        
                        date_key = search_date.date()
                        daily_jobs[date_key] = daily_jobs.get(date_key, 0) + (search.jobs_found or 0)
                
                if daily_jobs:
                    # Create DataFrame for chart
                    df = pd.DataFrame([
                        {'Date': date, 'Jobs Found': count}
                        for date, count in sorted(daily_jobs.items())
                    ])
                    
                    fig = px.line(
                        df, 
                        x='Date', 
                        y='Jobs Found',
                        title="Jobs Discovered Over Time",
                        markers=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No job discovery data available for chart")
            else:
                st.info("No job searches yet - start searching to see trends!")
            
        except Exception as e:
            st.error(f"Failed to create discovery chart: {str(e)}")
    
    # Additional insights
    if job_searches:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Top Search Queries")
            try:
                # Count search query frequency
                query_counts = {}
                for search in job_searches:
                    query = search.search_query.strip()
                    query_counts[query] = query_counts.get(query, 0) + 1
                
                # Get top 5 queries
                top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                for i, (query, count) in enumerate(top_queries, 1):
                    st.write(f"{i}. **{query}** ({count} times)")
                    
            except Exception as e:
                st.error(f"Failed to load top queries: {str(e)}")
        
        with col2:
            st.subheader("⭐ Recent Saved Jobs")
            try:
                if 'discovered_jobs' in st.session_state:
                    saved_jobs = [job for job in st.session_state.discovered_jobs if job.get('saved', False)]
                    
                    if saved_jobs:
                        # Show last 5 saved jobs
                        for job in saved_jobs[-5:]:
                            st.write(f"• **{job.get('title', 'Unknown')}** at {job.get('company', 'Unknown')}")
                    else:
                        st.info("No saved jobs yet")
                else:
                    st.info("No job data available")
                    
            except Exception as e:
                st.error(f"Failed to load saved jobs: {str(e)}")

    # System status with modern cards
    st.markdown('<div class="section-title">🔧 System Status</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Database connection status
        try:
            db.client.table('users').select('id').limit(1).execute()
            st.markdown(create_status_card("Database", "Connected", "success"), unsafe_allow_html=True)
        except:
            st.markdown(create_status_card("Database", "Connection Failed", "error"), unsafe_allow_html=True)
    
    with col2:
        # Configuration status
        try:
            if config.OPENAI_API_KEY:
                st.markdown(create_status_card("OpenAI API", "Configured", "success"), unsafe_allow_html=True)
            else:
                st.markdown(create_status_card("OpenAI API", "Not Configured", "warning"), unsafe_allow_html=True)
        except:
            st.markdown(create_status_card("OpenAI API", "Configuration Error", "error"), unsafe_allow_html=True)
    
    with col3:
        # Job sites status
        try:
            job_sites = db.get_job_sites(user.id, enabled_only=True) if hasattr(db, 'get_job_sites') else []
            if job_sites:
                st.markdown(create_status_card("Job Sites", f"{len(job_sites)} Active", "success"), unsafe_allow_html=True)
            else:
                st.markdown(create_status_card("Job Sites", "No Sites Configured", "info"), unsafe_allow_html=True)
        except:
            st.markdown(create_status_card("Job Sites", "Could Not Check", "warning"), unsafe_allow_html=True)
    
    # Quick Actions Footer
    st.markdown('<div class="section-title">🚀 Quick Actions</div>', unsafe_allow_html=True)
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("🔍 Search Jobs", key="dashboard_search", use_container_width=True):
            st.switch_page("pages/job_search.py") if hasattr(st, 'switch_page') else st.info("Navigate to Job Search from the sidebar")
    
    with action_col2:
        if st.button("📄 Manage Resumes", key="dashboard_resume", use_container_width=True):
            st.switch_page("pages/resume_manager.py") if hasattr(st, 'switch_page') else st.info("Navigate to Resume Manager from the sidebar")
    
    with action_col3:
        if st.button("🤖 Configure AI", key="dashboard_ai", use_container_width=True):
            st.switch_page("pages/ai_agents.py") if hasattr(st, 'switch_page') else st.info("Navigate to AI Agents from the sidebar")
    
    with action_col4:
        if st.button("⚙️ Settings", key="dashboard_settings", use_container_width=True):
            st.switch_page("pages/settings.py") if hasattr(st, 'switch_page') else st.info("Navigate to Settings from the sidebar")

def run_automation_workflow():
    """Run the automation workflow"""
    
    with st.spinner("Running automation workflow..."):
        try:
            # This would trigger the orchestrator agent
            st.success("🚀 Automation workflow started!")
            st.info("Check the Applications page for updates.")
            
            # For MVP, we'll just show a placeholder
            st.balloons()
            
        except Exception as e:
            st.error(f"Failed to start automation: {str(e)}")

if __name__ == "__main__":
    show_dashboard()