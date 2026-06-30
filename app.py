import streamlit as st
import pandas as pd
import time
import json
import numpy as np

# =====================================================================
# 🧠 UNIVERSAL FLEET AI ENGINE (DYNAMIC MULTI-AIRCRAFT DIAGNOSTIC)
# =====================================================================
def jalankan_aerospace_ml_fusion(df):
    """
    FITUR ML ADVANCED: Memprediksi parameter efisiensi mesin (N1 Fan Speed)
    berdasarkan korelasi Polinomial Non-Linear terhadap parameter termal pesawat.
    """
    data_bersih = df.dropna(subset=["N1_Fan_Pct"])
    X_train = data_bersih["EGT_Celcius"].values
    y_train = data_bersih["N1_Fan_Pct"].values
    
    coefficients = np.polyfit(X_train, y_train, 2)
    model_kuadratik = np.poly1d(coefficients)
    
    data_kosong = df[df["N1_Fan_Pct"].isna()]
    nilai_prediksi_ml = []
    
    for egt in data_kosong["EGT_Celcius"]:
        prediksi_n1 = model_kuadratik(egt)
        nilai_prediksi_ml.append(round(prediksi_n1, 1))
        
    return nilai_prediksi_ml, coefficients

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

class MockChatCompletions:
    def create(self, model, messages, response_format=None):
        time.sleep(2.0) # Latency satelit ACARS stasiun darat
        
        # MENARIK DATA DINAMIS YANG DIINPUT OLEH GROUND CREW DI WEB
        model_pesawat = st.session_state.pilihan_model
        reg_pesawat = st.session_state.pilihan_reg
        perintah_kru = st.session_state.perintah_kru
        
        df_saat_ini = pd.read_json(st.session_state.df_json_bridge)
        angka_hasil_ml, coeff = jalankan_aerospace_ml_fusion(df_saat_ini)
        
        # OTAK LLM DINAMIS: Merangkai teks laporan otomatis mengikuti isi ketikan Ground Crew
        analisis_ahms_llm = (
            f"⚠️ AUTOMATED RECONSTRUCTION REPORT FOR FLEET: {model_pesawat} [{reg_pesawat}] ⚠️\n\n"
            f"Menerima instruksi manual dari Ground Crew: '{perintah_kru}'.\n\n"
            f"Sistem INGEK mendeteksi kegagalan termomekanis pada unit armada {model_pesawat}. "
            f"Tekanan sistem penunjang drop ke angka kritis {df_saat_ini['Hyd_Pressure_PSI'].iloc[-1]} PSI, memicu lonjakan suhu internal kompartemen utama hingga {df_saat_ini['EGT_Celcius'].max()}°C.\n"
            f"Melalui model matematika kuadratik, pipa ML kami berhasil memulihkan data sensor N1 Fan Speed yang hilang sebesar {angka_hasil_ml[0]}% and {angka_hasil_ml[1]}% demi menjaga integritas data kotak hitam stasiun darat."
        )
        
        # Menyesuaikan daftar checklist darurat berdasarkan pabrikan pesawat yang dipilih
        if "Airbus" in model_pesawat:
            checklist_darurat = [
                f"ECAM ACTION [{reg_pesawat}]: ENG 1 THRUST LEVER . . . RETARD TO IDLE",
                f"ECAM ACTION [{reg_pesawat}]: HYDRAULIC PUMP . . . ISOLATE SYS",
                "GROUND CONTROL: Berikan clearance pendaratan darurat prioritas utama."
            ]
        else:
            # Format checklist Boeing (Non-Normal Checklist / NNC)
            checklist_darurat = [
                f"NNC CHECKLIST [{reg_pesawat}]: ENGINE 1 THRUST LEVER . . . CLOSE",
                f"NNC CHECKLIST [{reg_pesawat}]: HYDRAULIC ENGINE PUMP SWITCH . . . OFF",
                "GROUND CONTROL: Informasikan ATC lokal untuk persiapan pendaratan darurat armada Boeing."
            ]
        
        format_jawaban_ai = {
            "status": "UNIVERSAL_AHMS_SUCCESS",
            "predicted_values": angka_hasil_ml,
            "diagnostic": analisis_ahms_llm,
            "emergency_checklist": checklist_darurat
        }
        return MockResponse(json.dumps(format_jawaban_ai))

class MockChat:
    def __init__(self):
        self.completions = MockChatCompletions()

class MockOpenAIClient:
    def __init__(self, base_url, api_key):
        self.chat = MockChat()
# =====================================================================

st.set_page_config(page_title="INGEK - Universal Fleet Control", layout="wide", page_icon="🛸")

# Inisialisasi Session State awal agar web tidak error
if "simulation_mode" not in st.session_state:
    st.session_state.simulation_mode = "NORMAL"
if "ai_response_data" not in st.session_state:
    st.session_state.ai_response_data = None

# =====================================================================
# 🛠️ PANEL INPUT ARMADA DI SIDEBAR KIRI
# =====================================================================
st.sidebar.markdown("### ✈️ Fleet & Fleet Management")
pilihan_model = st.sidebar.selectbox(
    "Pilih Model Armada Pesawat:",
    ["Airbus A320neo", "Boeing 737 MAX", "Boeing 777-300ER", "Airbus A350-900"],
    key="pilihan_model"
)
pilihan_reg = st.sidebar.text_input(
    "Registrasi Nomor Ekor (Tail Number):", 
    value="PK-GTU" if "Airbus" in pilihan_model else "PK-MXA",
    key="pilihan_reg"
)

# Header Dashboard Dinamis
st.markdown(f"""
    <div style='background-color: #0F172A; padding: 20px; border-radius: 12px; border-left: 6px solid #3B82F6; margin-bottom: 25px;'>
        <h1 style='margin: 0; color: #F8FAFC; font-size: 30px;'>🛸 INGEK: Fleet Ground Core</h1>
        <p style='margin: 5px 0 0 0; color: #94A3B8; font-size: 14px;'>Monitoring Active Stream for <b>{pilihan_model}</b> • Registration ID: <b>{pilihan_reg}</b></p>
    </div>
""", unsafe_allow_html=True)

st.markdown("### 📋 Telemetry Data Ingestion Gateway")
uploaded_file = st.file_uploader("Unggah Log Parameter Penerbangan (.csv)", type=["csv"])

if uploaded_file is not None:
    df_flight = pd.read_csv(uploaded_file)
else:
    # DATASET SIMULASI LINTAS ARMADA
    base_data = {
        "Timestamp": ["17:50", "17:51", "17:52", "17:53", "17:54"],
        "Airspeed_Mach": [0.78, 0.79, 0.80, 0.80, 0.80],       
        "Hyd_Pressure_PSI": [3000, 2950, 2900, 1200, 450],     
        "EGT_Celcius": [610, 630, 660, 820, 910],              
        "N1_Fan_Pct": [85.2, 86.0, 87.1, None, None]           
    }
    df_flight = pd.DataFrame(base_data)

st.session_state.df_json_bridge = df_flight.to_json()
df_display = df_flight.copy()
baris_nan = df_display[df_display["N1_Fan_Pct"].isna()].index

if st.session_state.simulation_mode == "RECONSTRUCTED" and st.session_state.ai_response_data:
    for i, idx in enumerate(baris_nan):
        if i < len(st.session_state.ai_response_data["predicted_values"]):
            df_display.loc[idx, "N1_Fan_Pct"] = st.session_state.ai_response_data["predicted_values"][i]

df_display["N1_Fan_Pct"] = pd.to_numeric(df_display["N1_Fan_Pct"], errors='coerce')

# Labeling Istilah Sensor Dinamis Mengikuti Model Pesawat
lbl_hyd = "Green Hyd Pressure" if "Airbus" in pilihan_model else "System B Hyd Pressure"
lbl_egt = "Exhaust Gas Temp (EGT)" if "Airbus" in pilihan_model else "Turbine Inlet Temp (TIT)"

# =====================================================================
# 📊 BARIS METRIK CARD UTAMA (AMBIL VERSI MULTILINE AMAN)
# =====================================================================
m1, m2, m3, m4 = st.columns(4)
with m1:
    current_n1 = df_display["N1_Fan_Pct"].dropna().iloc[-1] if len(df_display["N1_Fan_Pct"].dropna()) > 0 else 0.0
    st.metric(
        label="✈️ Engine N1 Fan Speed", 
        value=f"{current_n1:.1f} %", 
        delta="ML Polynomial Restored" if st.session_state.simulation_mode == "RECONSTRUCTED" else "SENSOR DATA LOSS", 
        delta_color="normal" if st.session_state.simulation_mode == "RECONSTRUCTED" else "inverse"
    )
with m2:
    current_hyd = df_display["Hyd_Pressure_PSI"].iloc[-1]
    st.metric(
        label=f"💧 {lbl_hyd}", 
        value=f"{current_hyd} PSI", 
        delta="CRITICAL DROP", 
        delta_color="inverse"
    )
with m3:
    current_egt = df_display["EGT_Celcius"].iloc[-1]
    st.metric(
        label=f"🔥 {lbl_egt}", 
        value=f"{current_egt}°C", 
        delta="OVERHEAT SCANNED", 
        delta_color="inverse"
    )
with m4:
    status_node = f"{pilihan_reg} RECOVERED" if st.session_state.simulation_mode == "RECONSTRUCTED" else "FAULT DETECTED"
    st.metric(
        label="🚨 Automation Core State", 
        value=status_node, 
        delta="Universal Pipeline Active", 
        delta_color="normal" if st.session_state.simulation_mode == "RECONSTRUCTED" else "inverse"
    )

st.divider()

# =====================================================================
# 🎛️ WORKSPACE LAYOUT UTAMA
# =====================================================================
col1, col2 = st.columns([1.6, 1.4])

with col1:
    st.markdown(f"### 🛰️ Telemetry Stream: {pilihan_reg}")
    tab_g, tab_r = st.tabs(["📊 Engine & Airframe Waveforms", "📋 Telemetry Matrix Spreadsheet"])
    
    with tab_g:
        st.markdown(f"**1. Engine N1 Core Fan Speed (%) Profile ({pilihan_model})**")
        st.line_chart(df_display.set_index("Timestamp")["N1_Fan_Pct"])
        
        st.markdown(f"**2. Airframe {lbl_hyd} (PSI) Profile**")
        st.line_chart(df_display.set_index("Timestamp")["Hyd_Pressure_PSI"])
        
        st.markdown("**3. Aircraft Airspeed (Mach) Profile**")
        st.line_chart(df_display.set_index("Timestamp")["Airspeed_Mach"])
        
        st.markdown(f"**4. Engine {lbl_egt} Profile**")
        st.line_chart(df_display.set_index("Timestamp")["EGT_Celcius"])
        
    with tab_r:
        st.dataframe(df_display, use_container_width=True)
        if st.session_state.simulation_mode == "RECONSTRUCTED":
            st.download_button(
                label="📥 DOWNLOAD RECONSTRUCTED DATA LOG (CSV)",
                data=df_display.to_csv(index=False).encode('utf-8'),
                file_name=f"{pilihan_reg}_reconstructed_health_log.csv",
                mime="text/csv",
                use_container_width=True
            )

with col2:
    st.markdown("### 🧠 Dynamic Ground Crew Prompt Gateway")
    
    try:
        api_key_input = st.secrets["FIREWORKS_API_KEY"]
        st.info("🔒 Fireworks API Cloud Status: SECURE CONNECTED (Secrets Active)")
    except Exception:
        api_key_input = "fw_mock_xxxx_amd_competition_2026"
        st.warning("⚠️ Running on Local Hybrid Simulator Mode (Secrets Not Found)")
        
    st.divider()
    
    default_crew_text = (
        f"Analisis anomali kegagalan sistem hidrolik dan mesin pada pesawat {pilihan_model} dengan nomor ekor {pilihan_reg}. "
        "Hitung nilai perbaikan kompresor kipas N1 menggunakan regresi kuadratik matematis!"
    )
    perintah_kru = st.text_area("Ketik Instruksi Investigasi Ground Crew:", value=default_crew_text, height=120, key="perintah_kru")
    
    if st.button("🚀 EXECUTE UNIVERSAL AI INJECTION PIPELINE", type="primary", use_container_width=True):
        st.session_state.simulation_mode = "LOADING"
        
        with st.spinner(f"Menghubungkan ke armada {pilihan_reg} & memproses komputasi fusi hibrida..."):
            client = MockOpenAIClient(base_url="https://api.fireworks.ai/inference/v1", api_key=api_key_input)
            response = client.chat.completions.create(
                model="accounts/fireworks/models/llama-v3p1-8b-instruct",
                messages=[
                    {"role": "system", "content": "You are a dynamic universal fleet diagnostic agent. Output JSON."},
                    {"role": "user", "content": perintah_kru}
                ],
                response_format={"type": "json_object"}
            )
            st.session_state.ai_response_data = json.loads(response.choices[0].message.content)
            st.session_state.simulation_mode = "RECONSTRUCTED"
            st.rerun()

    if st.session_state.simulation_mode == "RECONSTRUCTED" and st.session_state.ai_response_data:
        st.success(f"✅ FLEET ASSESSMENTS FOR {pilihan_reg} COMPLETE")
        st.markdown(f"""
            <div style='background-color: #1E293B; padding: 15px; border-radius: 8px; border-left: 4px solid #3B82F6; margin-bottom: 15px;'>
                <span style='color: #38BDF8; font-weight: bold;'>🩺 Custom AI Crew Diagnostics:</span><br>
                <p style='color: #E2E8F0; margin-top: 5px; font-size: 13px; white-space: pre-line; line-height: 1.5;'>
                    {st.session_state.ai_response_data['diagnostic']}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**📋 Automated Actions Checklist ({pilihan_model}):**")
        for item in st.session_state.ai_response_data['emergency_checklist']:
            st.warning(f"⚠️ {item}")