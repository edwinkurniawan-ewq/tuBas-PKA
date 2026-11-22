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
        restart_flags = []
        board = [-1] * self.n
        steps.append(list(board))
        restart_flags.append(False)

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
                    restart_flags.append(False)
                    if dfs(col + 1): return True
                    board[col] = -1
                    steps.append(list(board))
                    restart_flags.append(False)
            return False
        dfs(0)
        return steps, restart_flags

    # 1. Steepest-Ascent Hill Climbing (Cek semua tetangga, ambil yang paling rendah konfliknya)
    def get_sahc_steps(self):
        steps = []
        restart_flags = []
        board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        steps.append(list(board))
        restart_flags.append(False)

        while True:
            current_conflicts = self.get_conflicts(board)
            if current_conflicts == 0:
                return steps, restart_flags
            best_conflicts = current_conflicts
            best_boards = []
            for i in range(self.n):
                original_val = board[i]
                for j in range(self.n):
                    if j != original_val:
                        board[i] = j
                        c = self.get_conflicts(board)
                        if c < best_conflicts:
                            best_conflicts = c
                            best_boards = [list(board)]
                        elif c == best_conflicts and best_conflicts < current_conflicts:
                            best_boards.append(list(board))
                board[i] = original_val

            if not best_boards:
                break
            board = random.choice(best_boards)
            steps.append(list(board))
            restart_flags.append(False)
        return steps, restart_flags

    # 2. First-Choice Hill Climbing (Acak tetangga, langsung ambil yang pertama lebih baik)
    def get_fchc_steps(self):
        steps = []
        restart_flags = []
        board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        steps.append(list(board))
        restart_flags.append(False)

        while True:
            current_conflicts = self.get_conflicts(board)
            if current_conflicts == 0:
                return steps, restart_flags

            neighbors = [(col, row) for col in range(self.n) for row in range(self.n) if row != board[col]]
            random.shuffle(neighbors)

            moved = False
            for col, row in neighbors:
                orig_val = board[col]
                board[col] = row
                c = self.get_conflicts(board)
                if c < current_conflicts:
                    steps.append(list(board))
                    restart_flags.append(False)
                    moved = True
                    break
                board[col] = orig_val

            if not moved:
                break
        return steps, restart_flags

    # 3. Random-Restart Hill Climbing
    def get_rhc_steps(self, max_restarts=100):
        steps = []
        restart_flags = []
        for attempt in range(max_restarts):
            board = [random.randint(0, self.n - 1) for _ in range(self.n)]
            steps.append(list(board))
            restart_flags.append(attempt > 0)

            while True:
                current_conflicts = self.get_conflicts(board)
                if current_conflicts == 0:
                    return steps, restart_flags
                best_conflicts = current_conflicts
                best_boards = []
                for i in range(self.n):
                    original_val = board[i]
                    for j in range(self.n):
                        if j != original_val:
                            board[i] = j
                            c = self.get_conflicts(board)
                            if c < best_conflicts:
                                best_conflicts = c
                                best_boards = [list(board)]
                            elif c == best_conflicts and best_conflicts < current_conflicts:
                                best_boards.append(list(board))
                    board[i] = original_val
                
                if not best_boards:
                    break 
                board = random.choice(best_boards)
                steps.append(list(board))
                restart_flags.append(False)
        return steps, restart_flags

    # 4. Min-Conflicts
    def get_mc_steps(self, max_steps=500, max_restarts=50):
        steps = []
        restart_flags = []
        for attempt in range(max_restarts):
            board = []
            # Greedy Initialization
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
            restart_flags.append(attempt > 0)

            # Main Min-Conflicts Loop
            for _ in range(max_steps):
                if self.get_conflicts(board) == 0:
                    return steps, restart_flags

                conflicted_cols = []
                for col in range(self.n):
                    row = board[col]
                    for c in range(self.n):
                        if c != col:
                            if board[c] == row or abs(board[c] - row) == abs(c - col):
                                conflicted_cols.append(col)
                                break

                if not conflicted_cols:
                    return steps, restart_flags

                col_to_fix = random.choice(conflicted_cols)
                orig_val = board[col_to_fix]
                min_c = float('inf')
                best_vals = []

                for val in range(self.n):
                    if val == orig_val:
                        continue
                    board[col_to_fix] = val
                    c = self.get_conflicts(board)
                    if c < min_c:
                        min_c = c
                        best_vals = [val]
                    elif c == min_c:
                        best_vals.append(val)

                board[col_to_fix] = random.choice(best_vals)
                steps.append(list(board))
                restart_flags.append(False)

        return steps, restart_flags

    # Bantuan Tsaritsa (1 langkah sepadan dengan algoritma tandingan)
    def get_tsaritsa_hint(self, current_board, algo="MC"):
        board = list(current_board)
        current_c = self.get_conflicts(board)
        if current_c == 0:
            return None, "Posisi semua Gnosis sudah aman!"

        # Strategi sepadan DFS
        if algo == "DFS":
            for col in range(self.n):
                has_conflict = False
                for prev_c in range(col):
                    if board[prev_c] == board[col] or abs(board[prev_c] - board[col]) == col - prev_c:
                        has_conflict = True
                        break
                
                if has_conflict:
                    for r in range(self.n):
                        safe = True
                        for prev_c in range(col):
                            if board[prev_c] == r or abs(board[prev_c] - r) == col - prev_c:
                                safe = False
                                break
                        if safe:
                            return [(col, r)], f"Bantuan (DFS): Geser kolom {col+1} ke baris {r+1} (aman dari kiri)."
            algo = "RHC"

        # Strategi sepadan First-Choice Hill Climbing
        if algo == "FCHC":
            neighbors = [(col, r) for col in range(self.n) for r in range(self.n) if r != board[col]]
            random.shuffle(neighbors)
            for col, r in neighbors:
                orig_r = board[col]
                board[col] = r
                c = self.get_conflicts(board)
                board[col] = orig_r
                if c < current_c:
                    return [(col, r)], f"Bantuan (FCHC): Pilihan pertama lebih baik -> kolom {col+1} ke baris {r+1} (konflik {c})."
            col = random.randint(0, self.n - 1)
            r = (board[col] + 1) % self.n
            return [(col, r)], f"Bantuan (FCHC): Terjebak Local Optimum! Geser paksa kolom {col+1} ke baris {r+1}."

        # Strategi sepadan Steepest-Ascent & Restart Hill Climbing
        if algo in ["SAHC", "RHC"]:
            best_c = current_c
            best_moves = []
            for col in range(self.n):
                orig_r = board[col]
                for r in range(self.n):
                    if r != orig_r:
                        board[col] = r
                        c = self.get_conflicts(board)
                        if c < best_c:
                            best_c = c
                            best_moves = [(col, r)]
                        elif c == best_c and best_c < current_c:
                            best_moves.append((col, r))
                board[col] = orig_r

            if best_moves:
                col, r = random.choice(best_moves)
                return [(col, r)], f"Bantuan ({algo}): Geser kolom {col+1} ke baris {r+1} (konflik turun jadi {best_c})."
            else:
                if algo == "SAHC":
                    col = random.randint(0, self.n - 1)
                    r = (board[col] + 1) % self.n
                    return [(col, r)], f"Bantuan (SAHC): Terjebak Local Optimum! Geser paksa kolom {col+1} ke baris {r+1}."
                else:
                    cols = random.sample(range(self.n), min(2, self.n))
                    moves = []
                    for c_idx in cols:
                        new_r = (board[c_idx] + random.randint(1, self.n - 1)) % self.n
                        moves.append((c_idx, new_r))
                    return moves, f"Bantuan (RHC Restart): Acak ulang {len(moves)} Gnosis untuk keluar dari jalan buntu!"

        # Strategi sepadan Min-Conflicts (Default Solo & Lawan MC)
        conflicted_cols = []
        for col in range(self.n):
            row = board[col]
            for c in range(self.n):
                if c != col:
                    if board[c] == row or abs(board[c] - row) == abs(c - col):
                        conflicted_cols.append(col)
                        break

        if conflicted_cols:
            col_to_fix = random.choice(conflicted_cols)
            min_c = float('inf')
            best_rows = []
            orig_r = board[col_to_fix]
            for r in range(self.n):
                if r == orig_r: continue
                board[col_to_fix] = r
                c = self.get_conflicts(board)
                if c < min_c:
                    min_c = c
                    best_rows = [r]
                elif c == min_c:
                    best_rows.append(r)
            board[col_to_fix] = orig_r
            best_r = random.choice(best_rows)
            return [(col_to_fix, best_r)], f"Bantuan (MC): Geser kolom {col_to_fix+1} ke baris {best_r+1} (konflik minimal)."

        return None, "Tidak ada langkah bantuan yang diperlukan."


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
COLOR_BTN_SELECTED = (35, 130, 145)
COLOR_BTN_HINT = (40, 120, 140)
COLOR_BTN_HINT_HOVER = (60, 155, 180)
COLOR_BTN_DISABLED = (45, 50, 60)
COLOR_DANGER = (180, 50, 50)
COLOR_SUCCESS = (90, 220, 130)

font_title = pygame.font.SysFont("cambria", 32, bold=True)
font_vn_name = pygame.font.SysFont("cambria", 26, bold=True)
font_subtitle = pygame.font.SysFont("cambria", 22, bold=True)
font_text = pygame.font.SysFont("cambria", 18)
font_small = pygame.font.SysFont("cambria", 15)
font_tiny = pygame.font.SysFont("cambria", 13)

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
            ("Tsaritsa", "Menahan", "Perbuatan dan tindakan mu selama ini hanya siklus untuk menggambarkan kamu adalah pahlawan. Tapi kenyataan nya adalah kamu adalah sebab dari kesengsaraan manusia."),
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
        self.animation_steps = []
        self.anim_index = 0
        self.last_update_time = 0
        self.anim_speed = 100
        self.active_algo = ""
        self.active_level = ""
        
        # --- VARIABEL MODE 3: AGENT VS AGENT (DUAL BOARD BENCHMARK) ---
        self.clash_algo1 = "DFS"
        self.clash_algo2 = "SAHC"
        self.clash_board1 = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.clash_board2 = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.clash_steps1 = []
        self.clash_steps2 = []
        self.clash_restart_flags1 = []
        self.clash_restart_flags2 = []
        self.clash_restarts1 = 0
        self.clash_restarts2 = 0
        self.clash_conflict_hist1 = []
        self.clash_conflict_hist2 = []
        self.clash_idx1 = 0
        self.clash_idx2 = 0
        self.clash_speed1 = 100
        self.clash_speed2 = 100
        self.clash_last_tick1 = 0
        self.clash_last_tick2 = 0
        self.clash_start_time = 0.0
        self.clash_elapsed1 = 0.0
        self.clash_elapsed2 = 0.0
        self.clash_calc_time1 = 0.0
        self.clash_calc_time2 = 0.0
        self.clash_done1 = False
        self.clash_done2 = False
        self.clash_solved1 = False
        self.clash_solved2 = False
        self.clash_first_winner = None
        
        # Rect tombol pilihan Agent vs Agent & Solo vs Phanes
        self.clash_btn_left_rects = {}
        self.clash_btn_right_rects = {}
        self.vs_btn_rects = {}
        self.btn_start_clash_rect = pygame.Rect(0,0,0,0)
        self.btn_rematch_clash_rect = pygame.Rect(0,0,0,0)
        
        # Variabel Bantuan Tsaritsa
        self.max_hints = 3
        self.hints_left = self.max_hints
        self.last_hint_cells = []
        
        # Variabel Timer Player
        self.player_start_time = 0.0
        self.player_timer = 0.0
        
        # Penampung Rect Tombol Dinamis
        self.btn_hint_rect = pygame.Rect(0,0,0,0)
        self.btn_acak_rect = pygame.Rect(0,0,0,0)
        self.btn_reset_rect = pygame.Rect(0,0,0,0)
        self.btn_back_rect = pygame.Rect(0,0,0,0)

    def update_board_size(self):
        self.agent = PhanesAgent(self.n)
        self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.board_agent = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.clash_board1 = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.clash_board2 = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.hints_left = self.max_hints
        self.last_hint_cells = []

    def get_algo_steps_and_speed(self, algo):
        if algo == "DFS":
            steps, r_flags = self.agent.get_dfs_steps()
            return steps, r_flags, 15
        elif algo == "SAHC":
            steps, r_flags = self.agent.get_sahc_steps()
            return steps, r_flags, 120
        elif algo == "FCHC":
            steps, r_flags = self.agent.get_fchc_steps()
            return steps, r_flags, 120
        elif algo == "RHC":
            steps, r_flags = self.agent.get_rhc_steps()
            return steps, r_flags, 70
        elif algo == "MC":
            steps, r_flags = self.agent.get_mc_steps()
            return steps, r_flags, 120
        return [], [], 100

    def start_agent_clash(self):
        self.state = "CLASH_PLAY"
        
        t0 = time.perf_counter()
        self.clash_steps1, self.clash_restart_flags1, self.clash_speed1 = self.get_algo_steps_and_speed(self.clash_algo1)
        self.clash_calc_time1 = time.perf_counter() - t0
        
        t1 = time.perf_counter()
        self.clash_steps2, self.clash_restart_flags2, self.clash_speed2 = self.get_algo_steps_and_speed(self.clash_algo2)
        self.clash_calc_time2 = time.perf_counter() - t1

        self.clash_board1 = list(self.clash_steps1[0]) if self.clash_steps1 else [0]*self.n
        self.clash_board2 = list(self.clash_steps2[0]) if self.clash_steps2 else [0]*self.n
        
        self.clash_restarts1 = 0
        self.clash_restarts2 = 0
        self.clash_conflict_hist1 = [self.agent.get_conflicts(self.clash_board1)]
        self.clash_conflict_hist2 = [self.agent.get_conflicts(self.clash_board2)]
        
        self.clash_idx1 = 1
        self.clash_idx2 = 1
        now_ms = pygame.time.get_ticks()
        self.clash_last_tick1 = now_ms
        self.clash_last_tick2 = now_ms
        
        self.clash_start_time = time.perf_counter()
        self.clash_elapsed1 = 0.0
        self.clash_elapsed2 = 0.0
        
        self.clash_done1 = (len(self.clash_steps1) <= 1)
        self.clash_done2 = (len(self.clash_steps2) <= 1)
        self.clash_solved1 = (-1 not in self.clash_board1 and self.agent.get_conflicts(self.clash_board1) == 0)
        self.clash_solved2 = (-1 not in self.clash_board2 and self.agent.get_conflicts(self.clash_board2) == 0)
        self.clash_first_winner = None
        
        if self.clash_solved1:
            self.clash_first_winner = f"{self.clash_algo1} (Kiri)"
        elif self.clash_solved2:
            self.clash_first_winner = f"{self.clash_algo2} (Kanan)"
            
        self.message = f"Duel Berlangsung: {self.clash_algo1} vs {self.clash_algo2}!"

    def apply_tsaritsa_hint(self):
        if self.hints_left <= 0:
            self.message = "Energi Cryo Tsaritsa habis!\nTidak ada sisa bantuan tersisa."
            return

        if self.agent.get_conflicts(self.board) == 0:
            self.message = "Papan sudah aman tanpa konflik!"
            return

        algo_to_use = self.active_algo if self.state == "VS_AGENT_PLAY" else "MC"
        moves, hint_msg = self.agent.get_tsaritsa_hint(self.board, algo=algo_to_use)

        if moves:
            for col, row in moves:
                self.board[col] = row
            self.hints_left -= 1
            self.last_hint_cells = list(moves)
            
            c = self.agent.get_conflicts(self.board)
            if c == 0:
                if self.state == "SOLO":
                    self.message = "Kemenangan Mutlak!\nSemua Gnosis telah dikumpulkan!"
                elif self.state == "VS_AGENT_PLAY":
                    self.vs_winner = "Player"
                    self.message = f"KAMU MENANG! Berhasil menaklukkan Phanes ({self.active_level})!"
            else:
                self.message = f"{hint_msg}\nSisa konflik: {c}"

    def draw_character(self, name, expression):
        w, h = screen.get_width(), screen.get_height()
        is_phanes = (name == "Phanes")
        x_pos = 150 if is_phanes else w - 400
        y_pos = 150
        
        sprite_dict = phanes_sprites if is_phanes else tsaritsa_sprites
        img = sprite_dict.get(expression)
        if not img:
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

    def draw_button(self, rect, text, custom_color=None, custom_hover=None, disabled=False, selected=False, small_font=False):
        mouse_pos = pygame.mouse.get_pos()
        if disabled:
            color = COLOR_BTN_DISABLED
        elif selected:
            color = COLOR_BTN_SELECTED
        else:
            base_c = custom_color if custom_color else COLOR_BTN
            hover_c = custom_hover if custom_hover else COLOR_BTN_HOVER
            color = hover_c if rect.collidepoint(mouse_pos) else base_c
        pygame.draw.rect(screen, color, rect, border_radius=5)
        if (custom_color or selected) and not disabled:
            pygame.draw.rect(screen, COLOR_TSARITSA, rect, 2 if selected else 1, border_radius=5)
        txt_color = (130, 140, 150) if disabled else COLOR_TEXT
        fnt = font_small if small_font else font_text
        txt_surf = fnt.render(text, True, txt_color)
        screen.blit(txt_surf, (rect.x + (rect.width - txt_surf.get_width())//2, rect.y + (rect.height - txt_surf.get_height())//2))

    def draw_grid(self, board_array, offset_x, offset_y, tile_size, highlight_cells=None):
        if highlight_cells is None:
            highlight_cells = []
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
                
                if (col, row) in highlight_cells:
                    pygame.draw.rect(screen, COLOR_TSARITSA, (x, y, tile_size, tile_size), 3)
                
                if board_array[col] == row:
                    self.draw_gnosis_piece(x, y, tile_size, col)
                else:
                    self.draw_empty_target(x, y, tile_size)

    def draw_conflict_graph(self, rect, history, line_color, label):
        pygame.draw.rect(screen, (20, 27, 40), rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_TILE_LIGHT, rect, 1, border_radius=6)

        curr_c = history[-1] if history else 0
        max_possible = max(1, (self.n * (self.n - 1)) // 2)
        max_c = max(max_possible, max(history) if history else 1)

        hdr = font_tiny.render(f"{label} | Konflik Saat Ini: {curr_c}", True, line_color)
        screen.blit(hdr, (rect.x + 8, rect.y + 4))

        pad_l, pad_r, pad_t, pad_b = 10, 10, 22, 8
        gx = rect.x + pad_l
        gy = rect.y + pad_t
        gw = max(10, rect.width - pad_l - pad_r)
        gh = max(10, rect.height - pad_t - pad_b)

        pygame.draw.line(screen, (50, 75, 95), (gx, gy + gh), (gx + gw, gy + gh), 1)

        if not history:
            return

        visible = history[-120:] if len(history) > 120 else history
        num_pts = len(visible)

        if num_pts == 1:
            py = gy + gh - int((visible[0] / max_c) * gh)
            pygame.draw.circle(screen, line_color, (gx + gw // 2, py), 3)
            return

        pts = []
        for idx, val in enumerate(visible):
            px = gx + int((idx / (num_pts - 1)) * gw)
            py = gy + gh - int((val / max_c) * gh)
            pts.append((px, py))

        pygame.draw.lines(screen, line_color, False, pts, 2)
        pygame.draw.circle(screen, (255, 255, 255), pts[-1], 3)

    def draw_solo(self):
        w, h = screen.get_width(), screen.get_height()
        
        board_pixel_size = min(500, h - 150)
        tile_size = max(10, board_pixel_size // self.n) 
        offset_x = 220
        offset_y = (h - (tile_size * self.n)) // 2
        
        self.draw_grid(self.board, offset_x, offset_y, tile_size, highlight_cells=self.last_hint_cells)

        conflicts = self.agent.get_conflicts(self.board)
        is_solved = (-1 not in self.board and conflicts == 0)

        if is_solved:
            p_expr = "Defeat" 
            t_expr = "Murka"       
        elif conflicts > 6:
            p_expr = "Mengejek"    
            t_expr = "Menahan"
        else:
            p_expr = "Santai"
            t_expr = "Santai"
        self.draw_gameplay_characters(p_expr, t_expr, tsaritsa_on_left=True)

        panel_x = 850
        pygame.draw.line(screen, COLOR_TILE_LIGHT, (panel_x-20, 50), (panel_x-20, h-50), 2)
        
        raw_lines = self.message.split('\n')
        wrapped_lines = []
        for r_line in raw_lines:
            words = r_line.split(' ')
            curr = ""
            for word in words:
                if font_text.size(curr + word)[0] < (w - panel_x - 20):
                    curr += word + " "
                else:
                    wrapped_lines.append(curr)
                    curr = word + " "
            wrapped_lines.append(curr)

        for i, line in enumerate(wrapped_lines):
            screen.blit(font_text.render(line, True, COLOR_TSARITSA), (panel_x, 45 + (i*23)))

        self.btn_hint_rect = pygame.Rect(panel_x, h - 245, 250, 42)
        hint_disabled = (self.hints_left <= 0 or is_solved)
        self.draw_button(
            self.btn_hint_rect,
            f"Bantuan Tsaritsa ({self.hints_left}/{self.max_hints})",
            custom_color=COLOR_BTN_HINT,
            custom_hover=COLOR_BTN_HINT_HOVER,
            disabled=hint_disabled
        )

        self.btn_acak_rect = pygame.Rect(panel_x, h - 190, 250, 40)
        self.draw_button(self.btn_acak_rect, "Acak Papan")
        
        self.btn_reset_rect = pygame.Rect(panel_x, h - 140, 250, 40)
        self.draw_button(self.btn_reset_rect, "Reset Papan")

        self.btn_back_rect = pygame.Rect(panel_x, h - 90, 250, 40)
        self.draw_button(self.btn_back_rect, "Kembali ke Menu Utama")

    def draw_clash_menu(self):
        screen.fill(COLOR_BG)
        w, h = screen.get_width(), screen.get_height()
        
        title = font_title.render("BENCHMARK: AGENT VS AGENT (DUAL BOARD)", True, COLOR_TSARITSA)
        screen.blit(title, (w//2 - title.get_width()//2, 45))
        
        sub = font_text.render(f"Pilih 2 dari 5 algoritma untuk diadu secara real-time pada papan {self.n}x{self.n}:", True, COLOR_TEXT)
        screen.blit(sub, (w//2 - sub.get_width()//2, 90))

        algos = [
            ("DFS", "1. Depth-First Search (DFS)"),
            ("SAHC", "2. Steepest-Ascent HC (SAHC)"),
            ("FCHC", "3. First-Choice HC (FCHC)"),
            ("RHC", "4. Restart Hill Climbing (RHC)"),
            ("MC", "5. Min-Conflicts (MC)")
        ]

        # Kolom Kiri (Papan 1)
        col1_x = w//2 - 360
        lbl1 = font_subtitle.render(f"Papan Kiri: {self.clash_algo1}", True, COLOR_TSARITSA)
        screen.blit(lbl1, (col1_x + 155 - lbl1.get_width()//2, 135))
        
        self.clash_btn_left_rects = {}
        for i, (code, label) in enumerate(algos):
            r = pygame.Rect(col1_x, 170 + i*52, 310, 42)
            self.clash_btn_left_rects[code] = r
            self.draw_button(r, label, selected=(self.clash_algo1 == code), small_font=True)

        # Kolom Kanan (Papan 2)
        col2_x = w//2 + 50
        lbl2 = font_subtitle.render(f"Papan Kanan: {self.clash_algo2}", True, COLOR_DANGER)
        screen.blit(lbl2, (col2_x + 155 - lbl2.get_width()//2, 135))

        self.clash_btn_right_rects = {}
        for i, (code, label) in enumerate(algos):
            r = pygame.Rect(col2_x, 170 + i*52, 310, 42)
            self.clash_btn_right_rects[code] = r
            self.draw_button(r, label, selected=(self.clash_algo2 == code), small_font=True)

        vs_lbl = font_title.render("VS", True, COLOR_TEXT)
        screen.blit(vs_lbl, (w//2 - vs_lbl.get_width()//2, 275))

        self.btn_start_clash_rect = pygame.Rect(w//2 - 175, h - 135, 350, 48)
        self.draw_button(
            self.btn_start_clash_rect,
            f"Mulai Duel ({self.clash_algo1} vs {self.clash_algo2})",
            custom_color=COLOR_BTN_HINT,
            custom_hover=COLOR_BTN_HINT_HOVER
        )

        self.btn_back_rect = pygame.Rect(w//2 - 175, h - 75, 350, 42)
        self.draw_button(self.btn_back_rect, "Kembali ke Menu Utama")

    def draw_clash_play(self):
        w, h = screen.get_width(), screen.get_height()
        
        board_pixel_size = min((w - 280) // 2, h - 345)
        tile_size = max(10, board_pixel_size // self.n)
        actual_board_w = tile_size * self.n
        actual_board_h = tile_size * self.n

        # Karakter di Sisi Kiri
        if self.clash_done1 and self.clash_done2:
            p_expr = "Santai"
            t_expr = "Murka" if (self.clash_solved1 or self.clash_solved2) else "Menahan"
        else:
            p_expr = "Bingung"
            t_expr = "Santai"
        self.draw_gameplay_characters(p_expr, t_expr, tsaritsa_on_left=True)

        # --- PAPAN KIRI (ALGORITMA 1) ---
        offset_x1 = 220
        offset_y1 = 110
        curr_s1 = max(0, self.clash_idx1 - 1)
        curr_c1 = self.agent.get_conflicts(self.clash_board1)
        
        header1 = f"Agent 1: {self.clash_algo1}"
        screen.blit(font_subtitle.render(header1, True, COLOR_TSARITSA), (offset_x1, 25))
        
        stat1 = f"Langkah: {curr_s1} | Konflik: {curr_c1} | Restart: {self.clash_restarts1} | {self.clash_elapsed1:.2f}s"
        screen.blit(font_small.render(stat1, True, COLOR_TEXT), (offset_x1, 55))
        
        if self.clash_done1:
            if self.clash_solved1:
                st1_txt = f"SOLUSI DITEMUKAN! (CPU: {self.clash_calc_time1*1000:.2f} ms)"
                st1_col = COLOR_SUCCESS
            else:
                st1_txt = f"MENTOK LOCAL OPTIMUM ({curr_c1} konflik)"
                st1_col = COLOR_DANGER
        else:
            st1_txt = "Sedang mencari solusi..."
            st1_col = COLOR_TSARITSA
        screen.blit(font_small.render(st1_txt, True, st1_col), (offset_x1, 78))
        
        self.draw_grid(self.clash_board1, offset_x1, offset_y1, tile_size)

        graph1_rect = pygame.Rect(offset_x1, offset_y1 + actual_board_h + 10, max(240, actual_board_w), 78)
        self.draw_conflict_graph(graph1_rect, self.clash_conflict_hist1, COLOR_TSARITSA, f"Grafik Konflik {self.clash_algo1}")

        # --- PAPAN KANAN (ALGORITMA 2) ---
        offset_x2 = w - 40 - max(240, actual_board_w)
        offset_y2 = 110
        curr_s2 = max(0, self.clash_idx2 - 1)
        curr_c2 = self.agent.get_conflicts(self.clash_board2)

        header2 = f"Agent 2: {self.clash_algo2}"
        screen.blit(font_subtitle.render(header2, True, COLOR_DANGER), (offset_x2, 25))

        stat2 = f"Langkah: {curr_s2} | Konflik: {curr_c2} | Restart: {self.clash_restarts2} | {self.clash_elapsed2:.2f}s"
        screen.blit(font_small.render(stat2, True, COLOR_TEXT), (offset_x2, 55))

        if self.clash_done2:
            if self.clash_solved2:
                st2_txt = f"SOLUSI DITEMUKAN! (CPU: {self.clash_calc_time2*1000:.2f} ms)"
                st2_col = COLOR_SUCCESS
            else:
                st2_txt = f"MENTOK LOCAL OPTIMUM ({curr_c2} konflik)"
                st2_col = COLOR_DANGER
        else:
            st2_txt = "Sedang mencari solusi..."
            st2_col = COLOR_TSARITSA
        screen.blit(font_small.render(st2_txt, True, st2_col), (offset_x2, 78))

        self.draw_grid(self.clash_board2, offset_x2, offset_y2, tile_size)

        graph2_rect = pygame.Rect(offset_x2, offset_y2 + actual_board_h + 10, max(240, actual_board_w), 78)
        self.draw_conflict_graph(graph2_rect, self.clash_conflict_hist2, COLOR_DANGER, f"Grafik Konflik {self.clash_algo2}")

        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            screen.blit(font_text.render(line, True, COLOR_TEXT), (220, h - 75 + (i*22)))

        self.btn_rematch_clash_rect = pygame.Rect(w - 540, h - 65, 240, 45)
        self.draw_button(
            self.btn_rematch_clash_rect,
            "Ulangi Duel (Acak Baru)",
            custom_color=COLOR_BTN_HINT,
            custom_hover=COLOR_BTN_HINT_HOVER
        )

        self.btn_back_rect = pygame.Rect(w - 280, h - 65, 240, 45)
        self.draw_button(self.btn_back_rect, "Ganti Algoritma / Kembali")

    def draw_vs_menu(self):
        screen.fill(COLOR_BG)
        w, h = screen.get_width(), screen.get_height()
        title = font_title.render("PILIH TINGKAT KESULITAN LAWAN (PHANES)", True, COLOR_TSARITSA)
        screen.blit(title, (w//2 - title.get_width()//2, 75))
        
        levels = [
            ("Easy", "FCHC", "1. Easy - First-Choice Hill Climbing (FCHC)"),
            ("Medium", "MC", "2. Medium - Min-Conflicts (MC)"),
            ("Hard", "RHC", "3. Hard - Restart Hill Climbing (RHC)"),
            ("Hell", "DFS", "4. Hell - Depth-First Search (DFS)")
        ]

        self.vs_btn_rects = {}
        for i, (lvl, code, label) in enumerate(levels):
            r = pygame.Rect(w//2 - 210, 175 + i*68, 420, 52)
            self.vs_btn_rects[(lvl, code)] = r
            self.draw_button(r, label)

        self.btn_back_rect = pygame.Rect(w//2 - 210, h - 95, 420, 50)
        self.draw_button(self.btn_back_rect, "Kembali ke Menu")

    def draw_vs_play(self):
        w, h = screen.get_width(), screen.get_height()
        
        board_pixel_size = min((w - 150) // 2, h - 250)
        self.vs_tile_size = max(10, board_pixel_size // self.n) 
        actual_board_w = self.vs_tile_size * self.n
        
        # Papan Pemain (Tengah-Kiri)
        offset_x1 = 220
        offset_y1 = 100
        title_player = f"Papan Tsaritsa (Kamu) - {self.player_timer:.2f}s"
        screen.blit(font_subtitle.render(title_player, True, COLOR_TSARITSA), (offset_x1, 60))
        self.draw_grid(self.board, offset_x1, offset_y1, self.vs_tile_size, highlight_cells=self.last_hint_cells)
        
        # Papan Agent (Kanan)
        offset_x2 = w - 50 - actual_board_w
        offset_y2 = 100
        title_agent = f"Papan Phanes [{self.active_level} - {self.active_algo}]"
        screen.blit(font_subtitle.render(title_agent, True, COLOR_DANGER), (offset_x2, 60))
        self.draw_grid(self.board_agent, offset_x2, offset_y2, self.vs_tile_size)

        if self.vs_winner == "Player":
            p_expr = "Defeat"
            t_expr = "Murka"
        elif self.vs_winner == "Agent":
            p_expr = "Mengejek"
            t_expr = "Defeat"
        else:
            p_expr = "Bingung" 
            t_expr = "Santai"
            
        self.draw_gameplay_characters(p_expr, t_expr, tsaritsa_on_left=True)

        lines = self.message.split('\n')
        for i, line in enumerate(lines):
            screen.blit(font_text.render(line, True, COLOR_TEXT), (220, h - 105 + (i*24)))

        self.btn_hint_rect = pygame.Rect(w - 550, h - 80, 250, 50)
        hint_disabled = (self.hints_left <= 0 or self.vs_winner is not None)
        self.draw_button(
            self.btn_hint_rect,
            f"Bantuan {self.active_algo} ({self.hints_left}/{self.max_hints})",
            custom_color=COLOR_BTN_HINT,
            custom_hover=COLOR_BTN_HINT_HOVER,
            disabled=hint_disabled
        )

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
                    self.hints_left = self.max_hints
                    self.last_hint_cells = []
                    self.message = "Semua Gnosis telah diletakkan secara acak.\nGeser bidak di kolomnya masing-masing\nuntuk mencari posisi aman tanpa konflik."
                elif 310 <= y <= 360: 
                    self.state = "VS_MENU"
                elif 380 <= y <= 430: 
                    self.state = "CLASH_MENU"
            return

        if self.state == "VS_MENU":
            if self.btn_back_rect.collidepoint(pos):
                self.state = "MENU"
                return
            for (lvl, code), rect in self.vs_btn_rects.items():
                if rect.collidepoint(pos):
                    self.start_vs_agent(lvl, code)
                    return
            return

        if self.state == "CLASH_MENU":
            if self.btn_back_rect.collidepoint(pos):
                self.state = "MENU"
                return
            for code, rect in self.clash_btn_left_rects.items():
                if rect.collidepoint(pos):
                    self.clash_algo1 = code
                    return
            for code, rect in self.clash_btn_right_rects.items():
                if rect.collidepoint(pos):
                    self.clash_algo2 = code
                    return
            if self.btn_start_clash_rect.collidepoint(pos):
                self.start_agent_clash()
                return
            return

        if self.state == "CLASH_PLAY":
            if self.btn_back_rect.collidepoint(pos):
                self.state = "CLASH_MENU"
                return
            if self.btn_rematch_clash_rect.collidepoint(pos):
                self.start_agent_clash()
                return
            return

        if self.state == "SOLO" and self.btn_hint_rect.collidepoint(pos):
            self.apply_tsaritsa_hint()
            return

        if self.state == "VS_AGENT_PLAY" and not self.vs_winner and self.btn_hint_rect.collidepoint(pos):
            self.apply_tsaritsa_hint()
            return

        # Handle Tombol Acak, Reset, dan Kembali
        if self.btn_back_rect.collidepoint(pos):
            self.state = "MENU"
            return
            
        if self.state == "SOLO":
            if self.btn_acak_rect.collidepoint(pos):
                self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
                self.hints_left = self.max_hints
                self.last_hint_cells = []
                self.message = "Papan pemain telah diacak ulang!"
                return

            if self.btn_reset_rect.collidepoint(pos):
                self.board = [0] * self.n  
                self.hints_left = self.max_hints
                self.last_hint_cells = []
                self.message = "Papan pemain telah di-reset!"
                return

            board_pixel_size = min(500, h - 150)
            tile_size = max(10, board_pixel_size // self.n) 
            offset_x = 220
            offset_y = (h - (tile_size * self.n)) // 2
            
            if offset_x <= x <= offset_x + tile_size*self.n and offset_y <= y <= offset_y + tile_size*self.n:
                col = (x - offset_x) // tile_size
                row = (y - offset_y) // tile_size
                
                self.board[col] = row 
                self.last_hint_cells = []
                
                c = self.agent.get_conflicts(self.board)
                if c == 0:
                    self.message = "Kemenangan Mutlak!\nSemua Gnosis telah dikumpulkan!"
                else:
                    self.message = f"Jumlah Konflik saat ini: {c}"

        # Klik Papan Kiri di Mode VS_AGENT_PLAY
        if self.state == "VS_AGENT_PLAY" and not self.vs_winner:
            board_pixel_size = min((w - 150) // 2, h - 250)
            self.vs_tile_size = max(10, board_pixel_size // self.n) 
            
            offset_x1 = 220
            offset_y1 = 100
            
            if offset_x1 <= x <= offset_x1 + self.vs_tile_size*self.n and offset_y1 <= y <= offset_y1 + self.vs_tile_size*self.n:
                col = (x - offset_x1) // self.vs_tile_size
                row = (y - offset_y1) // self.vs_tile_size
                
                self.board[col] = row 
                self.last_hint_cells = []
                
                if self.agent.get_conflicts(self.board) == 0:
                    self.vs_winner = "Player"
                    self.message = f"KAMU MENANG! Berhasil menaklukkan Phanes ({self.active_level})!"

    def start_vs_agent(self, level, algo):
        self.state = "VS_AGENT_PLAY"
        self.active_level = level
        self.active_algo = algo
        self.board = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.board_agent = [random.randint(0, self.n - 1) for _ in range(self.n)]
        self.vs_winner = None
        self.hints_left = self.max_hints
        self.last_hint_cells = []
        self.message = f"Level {level}: Geser bidakmu dan kalahkan {algo} Phanes!"
        
        self.player_start_time = time.perf_counter()
        self.player_timer = 0.0
        
        self.animation_steps, _, self.anim_speed = self.get_algo_steps_and_speed(algo)
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
                elif event.key == pygame.K_h:
                    if game.state == "SOLO" or (game.state == "VS_AGENT_PLAY" and not game.vs_winner):
                        game.apply_tsaritsa_hint()
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

        # --- UPDATE ANIMASI & TIMER DUAL BOARD (AGENT VS AGENT) ---
        if game.state == "CLASH_PLAY":
            now_perf = time.perf_counter()
            
            # Update Agent 1 (Kiri)
            if not game.clash_done1:
                game.clash_elapsed1 = now_perf - game.clash_start_time
                if current_time - game.clash_last_tick1 > game.clash_speed1:
                    if game.clash_idx1 < len(game.clash_steps1):
                        game.clash_board1 = game.clash_steps1[game.clash_idx1]
                        if game.clash_restart_flags1[game.clash_idx1]:
                            game.clash_restarts1 += 1
                        game.clash_conflict_hist1.append(game.agent.get_conflicts(game.clash_board1))
                        game.clash_idx1 += 1
                        game.clash_last_tick1 = current_time
                    else:
                        game.clash_done1 = True
                        game.clash_solved1 = (-1 not in game.clash_board1 and game.agent.get_conflicts(game.clash_board1) == 0)
                        if game.clash_solved1 and not game.clash_first_winner:
                            game.clash_first_winner = f"{game.clash_algo1} (Kiri)"

            # Update Agent 2 (Kanan)
            if not game.clash_done2:
                game.clash_elapsed2 = now_perf - game.clash_start_time
                if current_time - game.clash_last_tick2 > game.clash_speed2:
                    if game.clash_idx2 < len(game.clash_steps2):
                        game.clash_board2 = game.clash_steps2[game.clash_idx2]
                        if game.clash_restart_flags2[game.clash_idx2]:
                            game.clash_restarts2 += 1
                        game.clash_conflict_hist2.append(game.agent.get_conflicts(game.clash_board2))
                        game.clash_idx2 += 1
                        game.clash_last_tick2 = current_time
                    else:
                        game.clash_done2 = True
                        game.clash_solved2 = (-1 not in game.clash_board2 and game.agent.get_conflicts(game.clash_board2) == 0)
                        if game.clash_solved2 and not game.clash_first_winner:
                            game.clash_first_winner = f"{game.clash_algo2} (Kanan)"

            # Evaluasi Pesan Hasil Duel
            if game.clash_done1 and game.clash_done2:
                if game.clash_first_winner:
                    game.message = f"DUEL SELESAI! Pemenang tercepat: {game.clash_first_winner}!"
                else:
                    game.message = "DUEL SELESAI! Kedua algoritma terjebak di Local Optimum."
            elif game.clash_first_winner:
                game.message = f"{game.clash_first_winner} sudah menemukan solusi! Menunggu lawan..."

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
                        game.message = f"PHANES MENANG! Level {game.active_level} ({game.active_algo}) terlalu cepat."
                    else:
                        c_agent = game.agent.get_conflicts(game.board_agent)
                        game.vs_winner = "Player"
                        game.message = f"KAMU MENANG! Phanes [{game.active_level} - {game.active_algo}] terjebak Local Optimum ({c_agent} konflik)!"

        screen.fill(COLOR_BG)

        if game.state == "VN_STORY":
            game.draw_vn_scene()
        elif game.state == "MENU":
            game.draw_menu()
        elif game.state == "VS_MENU":
            game.draw_vs_menu()
        elif game.state == "VS_AGENT_PLAY":
            game.draw_vs_play()
        elif game.state == "CLASH_MENU":
            game.draw_clash_menu()
        elif game.state == "CLASH_PLAY":
            game.draw_clash_play()
        else:
            game.draw_solo()

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