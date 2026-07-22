import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ================= 1. การตั้งค่าหน้าเพจ & CSS (Page Config & Styling) =================
st.set_page_config(page_title="PVD Consolidation Analysis", page_icon="🏗️", layout="wide")

# ปรับแต่ง CSS เล็กน้อยเพื่อให้ฟอนต์และช่องว่างดูสบายตาขึ้น
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1, h2, h3 { color: #1E3A8A; font-family: 'Kanit', sans-serif; }
    .stMetric { background-color: #F3F4F6; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ PVD Consolidation & Settlement Calculator")
st.markdown("โปรแกรมวิเคราะห์การปรับปรุงคุณภาพดินด้วยท่อระบายน้ำแนวดิ่ง (Prefabricated Vertical Drains) อ้างอิงทฤษฎี Barron, Terzaghi และ Carillo[cite: 1]")
st.markdown("---")

# ================= 2. จัดโครงสร้าง UI ด้วย Tabs =================
tab_inputs, tab_calcs, tab_graphs = st.tabs([
    "📝 1. ป้อนข้อมูลพารามิเตอร์ (Inputs)", 
    "🧮 2. ลำดับการคำนวณ (Step-by-Step)", 
    "📊 3. กราฟวิเคราะห์ (Analysis View)"
])

# ----------------- Tab 1: ป้อนข้อมูล (Inputs) -----------------
with tab_inputs:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🌱 1. คุณสมบัติของดิน")
        with st.container(border=True):
            H = st.number_input("ความหนาชั้นดินเหนียว H (m)", value=30.0)
            Hd = st.number_input("ระยะระบายน้ำแนวดิ่ง Hd (m)", value=15.0, help="H/2 สำหรับการระบายน้ำสองทิศทาง (Double drainage)")
            Cv = st.number_input("สปส.อัดตัวคายน้ำแนวดิ่ง Cv (m²/day)", value=0.002, format="%.4f")
            kr_kv = st.number_input("อัตราส่วน kr/kv", value=7.0)
            
    with col2:
        st.subheader("📉 2. พารามิเตอร์การทรุดตัว")
        with st.container(border=True):
            Cc = st.number_input("Compression Index (Cc)", value=0.29)
            e0 = st.number_input("Initial Void Ratio (e0)", value=1.10)
            sigma0 = st.number_input("Effective Stress เดิม σ'0 (kN/m²)", value=40.0)
            d_sigma = st.number_input("น้ำหนักบรรทุกเพิ่ม Δσ (kN/m²)", value=80.0)

    with col3:
        st.subheader("📏 3. คุณสมบัติ PVD")
        with st.container(border=True):
            pattern = st.selectbox("รูปแบบการติดตั้ง", ["Square (สี่เหลี่ยม)", "Triangular (สามเหลี่ยม)"])
            S = st.number_input("ระยะห่าง PVD, S (m)", value=1.0)
            col3_1, col3_2 = st.columns(2)
            a = col3_1.number_input("ความหนา a (mm)", value=5.0) / 1000
            b = col3_2.number_input("ความกว้าง b (mm)", value=100.0) / 1000
            dw_method = st.selectbox("วิธีหา Equivalent Dia. (dw)", ["Rixner", "Hansbo"])
            t = st.number_input("เวลาประเมิน t (วัน)", value=90.0)

    # Expander สำหรับ Sand Mat
    with st.expander("⚙️ การตั้งค่าขั้นสูง: ชั้นทรายซับน้ำ (Sand Mat Configuration)"):
        use_sand_mat = st.checkbox("เปิดใช้การคำนวณผลกระทบจาก Sand Mat (ค่า L)")
        if use_sand_mat:
            sm_col1, sm_col2 = st.columns(2)
            Hm = sm_col1.number_input("ความหนา Sand Mat, Hm (m)", value=0.5)
            B = sm_col2.number_input("ครึ่งหนึ่งของความกว้าง, B (m)", value=40.0)
            kc = sm_col1.number_input("ค่าการซึมน้ำของดิน, kc (m/s)", value=1e-9, format="%.1e")
            km = sm_col2.number_input("ค่าการซึมน้ำของทราย, km (m/s)", value=1e-5, format="%.1e")
        else:
            L = 0.0

# ----------------- Tab 2: ลำดับการคำนวณ (Calculations) -----------------
with tab_calcs:
    st.info("💡 การคำนวณจะแสดงผลทีละขั้นตอน เพื่อให้ง่ายต่อการติดตามและทำความเข้าใจทฤษฎีการระบายน้ำ")
    
    calc_col1, calc_col2 = st.columns(2)
    
    with calc_col1:
        st.markdown("### ขั้นที่ 1: พารามิเตอร์เรขาคณิต (Geometric Parameters)")
        
        if dw_method == "Rixner":
            dw = (a + b) / 2
            st.latex(r"d_w = \frac{a+b}{2} = " + f"{dw:.4f} \\text{{ m}}")
        else:
            dw = 2 * (a + b) / math.pi
            st.latex(r"d_w = \frac{2(a+b)}{\pi} = " + f"{dw:.4f} \\text{{ m}}")
            
        if pattern == "Square (สี่เหลี่ยม)":
            de = 1.13 * S
            st.latex(r"d_e = 1.13S = " + f"{de:.4f} \\text{{ m}}")
        else:
            de = 1.05 * S
            st.latex(r"d_e = 1.05S = " + f"{de:.4f} \\text{{ m}}")
            
        n = de / dw
        Fn = ((n**2) / (n**2 - 1)) * math.log(n) - ((3 * n**2 - 1) / (4 * n**2))
        st.latex(r"F_n = \frac{n^2}{n^2-1}\ln(n) - \frac{3n^2-1}{4n^2} = " + f"{Fn:.4f}")

        st.markdown("### ขั้นที่ 2: ตัวประกอบเวลา (Time Factors)")
        Cr = kr_kv * Cv
        Tr = (Cr * t) / (de**2)
        st.latex(r"C_r = \left(\frac{k_r}{k_v}\right) C_v = " + f"{Cr:.4f}")
        st.latex(r"T_r = \frac{C_r \cdot t}{d_e^2} = " + f"{Tr:.4f}")
        
        Tv = (Cv * t) / (Hd**2)
        st.latex(r"T_v = \frac{C_v \cdot t}{H_d^2} = " + f"{Tv:.5f}")

    with calc_col2:
        st.markdown("### ขั้นที่ 3: ระดับการอัดตัวคายน้ำ (Degree of Consolidation)")
        if use_sand_mat:
            L = (32 / (math.pi**2)) * (1 / (n**2)) * (H / Hm) * (kc / km) * ((B / dw)**2)
            st.latex(r"L (\text{Resistance Index}) = " + f"{L:.4f}")
            Ur = 1 - math.exp((-8 * Tr) / (Fn + 0.8 * L))
            st.latex(r"U_r = 1 - \exp\left(\frac{-8T_r}{F_n + 0.8L}\right) = " + f"{Ur*100:.2f}\\%")
        else:
            Ur = 1 - math.exp((-8 * Tr) / (Fn))
            st.latex(r"U_r = 1 - \exp\left(\frac{-8T_r}{F_n}\right) = " + f"{Ur*100:.2f}\\%")

        Uv = math.sqrt(4 * Tv) / math.pi
        if Uv > 1.0: Uv = 1.0
        st.latex(r"U_v \approx \frac{\sqrt{4 \cdot T_v}}{\pi} = " + f"{Uv*100:.2f}\\%")
        
        Uav = 1 - (1 - Ur) * (1 - Uv)
        st.success(f"**U_av รวม (Carillo's Theory): {Uav*100:.2f}%**")
        st.latex(r"U_{av} = 1 - (1 - U_r)(1 - U_v)")

    st.markdown("---")
    st.markdown("### ขั้นที่ 4: การทรุดตัว (Settlement Analysis)")
    S_final = H * (Cc / (1 + e0)) * math.log10((sigma0 + d_sigma) / sigma0)
    St = Uav * S_final
    
    m1, m2 = st.columns(2)
    m1.metric("การทรุดตัวสูงสุดที่เป็นไปได้ (Ultimate Settlement)", f"{S_final:.4f} m", "100% Consolidation")
    m2.metric(f"การทรุดตัวที่เวลา {t} วัน (Current Settlement)", f"{St:.4f} m", f"{Uav*100:.2f}% Consolidation", delta_color="off")

# ----------------- Tab 3: กราฟวิเคราะห์ (Graphs) -----------------
with tab_graphs:
    st.markdown("### กราฟแสดงความสัมพันธ์ของระยะเวลา การทรุดตัว และระดับการอัดตัวคายน้ำ")
    
    time_array = np.arange(1, 366, 5)
    Uav_array = []
    St_array = []

    for time_step in time_array:
        temp_Tr = (Cr * time_step) / (de**2)
        temp_Ur = 1 - math.exp((-8 * temp_Tr) / (Fn + 0.8 * L if use_sand_mat else Fn))
        
        temp_Tv = (Cv * time_step) / (Hd**2)
        temp_Uv = math.sqrt(4 * temp_Tv) / math.pi
        if temp_Uv > 1.0: temp_Uv = 1.0
        
        temp_Uav = 1 - (1 - temp_Ur) * (1 - temp_Uv)
        
        Uav_array.append(temp_Uav * 100)
        St_array.append(temp_Uav * S_final)

    # ใช้ Plotly เพื่อความทันสมัยและ Interactive
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=time_array, y=St_array, name="Settlement (m)", line=dict(color="#1D4ED8", width=3)),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=time_array, y=Uav_array, name="Degree of Consolidation (%)", line=dict(color="#10B981", width=3, dash="dot")),
        secondary_y=True,
    )

    # ตั้งค่าแกนและ Layout ให้ดูโปร่งตา
    fig.update_layout(
        title_text="Time vs Settlement & Consolidation",
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(title_text="ระยะเวลา Time (Days)", showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(title_text="<b>Settlement</b> (m)", secondary_y=False, showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(title_text="<b>Degree of Consolidation</b> (%)", secondary_y=True, range=[0, 105])

    st.plotly_chart(fig, use_container_width=True)
