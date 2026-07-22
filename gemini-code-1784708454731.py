import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import math

# ==========================================
# 1. Backend Logic (PVD Calculator Class)
# ==========================================
class PVDCalculator:
    @staticmethod
    def calc_equivalent_diameter(a: float, b: float, method: str = "rixner") -> float:
        if method.lower() == "hansbo": return 2 * (a + b) / math.pi
        else: return (a + b) / 2.0 
    @staticmethod
    def calc_effective_diameter(S: float, pattern: str = "square") -> float:
        if pattern.lower() == "triangular": return 1.05 * S
        else: return 1.13 * S
    @staticmethod
    def calc_spacing_factor(de: float, dw: float) -> float:
        n = de / dw
        if n <= 1: raise ValueError("ค่าระยะห่าง PVD แคบเกินไป (n <= 1)")
        term1 = (n**2 / (n**2 - 1)) * math.log(n)
        term2 = (3 * n**2 - 1) / (4 * n**2)
        return term1 - term2
    @staticmethod
    def calc_radial_consolidation_coeff(Cv: float, kr_kv_ratio: float) -> float:
        return kr_kv_ratio * Cv
    @staticmethod
    def calc_time_factor_radial(Cr: float, t: float, de: float) -> float:
        return (Cr * t) / (de**2)
    @staticmethod
    def calc_time_factor_vertical(Cv: float, t: float, Hd: float) -> float:
        return (Cv * t) / (Hd**2)
    @staticmethod
    def calc_degree_of_vertical_consolidation(Tv: float) -> float:
        return math.sqrt(4 * Tv) / math.pi
    @staticmethod
    def calc_sand_mat_resistance(n: float, H: float, Hm: float, kc: float, km: float, B: float, dw: float) -> float:
        term1 = 32 / (math.pi**2)
        term2 = 1 / (n**2)
        term3 = H / Hm
        term4 = kc / km
        term5 = (B / dw)**2
        return term1 * term2 * term3 * term4 * term5
    @staticmethod
    def calc_degree_of_radial_consolidation(Tr: float, Fn: float, L: float = 0.0) -> float:
        denominator = Fn + (0.8 * L)
        return 1.0 - math.exp((-8 * Tr) / denominator)
    @staticmethod
    def calc_average_degree_of_consolidation(Ur: float, Uv: float) -> float:
        return 1.0 - ((1.0 - Ur) * (1.0 - Uv))
    @staticmethod
    def calc_ultimate_settlement(H: float, Cc: float, e0: float, sigma0_prime: float, delta_sigma: float) -> float:
        stress_ratio = (sigma0_prime + delta_sigma) / sigma0_prime
        return H * (Cc / (1 + e0)) * math.log10(stress_ratio)

# ==========================================
# 2. UI & Frontend (Streamlit)
# ==========================================
st.set_page_config(page_title="PVD Design Application", page_icon="🏗️", layout="wide")

# -- Header Section --
st.title("🏗️ ระบบออกแบบและคำนวณการปรับปรุงคุณภาพดินด้วย PVD")
st.markdown("""
แอปพลิเคชันนี้ใช้สำหรับคำนวณอัตราการอัดตัวคายน้ำ (Consolidation) และระยะการทรุดตัวของชั้นดินอ่อน 
โดยอิงตามทฤษฎีของ Barron (1948), Terzaghi และ Carillo (1942)
""")

# -- Image Placeholder --
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Vertical_drains_installation.jpg/800px-Vertical_drains_installation.jpg", 
         caption="ภาพประกอบจำลองการติดตั้ง PVD", width=600)
st.divider()

# -- Sidebar: Input Data --
with st.sidebar:
    st.header("⚙️ กำหนดพารามิเตอร์ (Inputs)")
    
    with st.expander("1. ข้อมูลแผ่น PVD", expanded=True):
        a_mm = st.number_input("ความหนา PVD, a (mm)", min_value=1.0, value=5.0, help="ปกติหนาประมาณ 5 mm")
        b_mm = st.number_input("ความกว้าง PVD, b (mm)", min_value=10.0, value=100.0, help="ปกติกว้างประมาณ 100 mm")
        pattern = st.selectbox("รูปแบบการติดตั้ง", options=["Square (สี่เหลี่ยม)", "Triangular (สามเหลี่ยม)"])
        pattern_val = "square" if "Square" in pattern else "triangular"
        S_m = st.number_input("ระยะห่างระหว่าง PVD, S (m)", min_value=0.1, value=1.0, step=0.1)

    with st.expander("2. ข้อมูลชั้นดิน (Soil Properties)", expanded=True):
        H_m = st.number_input("ความหนาชั้นดินอ่อน, H (m)", min_value=1.0, value=12.0)
        drainage = st.selectbox("การระบายน้ำ", options=["Double Drainage (ระบาย 2 ทาง)", "Single Drainage (ระบายทางเดียว)"])
        Cv = st.number_input("สัมประสิทธิ์การอัดตัวคายน้ำแนวดิ่ง, Cv (cm²/day)", min_value=0.1, value=20.0)
        kr_kv = st.number_input("อัตราส่วน kr/kv", min_value=1.0, value=7.0, help="โดยทั่วไปใน กทม. อยู่ที่ 4-10")
        
        st.markdown("**พารามิเตอร์การทรุดตัว (Settlement):**")
        Cc = st.number_input("Compression Index, Cc", min_value=0.01, value=0.29)
        e0 = st.number_input("Initial Void Ratio, e0", min_value=0.1, value=1.10)
        sigma0 = st.number_input("Initial Effective Stress (kPa)", min_value=1.0, value=40.0)
        delta_sigma = st.number_input("Added Stress / Preload (kPa)", min_value=1.0, value=80.0)

    with st.expander("3. ข้อมูล Sand Mat (ทางเลือก)"):
        use_sandmat = st.checkbox("คำนวณผลกระทบ Sand Mat (L)", value=False)
        if use_sandmat:
            Hm = st.number_input("ความหนา Sand Mat, Hm (m)", min_value=0.1, value=0.5)
            B_width = st.number_input("ความกว้างครึ่งหนึ่งของพื้นที่, B (m)", min_value=1.0, value=40.0)
            kc = st.number_input("kc (cm/s) ดินเหนียว", value=1e-7, format="%e")
            km = st.number_input("km (cm/s) ทรายรอง", value=1e-3, format="%e")
        else:
            Hm, B_width, kc, km = 0, 0, 0, 0

    target_time = st.slider("ช่วงเวลาที่ต้องการตรวจสอบ (วัน)", min_value=10, max_value=365, value=90, step=10)

# ==========================================
# 3. Data Validation & Processing
# ==========================================
# ตรวจสอบและแปลงหน่วยให้สอดคล้องกัน (ใช้หน่วย cm สำหรับการคำนวณภายใน)
a_cm, b_cm = a_mm / 10.0, b_mm / 10.0
S_cm = S_m * 100.0
H_cm = H_m * 100.0
Hd_cm = H_cm / 2.0 if "Double" in drainage else H_cm

try:
    # 3.1 คำนวณค่าพารามิเตอร์พื้นฐาน
    dw = PVDCalculator.calc_equivalent_diameter(a_cm, b_cm, "rixner")
    de = PVDCalculator.calc_effective_diameter(S_cm, pattern_val)
    Fn = PVDCalculator.calc_spacing_factor(de, dw)
    Cr = PVDCalculator.calc_radial_consolidation_coeff(Cv, kr_kv)
    
    # คำนวณ Sand Mat Resistance
    L = 0.0
    if use_sandmat:
        n_val = de / dw
        L = PVDCalculator.calc_sand_mat_resistance(n_val, H_m, Hm, kc, km, B_width, dw/100.0)

    # 3.2 คำนวณ Ultimate Settlement
    S_final = PVDCalculator.calc_ultimate_settlement(H_m, Cc, e0, sigma0, delta_sigma)

    # 3.3 คำนวณค่า ณ วันที่ระบุเป้าหมาย (Target Time)
    Tr_target = PVDCalculator.calc_time_factor_radial(Cr, target_time, de)
    Tv_target = PVDCalculator.calc_time_factor_vertical(Cv, target_time, Hd_cm)
    Ur_target = PVDCalculator.calc_degree_of_radial_consolidation(Tr_target, Fn, L)
    Uv_target = PVDCalculator.calc_degree_of_vertical_consolidation(Tv_target)
    Uav_target = PVDCalculator.calc_average_degree_of_consolidation(Ur_target, Uv_target)
    St_target = PVDCalculator.calc_settlement_at_t(Uav_target, S_final)

    # 3.4 สร้างชุดข้อมูลสำหรับ Plot Graph (ตั้งแต่ 1 วัน ถึง 365 วัน)
    times = np.arange(1, 366, 2)
    uav_list, st_list = [], []
    for t in times:
        tr = PVDCalculator.calc_time_factor_radial(Cr, t, de)
        tv = PVDCalculator.calc_time_factor_vertical(Cv, t, Hd_cm)
        ur = PVDCalculator.calc_degree_of_radial_consolidation(tr, Fn, L)
        uv = PVDCalculator.calc_degree_of_vertical_consolidation(tv)
        uav = PVDCalculator.calc_average_degree_of_consolidation(ur, uv)
        uav_list.append(uav * 100) # แปลงเป็น %
        st_list.append(uav * S_final)
    
    df_plot = pd.DataFrame({"Time": times, "Uav": uav_list, "Settlement": st_list})

    # ==========================================
    # 4. Display Results
    # ==========================================
    st.subheader("📊 สรุปผลการออกแบบ (Design Summary)")
    
    # แสดงตัวแปรที่แปลงแล้วบางส่วนเพื่อให้ Engineer ตรวจสอบ
    with st.expander("ดูค่าพารามิเตอร์ตัวกลาง (Intermediate Parameters)"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Equivalent Dia. (dw)", f"{dw:.2f} cm")
        c2.metric("Effective Dia. (de)", f"{de:.2f} cm")
        c3.metric("Spacing Factor (Fn)", f"{Fn:.2f}")
        c4.metric("Radial Coeff. (Cr)", f"{Cr:.2f} cm²/day")
        if use_sandmat:
            st.metric("Sand Mat Resistance (L)", f"{L:.2f}")

    # แสดง Metric หลัก
    col1, col2, col3 = st.columns(3)
    col1.metric("การทรุดตัวสูงสุด (Ultimate Settlement)", f"{S_final:.3f} m")
    col2.metric(f"ระดับการอัดตัวที่ {target_time} วัน (Uav)", f"{Uav_target*100:.2f} %")
    col3.metric(f"ระยะทรุดตัวที่ {target_time} วัน", f"{St_target:.3f} m")

    if Uav_target < 0.9:
        st.warning(f"⚠️ ที่ {target_time} วัน ระดับการอัดตัวคายน้ำยังไม่ถึง 90% แนะนำให้ลดระยะห่าง S หรือเพิ่มระยะเวลาการถมดิน (Preloading)")
    else:
        st.success(f"✅ ที่ {target_time} วัน ระดับการอัดตัวคายน้ำผ่านเกณฑ์ (>= 90%)")

    # ==========================================
    # 5. Data Visualization (Plotly)
    # ==========================================
    st.divider()
    st.subheader("📈 กราฟแสดงความสัมพันธ์ตามเวลา (Time-Settlement Curves)")
    
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        # กราฟ Degree of Consolidation vs Time
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_plot["Time"], y=df_plot["Uav"], mode='lines', name='Uav (%)', line=dict(color='blue', width=3)))
        fig1.add_vline(x=target_time, line_dash="dash", line_color="red", annotation_text=f"{target_time} วัน")
        fig1.update_layout(title="ระดับการอัดตัวคายน้ำเฉลี่ยรวม (Uav) เทียบกับเวลา", 
                           xaxis_title="เวลา (วัน)", yaxis_title="Degree of Consolidation (%)",
                           yaxis_range=[0, 105], template="plotly_white")
        st.plotly_chart(fig1, use_container_width=True)

    with g_col2:
        # กราฟ Settlement vs Time
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_plot["Time"], y=df_plot["Settlement"], mode='lines', name='Settlement (m)', line=dict(color='green', width=3)))
        fig2.add_vline(x=target_time, line_dash="dash", line_color="red")
        fig2.update_layout(title="ระยะการทรุดตัว (Settlement) เทียบกับเวลา", 
                           xaxis_title="เวลา (วัน)", yaxis_title="Settlement (m)",
                           yaxis_autorange="reversed", # กราฟทรุดตัว นิยมให้แกน Y กลับหัวลง (ชี้ลงล่าง)
                           template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

except ValueError as e:
    st.error(f"❌ เกิดข้อผิดพลาดในการคำนวณ: {e}")
except ZeroDivisionError:
    st.error("❌ เกิดข้อผิดพลาด: มีการหารด้วยศูนย์ กรุณาตรวจสอบค่า Input ไม่ให้มีค่าเป็น 0 ในจุดที่ไม่เหมาะสม")
except Exception as e:
    st.error(f"❌ ระบบขัดข้อง กรุณาตรวจสอบข้อมูลนำเข้า: {e}")