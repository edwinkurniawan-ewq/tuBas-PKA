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

    def solve_hill_climbing(self):
        while True:
            board = [random.randint(0, self.n - 1) for _ in range(self.n)]
            while True:
                current_conflicts = self.get_conflicts(board)
                if current_conflicts == 0: return board
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
                if best_conflicts >= current_conflicts: break
                board = best_board

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

    def solve_min_conflicts(self, max_steps=2000):
        board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        for _ in range(max_steps):
            if self.get_conflicts(board) == 0: return board
            conflicted_vars = []
            for i in range(self.n):
                for j in range(self.n):
                    if i != j and (board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j)):
                        conflicted_vars.append(i); break
            if not conflicted_vars: return board
            var = random.choice(conflicted_vars)
            min_conflicts, best_val = float('inf'), board[var]
            for val in range(self.n):
                board[var] = val
                c = self.get_conflicts(board)
                if c < min_conflicts:
                    min_conflicts, best_val = c, val
            board[var] = best_val
        return board

    def get_mc_steps(self, max_steps=2000):
        steps = []
        board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        steps.append(list(board))
        for _ in range(max_steps):
            if self.get_conflicts(board) == 0: break
            conflicted_vars = []
            for i in range(self.n):
                for j in range(self.n):
                    if i != j and (board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j)):
                        conflicted_vars.append(i); break
            if not conflicted_vars: break
            
            var = random.choice(conflicted_vars)
            min_conflicts, best_val = float('inf'), board[var]
            for val in range(self.n):
                board[var] = val
                c = self.get_conflicts(board)
                if c < min_conflicts:
                    min_conflicts, best_val = c, val
            board[var] = best_val
            steps.append(list(board))
        return steps


# --- ANTARMUKA GRAFIS PYGAME ---
pygame.init()

WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tsaritsa: Searching for Gnosis")

base_path = os.path.dirname(os.path.abspath(__file__))

# 1. Memuat Gambar Gnosis
base_path = os.path.dirname(os.path.abspath(__file__))
asset_folder = "Aset Gnosis(Bidak ratu)" # Nama subfolder tempat aset berada

# Daftar nama file yang sudah disesuaikan dengan ejaan barumu (pakai underscore)
gnosis_filenames = [
    "gnosis_Anemo.png", 
    "gnosis_Cryo.png", 
    "gnosis_Dendro.png", 
    "gnosis_Electro.png",
    "gnosis_Geo.png", 
    "gnosis_Hydro-focalors.png", 
    "gnosis_hydro.png", 
    "gnosis_pyro.png"
]

gnosis_images = []
for filename in gnosis_filenames:
    try:
        # Menggabungkan lokasi file script + nama folder + nama gambar
        img_path = os.path.join(base_path, asset_folder, filename)
        img = pygame.image.load(img_path).convert_alpha()
        gnosis_images.append(img)
    except Exception as e:
        print(f"Gagal memuat {filename}")
        gnosis_images.append(None)

# 2. Memuat Gambar Karakter Visual Novel (Jika Ada)
try:
    img_phanes = pygame.image.load(os.path.join(base_path, "phanes_sprite.png")).convert_alpha()
except Exception:
    img_phanes = None

try:
    img_tsaritsa = pygame.image.load(os.path.join(base_path, "tsaritsa_sprite.png")).convert_alpha()
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
        self.n = 8
        self.agent = PhanesAgent(self.n)
        
        # Inisialisasi Visual Novel Mode
        self.state = "VN_STORY"
        self.dialogues = [
            ("Phanes", "Papan ini telah disiapkan khusus untuk permainan ini. Pecahan Descender Ketiga tersebar tak beraturan di seluruh penjuru Teyvat."),
            ("Phanes", "Memecah tubuhnya menjadi 8 bagian ,menukarnya dengan kebangkitan mu..betapa naif dirinya itu."),
            ("Tsaritsa", "Aku akan mengumpulkan semua 8 bagian itu. Tidak peduli seberapa sulit jalannya,seberapa banyak rintangan,dan seberapa banyak kau menghalangiku."),
            ("Phanes", "Menarik. Descender ketiga memiliki kekuatan yang besar,dan hanya pecahannya saja bisa merubah tatanan Teyvat. Aku ingin melihat upaya mu mengumpulkan semua pecahan itu."),
            ("Tsaritsa", "Jangan meremehkan manusia,Phanes. Kau tidak akan mengerti bagaimana tekad manusia bisa membawa mereka untuk menjatuhkan Prinsip Langit mu itu"),
            ("Phanes", "HAHHAHAHAHHAH. OMONG KOSONG MU TIDAK AKAN BERGUNA DIHADAPAN KU SAJA,TSARITSA.BUKTIKAN SAJA KATA KATAMU ITU"),
            ("Phanes", " sekarang...BIARKAN PERMAINAN INI DIMULAI!!!")
        ]
        self.dialogue_idx = 0
        
        self.board = [-1] * self.n 
        self.message = ""
        self.times = {"DFS": 0, "HC": 0, "MC": 0}
        self.animation_steps = []
        self.anim_index = 0
        self.last_update_time = 0
        self.anim_speed = 100
        self.active_algo = ""
        
        self.btn_anim_dfs = pygame.Rect(600, 220, 250, 35)
        self.btn_anim_hc = pygame.Rect(600, 265, 250, 35)
        self.btn_anim_mc = pygame.Rect(600, 310, 250, 35)

    def update_board_size(self):
        self.agent = PhanesAgent(self.n)
        self.board = [-1] * self.n

    # --- FUNGSI VISUAL NOVEL ---
    def draw_character(self, name):
        # Tentukan posisi dan gambar
        is_phanes = (name == "Phanes")
        x_pos = 100 if is_phanes else WIDTH - 350
        y_pos = 150
        
        if is_phanes and img_phanes:
            scaled = pygame.transform.smoothscale(img_phanes, (250, 450))
            screen.blit(scaled, (x_pos, y_pos))
        elif not is_phanes and img_tsaritsa:
            scaled = pygame.transform.smoothscale(img_tsaritsa, (250, 450))
            screen.blit(scaled, (x_pos, y_pos))
        else:
            # Fallback Siluet Manual (Gelap)
            color = (60, 70, 90) if is_phanes else (100, 140, 160)
            # Badan
            pygame.draw.ellipse(screen, color, (x_pos, y_pos + 150, 250, 350))
            # Kepala
            pygame.draw.circle(screen, color, (x_pos + 125, y_pos + 100), 70)

    def draw_vn_scene(self):
        screen.fill(COLOR_BG)
        speaker, text = self.dialogues[self.dialogue_idx]
        
        # 1. Gambar Karakter
        self.draw_character(speaker)
        
        # 2. Kotak Nama
        name_rect = pygame.Rect(50, HEIGHT - 200, 200, 40)
        pygame.draw.rect(screen, COLOR_BTN, name_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_TSARITSA, name_rect, 2, border_radius=10)
        
        name_surf = font_vn_name.render(speaker, True, COLOR_TEXT)
        screen.blit(name_surf, (name_rect.x + 20, name_rect.y + 5))

        # 3. Textbox Bawah (Semi transparan)
        tb_surface = pygame.Surface((WIDTH - 100, 130), pygame.SRCALPHA)
        tb_surface.fill((10, 15, 25, 200)) # Hitam transparan
        screen.blit(tb_surface, (50, HEIGHT - 150))
        pygame.draw.rect(screen, COLOR_TILE_LIGHT, (50, HEIGHT - 150, WIDTH - 100, 130), 2)
        
        # 4. Render Teks Dialog (Pemecah baris sederhana)
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

        # Hint klik
        hint = font_text.render("[Klik di mana saja untuk lanjut...]", True, COLOR_TILE_LIGHT)
        screen.blit(hint, (WIDTH - 300, HEIGHT - 40))

    # --- FUNGSI GAMEPLAY PAPAN ---
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

        lbl_size = font_subtitle.render(f"Ukuran Papan (N): {self.n}", True, COLOR_TEXT)
        screen.blit(lbl_size, (WIDTH//2 - lbl_size.get_width()//2, 160))
        
        pygame.draw.rect(screen, COLOR_BTN, (WIDTH//2 - 120, 155, 40, 40), border_radius=5)
        pygame.draw.rect(screen, COLOR_BTN, (WIDTH//2 + 80, 155, 40, 40), border_radius=5)
        screen.blit(font_title.render("<", True, COLOR_TEXT), (WIDTH//2 - 110, 155))
        screen.blit(font_title.render(">", True, COLOR_TEXT), (WIDTH//2 + 90, 155))

        buttons = ["1. Solo Player", "2. Solo vs Phanes", "3. Agent vs Agent (Benchmark)"]
        for i, text in enumerate(buttons):
            btn_surface = font_subtitle.render(text, True, COLOR_TEXT)
            rect = pygame.Rect(WIDTH//2 - 175, 240 + i*70, 350, 50)
            mouse_pos = pygame.mouse.get_pos()
            color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else COLOR_BTN
            pygame.draw.rect(screen, color, rect, border_radius=8)
            screen.blit(btn_surface, (WIDTH//2 - btn_surface.get_width()//2, 250 + i*70))

    def get_tile_info(self):
        board_pixel_size = min(550, HEIGHT - 60)
        tile_size = max(10, board_pixel_size // self.n) 
        offset_x = 30
        offset_y = (HEIGHT - (tile_size * self.n)) // 2
        return tile_size, offset_x, offset_y

    def draw_board(self):
        tile_size, offset_x, offset_y = self.get_tile_info()
        conflicts = set()
        
        for i in range(self.n):
            if self.board[i] == -1: continue
            for j in range(i + 1, self.n):
                if self.board[j] == -1: continue
                if self.board[i] == self.board[j] or abs(self.board[i] - self.board[j]) == j - i:
                    conflicts.add(i); conflicts.add(j)

        for row in range(self.n):
            for col in range(self.n):
                color = COLOR_TILE_LIGHT if (row + col) % 2 == 0 else COLOR_TILE_DARK
                x = offset_x + col * tile_size
                y = offset_y + row * tile_size
                
                is_danger = (col in conflicts) and (self.board[col] == row)
                if is_danger:
                    pygame.draw.rect(screen, COLOR_DANGER, (x, y, tile_size, tile_size))
                else:
                    pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))
                
                if self.board[col] == row:
                    self.draw_gnosis_piece(x, y, tile_size, col)
                else:
                    self.draw_empty_target(x, y, tile_size)

    def draw_button(self, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        color = COLOR_BTN_HOVER if rect.collidepoint(mouse_pos) else COLOR_BTN
        pygame.draw.rect(screen, color, rect, border_radius=5)
        txt_surf = font_text.render(text, True, COLOR_TEXT)
        screen.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width())//2, rect.y + 8))

    def draw_ui_panel(self):
        panel_x = 600
        pygame.draw.line(screen, COLOR_TILE_LIGHT, (panel_x-20, 50), (panel_x-20, HEIGHT-50), 2)
        
        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            screen.blit(font_text.render(line, True, COLOR_TSARITSA), (panel_x, 50 + (i*25)))
        
        if self.state in ["CLASH_MENU", "ANIMATING"]:
            screen.blit(font_subtitle.render("Waktu Kalkulasi Phanes:", True, COLOR_TEXT), (panel_x, 120))
            screen.blit(font_text.render(f"1. DFS: {self.times['DFS']:.5f} detik", True, COLOR_TEXT), (panel_x, 150))
            screen.blit(font_text.render(f"2. Hill Climb: {self.times['HC']:.5f} detik", True, COLOR_TEXT), (panel_x, 170))
            screen.blit(font_text.render(f"3. Min-Conflict: {self.times['MC']:.5f} detik", True, COLOR_TEXT), (panel_x, 190))
            
            if self.state == "CLASH_MENU":
                self.draw_button(self.btn_anim_dfs, "Tonton Animasi DFS")
                self.draw_button(self.btn_anim_hc, "Tonton Animasi Hill Climb")
                self.draw_button(self.btn_anim_mc, "Tonton Animasi Min-Conflicts")

        btn_back = pygame.Rect(panel_x, HEIGHT - 90, 250, 40)
        self.draw_button(btn_back, "Kembali ke Menu")

    def handle_click(self, pos):
        x, y = pos
        
        if self.state == "VN_STORY":
            # Maju ke dialog berikutnya
            self.dialogue_idx += 1
            if self.dialogue_idx >= len(self.dialogues):
                self.state = "MENU" # Prolog selesai
            return

        if self.state == "MENU":
            if 155 <= y <= 195:
                if WIDTH//2 - 120 <= x <= WIDTH//2 - 80 and self.n > 4:
                    self.n -= 1; self.update_board_size()
                elif WIDTH//2 + 80 <= x <= WIDTH//2 + 120 and self.n < 32:
                    self.n += 1; self.update_board_size()
            if WIDTH//2 - 175 <= x <= WIDTH//2 + 175:
                if 240 <= y <= 290: self.start_solo()
                elif 310 <= y <= 360: self.start_vs_agent()
                elif 380 <= y <= 430: self.start_agent_clash()
                
        else:
            if 600 <= x <= 850 and HEIGHT - 90 <= y <= HEIGHT - 50:
                self.state = "MENU"; return

            if self.state == "CLASH_MENU":
                if self.btn_anim_dfs.collidepoint(pos): self.play_animation("DFS")
                elif self.btn_anim_hc.collidepoint(pos): self.play_animation("HC")
                elif self.btn_anim_mc.collidepoint(pos): self.play_animation("MC")

            if self.state in ["SOLO", "VS_AGENT"]:
                tile_size, offset_x, offset_y = self.get_tile_info()
                for row in range(self.n):
                    for col in range(self.n):
                        rect = pygame.Rect(offset_x + col*tile_size, offset_y + row*tile_size, tile_size, tile_size)
                        if rect.collidepoint(pos):
                            if self.board[col] == row:
                                self.board[col] = -1 
                            else:
                                self.board[col] = row 
                            
                            c = self.agent.get_conflicts(self.board)
                            placed = self.n - self.board.count(-1)
                            if -1 not in self.board and c == 0:
                                self.message = "Kemenangan Mutlak!\nSemua Gnosis telah dikumpulkan!"
                            else:
                                self.message = f"Bidak di papan: {placed}/{self.n}\nJumlah Konflik: {c}"
                            return

    def start_solo(self):
        self.state = "SOLO"
        self.board = [-1] * self.n
        self.message = "Setiap kolom memiliki satu bidak.\nKlik petak kosong untuk\nmemindahkannya.\n\nKlik bidak yang sama\nuntuk mencabutnya."

    def start_vs_agent(self):
        self.state = "VS_AGENT"
        self.board = [-1] * self.n
        start = time.time()
        self.agent.solve_dfs() 
        t_agent = time.time() - start
        self.message = f"Phanes telah menang dalam\n{t_agent:.4f} detik!\n\nSekarang giliranmu."

    def start_agent_clash(self):
        self.state = "LOADING_CLASH"
        self.board = [-1] * self.n
        self.message = "Phanes sedang beradu\nAlgoritma di belakang layar...\n(Harap tunggu sesaat)"
        self.draw_board(); self.draw_ui_panel(); pygame.display.flip()

        start = time.time(); self.agent.solve_dfs(); self.times["DFS"] = time.time() - start
        start = time.time(); self.agent.solve_hill_climbing(); self.times["HC"] = time.time() - start
        start = time.time(); self.agent.solve_min_conflicts(); self.times["MC"] = time.time() - start
        
        self.state = "CLASH_MENU"
        self.message = "Pertarungan Selesai!\nSilakan pilih algoritma yang\ningin kamu lihat visualisasinya."

    def play_animation(self, algo):
        self.active_algo = algo
        self.message = f"Mengumpulkan rekaman langkah\n{algo}..."
        self.draw_board(); self.draw_ui_panel(); pygame.display.flip()

        if algo == "DFS":
            self.animation_steps = self.agent.get_dfs_steps(); self.anim_speed = 5 
        elif algo == "HC":
            self.animation_steps = self.agent.get_hc_steps(); self.anim_speed = 100
        elif algo == "MC":
            self.animation_steps = self.agent.get_mc_steps(); self.anim_speed = 200

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

        if game.state == "ANIMATING":
            if current_time - game.last_update_time > game.anim_speed:
                if game.anim_index < len(game.animation_steps):
                    game.board = game.animation_steps[game.anim_index]
                    game.message = f"Memutar ulang pergerakan\n{game.active_algo} AI...\nLangkah: {game.anim_index}/{len(game.animation_steps)}"
                    game.anim_index += 1
                    game.last_update_time = current_time
                else:
                    game.state = "CLASH_MENU"
                    game.message = f"Animasi {game.active_algo} selesai!\nPilih algoritma lain untuk\nditonton."

        screen.fill(COLOR_BG)

        # Logic Menggambar berdasarkan State
        if game.state == "VN_STORY":
            game.draw_vn_scene()
        elif game.state != "LOADING_CLASH":
            if game.state == "MENU":
                game.draw_menu()
            else:
                game.draw_board()
                game.draw_ui_panel()

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