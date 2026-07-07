import pandas as pd
import streamlit as st
import datetime
import numpy as np
import time
import json
import streamlit.components.v1 as components  # Required for stable live automation

# ==========================================
# PHASE 1: INITIAL CONFIGURATION & SUITE SETUP
# ==========================================
st.set_page_config(
    page_title="INGEK - Universal Fleet Control", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Scannability and Flight Deck Ergonomics
st.markdown("""
    <style>
    html { scroll-behavior: smooth; }
    .block-container { padding-top: 3.5rem; padding-bottom: 2rem; }
    
    /* Modify standard browser scrollbar to be thick and touch/click responsive */
    ::-webkit-scrollbar { width: 14px; height: 14px; }
    ::-webkit-scrollbar-track { background: #111217; border-radius: 4px; }
    ::-webkit-scrollbar-thumb { background: #3b3f54; border-radius: 8px; border: 3px solid #111217; }
    ::-webkit-scrollbar-thumb:hover { background: #ff4b4b; }
    .stDeployButton { display:none; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# PHASE 2: PERSISTENT STATE INITIALIZATION
# ==========================================
if 'sudah_dianalisa' not in st.session_state:
    st.session_state.sudah_dianalisa = False
if 'hasil_analisa' not in st.session_state:
    st.session_state.hasil_analisa = ""
if 'checklist' not in st.session_state:
    st.session_state.checklist = []
if 'status_warna' not in st.session_state:
    st.session_state.status_warna = "normal"
if 'local_buffer' not in st.session_state:
    st.session_state.local_buffer = []
if 'komponen' not in st.session_state:
    st.session_state.komponen = "ALL APPLIED SYSTEMS"
if 'status' not in st.session_state:
    st.session_state.status = "NOMINAL & OPERATIONAL"

# Ground Core initial base telemetry database (Padang Time Zone Sync: UTC + 7 Hours)
if 'telemetry_history' not in st.session_state:
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    st.session_state.telemetry_history = pd.DataFrame([
        {
            'Date': (now - datetime.timedelta(seconds=10)).strftime("%d/%m/%Y"),
            'Timestamp': (now - datetime.timedelta(seconds=10)).strftime("%H:%M:%S"),
            'Airspeed (Knots)': 450, 'N1 Fan Speed (%)': 92, 'Hydraulic Pressure (PSI)': 3000, 'FGT Thermal (°C)': 620, 'Status': 'NORMAL'
        },
        {
            'Date': (now - datetime.timedelta(seconds=5)).strftime("%d/%m/%Y"),
            'Timestamp': (now - datetime.timedelta(seconds=5)).strftime("%H:%M:%S"),
            'Airspeed (Knots)': 452, 'N1 Fan Speed (%)': 93, 'Hydraulic Pressure (PSI)': 2995, 'FGT Thermal (°C)': 625, 'Status': 'NORMAL'
        }
    ])

# ==========================================
# PHASE 3: BACKGROUND DATA LOGIC & PIPELINE PROCESSOR
# ==========================================
def analisa_spesifik(kondisi_simulasi, model_pesawat, reg_pesawat, waktu_str, tanggal_str):
    if kondisi_simulasi == "Normal Flight Profile":
        status_warna = "normal"
        komponen = "ALL APPLIED SYSTEMS"
        status = "NOMINAL & OPERATIONAL"
        teks = (f"🟢 INGEK SAFE REPORT: {komponen}\n"
                f"Fleet: {model_pesawat} [{reg_pesawat}]\n"
                f"Transmission Time: {tanggal_str} | {waktu_str}\n"
                f"Status: {status}\n\n"
                f"✨ All aircraft instruments are transmitting raw telemetry within safe limits.\n"
                f"No structural distortion detected in the pitot-static system, core engine thermal sensors, or hydraulic channels.")
        cek = ["Maintain current flight envelope parameters", "Continue periodic ground core station telemetry monitoring"]
        
    elif kondisi_simulasi == "Pitot-Static Failure (Speed Freeze)":
        status_warna = "anomali"
        komponen = "PITOT-STATIC SYSTEM"
        status = "ANOMALY DATA FREEZE DETECTED"
        teks = (f"🛠️ INGEK DIAGNOSTICS: {komponen}\n"
                f"Fleet: {model_pesawat} [{reg_pesawat}]\n"
                f"Transmission Time: {tanggal_str} | {waktu_str}\n"
                f"Status: {status}\n\n"
                f"🚨 Critical Anomaly: Sensors recorded a sudden freeze/drop in cruise airspeed stream.\n"
                f"INGEK mathematical data reconstruction models indicate significant instrumentation deviation compared to backup parameters.")
        cek = ["Instruct flight crew to toggle the Pitot Heat switch to ON", 
               "Utilize manual pitch and thrust references immediately (Unreliable Airspeed Procedure)"]
        
    elif kondisi_simulasi == "Engine Overheat Anomaly":
        status_warna = "anomali"
        komponen = "PROPULSION (CORE ENGINE)"
        status = "THERMAL OVERHEAT CRITICAL"
        teks = (f"🔥 INGEK DIAGNOSTICS: {komponen}\n"
                f"Fleet: {model_pesawat} [{reg_pesawat}]\n"
                f"Transmission Time: {tanggal_str} | {waktu_str}\n"
                f"Status: {status}\n\n"
                f"🚨 Critical Anomaly: Severe Exhaust Gas Temperature (FGT) thermal spike detected beyond structural limits.\n"
                f"High degradation risk of internal high-pressure turbine blades.")
        cek = ["Retard the affected engine Thrust Lever to the Idle position", 
               "Monitor Fuel Flow and core N1 Fan Speed parameters intensively"]
        
    else:
        status_warna = "anomali"
        komponen = "HYDRAULIC ACTUATOR SYSTEM"
        status = "PRESSURE CRITICAL DROP"
        teks = (f"⚠️ INGEK DIAGNOSTICS: {komponen}\n"
                f"Fleet: {model_pesawat} [{reg_pesawat}]\n"
                f"Transmission Time: {tanggal_str} | {waktu_str}\n"
                f"Status: {status}\n\n"
                f"🚨 Critical Anomaly: Main hydraulic utility pressure dropped severely below 1000 PSI.\n"
                f"Imminent risk of losing flight control surface actuator authority.")
        cek = ["Activate backup auxiliary/electric hydraulic pumps immediately", 
               "Crosscheck flight deck hydraulic reservoir level parameters (Fluid Quantity Logging)"]
               
    return komponen, status, teks, cek, status_warna

# Synchronize current Padang local timezone clock (WIB: UTC + 7 Hours)
waktu_sekarang = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
tgl_sekarang_str = waktu_sekarang.strftime("%d/%m/%Y")
waktu_aktual_komputer = waktu_sekarang.strftime("%H:%M:%S")

# ==========================================
# PHASE 4: MISSION CONTROL SIDEBAR INTERFACE
# ==========================================
st.sidebar.title("🛸 Mission Control Center")
st.sidebar.subheader("Team Cingkariak | AMD Hackathon")
st.sidebar.markdown("---")

# NEW FEATURE: Core Operation Mode Selector
operation_mode = st.sidebar.radio(
    "Core Operation Mode:",
    ("🟢 LIVE TELEMETRY STREAM", "📂 HISTORICAL DATA RETRIEVAL"),
    help="Switch between live satellite streaming or pulling recorded parameters via time offset."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ✈️ Fleet Management")
model = st.sidebar.selectbox("Aircraft Model:", ["Boeing 737-800", "Airbus A320neo"])
ekor = st.sidebar.text_input("Registration Mark:", value="PK-GTU")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Historical Date Selector")
tanggal_pilihan = st.sidebar.date_input("Historical Flight Date:", value=datetime.date.today() - datetime.timedelta(days=1))

st.sidebar.markdown("### ⏳ Time Offset Configuration")
jam_lalu = st.sidebar.number_input("Hours Ago:", min_value=0, max_value=23, value=0)
menit_lalu = st.sidebar.number_input("Minutes Ago:", min_value=0, max_value=59, value=5)
detik_lalu = st.sidebar.number_input("Seconds Ago:", min_value=0, max_value=59, value=0)

# Calculate historical targeted time stamp based on sidebar offset selectors
waktu_target_dt = waktu_sekarang - datetime.timedelta(hours=jam_lalu, minutes=menit_lalu, seconds=detik_lalu)
waktu_target_str = waktu_target_dt.strftime("%H:%M:%S")
tgl_lalu_str = tanggal_pilihan.strftime("%d/%m/%Y")

st.sidebar.markdown("---")
status_jaringan = st.sidebar.radio(
    "Select Network Condition:",
    ("ONLINE (Normal)", "OFFLINE / LOSS OF SIGNAL (LOS)"),
    help="Simulates data caching behavior on internal aircraft memory storage when datalink drops."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Simulation Scenario Controls")
kondisi_simulasi = st.sidebar.selectbox(
    "Configure Flight Condition:", 
    ["Normal Flight Profile", "Pitot-Static Failure (Speed Freeze)", "Engine Overheat Anomaly", "Hydraulic Drop"]
)

st.sidebar.markdown("---")
tombol_eksekusi = st.sidebar.button("🚨 EXECUTE AI PIPELINE", type="primary", use_container_width=True)

# Dynamically handle Automation Checkbox based on Operation Mode
mode_otomatis = False
if operation_mode == "🟢 LIVE TELEMETRY STREAM":
    st.sidebar.markdown("### 🕒 Telemetry Stream Automation")
    mode_otomatis = st.sidebar.checkbox(
        "Enable Auto Transmission (3 Seconds)", 
        value=False,
        help="Pushes new live telemetry data automatically every 3 seconds matching Padang WIB."
    )

# ==========================================
# PHASE 5: RUNTIME DATA INJECTION PROCESSOR (LIVE VS HISTORICAL)
# ==========================================
if operation_mode == "📂 HISTORICAL DATA RETRIEVAL":
    # HISTORICAL GENERATOR ENGINE: Instantly generates a sequence ending exactly at the selected offset time
    t1 = (waktu_target_dt - datetime.timedelta(seconds=15)).strftime("%H:%M:%S")
    t2 = (waktu_target_dt - datetime.timedelta(seconds=10)).strftime("%H:%M:%S")
    t3 = (waktu_target_dt - datetime.timedelta(seconds=5)).strftime("%H:%M:%S")
    t4 = waktu_target_str
    
    if kondisi_simulasi == "Normal Flight Profile":
        speeds, n1s, hyds, fgts, stats = [450, 451, 449, 450], [92, 92, 91, 92], [3000, 2998, 3002, 3000], [620, 622, 619, 620], "NORMAL"
    elif kondisi_simulasi == "Pitot-Static Failure (Speed Freeze)":
        speeds, n1s, hyds, fgts, stats = [450, 452, 210, 140], [92, 93, 92, 91], [2995, 2990, 2985, 2980], [625, 628, 624, 626], "CRITICAL ANOMALY"
    elif kondisi_simulasi == "Engine Overheat Anomaly":
        speeds, n1s, hyds, fgts, stats = [452, 448, 450, 447], [93, 85, 76, 71], [2995, 2980, 2970, 2960], [625, 740, 850, 910], "CRITICAL ANOMALY"
    else: # Hydraulic Drop
        speeds, n1s, hyds, fgts, stats = [451, 448, 446, 445], [92, 92, 91, 92], [2990, 1800, 950, 450], [622, 625, 628, 630], "CRITICAL ANOMALY"

    df_historical = pd.DataFrame({
        'Date': [tgl_lalu_str, tgl_lalu_str, tgl_lalu_str, tgl_lalu_str],
        'Timestamp': [t1, t2, t3, t4],
        'Airspeed (Knots)': speeds,
        'N1 Fan Speed (%)': n1s,
        'Hydraulic Pressure (PSI)': hyds,
        'FGT Thermal (°C)': fgts,
        'Status': [stats]*4
    })
    display_df = df_historical
    
    komp, stat, teks, cek, sw = analisa_spesifik(kondisi_simulasi, model, ekor, waktu_target_str, tgl_lalu_str)
    st.session_state.hasil_analisa = teks
    st.session_state.checklist = cek
    st.session_state.komponen = komp
    st.session_state.status = stat
    st.session_state.status_warna = sw
    st.session_state.sudah_dianalisa = True

else:
    # LIVE TELEMETRY MODE ENGINE
    if tombol_eksekusi:
        if kondisi_simulasi == "Normal Flight Profile":
            speed, n1_fan, hydraulic, fgt, status = int(np.random.normal(450, 4)), int(np.random.normal(92, 1)), int(np.random.normal(3000, 15)), int(np.random.normal(620, 8)), "NORMAL"
        elif kondisi_simulasi == "Pitot-Static Failure (Speed Freeze)":
            speed, n1_fan, hydraulic, fgt, status = int(np.random.normal(240, 10)), int(np.random.normal(91, 2)), int(np.random.normal(2980, 20)), int(np.random.normal(628, 10)), "CRITICAL ANOMALY"
        elif kondisi_simulasi == "Engine Overheat Anomaly":
            speed, n1_fan, hydraulic, fgt, status = int(np.random.normal(448, 5)), int(np.random.normal(71, 3)), int(np.random.normal(2960, 20)), int(np.random.normal(910, 25)), "CRITICAL ANOMALY"
        else:
            speed, n1_fan, hydraulic, fgt, status = int(np.random.normal(430, 8)), int(np.random.normal(90, 1)), int(np.random.normal(450, 40)), int(np.random.normal(635, 12)), "CRITICAL ANOMALY"
            
        paket_data = {
            'Date': tgl_sekarang_str, 'Timestamp': waktu_aktual_komputer,
            'Airspeed (Knots)': speed, 'N1 Fan Speed (%)': n1_fan,
            'Hydraulic Pressure (PSI)': hydraulic, 'FGT Thermal (°C)': fgt, 'Status': status
        }
        
        if status_jaringan == "ONLINE (Normal)":
            if len(st.session_state.local_buffer) > 0:
                df_buffered = pd.DataFrame(st.session_state.local_buffer)
                st.session_state.telemetry_history = pd.concat([st.session_state.telemetry_history, df_buffered], ignore_index=True)
                st.session_state.local_buffer.clear()
                st.sidebar.success("✅ Onboard memory packets re-synchronized successfully!")
                
            df_new = pd.DataFrame([paket_data])
            st.session_state.telemetry_history = pd.concat([st.session_state.telemetry_history, df_new], ignore_index=True)
        else:
            st.session_state.local_buffer.append(paket_data)
            st.sidebar.error("⚠️ Datalink Link Broken (LOS)! Telemetry cached in onboard aircraft storage.")
            
        komp, stat, teks, cek, sw = analisa_spesifik(kondisi_simulasi, model, ekor, waktu_aktual_komputer, tgl_sekarang_str)
        st.session_state.hasil_analisa = teks
        st.session_state.checklist = cek
        st.session_state.komponen = komp
        st.session_state.status = stat
        st.session_state.status_warna = sw
        st.session_state.sudah_dianalisa = True
        
    display_df = st.session_state.telemetry_history

# ==========================================
# PHASE 6: MAIN INTERFACE RENDERING
# ==========================================
# Dynamic Mode Header Badge for Ground Crew visibility
if operation_mode == "📂 HISTORICAL DATA RETRIEVAL":
    st.warning(f"📂 HISTORICAL DATA ARCHIVE MODE — QUERY TARGET: {tgl_lalu_str} @ {waktu_target_str}")
else:
    st.success("🟢 LIVE STATION CORE STREAM — RECEIVING REAL-TIME SATELLITE DATALINK")

if st.session_state.sudah_dianalisa and not display_df.empty:
    m1, m2, m3, m4 = st.columns(4)
    data_akhir = display_df.iloc[-1]
    
    if st.session_state.status_warna == "normal":
        with m1: st.success(f"**Airspeed Indicator**\n### {data_akhir['Airspeed (Knots)']} Knots\n🟢 STATUS SAFE")
        with m2: st.success(f"**N1 Fan Speed**\n### {data_akhir['N1 Fan Speed (%)']}%\n🟢 ENGINE NOMINAL")
        with m3: st.success(f"**Hydraulic Pressure**\n### {data_akhir['Hydraulic Pressure (PSI)']} PSI\n🟢 PRESSURE STABLE")
        with m4: st.success(f"**FGT Exhaust Temp**\n### {data_akhir['FGT Thermal (°C)']}°C\n🟢 THERMAL SAFE")
    else:
        with m1: st.error(f"**Airspeed Indicator**\n### {data_akhir['Airspeed (Knots)']} Knots\n🚨 FREEZE DROP") if kondisi_simulasi == "Pitot-Static Failure (Speed Freeze)" else st.success(f"**Airspeed Indicator**\n### {data_akhir['Airspeed (Knots)']} Knots\n🟢 NOMINAL")
        with m2: st.error(f"**N1 Fan Speed**\n### {data_akhir['N1 Fan Speed (%)']}%\n🚨 ENGINE ANOMALY") if kondisi_simulasi == "Engine Overheat Anomaly" else st.success(f"**N1 Fan Speed**\n### {data_akhir['N1 Fan Speed (%)']}%\n🟢 NOMINAL")
        with m3: st.error(f"**Hydraulic Pressure**\n### {data_akhir['Hydraulic Pressure (PSI)']} PSI\n🚨 CRITICAL DROP") if kondisi_simulasi == "Hydraulic Drop" else st.success(f"**Hydraulic Pressure**\n### {data_akhir['Hydraulic Pressure (PSI)']} PSI\n🟢 NOMINAL")
        with m4: st.error(f"**FGT Exhaust Temp**\n### {data_akhir['FGT Thermal (°C)']}°C\n🚨 OVERHEAT CRITICAL") if kondisi_simulasi == "Engine Overheat Anomaly" else st.success(f"**FGT Exhaust Temp**\n### {data_akhir['FGT Thermal (°C)']}°C\n🟢 NOMINAL")
    st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"### 📡 Telemetry Stream Log: {ekor}")
    df_chart = display_df.set_index('Timestamp')
    st.line_chart(df_chart[['Airspeed (Knots)', 'N1 Fan Speed (%)', 'Hydraulic Pressure (PSI)', 'FGT Thermal (°C)']])
    st.dataframe(display_df.iloc[::-1], use_container_width=True, height=280)

with col2:
    st.markdown("### 🧠 Dynamic Ground Crew Gateway")
    st.info(f" 📅 **Ground Core System Date:** {tgl_sekarang_str} | **Flight Recorder Target Date:** {tgl_lalu_str}")
    
    if len(st.session_state.local_buffer) > 0 and operation_mode == "🟢 LIVE TELEMETRY STREAM":
        st.warning(f"📦 **Onboard Aircraft Storage Active:** {len(st.session_state.local_buffer)} raw packets queued in cache due to Loss of Signal (LOS).")
    
    if st.session_state.sudah_dianalisa:
        if st.session_state.status_warna == "normal":
            st.success(f"Base Configuration State Nominal | STATUS: {st.session_state.status}")
        else:
            st.error(f"❌ ANOMALY DETECTED: {st.session_state.komponen} | STATUS: {st.session_state.status}")
            
        st.code(st.session_state.hasil_analisa, language="text")
        
        st.markdown("#### 📋 Ground Crew Emergency Action Protocols:")
        for item in st.session_state.checklist:
            if st.session_state.status_warna == "normal":
                st.success(f"✨ Recommendation: {item}")
            else:
                st.warning(f"⚠️ Emergency Mitigation: {item}")
    else:
        st.info("💡 **INGEK Ground System Idle.** Metric cards hidden to prioritize computing workspace resources. Configure aircraft settings and trigger **EXECUTE AI PIPELINE** to begin active scanning feeds.")

# ==========================================
# PHASE 7: BULLETPROOF AUTOMATION LOOP (ONLY EXECUTES DURING LIVE MODE)
# ==========================================
if operation_mode == "🟢 LIVE TELEMETRY STREAM" and mode_otomatis:
    js_automation_code = (
        "<script>"
        "(function() {"
        "    console.log('INGEK Live Datalink Pulse: " + str(time.time()) + "');"
        "    if (window.parent._ingekTimeoutRef) {"
        "        clearTimeout(window.parent._ingekTimeoutRef);"
        "    }"
        "    window.parent._ingekTimeoutRef = setTimeout(function() {"
        "        var buttons = window.parent.document.querySelectorAll('button');"
        "        for (var i = 0; i < buttons.length; i++) {"
        "            if (buttons[i].textContent.includes('EXECUTE AI PIPELINE')) {"
        "                if (!buttons[i].disabled) {"
        "                    buttons[i].click();"
        "                    break;"
        "                }"
        "            }"
        "        }"
        "    }, 3000);"
        "})();"
        "</script>"
    )
    components.html(js_automation_code, height=0, width=0)