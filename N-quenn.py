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

# Setup Layar Fleksibel / Resizable
screen = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
pygame.display.set_caption("Tsaritsa: Searching for Gnosis")
is_fullscreen = False

base_path = os.path.dirname(os.path.abspath(__file__))
asset_folder = "Assets"

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

# --- 2. Memuat Gambar Karakter Visual Novel (Berbagai Ekspresi) ---
phanes_sprites = {}
tsaritsa_sprites = {}

phanes_files = {
    "Mengejek": "Phanes_Taunting_Right.png",
    "Bingung": "Phanes_Confused_Front.png",
    "Santai": "Phanes_Shrug_Front.png",
    "Menatap": "Phanes_Stare_Front.png",
    "Tersinggung": "Phanes_Offended_Front.png",
    "Pergi": "Phanes_Leaving_Left.png",
    "Buka_Portal": "Phanes_Leaving_Open_Portal_Left.png",
    "Tutup_Portal": "Phanes_Leaving_Closed_Portal.png",
    "Defeat": "Phanes_Defeat_Front.png"
}

tsaritsa_files = {
    "Menahan": "Tsaritsa_Grief_Left.png",
    "Murka": "Tsaritsa_Angry_Left.png",
    "Sabar": "Tsaritsa_Closed_Eyes_Right.png",
    "Merenung": "Tsaritsa_Reminiscing_Right.png",
    "Santai": "Tsaritsa_Focus_Left.png",
    "Defeat": "Tsaritsa_Defeat_Left.png"
}

for expr, filename in phanes_files.items():
    try:
        path = os.path.join(base_path, asset_folder, filename)
        phanes_sprites[expr] = pygame.image.load(path).convert_alpha()
    except Exception:
        phanes_sprites[expr] = None

for expr, filename in tsaritsa_files.items():
    try:
        path = os.path.join(base_path, asset_folder, filename)
        tsaritsa_sprites[expr] = pygame.image.load(path).convert_alpha()
    except Exception:
        tsaritsa_sprites[expr] = None


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
            ("Phanes", "Mengejek", "Akhirnya."),
            ("Phanes", "Mengejek", "Tubuh Descender Ke-3 berhasil saya bagi menjadi 8 bagian."),
            ("Tsaritsa", "Menahan", "..."),
            ("Phanes", "Mengejek", "Papan ini merepresentasikan posisi bagian-bagian tubuh Descender Ke-3 di seluruh penjuru Teyvat."),
            ("Phanes", "Mengejek", "Namun karena kekuatan yang tersimpan dalam tiap bagian terlalu kuat..."),
            ("Phanes", "Mengejek", "Bagian nya harus disebar diposisi yang spesifik, Heh. Bahkan dalam kematiannya dia tetap menjadi beban di hadapan saya-"),
            ("Tsaritsa", "Menahan", "Cukup."),
            ("Phanes", "Bingung", "Hm?"),
            ("Tsaritsa", "Menahan", "Setiap kata yang keluar dari mulut mu adalah ejekan terhadap pengorbanannya."),
            ("Phanes", "Santai", "Ah, saya lupa. Sebagai syarat dapat membagi tubuhnya adalah untuk membangkitkan kamu kembali."),
            ("Phanes", "Santai", "Tapi kenapa kamu marah?"),
            ("Phanes", "Santai", "Saya telah membangkitkan kamu kembali, harusnya kamu bersyukur-"),
            ("Tsaritsa", "Menahan", "BERSYUKUR?!"),
            ("Tsaritsa", "Menahan", "SETELAH KAMU MEMBUNUH SUAMI DAN ANAKKU?!"),
            ("Phanes", "Santai", "..."),
            ("Phanes", "Menatap", "Apa yang kamu dan dia lakukan mengancam kehidupan manusia. Yang saya lakukan adalah akibat dari rasa ''Cinta'' saya terhadap manusia."),
            ("Tsaritsa", "Menahan", "''Cinta''?"),
            ("Tsaritsa", "Menahan", "Perbuatan dan tindakan mu selama ini hanya siklus untuk menggambarkan kamu adalah pahlawan. Tapi kenyataan nya adalah kamu adalah sebab dari kesengsaraan manuasia."),
            ("Tsaritsa", "Murka", "Bahkan kamu tidak mengetahui arti sebenarnya dari ''Cinta'' Phanes."),
            ("Phanes", "Tersinggung", "..."),
            ("Phanes", "Tersinggung", "Jaga"),
            ("Phanes", "Tersinggung", "Jaga mulutmu"),
            ("Tsaritsa", "Murka", "Aku akan mengumpulkan semua 8 bagian itu. Tidak peduli seberapa sulit jalannya, seberapa banyak rintangan, dan seberapa banyak kau menghalangiku."),
            ("Phanes", "Tersinggung", "Hmph."),
            ("Phanes", "Pergi", "Silahkan dan coba."),
            ("Phanes", "Buka_Portal", ""),
            ("Phanes", "Tutup_Portal", ""),
            ("Tsaritsa", "Murka", "..."),
            ("Tsaritsa", "Menahan", "..."),
            ("Tsaritsa", "Sabar", "..."),
            ("Tsaritsa", "Merenung", "█████████")
        ]
        self.dialogue_idx = 0
        
        self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.board_agent = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.vs_winner = None
        
        self.message = ""
        self.times = {"DFS": 0.0, "HC": 0.0, "MC": 0.0}
        self.animation_steps = []
        self.anim_index = 0
        self.last_update_time = 0
        self.anim_speed = 100
        self.active_algo = ""
        
        # Variabel Timer Player
        self.player_start_time = 0.0
        self.player_timer = 0.0
        
        # Penampung Rect Tombol Dinamis
        self.btn_anim_dfs_rect = pygame.Rect(0,0,0,0)
        self.btn_anim_hc_rect = pygame.Rect(0,0,0,0)
        self.btn_anim_mc_rect = pygame.Rect(0,0,0,0)
        self.btn_vs_dfs_rect = pygame.Rect(0,0,0,0)
        self.btn_vs_hc_rect = pygame.Rect(0,0,0,0)
        self.btn_vs_mc_rect = pygame.Rect(0,0,0,0)
        self.btn_acak_rect = pygame.Rect(0,0,0,0)
        self.btn_reset_rect = pygame.Rect(0,0,0,0)
        self.btn_back_rect = pygame.Rect(0,0,0,0)

    def update_board_size(self):
        self.agent = PhanesAgent(self.n)
        self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.board_agent = [random.randint(0, self.n - 1) for _ in range(self.n)]

    def draw_character(self, name, expression):
        w, h = screen.get_width(), screen.get_height()
        is_phanes = (name == "Phanes")
        x_pos = 150 if is_phanes else w - 400
        y_pos = 150
        
        # Ambil gambar dari kamus sprite berdasarkan ekspresi, dengan fallback aman
        sprite_dict = phanes_sprites if is_phanes else tsaritsa_sprites
        img = sprite_dict.get(expression)
        if not img:
            # Ambil nilai pertama yang tersedia jika ekspresi tidak ditemukan
            img = next(iter(sprite_dict.values())) if sprite_dict else None
        
        if img:
            scaled = pygame.transform.smoothscale(img, (450, 400))
            screen.blit(scaled, (x_pos, y_pos))
        else:
            color = (60, 70, 90) if is_phanes else (100, 140, 160)
            pygame.draw.ellipse(screen, color, (x_pos, y_pos + 150, 250, 350))
            pygame.draw.circle(screen, color, (x_pos + 125, y_pos + 100), 70)

    def draw_vn_scene(self):
        screen.fill(COLOR_BG)
        w, h = screen.get_width(), screen.get_height()
        
        # Unpack 3 elemen (speaker, expression, text)
        speaker, expression, text = self.dialogues[self.dialogue_idx]
        self.draw_character(speaker, expression)
        
        name_rect = pygame.Rect(50, h - 200, 200, 40)
        pygame.draw.rect(screen, COLOR_BTN, name_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_TSARITSA, name_rect, 2, border_radius=10)
        
        name_surf = font_vn_name.render(speaker, True, COLOR_TEXT)
        screen.blit(name_surf, (name_rect.x + 20, name_rect.y + 5))

        tb_surface = pygame.Surface((w - 100, 130), pygame.SRCALPHA)
        tb_surface.fill((10, 15, 25, 200))
        screen.blit(tb_surface, (50, h - 150))
        pygame.draw.rect(screen, COLOR_TILE_LIGHT, (50, h - 150, w - 100, 130), 2)
        
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            if font_text.size(current_line + word)[0] < w - 150:
                current_line += word + " "
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for i, line in enumerate(lines):
            text_surf = font_text.render(line, True, COLOR_TEXT)
            screen.blit(text_surf, (70, h - 130 + (i * 25)))

        hint = font_text.render("[Klik / Tekan Spasi untuk lanjut...]", True, COLOR_TILE_LIGHT)
        screen.blit(hint, (w - 350, h - 40))

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

    def draw_gameplay_characters(self, phanes_expr, tsaritsa_expr=None, tsaritsa_on_left=False):
        w, h = screen.get_width(), screen.get_height()
        
        # 1. Phanes di Kiri Atas
        p_img = phanes_sprites.get(phanes_expr) or phanes_sprites.get("Mengejek")
        if p_img:
            scaled_p = pygame.transform.smoothscale(p_img, (180, 160))
            screen.blit(scaled_p, (20, 20))
            lbl_p = font_text.render("Phanes", True, COLOR_DANGER)
            screen.blit(lbl_p, (20, 185))

        # 2. Tsaritsa
        if tsaritsa_expr:
            t_img = tsaritsa_sprites.get(tsaritsa_expr) or tsaritsa_sprites.get("Murka")
            if t_img:
                scaled_t = pygame.transform.smoothscale(t_img, (180, 160))
                
                # ATUR POSISI menggunakan 'w' dan 'h' dinamis
                if tsaritsa_on_left:
                    t_x = 20
                    t_y = h - 220
                    lbl_x = 20
                    lbl_y = h - 60
                else:
                    t_x = w - 200
                    t_y = h - 220
                    lbl_x = w - 200
                    lbl_y = h - 60
                
                screen.blit(scaled_t, (t_x, t_y))
                lbl_t = font_text.render("Tsaritsa", True, COLOR_TSARITSA)
                screen.blit(lbl_t, (lbl_x, lbl_y))

    def draw_menu(self):
        screen.fill(COLOR_BG)
        w, h = screen.get_width(), screen.get_height()
        title = font_title.render("TSARITSA: SEARCHING FOR GNOSIS", True, COLOR_TSARITSA)
        screen.blit(title, (w//2 - title.get_width()//2, 80))

        lbl_text = f"Ukuran Papan (N): {self.n} x {self.n}"
        lbl_size = font_subtitle.render(lbl_text, True, COLOR_TEXT)
        screen.blit(lbl_size, (w//2 - lbl_size.get_width()//2, 160))
        
        half_lbl = lbl_size.get_width() // 2
        left_btn_x = w//2 - half_lbl - 60
        right_btn_x = w//2 + half_lbl + 20
        
        pygame.draw.rect(screen, COLOR_BTN, (left_btn_x, 155, 40, 40), border_radius=5)
        pygame.draw.rect(screen, COLOR_BTN, (right_btn_x, 155, 40, 40), border_radius=5)
        screen.blit(font_title.render("<", True, COLOR_TEXT), (left_btn_x + 10, 155))
        screen.blit(font_title.render(">", True, COLOR_TEXT), (right_btn_x + 10, 155))

        buttons = ["1. Solo Player", "2. Solo vs Phanes (Balapan)", "3. Agent vs Agent (Benchmark)"]
        for i, text in enumerate(buttons):
            btn_surface = font_subtitle.render(text, True, COLOR_TEXT)
            rect = pygame.Rect(w//2 - 175, 240 + i*70, 350, 50)
            mouse_pos = pygame.mouse.get_pos()
            color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else COLOR_BTN
            pygame.draw.rect(screen, color, rect, border_radius=8)
            screen.blit(btn_surface, (w//2 - btn_surface.get_width()//2, 250 + i*70))

    def draw_button(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else COLOR_BTN
        pygame.draw.rect(screen, color, rect, border_radius=5)
        txt_surf = font_text.render(text, True, COLOR_TEXT)
        screen.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width())//2, rect.y + 8))

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

    def draw_solo_or_clash(self):
        w, h = screen.get_width(), screen.get_height()
        
        # Hitung ukuran papan di sisi kiri menggunakan 'h' dinamis
        board_pixel_size = min(500, h - 150)
        tile_size = max(10, board_pixel_size // self.n) 
        offset_x = 220  # Digeser sedikit ke kanan agar muat potret Phanes di kiri
        offset_y = (h - (tile_size * self.n)) // 2
        
        self.draw_grid(self.board, offset_x, offset_y, tile_size)

        # --- ATUR EKSPRESI BERDASARKAN KONFLIK (MODE 1 & 3) ---
        conflicts = self.agent.get_conflicts(self.board)
        is_solved = (-1 not in self.board and conflicts == 0)

        if self.state == "SOLO":
            if is_solved:
                p_expr = "Defeat" # Phanes kesal pemain menang
                t_expr = "Murka"       # Tsaritsa menang
            elif conflicts > 6:
                p_expr = "Mengejek"    # Phanes mengejek banyak konflik
                t_expr = "Menahan"
            else:
                p_expr = "Santai"
                t_expr = "Santai"
            self.draw_gameplay_characters(p_expr, t_expr, tsaritsa_on_left=True)
        elif self.state in ["CLASH_MENU", "ANIMATING"]:
            # Mode 3: Hanya Phanes dengan 2 state (Berpikir/Animasi vs Selesai)
            p_expr = "Bingung" if self.state == "ANIMATING" else "Santai"
            self.draw_gameplay_characters(p_expr, None)

        # Panel UI di sebelah kanan
        panel_x = 850
        pygame.draw.line(screen, COLOR_TILE_LIGHT, (panel_x-20, 50), (panel_x-20, h-50), 2)
        
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
            
            self.btn_anim_dfs_rect = pygame.Rect(panel_x, 280, 250, 35)
            self.btn_anim_hc_rect = pygame.Rect(panel_x, 325, 250, 35)
            self.btn_anim_mc_rect = pygame.Rect(panel_x, 370, 250, 35)
            
            if self.state == "CLASH_MENU":
                self.draw_button(self.btn_anim_dfs_rect, "Jalankan DFS")
                self.draw_button(self.btn_anim_hc_rect, "Jalankan Hill Climb")
                self.draw_button(self.btn_anim_mc_rect, "Jalankan Min-Conflicts")

        self.btn_acak_rect = pygame.Rect(panel_x, h - 190, 250, 40)
        self.draw_button(self.btn_acak_rect, "Acak Papan")
        
        self.btn_reset_rect = pygame.Rect(panel_x, h - 140, 250, 40)
        self.draw_button(self.btn_reset_rect, "Reset Papan")

        self.btn_back_rect = pygame.Rect(panel_x, h - 90, 250, 40)
        self.draw_button(self.btn_back_rect, "Kembali ke Menu Utama")

    def draw_vs_menu(self):
        screen.fill(COLOR_BG)
        w, h = screen.get_width(), screen.get_height()
        title = font_title.render("PILIH ALGORITMA LAWAN (PHANES)", True, COLOR_TSARITSA)
        screen.blit(title, (w//2 - title.get_width()//2, 100))
        
        self.btn_vs_dfs_rect = pygame.Rect(w//2 - 175, 250, 350, 50)
        self.btn_vs_hc_rect = pygame.Rect(w//2 - 175, 320, 350, 50)
        self.btn_vs_mc_rect = pygame.Rect(w//2 - 175, 390, 350, 50)
        self.btn_back_rect = pygame.Rect(w//2 - 175, h - 100, 350, 50)
        
        self.draw_button(self.btn_vs_dfs_rect, "1. Lawan DFS")
        self.draw_button(self.btn_vs_hc_rect, "2. Lawan Hill Climbing")
        self.draw_button(self.btn_vs_mc_rect, "3. Lawan Min-Conflicts")
        self.draw_button(self.btn_back_rect, "Kembali ke Menu")

    def draw_vs_play(self):
        w, h = screen.get_width(), screen.get_height()
        
        # Batasi max height papan agar menyisakan ruang lega di bawah menggunakan 'h' dinamis
        board_pixel_size = min((w - 150) // 2, h - 250)
        self.vs_tile_size = max(10, board_pixel_size // self.n) 
        actual_board_w = self.vs_tile_size * self.n
        
        # Papan Pemain (Tengah-Kiri)
        offset_x1 = 220
        offset_y1 = 100
        title_player = f"Papan Tsaritsa (Kamu) - {self.player_timer:.2f}s"
        screen.blit(font_subtitle.render(title_player, True, COLOR_TSARITSA), (offset_x1, 60))
        self.draw_grid(self.board, offset_x1, offset_y1, self.vs_tile_size)
        
        # Papan Agent (Kanan)
        offset_x2 = w - 50 - actual_board_w
        offset_y2 = 100
        screen.blit(font_subtitle.render(f"Papan Phanes ({self.active_algo})", True, COLOR_DANGER), (offset_x2, 60))
        self.draw_grid(self.board_agent, offset_x2, offset_y2, self.vs_tile_size)

        # --- ATUR 2 STATE (MENANG / KALAH) UNTUK MODE 2 ---
        if self.vs_winner == "Player":
            p_expr = "Defeat"
            t_expr = "Murka"
        elif self.vs_winner == "Agent":
            p_expr = "Mengejek"
            t_expr = "Defeat"
        else:
            p_expr = "Bingung" # Sedang bertanding / berpikir
            t_expr = "Santai"
            
        self.draw_gameplay_characters(p_expr, t_expr, tsaritsa_on_left=True)

        # Informasi di Bawah menggunakan 'h' dinamis
        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            screen.blit(font_subtitle.render(line, True, COLOR_TEXT), (220, h - 100 + (i*25)))

        btn_back = pygame.Rect(w - 280, h - 80, 250, 50)
        self.draw_button(btn_back, "Menyerah / Kembali")
        self.btn_back_rect = btn_back

    def handle_click(self, pos):
        x, y = pos
        w, h = screen.get_width(), screen.get_height()
        
        if self.state == "VN_STORY":
            self.dialogue_idx += 1
            if self.dialogue_idx >= len(self.dialogues):
                self.state = "MENU"
            return

        if self.state == "MENU":
            lbl_text = f"Ukuran Papan (N): {self.n} x {self.n}"
            half_lbl = font_subtitle.size(lbl_text)[0] // 2
            left_btn_x = w//2 - half_lbl - 60
            right_btn_x = w//2 + half_lbl + 20
            
            if 155 <= y <= 195:
                if left_btn_x <= x <= left_btn_x + 40 and self.size_index > 0:
                    self.size_index -= 1
                    self.n = self.available_sizes[self.size_index]
                    self.update_board_size()
                elif right_btn_x <= x <= right_btn_x + 40 and self.size_index < len(self.available_sizes) - 1:
                    self.size_index += 1
                    self.n = self.available_sizes[self.size_index]
                    self.update_board_size()
                    
            if w//2 - 175 <= x <= w//2 + 175:
                if 240 <= y <= 290: 
                    self.state = "SOLO"
                    self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
                    self.message = "Semua Gnosis telah diletakkan secara acak.\nGeser bidak di kolomnya masing-masing\nuntuk mencari posisi aman tanpa konflik."
                elif 310 <= y <= 360: 
                    self.state = "VS_MENU"
                elif 380 <= y <= 430: 
                    self.state = "CLASH_MENU"
                    self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
                    self.times = {"DFS": 0.0, "HC": 0.0, "MC": 0.0}
                    self.message = "Mode Benchmark AI.\nPilih algoritma untuk diuji."
            return

        if self.state == "VS_MENU":
            if self.btn_back_rect.collidepoint(pos): self.state = "MENU"
            elif self.btn_vs_dfs_rect.collidepoint(pos): self.start_vs_agent("DFS")
            elif self.btn_vs_hc_rect.collidepoint(pos): self.start_vs_agent("HC")
            elif self.btn_vs_mc_rect.collidepoint(pos): self.start_vs_agent("MC")
            return

        # Handle Tombol Acak, Reset, dan Kembali
        if self.btn_back_rect.collidepoint(pos):
            self.state = "MENU"
            return
            
        if self.btn_acak_rect.collidepoint(pos):
            if self.state in ["SOLO", "CLASH_MENU", "VS_AGENT_PLAY"]:
                self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
                if self.state != "CLASH_MENU":
                    self.message = "Papan pemain telah diacak ulang!"
            return

        if self.btn_reset_rect.collidepoint(pos):
            if self.state in ["SOLO", "CLASH_MENU", "VS_AGENT_PLAY"]:
                self.board = [0] * self.n  
                if self.state != "CLASH_MENU":
                    self.message = "Papan pemain telah di-reset!"
            return

        # Klik Papan di Mode SOLO (Menggunakan 'h' dinamis)
        if self.state == "SOLO":
            board_pixel_size = min(500, h - 150)
            tile_size = max(10, board_pixel_size // self.n) 
            offset_x = 220
            offset_y = (h - (tile_size * self.n)) // 2
            
            if offset_x <= x <= offset_x + tile_size*self.n and offset_y <= y <= offset_y + tile_size*self.n:
                col = (x - offset_x) // tile_size
                row = (y - offset_y) // tile_size
                
                self.board[col] = row 
                
                c = self.agent.get_conflicts(self.board)
                if c == 0:
                    self.message = "Kemenangan Mutlak!\nSemua Gnosis telah dikumpulkan!"
                else:
                    self.message = f"Jumlah Konflik saat ini: {c}"

        # Klik Papan Kiri di Mode VS_AGENT_PLAY (Menggunakan 'h' dinamis)
        if self.state == "VS_AGENT_PLAY" and not self.vs_winner:
            board_pixel_size = min((w - 150) // 2, h - 250)
            self.vs_tile_size = max(10, board_pixel_size // self.n) 
            
            offset_x1 = 220
            offset_y1 = 100
            
            if offset_x1 <= x <= offset_x1 + self.vs_tile_size*self.n and offset_y1 <= y <= offset_y1 + self.vs_tile_size*self.n:
                col = (x - offset_x1) // self.vs_tile_size
                row = (y - offset_y1) // self.vs_tile_size
                
                self.board[col] = row 
                
                if self.agent.get_conflicts(self.board) == 0:
                    self.vs_winner = "Player"
                    self.message = "KAMU MENANG! Berhasil mengalahkan kecerdasan Phanes!"

        # Klik Menu Clash
        if self.state == "CLASH_MENU":
            if self.btn_anim_dfs_rect.collidepoint(pos): self.play_animation("DFS")
            elif self.btn_anim_hc_rect.collidepoint(pos): self.play_animation("HC")
            elif self.btn_anim_mc_rect.collidepoint(pos): self.play_animation("MC")

    def start_vs_agent(self, algo):
        self.state = "VS_AGENT_PLAY"
        self.active_algo = algo
        self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.board_agent = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.vs_winner = None
        self.message = f"Balapan dimulai! Geser bidakmu dan kalahkan {algo} Phanes!"
        
        self.player_start_time = time.perf_counter()
        self.player_timer = 0.0
        
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
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    if game.state == "VN_STORY":
                        game.dialogue_idx += 1
                        if game.dialogue_idx >= len(game.dialogues):
                            game.state = "MENU"
                elif event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    is_fullscreen = False
                    screen = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
            elif event.type == pygame.VIDEORESIZE:
                if not is_fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

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
                    
        elif game.state == "VS_AGENT_PLAY" and not game.vs_winner:
            game.player_timer = time.perf_counter() - game.player_start_time
            
            if current_time - game.last_update_time > game.anim_speed:
                if game.anim_index < len(game.animation_steps):
                    game.board_agent = game.animation_steps[game.anim_index]
                    game.anim_index += 1
                    game.last_update_time = current_time
                else:
                    if -1 not in game.board_agent and game.agent.get_conflicts(game.board_agent) == 0:
                        game.vs_winner = "Agent"
                        game.message = f"PHANES MENANG! Algoritma {game.active_algo} terlalu cepat."

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