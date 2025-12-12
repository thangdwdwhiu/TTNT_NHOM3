import heapq
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.widgets import TextBox, Button
import sys

# ==========================================
# 1. DỮ LIỆU & LOGIC A* (Giữ nguyên)
# ==========================================
mini_map = [
    ["1", ".", "2", "3", ".", "4", "5", ".", "6", "7"],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    ["8", "9", ".", "10", "11", "12", ".", "13", "14", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    ["15", "16", ".", "17", "18", ".", "19", "20", ".", "21"],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    ["22", "23", ".", "24", "25", "26", ".", "27", "28", "."],
    [".", ".", ".", ".", ".", ".", ".", ".", ".", "."],
    ["29", "30", ".", "31", "32", "33", ".", "34", "35", "."]
]

def tim_vi_tri(giatri, luoi):
    for r, dong in enumerate(luoi):
        for c, o in enumerate(dong):
            if str(o) == str(giatri): return (r, c)
    return None

def heuristic(nut, dich):
    return abs(nut[0] - dich[0]) + abs(nut[1] - dich[1])

def hang_xom(nut, batdau, dich, luoi):
    dong, cot = nut
    huong = [(-1,0), (1,0), (0,-1), (0,1)]
    ket_qua = []
    for dx, dy in huong:
        nd, nc = dong + dx, cot + dy
        if 0 <= nd < len(luoi) and 0 <= nc < len(luoi[0]):
            o = luoi[nd][nc]
            if o == "." or (nd, nc) == batdau or (nd, nc) == dich:
                ket_qua.append((nd, nc))
    return ket_qua

def a_sao(batdau, dich, luoi):
    mo = []; heapq.heappush(mo, (0, batdau))
    dong = set()
    g_diem = {batdau: 0}
    f_diem = {batdau: heuristic(batdau, dich)}
    cha = {batdau: None}
    so_node_duyet = 0 

    while mo:
        _, nut_hien_tai = heapq.heappop(mo)
        if nut_hien_tai in dong: continue
        dong.add(nut_hien_tai)
        so_node_duyet += 1

        if nut_hien_tai == dich:
            duong_di = []
            cur = nut_hien_tai
            while cur:
                duong_di.append(cur)
                cur = cha[cur]
            duong_di.reverse()
            return duong_di, g_diem[dich], so_node_duyet

        for xom in hang_xom(nut_hien_tai, batdau, dich, luoi):
            if xom in dong: continue
            g_tam = g_diem[nut_hien_tai] + 1
            if xom not in g_diem or g_tam < g_diem[xom]:
                g_diem[xom] = g_tam
                f_diem[xom] = g_tam + heuristic(xom, dich)
                cha[xom] = nut_hien_tai
                heapq.heappush(mo, (f_diem[xom], xom))
    return None, 0, so_node_duyet

# ==========================================
# 2. GIAO DIỆN BÁO CÁO (Sidebar Stats)
# ==========================================
class AStarGUI:
    def __init__(self, luoi):
        self.luoi = luoi
        self.rows = len(luoi)
        self.cols = len(luoi[0])
        self.path_lines = []     
        self.head_point = None
        self.result_texts = [] # Lưu các dòng text kết quả để cập nhật

        # Cấu hình cửa sổ: Rộng hơn để chứa Sidebar
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        
        # CHIA KHUNG HÌNH: Dành 65% bên trái cho bản đồ, 35% bên phải cho Text
        plt.subplots_adjust(left=0.05, right=0.60, bottom=0.15, top=0.95)
        
        self.khoi_tao_nen()
        self.tao_sidebar_thong_so() # Hàm mới để vẽ cột bên phải
        self.tao_widgets()
        
        print("✅ Giao diện Báo cáo đã sẵn sàng!")
        plt.show(block=True)

    def khoi_tao_nen(self):
        # Vẽ bản đồ
        color_map = [[0]*self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                if self.luoi[r][c] != '.': color_map[r][c] = 1 
        
        cmap = mcolors.ListedColormap(['white', '#6FA8DC']) 
        self.ax.imshow(color_map, cmap=cmap, origin='upper')

        self.ax.set_xticks([x - 0.5 for x in range(1, self.cols)], minor=True)
        self.ax.set_yticks([y - 0.5 for y in range(1, self.rows)], minor=True)
        self.ax.grid(which="minor", color="lightgray", linestyle='-', linewidth=1)
        self.ax.tick_params(which="minor", bottom=False, left=False)
        self.ax.set_xticks([]); self.ax.set_yticks([])
        
        for r in range(self.rows):
            for c in range(self.cols):
                txt = self.luoi[r][c]
                if txt != '.':
                    self.ax.text(c, r, txt, ha='center', va='center', color='black', fontsize=9, zorder=3)

    def tao_sidebar_thong_so(self):
        # Vẽ các thông số cố định bên phải (Sidebar)
        # Sử dụng tọa độ của Figure (0-1), vùng bên phải là > 0.65
        x_pos = 0.63
        
        # 1. KẾT QUẢ THỰC NGHIỆM (Sẽ cập nhật số liệu)
        self.fig.text(x_pos, 0.85, "KẾT QUẢ THỰC NGHIỆM", fontsize=14, fontweight='bold', color='darkblue')
        self.txt_cost = self.fig.text(x_pos, 0.80, "• Tổng chi phí (Cost): ...", fontsize=12)
        self.txt_node = self.fig.text(x_pos, 0.76, "• Số node đã duyệt: ...", fontsize=12)
        
        # 2. CÔNG THỨC A*
        self.fig.text(x_pos, 0.65, "CÔNG THỨC A* CỐT LÕI", fontsize=14, fontweight='bold', color='darkred')
        # Hộp công thức màu vàng nhạt
        self.fig.text(x_pos, 0.58, r"$f(n) = g(n) + h(n)$", fontsize=16, 
                      bbox={'facecolor':'#FFFFE0', 'alpha':0.5, 'pad':10})
        
        self.fig.text(x_pos, 0.53, "Trong đó:", fontsize=11, fontstyle='italic')
        self.fig.text(x_pos+0.02, 0.49, "- f(n): Tổng chi phí ước tính", fontsize=11)
        self.fig.text(x_pos+0.02, 0.46, "- g(n): Chi phí thực từ Start", fontsize=11)
        self.fig.text(x_pos+0.02, 0.43, "- h(n): Heuristic ước tính đến End", fontsize=11)

        # 3. HEURISTIC MANHATTAN
        self.fig.text(x_pos, 0.35, "HEURISTIC (MANHATTAN)", fontsize=14, fontweight='bold', color='green')
        self.fig.text(x_pos, 0.28, r"$h(n) = |x_1 - x_2| + |y_1 - y_2|$", fontsize=14)

    def tao_widgets(self):
        # Ô nhập liệu nằm bên dưới bản đồ
        ax_box_start = plt.axes([0.1, 0.05, 0.1, 0.05])
        self.txt_start = TextBox(ax_box_start, 'Start: ', initial="1")
        
        ax_box_end = plt.axes([0.3, 0.05, 0.1, 0.05])
        self.txt_end = TextBox(ax_box_end, 'End: ', initial="35")
        
        ax_btn = plt.axes([0.45, 0.05, 0.15, 0.05])
        self.btn_run = Button(ax_btn, 'CHẠY', color='#90EE90', hovercolor='0.975')
        self.btn_run.on_clicked(self.xu_ly_chay)

    def xoa_duong_cu(self):
        for line in self.path_lines: line.remove()
        self.path_lines = []
        if self.head_point:
            self.head_point.remove()
            self.head_point = None
        self.fig.canvas.draw_idle()

    def xu_ly_chay(self, event):
        val_start = self.txt_start.text
        val_end = self.txt_end.text
        
        bd = tim_vi_tri(val_start, self.luoi)
        dc = tim_vi_tri(val_end, self.luoi)
        self.xoa_duong_cu() 

        if not bd or not dc:
            self.txt_cost.set_text("❌ Lỗi: Số nhà không hợp lệ!")
            self.txt_cost.set_color("red")
            self.fig.canvas.draw_idle()
            return

        path, cost, opened = a_sao(bd, dc, self.luoi)
        
        if path:
            # CẬP NHẬT KẾT QUẢ VÀO SIDEBAR
            self.txt_cost.set_text(f"• Tổng chi phí (Cost): {cost}")
            self.txt_cost.set_color("black")
            self.txt_node.set_text(f"• Số node đã duyệt: {opened}")
            
            self.chay_animation(path)
        else:
            self.txt_cost.set_text("❌ Không tìm thấy đường đi!")
            self.txt_cost.set_color("red")
            self.fig.canvas.draw_idle()

    def chay_animation(self, path):
        x_vals = []
        y_vals = []
        for i in range(len(path)):
            point = path[i]
            y_vals.append(point[0])
            x_vals.append(point[1])
            
            line, = self.ax.plot(x_vals, y_vals, color='#F29F3F', linewidth=5, zorder=2)
            self.path_lines.append(line)
            
            if self.head_point: self.head_point.remove()
            self.head_point = self.ax.scatter(point[1], point[0], color='red', s=120, zorder=4, edgecolors='white')
            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            plt.pause(0.1)

# ==========================================
# 3. CHƯƠNG TRÌNH CHÍNH
# ==========================================
if __name__ == "__main__":
    app = AStarGUI(mini_map)