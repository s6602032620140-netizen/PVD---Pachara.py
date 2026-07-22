import math

# ================= 1. กำหนดตัวแปร (Input Parameters) =================

# 1.1 คุณสมบัติของดิน (Soil Properties)
H = 30.0          # ความหนาของชั้นดินเหนียว (m)
Hd = 15.0         # ระยะระบายน้ำแนวดิ่ง (m) (เช่น H/2 สำหรับ Double drainage)
Cv = 0.002        # สัมประสิทธิ์การอัดตัวคายน้ำแนวดิ่ง (m²/day)
kr_kv = 7.0       # อัตราส่วน kr/kv

# 1.2 พารามิเตอร์การทรุดตัว (Settlement Parameters)
Cc = 0.29         # Compression Index
e0 = 1.10         # Initial Void Ratio
sigma0 = 40.0     # Effective Overburden Stress เดิม (kN/m²)
d_sigma = 80.0    # น้ำหนักบรรทุกที่เพิ่มขึ้น (kN/m²)

# 1.3 คุณสมบัติของ PVD (PVD Properties)
a = 5.0 / 1000    # ความหนาของแผ่น PVD (m)
b = 100.0 / 1000  # ความกว้างของแผ่น PVD (m)
dw_method = "Rixner" # เลือก: "Rixner" หรือ "Hansbo"
pattern = "Square"   # เลือก: "Square" หรือ "Triangular"
S = 1.0           # ระยะห่างระหว่าง PVD (m)

# 1.4 ชั้นทรายซับน้ำ (Sand Mat)
use_sand_mat = True  # เปลี่ยนเป็น False หากไม่คิดผลของ Sand Mat
Hm = 0.5          # ความหนาของ Sand Mat (m)
B = 40.0          # ครึ่งหนึ่งของความกว้างแผ่นทราย (m)
kc = 1e-9         # ค่าการซึมน้ำของดินเหนียว (m/s)
km = 1e-5         # ค่าการซึมน้ำของแผ่นทราย (m/s)

# 1.5 เวลาที่ต้องการคำนวณ
t = 90.0          # เวลา (วัน)


# ================= 2. ส่วนการคำนวณ (Calculations) =================

# 2.1 คำนวณ dw (Equivalent Diameter)
if dw_method == "Rixner":
    dw = (a + b) / 2
else:
    dw = 2 * (a + b) / math.pi

# 2.2 คำนวณ de (Influence Diameter)
if pattern == "Square":
    de = 1.13 * S
else:
    de = 1.05 * S

# 2.3 คำนวณ n และ Fn (Drain spacing factor)
n = de / dw
Fn = ((n**2) / (n**2 - 1)) * math.log(n) - ((3 * n**2 - 1) / (4 * n**2))

# 2.4 คำนวณ Cr และ Tr
Cr = kr_kv * Cv
Tr = (Cr * t) / (de**2)

# 2.5 คำนวณ Sand Mat Resistance (L)
if use_sand_mat:
    L = (32 / (math.pi**2)) * (1 / (n**2)) * (H / Hm) * (kc / km) * ((B / dw)**2)
else:
    L = 0.0

# 2.6 คำนวณ Ur (การอัดตัวแนวรัศมี)
Ur = 1 - math.exp((-8 * Tr) / (Fn + 0.8 * L))

# 2.7 คำนวณ Uv (การอัดตัวแนวดิ่ง)
Tv = (Cv * t) / (Hd**2)
Uv = math.sqrt(4 * Tv) / math.pi
if Uv > 1.0: 
    Uv = 1.0  # จำกัดค่าไม่ให้เกิน 100%

# 2.8 คำนวณ Uav (การอัดตัวเฉลี่ยรวมตามทฤษฎี Carillo)
Uav = 1 - (1 - Ur) * (1 - Uv)

# 2.9 คำนวณการทรุดตัว (Settlement)
S_final = H * (Cc / (1 + e0)) * math.log10((sigma0 + d_sigma) / sigma0)
St = Uav * S_final


# ================= 3. ส่วนแสดงผล (Print Results) =================

print("--- ผลการคำนวณพารามิเตอร์ PVD ---")
print(f"Equivalent Diameter (dw): {dw:.4f} m")
print(f"Influence Diameter (de): {de:.4f} m")
print(f"Spacing Ratio (n): {n:.2f}")
print(f"Drain Spacing Factor (Fn): {Fn:.4f}")
print(f"Radial Coefficient (Cr): {Cr:.4f} m²/day")
print(f"Radial Time Factor (Tr): {Tr:.4f}")

print("\n--- ผลการคำนวณการอัดตัวคายน้ำ ---")
if use_sand_mat:
    print(f"Sand Mat Resistance (L): {L:.4f}")
print(f"Degree of Radial Consolidation (Ur): {Ur*100:.2f} %")
print(f"Vertical Time Factor (Tv): {Tv:.5f}")
print(f"Degree of Vertical Consolidation (Uv): {Uv*100:.2f} %")
print(f"Average Degree of Consolidation (Uav): {Uav*100:.2f} %")

print("\n--- ผลการคำนวณการทรุดตัว ---")
print(f"Ultimate Settlement (S_final): {S_final:.4f} m")
print(f"Settlement at {t} days (St): {St:.4f} m")
