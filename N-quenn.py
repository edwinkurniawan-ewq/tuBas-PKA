import pygame
import sys
import time
import random
import os

# --- LOGIKA AI PHANES ---
class PhanesAgent:
    def __init__(self, n):
        self.n = n

    def get_conflicts(self, board):
        conflicts = 0
        for i in range(self.n):
            if board[i] == -1: continue
            for j in range(i + 1, self.n):
                if board[j] == -1: continue
                if board[i] == board[j] or abs(board[i] - board[j]) == j - i:
                    conflicts += 1
        return conflicts

    def solve_dfs(self):
        def dfs(col, board):
            if col == self.n: return board
            for row in range(self.n):
                safe = True
                for i in range(col):
                    if board[i] == row or abs(board[i] - row) == col - i:
                        safe = False
                        break
                if safe:
                    board[col] = row
                    res = dfs(col + 1, board)
                    if res: return res
                    board[col] = -1
            return None
        return dfs(0, [-1]*self.n)

    def get_dfs_steps(self):
        steps = []
        board = [-1] * self.n
        steps.append(list(board))
        def dfs(col):
            if col == self.n: return True
            for row in range(self.n):
                safe = True
                for i in range(col):
                    if board[i] == row or abs(board[i] - row) == col - i:
                        safe = False; break
                if safe:
                    board[col] = row
                    steps.append(list(board))
                    if dfs(col + 1): return True
                    board[col] = -1
                    steps.append(list(board))
            return False
        dfs(0)
        return steps

    def get_hc_steps(self):
        steps = []
        while True:
            board = [random.randint(0, self.n - 1) for _ in range(self.n)]
            steps.append(list(board))
            while True:
                current_conflicts = self.get_conflicts(board)
                if current_conflicts == 0: return steps
                best_conflicts, best_board = current_conflicts, list(board)
                for i in range(self.n):
                    original_val = board[i]
                    for j in range(self.n):
                        if j != original_val:
                            board[i] = j
                            c = self.get_conflicts(board)
                            if c < best_conflicts:
                                best_conflicts, best_board = c, list(board)
                    board[i] = original_val
                
                if best_conflicts >= current_conflicts:
                    break 
                board = list(best_board)
                steps.append(list(board))

    def get_mc_steps(self, max_steps=2000):
        steps = []
        board = []
        
        # 1. Greedy Initialization 
        for col in range(self.n):
            min_c = float('inf')
            best_r = []
            for row in range(self.n):
                c = 0
                for prev_col in range(col):
                    pr = board[prev_col]
                    if pr == row or abs(pr - row) == abs(prev_col - col):
                        c += 1
                if c < min_c:
                    min_c = c
                    best_r = [row]
                elif c == min_c:
                    best_r.append(row)
            board.append(random.choice(best_r))
            
        steps.append(list(board))
        
        # 2. Main Min-Conflicts Loop
        for _ in range(max_steps):
            if self.get_conflicts(board) == 0: break
            
            conflicted_cols = []
            for col in range(self.n):
                row = board[col]
                is_conflicted = False
                for c in range(self.n):
                    if c != col:
                        if board[c] == row or abs(board[c] - row) == abs(c - col):
                            is_conflicted = True
                            break
                if is_conflicted:
                    conflicted_cols.append(col)
                    
            if not conflicted_cols: break
            
            col_to_fix = random.choice(conflicted_cols)
            min_c = float('inf')
            best_vals = []
            
            for val in range(self.n):
                board[col_to_fix] = val
                c = self.get_conflicts(board)
                if c < min_c:
                    min_c = c
                    best_vals = [val]
                elif c == min_c:
                    best_vals.append(val)
                    
            board[col_to_fix] = random.choice(best_vals)
            steps.append(list(board))
            
        return steps


# --- ANTARMUKA GRAFIS PYGAME ---
pygame.init()

# Layar diperlebar menjadi 1200 untuk memuat 2 papan
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tsaritsa: Searching for Gnosis")

base_path = os.path.dirname(os.path.abspath(__file__))
asset_folder = "Assets"

# 1. Memuat Gambar Gnosis
gnosis_filenames = [
    "gnosis_Anemo.png", "gnosis_Cryo.png", "gnosis_Dendro.png", "gnosis_Electro.png",
    "gnosis_Geo.png", "gnosis_hydro.png", "gnosis_Hydro-focalors.png", "gnosis_pyro.png"
]
gnosis_images = []
for filename in gnosis_filenames:
    try:
        img_path = os.path.join(base_path, asset_folder, filename)
        img = pygame.image.load(img_path).convert_alpha()
        gnosis_images.append(img)
    except Exception:
        gnosis_images.append(None)

# 2. Memuat Gambar Karakter Visual Novel
try:
    img_phanes = pygame.image.load(os.path.join(base_path, asset_folder, "Phanes_Dominance.png")).convert_alpha()
except Exception:
    img_phanes = None

try:
    img_tsaritsa = pygame.image.load(os.path.join(base_path, asset_folder, "Tsaritsa_Focus.png")).convert_alpha()
except Exception:
    img_tsaritsa = None


COLOR_BG = (15, 20, 30)
COLOR_TILE_DARK = (30, 40, 60)
COLOR_TILE_LIGHT = (50, 65, 90)
COLOR_TSARITSA = (150, 230, 255)
COLOR_GNOSIS = (70, 150, 170)
COLOR_TEXT = (220, 230, 240)
COLOR_BTN = (45, 80, 120)
COLOR_BTN_HOVER = (60, 105, 155)
COLOR_DANGER = (180, 50, 50)

font_title = pygame.font.SysFont("cambria", 32, bold=True)
font_vn_name = pygame.font.SysFont("cambria", 26, bold=True)
font_subtitle = pygame.font.SysFont("cambria", 22, bold=True)
font_text = pygame.font.SysFont("cambria", 18)

class GameGUI:
    def __init__(self):
        self.available_sizes = [4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.size_index = 4 
        self.n = self.available_sizes[self.size_index]
        self.agent = PhanesAgent(self.n)
        
        self.state = "VN_STORY"
        self.dialogues = [
            ("Phanes", "Papan ini telah disiapkan khusus untuk permainan ini. Pecahan Descender Ketiga tersebar tak beraturan di seluruh penjuru Teyvat."),
            ("Phanes", "Memecah tubuhnya menjadi 8 bagian, menukarnya dengan kebangkitan mu..betapa naif dirinya itu."),
            ("Tsaritsa", "Aku akan mengumpulkan semua 8 bagian itu. Tidak peduli seberapa sulit jalannya, seberapa banyak rintangan, dan seberapa banyak kau menghalangiku."),
            ("Phanes", "Menarik. Descender ketiga memiliki kekuatan yang besar, dan hanya pecahannya saja bisa merubah tatanan Teyvat. Aku ingin melihat upaya mu mengumpulkan semua pecahan itu."),
            ("Tsaritsa", "Jangan meremehkan manusia, Phanes. Kau tidak akan mengerti bagaimana tekad manusia bisa membawa mereka untuk menjatuhkan Prinsip Langit mu itu"),
            ("Phanes", "HAHHAHAHAHHAH. OMONG KOSONG MU TIDAK AKAN BERGUNA DIHADAPAN KU SAJA, TSARITSA. BUKTIKAN SAJA KATA KATAMU ITU"),
            ("Phanes", "sekarang...BIARKAN PERMAINAN INI DIMULAI!!!")
        ]
        self.dialogue_idx = 0
        
        # Variabel Papan
        self.board = [-1] * self.n          # Papan utama (Solo / Clash)
        self.board_agent = [-1] * self.n    # Papan kedua (Khusus Agent di Mode VS)
        self.vs_winner = None
        
        self.message = ""
        self.times = {"DFS": 0.0, "HC": 0.0, "MC": 0.0}
        self.animation_steps = []
        self.anim_index = 0
        self.last_update_time = 0
        self.anim_speed = 100
        self.active_algo = ""
        
        # Tombol Clash Menu
        self.btn_anim_dfs = pygame.Rect(750, 270, 250, 35)
        self.btn_anim_hc = pygame.Rect(750, 315, 250, 35)
        self.btn_anim_mc = pygame.Rect(750, 360, 250, 35)
        
        # Tombol Pilih Algoritma VS
        self.btn_vs_dfs = pygame.Rect(WIDTH//2 - 175, 250, 350, 50)
        self.btn_vs_hc = pygame.Rect(WIDTH//2 - 175, 320, 350, 50)
        self.btn_vs_mc = pygame.Rect(WIDTH//2 - 175, 390, 350, 50)

    def update_board_size(self):
        self.agent = PhanesAgent(self.n)
        self.board = [-1] * self.n
        self.board_agent = [-1] * self.n

    def draw_character(self, name):
        is_phanes = (name == "Phanes")
        x_pos = 150 if is_phanes else WIDTH - 400
        y_pos = 150
        
        if is_phanes and img_phanes:
            scaled = pygame.transform.smoothscale(img_phanes, (450, 435))
            screen.blit(scaled, (x_pos, y_pos))
        elif not is_phanes and img_tsaritsa:
            scaled = pygame.transform.smoothscale(img_tsaritsa, (450, 410))
            screen.blit(scaled, (x_pos, y_pos))
        else:
            color = (60, 70, 90) if is_phanes else (100, 140, 160)
            pygame.draw.ellipse(screen, color, (x_pos, y_pos + 150, 250, 350))
            pygame.draw.circle(screen, color, (x_pos + 125, y_pos + 100), 70)

    def draw_vn_scene(self):
        screen.fill(COLOR_BG)
        speaker, text = self.dialogues[self.dialogue_idx]
        self.draw_character(speaker)
        
        name_rect = pygame.Rect(50, HEIGHT - 200, 200, 40)
        pygame.draw.rect(screen, COLOR_BTN, name_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_TSARITSA, name_rect, 2, border_radius=10)
        
        name_surf = font_vn_name.render(speaker, True, COLOR_TEXT)
        screen.blit(name_surf, (name_rect.x + 20, name_rect.y + 5))

        tb_surface = pygame.Surface((WIDTH - 100, 130), pygame.SRCALPHA)
        tb_surface.fill((10, 15, 25, 200))
        screen.blit(tb_surface, (50, HEIGHT - 150))
        pygame.draw.rect(screen, COLOR_TILE_LIGHT, (50, HEIGHT - 150, WIDTH - 100, 130), 2)
        
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            if font_text.size(current_line + word)[0] < WIDTH - 150:
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for i, line in enumerate(lines):
            text_surf = font_text.render(line, True, COLOR_TEXT)
            screen.blit(text_surf, (70, HEIGHT - 130 + (i * 25)))

        hint = font_text.render("[Klik di mana saja untuk lanjut...]", True, COLOR_TILE_LIGHT)
        screen.blit(hint, (WIDTH - 300, HEIGHT - 40))

    def draw_empty_target(self, x, y, size):
        m = size * 0.35
        points = [(x + size/2, y + m), (x + size - m, y + size/2),
                  (x + size/2, y + size - m), (x + m, y + size/2)]
        pygame.draw.polygon(screen, COLOR_GNOSIS, points, max(1, int(size*0.05)))

    def draw_gnosis_piece(self, x, y, size, col_index):
        img = gnosis_images[col_index % len(gnosis_images)]
        if img:
            img_size = int(size * 0.8) 
            scaled_img = pygame.transform.smoothscale(img, (img_size, img_size))
            img_x = x + (size - img_size) // 2
            img_y = y + (size - img_size) // 2
            screen.blit(scaled_img, (img_x, img_y))
        else:
            m = size * 0.2
            points = [
                (x + m, y + size - m), (x + size - m, y + size - m), 
                (x + size - m*0.8, y + m*1.2), (x + size*0.7, y + size*0.5), 
                (x + size/2, y + m), (x + size*0.3, y + size*0.5), 
                (x + m*0.8, y + m*1.2)
            ]
            pygame.draw.polygon(screen, COLOR_TSARITSA, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, max(1, int(size*0.03)))

    def draw_menu(self):
        screen.fill(COLOR_BG)
        title = font_title.render("TSARITSA: SEARCHING FOR GNOSIS", True, COLOR_TSARITSA)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        lbl_size = font_subtitle.render(f"Ukuran Papan (N): {self.n} x {self.n}", True, COLOR_TEXT)
        screen.blit(lbl_size, (WIDTH//2 - lbl_size.get_width()//2, 160))
        
        pygame.draw.rect(screen, COLOR_BTN, (WIDTH//2 - 130, 155, 40, 40), border_radius=5)
        pygame.draw.rect(screen, COLOR_BTN, (WIDTH//2 + 90, 155, 40, 40), border_radius=5)
        screen.blit(font_title.render("<", True, COLOR_TEXT), (WIDTH//2 - 120, 155))
        screen.blit(font_title.render(">", True, COLOR_TEXT), (WIDTH//2 + 100, 155))

        buttons = ["1. Solo Player", "2. Solo vs Phanes (Balapan)", "3. Agent vs Agent (Benchmark)"]
        for i, text in enumerate(buttons):
            btn_surface = font_subtitle.render(text, True, COLOR_TEXT)
            rect = pygame.Rect(WIDTH//2 - 175, 240 + i*70, 350, 50)
            mouse_pos = pygame.mouse.get_pos()
            color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else COLOR_BTN
            pygame.draw.rect(screen, color, rect, border_radius=8)
            screen.blit(btn_surface, (WIDTH//2 - btn_surface.get_width()//2, 250 + i*70))

    def draw_button(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else COLOR_BTN
        pygame.draw.rect(screen, color, rect, border_radius=5)
        txt_surf = font_text.render(text, True, COLOR_TEXT)
        screen.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width())//2, rect.y + 8))

    # --- FUNGSI GENERIK MENGGAMBAR PAPAN ---
    def draw_grid(self, board_array, offset_x, offset_y, tile_size):
        conflicts = set()
        for i in range(self.n):
            if board_array[i] == -1: continue
            for j in range(i + 1, self.n):
                if board_array[j] == -1: continue
                if board_array[i] == board_array[j] or abs(board_array[i] - board_array[j]) == j - i:
                    conflicts.add(i); conflicts.add(j)

        for row in range(self.n):
            for col in range(self.n):
                color = COLOR_TILE_LIGHT if (row + col) % 2 == 0 else COLOR_TILE_DARK
                x = offset_x + col * tile_size
                y = offset_y + row * tile_size
                
                is_danger = (col in conflicts) and (board_array[col] == row)
                if is_danger:
                    pygame.draw.rect(screen, COLOR_DANGER, (x, y, tile_size, tile_size))
                else:
                    pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))
                
                if board_array[col] == row:
                    self.draw_gnosis_piece(x, y, tile_size, col)
                else:
                    self.draw_empty_target(x, y, tile_size)

    # --- RENDERER KHUSUS SOLO & CLASH ---
    def draw_solo_or_clash(self):
        # Hitung ukuran papan di sisi kiri
        board_pixel_size = min(600, HEIGHT - 80)
        tile_size = max(10, board_pixel_size // self.n) 
        offset_x = 50
        offset_y = (HEIGHT - (tile_size * self.n)) // 2
        
        self.draw_grid(self.board, offset_x, offset_y, tile_size)

        # Panel UI di sebelah kanan
        panel_x = 720
        pygame.draw.line(screen, COLOR_TILE_LIGHT, (panel_x-20, 50), (panel_x-20, HEIGHT-50), 2)
        
        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            screen.blit(font_text.render(line, True, COLOR_TSARITSA), (panel_x, 50 + (i*25)))
        
        if self.state in ["CLASH_MENU", "ANIMATING"]:
            screen.blit(font_subtitle.render("Waktu Kalkulasi Phanes:", True, COLOR_TEXT), (panel_x, 160))
            
            str_dfs = f"{self.times['DFS']:.5f} detik" if self.times['DFS'] > 0 else "Belum diuji"
            str_hc = f"{self.times['HC']:.5f} detik" if self.times['HC'] > 0 else "Belum diuji"
            str_mc = f"{self.times['MC']:.5f} detik" if self.times['MC'] > 0 else "Belum diuji"
            
            screen.blit(font_text.render(f"1. DFS: {str_dfs}", True, COLOR_TEXT), (panel_x, 190))
            screen.blit(font_text.render(f"2. Hill Climb: {str_hc}", True, COLOR_TEXT), (panel_x, 215))
            screen.blit(font_text.render(f"3. Min-Conflict: {str_mc}", True, COLOR_TEXT), (panel_x, 240))
            
            if self.state == "CLASH_MENU":
                self.draw_button(self.btn_anim_dfs, "Jalankan DFS")
                self.draw_button(self.btn_anim_hc, "Jalankan Hill Climb")
                self.draw_button(self.btn_anim_mc, "Jalankan Min-Conflicts")

        btn_back = pygame.Rect(panel_x, HEIGHT - 90, 250, 40)
        self.draw_button(btn_back, "Kembali ke Menu Utama")
        self.btn_back_rect = btn_back

    # --- RENDERER KHUSUS MODE VS (DUAL BOARD) ---
    def draw_vs_menu(self):
        screen.fill(COLOR_BG)
        title = font_title.render("PILIH ALGORITMA LAWAN (PHANES)", True, COLOR_TSARITSA)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        self.draw_button(self.btn_vs_dfs, "1. Lawan DFS")
        self.draw_button(self.btn_vs_hc, "2. Lawan Hill Climbing")
        self.draw_button(self.btn_vs_mc, "3. Lawan Min-Conflicts")
        
        btn_back = pygame.Rect(WIDTH//2 - 175, HEIGHT - 100, 350, 50)
        self.draw_button(btn_back, "Kembali ke Menu")
        self.btn_back_rect = btn_back

    def draw_vs_play(self):
        board_pixel_size = min(480, HEIGHT - 180)
        self.vs_tile_size = max(10, board_pixel_size // self.n) 
        
        # Papan Pemain (Kiri)
        offset_x1 = 50
        offset_y1 = 100
        screen.blit(font_subtitle.render("Papan Tsaritsa (Kamu)", True, COLOR_TSARITSA), (offset_x1, 60))
        self.draw_grid(self.board, offset_x1, offset_y1, self.vs_tile_size)
        
        # Papan Agent (Kanan)
        offset_x2 = 650
        offset_y2 = 100
        screen.blit(font_subtitle.render(f"Papan Phanes ({self.active_algo})", True, COLOR_DANGER), (offset_x2, 60))
        self.draw_grid(self.board_agent, offset_x2, offset_y2, self.vs_tile_size)

        # Informasi di Bawah
        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            screen.blit(font_subtitle.render(line, True, COLOR_TEXT), (50, HEIGHT - 70 + (i*25)))

        btn_back = pygame.Rect(WIDTH - 300, HEIGHT - 80, 250, 50)
        self.draw_button(btn_back, "Menyerah / Kembali")
        self.btn_back_rect = btn_back

    # --- HANDLE KLIK ---
    def handle_click(self, pos):
        x, y = pos
        
        if self.state == "VN_STORY":
            self.dialogue_idx += 1
            if self.dialogue_idx >= len(self.dialogues):
                self.state = "MENU"
            return

        if self.state == "MENU":
            if 155 <= y <= 195:
                if WIDTH//2 - 130 <= x <= WIDTH//2 - 90 and self.size_index > 0:
                    self.size_index -= 1
                    self.n = self.available_sizes[self.size_index]
                    self.update_board_size()
                elif WIDTH//2 + 90 <= x <= WIDTH//2 + 130 and self.size_index < len(self.available_sizes) - 1:
                    self.size_index += 1
                    self.n = self.available_sizes[self.size_index]
                    self.update_board_size()
                    
            if WIDTH//2 - 175 <= x <= WIDTH//2 + 175:
                if 240 <= y <= 290: 
                    self.state = "SOLO"
                    self.board = [-1] * self.n
                    self.message = "Setiap kolom memiliki satu bidak.\nKlik petak kosong untuk\nmemindahkannya.\nKlik bidak untuk mencabutnya."
                elif 310 <= y <= 360: 
                    self.state = "VS_MENU"
                elif 380 <= y <= 430: 
                    self.state = "CLASH_MENU"
                    self.board = [-1] * self.n
                    self.times = {"DFS": 0.0, "HC": 0.0, "MC": 0.0}
                    self.message = "Mode Benchmark AI.\nPilih algoritma untuk diuji."
            return

        if self.state == "VS_MENU":
            if self.btn_back_rect.collidepoint(pos): self.state = "MENU"
            elif self.btn_vs_dfs.collidepoint(pos): self.start_vs_agent("DFS")
            elif self.btn_vs_hc.collidepoint(pos): self.start_vs_agent("HC")
            elif self.btn_vs_mc.collidepoint(pos): self.start_vs_agent("MC")
            return

        # Handle Tombol Kembali Generik
        if hasattr(self, 'btn_back_rect') and self.btn_back_rect.collidepoint(pos):
            self.state = "MENU"
            return

        # Klik Papan di Mode SOLO
        if self.state == "SOLO":
            board_pixel_size = min(600, HEIGHT - 80)
            tile_size = max(10, board_pixel_size // self.n) 
            offset_x = 50
            offset_y = (HEIGHT - (tile_size * self.n)) // 2
            
            if offset_x <= x <= offset_x + tile_size*self.n and offset_y <= y <= offset_y + tile_size*self.n:
                col = (x - offset_x) // tile_size
                row = (y - offset_y) // tile_size
                
                if self.board[col] == row: self.board[col] = -1 
                else: self.board[col] = row 
                
                c = self.agent.get_conflicts(self.board)
                if -1 not in self.board and c == 0:
                    self.message = "Kemenangan Mutlak!\nSemua Gnosis telah dikumpulkan!"
                else:
                    placed = self.n - self.board.count(-1)
                    self.message = f"Bidak di papan: {placed}/{self.n}\nJumlah Konflik: {c}"

        # Klik Papan Kiri di Mode VS_AGENT_PLAY
        if self.state == "VS_AGENT_PLAY" and not self.vs_winner:
            offset_x = 50
            offset_y = 100
            if offset_x <= x <= offset_x + self.vs_tile_size*self.n and offset_y <= y <= offset_y + self.vs_tile_size*self.n:
                col = (x - offset_x) // self.vs_tile_size
                row = (y - offset_y) // self.vs_tile_size
                
                if self.board[col] == row: self.board[col] = -1 
                else: self.board[col] = row 
                
                if -1 not in self.board and self.agent.get_conflicts(self.board) == 0:
                    self.vs_winner = "Player"
                    self.message = "KAMU MENANG! Berhasil mengalahkan kecerdasan Phanes!"

        # Klik Menu Clash
        if self.state == "CLASH_MENU":
            if self.btn_anim_dfs.collidepoint(pos): self.play_animation("DFS")
            elif self.btn_anim_hc.collidepoint(pos): self.play_animation("HC")
            elif self.btn_anim_mc.collidepoint(pos): self.play_animation("MC")

    def start_vs_agent(self, algo):
        self.state = "VS_AGENT_PLAY"
        self.active_algo = algo
        self.board = [-1] * self.n
        self.board_agent = [-1] * self.n
        self.vs_winner = None
        self.message = f"Balapan dimulai! Kalahkan {algo} milik Phanes!"
        
        # Kecepatan Animasi Phanes disesuaikan
        if algo == "DFS":
            self.animation_steps = self.agent.get_dfs_steps()
            self.anim_speed = 5 
        elif algo == "HC":
            self.animation_steps = self.agent.get_hc_steps()
            self.anim_speed = 100
        elif algo == "MC":
            self.animation_steps = self.agent.get_mc_steps()
            self.anim_speed = 150
            
        self.anim_index = 0
        self.last_update_time = pygame.time.get_ticks()

    def play_animation(self, algo):
        self.active_algo = algo
        self.message = f"Phanes sedang memproses\nalgoritma {algo}...\n(Harap tunggu)"
        self.draw_solo_or_clash()
        pygame.display.flip()

        start_time = time.perf_counter()
        
        if algo == "DFS":
            self.animation_steps = self.agent.get_dfs_steps(); self.anim_speed = 5 
        elif algo == "HC":
            self.animation_steps = self.agent.get_hc_steps(); self.anim_speed = 100
        elif algo == "MC":
            self.animation_steps = self.agent.get_mc_steps(); self.anim_speed = 150
            
        self.times[algo] = time.perf_counter() - start_time

        self.state = "ANIMATING"
        self.anim_index = 0
        self.last_update_time = pygame.time.get_ticks()

# --- GAME LOOP ---
try:
    game = GameGUI()
    clock = pygame.time.Clock()
    running = True

    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    game.handle_click(event.pos)

        # Update Animasi (Untuk Mode Clash)
        if game.state == "ANIMATING":
            if current_time - game.last_update_time > game.anim_speed:
                if game.anim_index < len(game.animation_steps):
                    game.board = game.animation_steps[game.anim_index]
                    game.message = f"Langkah: {game.anim_index}/{len(game.animation_steps)}"
                    game.anim_index += 1
                    game.last_update_time = current_time
                else:
                    game.state = "CLASH_MENU"
                    game.message = f"Pencarian {game.active_algo} Selesai!\nPilih algoritma lain."
                    
        # Update Animasi (Untuk Papan Agent di Mode VS)
        elif game.state == "VS_AGENT_PLAY" and not game.vs_winner:
            if current_time - game.last_update_time > game.anim_speed:
                if game.anim_index < len(game.animation_steps):
                    game.board_agent = game.animation_steps[game.anim_index]
                    game.anim_index += 1
                    game.last_update_time = current_time
                else:
                    # Agent selesai lebih dulu
                    if -1 not in game.board_agent and game.agent.get_conflicts(game.board_agent) == 0:
                        game.vs_winner = "Agent"
                        game.message = f"PHANES MENANG! Algoritma {game.active_algo} terlalu cepat untuk manusia."

        # RENDER LAYAR
        screen.fill(COLOR_BG)

        if game.state == "VN_STORY":
            game.draw_vn_scene()
        elif game.state == "MENU":
            game.draw_menu()
        elif game.state == "VS_MENU":
            game.draw_vs_menu()
        elif game.state == "VS_AGENT_PLAY":
            game.draw_vs_play()
        else:
            # Draw Mode Solo, Clash Menu, dan Animating Clash
            game.draw_solo_or_clash()

        pygame.display.flip()
        clock.tick(60)

except Exception as e:
    import traceback
    print("\n" + "="*40)
    print("TERJADI ERROR TERSEMBUNYI:")
    traceback.print_exc()
    print("="*40)
    input("\nTekan Enter di terminal untuk keluar...")
finally:
    pygame.quit()
    sys.exit()