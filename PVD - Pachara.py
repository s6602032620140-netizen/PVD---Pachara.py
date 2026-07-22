import math

class PVDCalculator:
    """
    คลาสสำหรับคำนวณการปรับปรุงคุณภาพดินด้วยวิธี Prefabricated Vertical Drains (PVD)
    อ้างอิงสมการจากทฤษฎี Barron, Terzaghi, Carillo และการคำนวณ Sand Mat
    """

    @staticmethod
    def calc_equivalent_diameter(a: float, b: float, method: str = "rixner") -> float:
        """
        คำนวณเส้นผ่านศูนย์กลางสมมูลของแผ่นระบายน้ำ (dw)
        :param a: ความหนาของ PVD (เช่น mm หรือ m)
        :param b: ความกว้างของ PVD (เช่น mm หรือ m)
        :param method: "rixner" (a+b)/2 หรือ "hansbo" 2(a+b)/pi
        :return: dw (หน่วยเดียวกับ a และ b)
        """
        if method.lower() == "hansbo":
            return 2 * (a + b) / math.pi
        else:
            return (a + b) / 2.0  # Rixner method (นิยมใช้ในเอกสาร)

    @staticmethod
    def calc_effective_diameter(S: float, pattern: str = "square") -> float:
        """
        คำนวณเส้นผ่านศูนย์กลางอิทธิพล (de)
        :param S: ระยะห่างระหว่าง PVD
        :param pattern: "square" (สี่เหลี่ยม) หรือ "triangular" (สามเหลี่ยม)
        :return: de (หน่วยเดียวกับ S)
        """
        if pattern.lower() == "triangular":
            return 1.05 * S
        else:
            return 1.13 * S

    @staticmethod
    def calc_spacing_factor(de: float, dw: float) -> float:
        """
        คำนวณตัวประกอบระยะห่างของแผ่นระบายน้ำ (Fn) ตามวิธีของ Barron (ไม่คิด Smear Zone)
        :param de: เส้นผ่านศูนย์กลางอิทธิพล
        :param dw: เส้นผ่านศูนย์กลางสมมูลของ PVD
        :return: Fn
        """
        n = de / dw
        if n <= 1:
            raise ValueError("ค่า n (de/dw) ต้องมากกว่า 1")
        
        term1 = (n**2 / (n**2 - 1)) * math.log(n)
        term2 = (3 * n**2 - 1) / (4 * n**2)
        return term1 - term2

    @staticmethod
    def calc_radial_consolidation_coeff(Cv: float, kr_kv_ratio: float) -> float:
        """
        คำนวณสัมประสิทธิ์การอัดตัวคายน้ำตามแนวรัศมี (Cr)
        :param Cv: สัมประสิทธิ์การอัดตัวคายน้ำในแนวดิ่ง
        :param kr_kv_ratio: อัตราส่วนความสามารถในการซึมน้ำ (kr/kv) ปกติอยู่ระหว่าง 4-10
        :return: Cr (หน่วยเดียวกับ Cv เช่น cm^2/day)
        """
        return kr_kv_ratio * Cv

    @staticmethod
    def calc_time_factor_radial(Cr: float, t: float, de: float) -> float:
        """
        คำนวณตัวประกอบเวลาในแนวรัศมี (Tr)
        :param Cr: สัมประสิทธิ์การอัดตัวคายน้ำตามแนวรัศมี
        :param t: เวลาที่พิจารณา
        :param de: เส้นผ่านศูนย์กลางอิทธิพล
        :return: Tr (ระวังเรื่องหน่วย Cr, t, de ต้องสอดคล้องกัน)
        """
        return (Cr * t) / (de**2)

    @staticmethod
    def calc_time_factor_vertical(Cv: float, t: float, Hd: float) -> float:
        """
        คำนวณตัวประกอบเวลาในแนวดิ่ง (Tv)
        :param Cv: สัมประสิทธิ์การอัดตัวคายน้ำในแนวดิ่ง
        :param t: เวลา
        :param Hd: ระยะทางระบายน้ำที่ไกลที่สุด (Drainage path)
        :return: Tv (ระวังเรื่องหน่วย Cv, t, Hd ต้องสอดคล้องกัน)
        """
        return (Cv * t) / (Hd**2)

    @staticmethod
    def calc_degree_of_vertical_consolidation(Tv: float) -> float:
        """
        คำนวณระดับการอัดตัวคายน้ำในแนวดิ่ง (Uv) ตามทฤษฎี Terzaghi
        *อ้างอิงตามสมการในสไลด์: Uv = sqrt(4 * Tv) / pi (สำหรับ Uv <= 60%)
        :param Tv: ตัวประกอบเวลาในแนวดิ่ง
        :return: Uv (ในรูปทศนิยม)
        """
        return math.sqrt(4 * Tv) / math.pi

    @staticmethod
    def calc_sand_mat_resistance(n: float, H: float, Hm: float, kc: float, km: float, B: float, dw: float) -> float:
        """
        คำนวณดัชนีความต้านทานต่อการระบายน้ำของ Sand Mat (L)
        :param n: ค่าอัตราส่วนพื้นที่ระบายน้ำ (de/dw)
        :param H: ความลึกของชั้นดินเหนียว
        :param Hm: ความหนาของแผ่นทราย (Sand Mat)
        :param kc: ค่าการซึมน้ำของดินเหนียว (เช่น cm/s)
        :param km: ค่าการซึมน้ำของแผ่นทราย (เช่น cm/s)
        :param B: ครึ่งหนึ่งของความกว้างแผ่นทราย
        :param dw: เส้นผ่านศูนย์กลางสมมูลของ PVD
        :return: ดัชนีความต้านทาน L (หน่วยของ H,Hm และ B,dw และ kc,km ต้องสอดคล้องกัน)
        """
        term1 = 32 / (math.pi**2)
        term2 = 1 / (n**2)
        term3 = H / Hm
        term4 = kc / km
        term5 = (B / dw)**2
        return term1 * term2 * term3 * term4 * term5

    @staticmethod
    def calc_degree_of_radial_consolidation(Tr: float, Fn: float, L: float = 0.0) -> float:
        """
        คำนวณระดับการอัดตัวคายน้ำตามแนวรัศมี (Ur) 
        *หากมีการพิจารณาผลของ Sand Mat ให้ใส่ค่า L 
        :param Tr: ตัวประกอบเวลาในแนวรัศมี
        :param Fn: ตัวประกอบระยะห่าง
        :param L: ดัชนีความต้านทานของ Sand Mat (ค่าเริ่มต้น = 0.0 ไม่คิดผลกระทบ)
        :return: Ur (ในรูปทศนิยม)
        """
        denominator = Fn + (0.8 * L)
        return 1.0 - math.exp((-8 * Tr) / denominator)

    @staticmethod
    def calc_average_degree_of_consolidation(Ur: float, Uv: float) -> float:
        """
        คำนวณระดับการอัดตัวคายน้ำเฉลี่ยรวม (Uav) ตามทฤษฎีของ Carillo (1942)
        :param Ur: ระดับการอัดตัวคายน้ำตามแนวรัศมี (ทศนิยม)
        :param Uv: ระดับการอัดตัวคายน้ำในแนวดิ่ง (ทศนิยม)
        :return: Uav (ในรูปทศนิยม)
        """
        return 1.0 - ((1.0 - Ur) * (1.0 - Uv))

    @staticmethod
    def calc_ultimate_settlement(H: float, Cc: float, e0: float, sigma0_prime: float, delta_sigma: float) -> float:
        """
        คำนวณค่าการยุบตัวสุดท้ายสูงสุด (Ultimate Settlement: S_final)
        :param H: ความหนาของชั้นดินอ่อน
        :param Cc: Compression Index
        :param e0: Void ratio เริ่มต้น
        :param sigma0_prime: Effective Overburden Stress เดิม
        :param delta_sigma: ความดันน้ำหนักบรรทุกที่เพิ่มขึ้น (เช่น จาก Preloading)
        :return: S_final (หน่วยเดียวกับ H)
        """
        stress_ratio = (sigma0_prime + delta_sigma) / sigma0_prime
        return H * (Cc / (1 + e0)) * math.log10(stress_ratio)

    @staticmethod
    def calc_settlement_at_t(Uav: float, S_final: float) -> float:
        """
        คำนวณค่าการยุบตัวที่เกิดขึ้น ณ เวลา t (St)
        :param Uav: ระดับการอัดตัวคายน้ำเฉลี่ยรวม (ทศนิยม)
        :param S_final: ค่าการยุบตัวสุดท้าย
        :return: St (หน่วยเดียวกับ S_final)
        """
        return Uav * S_final
