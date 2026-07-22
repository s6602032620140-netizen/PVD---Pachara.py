import streamlit as st
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="PVD Consolidation Calculator", layout="wide")

st.title("เครื่องมือคำนวณการปรับปรุงคุณภาพดินด้วย PVD")
st.markdown("โปรแกรมนี้ใช้ทฤษฎีของ Barron, Terzaghi และ Carillo ในการคำนวณอัตราการอัดตัวคายน้ำและการทรุดตัวของดิน")

# ================= แถบด้านข้างสำหรับรับค่าพารามิเตอร์ (Sidebar Inputs) =================
st.sidebar.header("1. คุณสมบัติของดิน (Soil Properties)")
H = st.sidebar.number_input("ความหนาของชั้นดินเหนียว H (m)", value=30.0)
Hd = st.sidebar.number_input("ระยะระบายน้ำแนวดิ่ง Hd (m) (เช่น H/2 สำหรับ Double drainage)", value=15.0)
Cv = st.sidebar.number_input("สัมประสิทธิ์การอัดตัวคายน้ำแนวดิ่ง Cv (m²/day)", value=0.002, format="%.4f")
kr_kv = st.sidebar.number_input("อัตราส่วน kr/kv", value=7.0)

st.sidebar.header("2. พารามิเตอร์การทรุดตัว (Settlement Parameters)")
Cc = st.sidebar.number_input("Compression Index (Cc)", value=0.29)
e0 = st.sidebar.number_input("Initial Void Ratio (e0)", value=1.10)
sigma0 = st.sidebar.number_input("Effective Overburden Stress เดิม σ'0 (kN/m²)", value=40.0)
d_sigma = st.sidebar.number_input("น้ำหนักบรรทุกที่เพิ่มขึ้น Δσ (kN/m²)", value=80.0)

st.sidebar.header("3. คุณสมบัติของ PVD (PVD Properties)")
a = st.sidebar.number_input("ความหนาของแผ่น PVD a (mm)", value=5.0) / 1000  # แปลงเป็น m
b = st.sidebar.number_input("ความกว้างของแผ่น PVD b (mm)", value=100.0) / 1000 # แปลงเป็น m
dw_method = st.sidebar.selectbox("วิธีคำนวณ Equivalent Diameter (dw)", ["Rixner", "Hansbo"])
pattern = st.sidebar.selectbox("รูปแบบการติดตั้ง PVD", ["Square (สี่เหลี่ยม)", "Triangular (สามเหลี่ยม)"])
S = st.sidebar.number_input("ระยะห่างระหว่าง PVD, S (m)", value=1.0)

st.sidebar.header("4. ชั้นทรายซับน้ำ (Sand Mat) - หากมี")
use_sand_mat = st.sidebar.checkbox("พิจารณาผลกระทบจาก Sand Mat (ค่า L)")
if use_sand_mat:
    Hm = st.sidebar.number_input("ความหนาของ Sand Mat, Hm (m)", value=0.5)
    B = st.sidebar.number_input("ครึ่งหนึ่งของความกว้างแผ่นทราย, B (m)", value=40.0)
    kc = st.sidebar.number_input("ค่าการซึมน้ำของดินเหนียว, kc (m/s)", value=1e-9, format="%.1e")
    km = st.sidebar.number_input("ค่าการซึมน้ำของแผ่นทราย, km (m/s)", value=1e-5, format="%.1e")
else:
    L = 0.0

st.sidebar.header("5. เวลาที่ต้องการคำนวณ")
t = st.sidebar.number_input("เวลา t (วัน)", value=90.0)

# ================= ส่วนการคำนวณ (Calculations) =================

col1, col2 = st.columns(2)

with col1:
    st.subheader("ผลการคำนวณพารามิเตอร์ PVD")
    
    # 1. คำนวณ dw
    if dw_method == "Rixner":
        dw = (a + b) / 2
        st.latex(r"d_w = \frac{a+b}{2} = " + f"{dw:.4f} \\text{{ m}}")
    else:
        dw = 2 * (a + b) / math.pi
        st.latex(r"d_w = \frac{2(a+b)}{\pi} = " + f"{dw:.4f} \\text{{ m}}")
        
    # 2. คำนวณ de
    if pattern == "Square (สี่เหลี่ยม)":
        de = 1.13 * S
        st.latex(r"d_e = 1.13S = " + f"{de:.4f} \\text{{ m}}")
    else:
        de = 1.05 * S
        st.latex(r"d_e = 1.05S = " + f"{de:.4f} \\text{{ m}}")
        
    # 3. คำนวณ n และ Fn
    n = de / dw
    Fn = ((n**2) / (n**2 - 1)) * math.log(n) - ((3 * n**2 - 1) / (4 * n**2))
    st.latex(r"n = \frac{d_e}{d_w} = " + f"{n:.2f}")
    st.latex(r"F_n = \frac{n^2}{n^2-1}\ln(n) - \frac{3n^2-1}{4n^2} = " + f"{Fn:.4f}")
    
    # 4. คำนวณ Cr และ Tr
    Cr = kr_kv * Cv
    Tr = (Cr * t) / (de**2)
    st.latex(r"C_r = \left(\frac{k_r}{k_v}\right) C_v = " + f"{Cr:.4f} \\text{{ m}}^2\\text{{/day}}")
    st.latex(r"T_r = \frac{C_r \cdot t}{d_e^2} = " + f"{Tr:.4f}")

with col2:
    st.subheader("ผลการคำนวณการอัดตัวคายน้ำ")
    
    # 5. คำนวณ Sand Mat Resistance (L)
    if use_sand_mat:
        L = (32 / (math.pi**2)) * (1 / (n**2)) * (H / Hm) * (kc / km) * ((B / dw)**2)
        st.markdown("**ดัชนีความต้านทานต่อการระบายน้ำ (L):**")
        st.latex(r"L = \frac{32}{\pi^2} \cdot \frac{1}{n^2} \cdot \frac{H}{H_m} \cdot \frac{k_c}{k_m} \cdot \left(\frac{B}{d_w}\right)^2 = " + f"{L:.4f}")
    
    # 6. คำนวณ Ur
    Ur = 1 - math.exp((-8 * Tr) / (Fn + 0.8 * L))
    if use_sand_mat:
        st.latex(r"U_r = 1 - \exp\left(\frac{-8T_r}{F_n + 0.8L}\right) = " + f"{Ur*100:.2f}\\%")
    else:
        st.latex(r"U_r = 1 - \exp\left(\frac{-8T_r}{F_n}\right) = " + f"{Ur*100:.2f}\\%")
        
    # 7. คำนวณ Uv
    Tv = (Cv * t) / (Hd**2)
    Uv = math.sqrt(4 * Tv) / math.pi # ประมาณการสำหรับ Uv <= 60%
    st.latex(r"T_v = \frac{C_v \cdot t}{H_d^2} = " + f"{Tv:.5f}")
    st.latex(r"U_v \approx \frac{\sqrt{4 \cdot T_v}}{\pi} = " + f"{Uv*100:.2f}\\%")
    
    # 8. คำนวณ Uav
    Uav = 1 - (1 - Ur) * (1 - Uv)
    st.latex(r"U_{av} = 1 - (1 - U_r)(1 - U_v) = " + f"{Uav*100:.2f}\\%")

st.markdown("---")
st.subheader("การคำนวณการทรุดตัว (Settlement)")
S_final = H * (Cc / (1 + e0)) * math.log10((sigma0 + d_sigma) / sigma0)
St = Uav * S_final

col3, col4 = st.columns(2)
with col3:
    st.latex(r"S_{final} = H \cdot \frac{C_c}{1+e_0} \cdot \log\left(\frac{\sigma'_0 + \Delta\sigma}{\sigma'_0}\right)")
    st.metric(label="การทรุดตัวสูงสุด (S_final)", value=f"{S_final:.4f} m")
with col4:
    st.latex(r"S_t = U_{av} \times S_{final}")
    st.metric(label=f"การทรุดตัวที่เวลา {t} วัน (S_t)", value=f"{St:.4f} m")

# ================= ส่วนของการสร้างกราฟแสดงความสัมพันธ์ตามเวลา =================
st.markdown("---")
st.subheader("กราฟแสดงความสัมพันธ์ของการทรุดตัวตามระยะเวลา (0 ถึง 365 วัน)")

time_array = np.arange(1, 366, 5)
Uav_array = []
St_array = []

for time_step in time_array:
    # คำนวณ Tr, Ur ใหม่ตามเวลา
    temp_Tr = (Cr * time_step) / (de**2)
    temp_Ur = 1 - math.exp((-8 * temp_Tr) / (Fn + 0.8 * L))
    
    # คำนวณ Tv, Uv ใหม่ตามเวลา
    temp_Tv = (Cv * time_step) / (Hd**2)
    temp_Uv = math.sqrt(4 * temp_Tv) / math.pi
    if temp_Uv > 1.0: temp_Uv = 1.0 # Limit upper bound
    
    # คำนวณ Uav และ St ใหม่
    temp_Uav = 1 - (1 - temp_Ur) * (1 - temp_Uv)
    temp_St = temp_Uav * S_final
    
    Uav_array.append(temp_Uav * 100)
    St_array.append(temp_St)

fig, ax1 = plt.subplots(figsize=(10, 5))

color = 'tab:blue'
ax1.set_xlabel('Time (Days)')
ax1.set_ylabel('Settlement (m)', color=color)
ax1.plot(time_array, St_array, color=color, linewidth=2, label='Settlement (m)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.axhline(y=S_final, color='tab:blue', linestyle='--', alpha=0.5, label='Ultimate Settlement')

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Degree of Consolidation (%)', color=color)  
ax2.plot(time_array, Uav_array, color=color, linewidth=2, linestyle='-.', label='Degree of Consolidation (%)')
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim([0, 105])

fig.tight_layout()  
st.pyplot(fig)
