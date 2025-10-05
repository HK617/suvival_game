import pygame
import random
import math
import json
import os

# ゲームの初期化
pygame.init()

# 画面設定
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Python Survivor")
print(SCREEN_WIDTH)
print(SCREEN_HEIGHT)
# ゲームの色
BLACK = (0, 0, 0)

#===================
# 音 (効果音、音楽)
#==================
# 音楽の初期化
#pygame.mixer.init()

# 背景音楽をロード
#pygame.mixer.music.load("bgm2.mp3")  # BGMファイルを置いてください（mp3やogg対応）

# 音量を調整（0.0 ～ 1.0）
#pygame.mixer.music.set_volume(0.2)

# 無限ループ再生
#pygame.mixer.music.play(-1)

#===================
# 画像
#==================
# 背景設定
# === Base（待機ルーム）画像 ===
base_image = pygame.image.load("base.png").convert_alpha()
base_image = pygame.transform.scale(base_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
# === 背景テクスチャ（タイル表示用） ===
bg_image = pygame.image.load("base.png").convert()  # ←質感を活かすなら convert() でOK
BG_W, BG_H = bg_image.get_width(), bg_image.get_height()
# ===ゲーム時背景===
background_image = pygame.image.load("SG_map1.png").convert_alpha()
background_image = pygame.transform.scale(background_image, (10000, 10000))

# Game Over / Start 画像
game_over_image = pygame.image.load("game_over.png").convert_alpha()
game_over_image = pygame.transform.scale(game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_start_image = pygame.image.load("game_start.png").convert_alpha()
game_start_image = pygame.transform.scale(game_start_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_clear_image = pygame.image.load("game_clear.png").convert_alpha()
game_clear_image = pygame.transform.scale(game_clear_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
# パワーアップ画面背景
power_up_back = pygame.image.load("power_up_back.png").convert_alpha()
power_up_back = pygame.transform.scale(power_up_back, (SCREEN_WIDTH, SCREEN_HEIGHT))

# パワーアップ用ボタン画像
attack_button = pygame.image.load("base_attack.png").convert_alpha()
attack_button = pygame.transform.scale(attack_button, (200, 60))
speed_button = pygame.image.load("player_speed.png").convert_alpha()
speed_button = pygame.transform.scale(speed_button, (200, 60))
hp_button = pygame.image.load("player_hp.png").convert_alpha()
hp_button = pygame.transform.scale(hp_button, (200, 60))
exp_button = pygame.image.load("EXP rato.png").convert_alpha()
exp_button = pygame.transform.scale(exp_button, (200, 60))

#ボタン画像
game_start_button = pygame.image.load("game_start_button.png").convert_alpha()
game_start_button = pygame.transform.scale(game_start_button, (300, 75))
power_up_button = pygame.image.load("power_up_button.png").convert_alpha()
power_up_button = pygame.transform.scale(power_up_button, (300, 75))
data_delete_button = pygame.image.load("data_delete_button.png").convert_alpha()
data_delete_button = pygame.transform.scale(data_delete_button, (300, 75))
restart_button = pygame.image.load("restart.png").convert_alpha()
restart_button = pygame.transform.scale(restart_button, (200, 50))
back_button = pygame.image.load("back.png").convert_alpha()
back_button = pygame.transform.scale(back_button, (200, 60))

#データ削除確認画像
delete_confirmation = pygame.image.load("delete_confirmation.png").convert_alpha()
delete_confirmation = pygame.transform.scale(delete_confirmation, (300, 200))

# 確認用ボタン画像（追加）
yes_button = pygame.image.load("yes.png").convert_alpha()
yes_button = pygame.transform.scale(yes_button, (140, 60))
no_button = pygame.image.load("no.png").convert_alpha()
no_button = pygame.transform.scale(no_button, (140, 60))

# レベルアップ選択用画像
choice_img1 = pygame.image.load("choices1.png").convert_alpha()
choice_img2 = pygame.image.load("choices2.png").convert_alpha()
choice_img3 = pygame.image.load("choices3.png").convert_alpha()
choice_img4 = pygame.image.load("choices4.png").convert_alpha()
choice_img5 = pygame.image.load("choices5.png").convert_alpha()
choice_img6 = pygame.image.load("choices6.png").convert_alpha()
choice_img7 = pygame.image.load("choices7.png").convert_alpha()
choice_img8 = pygame.image.load("choices8.png").convert_alpha()

# ---- レベルアップ選択肢の画像リスト（スケール済み）を用意 ----
CHOICE_IMG_W, CHOICE_IMG_H = 180, 180  # お好みで調整
_raw_choice_imgs = [
    choice_img1, choice_img2, choice_img3, choice_img4,
    choice_img5, choice_img6, choice_img7, choice_img8
]
choice_imgs = [
    pygame.transform.smoothscale(img, (CHOICE_IMG_W, CHOICE_IMG_H))
    for img in _raw_choice_imgs
]

# === レベルアップ選択肢の上限（好みで調整OK） ===
CHOICE_CAPS = {
    0: 5,  # Shortwave Duration
    1: 5,  # Laser Duration
    2: 6,  # EXP Rate
    3: 10, # Base Attack
    4: 5,  # Defense
    5: 10, # Critical Rate
    6: 10, # Critical Damage
    7: 5,  # Magnet Radius
}

# どの選択肢を何回取ったか（1プレイ内）
LEVELUP_PICK_COUNT = {i: 0 for i in range(8)}

CHOICE_COUNT = 8  # 選択肢の数（choices1〜8.png に対応）

def available_choices():
    """まだ上限に達していない choice_id のリストを返す"""
    return [i for i in range(CHOICE_COUNT) if LEVELUP_PICK_COUNT.get(i, 0) < CHOICE_CAPS.get(i, 0)]

# プレイヤー画像
player_original = pygame.image.load("player.png").convert_alpha()
player_original = pygame.transform.scale(player_original, (30, 30))
player_image = player_original

# プレイヤー描画位置（常に中央）
PLAYER_DRAW_X = SCREEN_WIDTH // 2 - player_original.get_width() // 2
PLAYER_DRAW_Y = SCREEN_HEIGHT // 2 - player_original.get_height() // 2

# 敵画像
enemy_image = pygame.image.load("SG_enemy(level1).png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (30, 30))

# EXPアイテム
exp_image = pygame.image.load("exp.png").convert_alpha()
exp_image = pygame.transform.scale(exp_image, (20, 20))

# Batteryアイテム
battery_image = pygame.image.load("battery.png").convert_alpha()
battery_image = pygame.transform.scale(battery_image, (20, 20))

#プレイヤー武器
# short wave画像（オリジナル3000×3000を保持）
Weapon_shortwave_base = pygame.image.load("short wave.png").convert_alpha()
shortwave_base_w, shortwave_base_h = Weapon_shortwave_base.get_size()
Weapon_shortwave_base.set_alpha(255)

# laser画像
weapon_laser_image_base = pygame.image.load("laser.png").convert_alpha()
weapon_laser_image_base = pygame.transform.scale(weapon_laser_image_base, (5, 800))
LASER_LENGTH = 1200  # 例：1200px

# セーブファイル名
SAVE_FILE = "savedata.json"

# フレームレート制御
clock = pygame.time.Clock()

# ===============================
# 日本語フォントの読みこと
# ===============================
def jp_font(size):
    """同梱フォントを最優先で使い、無ければシステム内の日本語フォントを探す"""
    # まずは同梱フォント（置いたパスに合わせて変更）
    try:
        return pygame.font.Font("fonts/NotoSansJP-Regular.ttf", size)
    except Exception:
        pass

    # システムフォントの候補（Windows / macOS / Linux）
    candidates = [
        "meiryo", "yu gothic ui", "yu gothic", "ms gothic",
        "hiragino sans", "hiragino kaku gothic pro", "noto sans cjk jp",
        "noto sans jp", "ipagothic", "ipaexgothic"
    ]
    available = set(pygame.font.get_fonts())  # 英小文字＆スペース無しで入ってくる
    for name in candidates:
        key = name.replace(" ", "").lower()
        if key in available:
            return pygame.font.SysFont(name, size)

    # どうしても見つからない最後の保険（等幅英字になる可能性あり）
    return pygame.font.Font(None, size)

# ===============================
# セーブデータの読み込み
# ===============================
def load_game_data():
    global persistent_attack_bonus, persistent_speed_bonus, persistent_maxhp_bonus, persistent_exp_bonus, battery
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            try:
                data = json.load(f)
                persistent_attack_bonus = data.get("persistent_attack_bonus", 0)
                persistent_speed_bonus = data.get("persistent_speed_bonus", 0)
                persistent_maxhp_bonus = data.get("persistent_maxhp_bonus", 0)
                persistent_exp_bonus = data.get("persistent_exp_bonus", 0)
                battery = data.get("battery", 0)
                print("セーブデータを読み込みました。")
            except json.JSONDecodeError:
                print("セーブファイルの読み込みに失敗しました。初期値を使用します。")
                persistent_attack_bonus = 0
                persistent_speed_bonus = 0
                persistent_maxhp_bonus = 0
                persistent_exp_bonus = 0
                battery = 0
    else:
        print("セーブファイルが見つかりません。初期値を使用します。")
        persistent_attack_bonus = 0
        persistent_speed_bonus = 0
        persistent_maxhp_bonus = 0
        persistent_exp_bonus = 0
        battery = 0

# ===============================
# セーブデータの保存
# ===============================
def save_game_data():
    data = {
        "persistent_attack_bonus": persistent_attack_bonus,
        "persistent_speed_bonus": persistent_speed_bonus,
        "persistent_maxhp_bonus": persistent_maxhp_bonus,
        "persistent_exp_bonus" : persistent_exp_bonus,
        "battery": battery
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=4) # indent=4 で見やすく整形して保存
    print("セーブデータを保存しました。")

# ===============================
# セーブデータの削除
# ===============================
def delete_save_data():
    global persistent_attack_bonus, persistent_speed_bonus, persistent_maxhp_bonus, persistent_exp_bonus, battery
    # 永続データを初期化（サバイバー安全初期値）
    persistent_attack_bonus = 1
    persistent_speed_bonus  = 5
    persistent_maxhp_bonus  = 10
    persistent_exp_bonus    = 1
    battery = 0
    save_game_data()
    # ゲーム全体をリセット（即時反映）
    reset_game()

# ===============================
# ゲーム描画
# ===============================
#base背景スクロール
def draw_tiled_bg(surface, texture, offset_x, offset_y):
    """texture を offset ずらしでタイル状に全面描画"""
    tw, th = texture.get_width(), texture.get_height()
    start_x = - (int(offset_x) % tw)
    start_y = - (int(offset_y) % th)
    x = start_x
    while x < surface.get_width():
        y = start_y
        while y < surface.get_height():
            surface.blit(texture, (x, y))
            y += th
        x += tw
        
def center_of_tile(gx, gy):
    return gx * TILE_W + TILE_W // 2, gy * TILE_H + TILE_H // 2
        
# --- 俯瞰トグル用のフラグ（未定義なら追加） ---
overlooking = False

# --- 背景タイルの設定（出現率） ---
BG_TILES = [
    ("bg1.png", 6),  # よく出す
    ("bg2.png", 3),  # 普通
    ("bg3.png", 1),  # レア
]

# --- シード（ゲーム毎に変えたいなら reset_game で更新） ---
BG_RANDOM_SEED = 1337

# --- タイルキャッシュ（グリッド→選ばれたタイルindex を保持） ---
bg_tile_cache = {}

# --- 読み込み（サイズ統一） ---
def load_bg_tiles(tiles, tile_w, tile_h):
    def scale_to_square(img, size):
        w, h = img.get_width(), img.get_height()
        if w == h:
            return pygame.transform.smoothscale(img, (size, size))
        # 画像全体が入るように「長辺=サイズ」に合わせて縮放し、余白は透明でパディング
        if w > h:
            new_w = size
            new_h = int(h * size / w)
        else:
            new_h = size
            new_w = int(w * size / h)
        scaled = pygame.transform.smoothscale(img, (new_w, new_h))
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.blit(scaled, ((size - new_w)//2, (size - new_h)//2))
        return surf

    images, cum_weights, total = [], [], 0.0
    for path, w in tiles:
        try:
            img = pygame.image.load(path).convert_alpha()  # 透明縁があってもOKに
        except pygame.error:
            img = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
            img.fill((40, 40, 40))
            pygame.draw.rect(img, (80, 80, 80), (0, 0, tile_w, tile_h), 6)

        # ★正方形に収める（タイルは tile_w == tile_h になっている前提）
        img = scale_to_square(img, tile_w)
        images.append(img)

        total += max(0.0, float(w))
        cum_weights.append(total)

    if total <= 0:
        cum_weights = [i+1 for i in range(len(images))]
        total = float(len(images))
    return images, cum_weights, total

# --- グリッドごとの重み付き乱数選択（安定乱数） ---
def _tile_hash(gx: int, gy: int) -> int:
    return ((gx * 1836311903) ^ (gy * 2971215073) ^ BG_RANDOM_SEED) & 0xffffffff

def _pick_weighted_index_from_hash(gx: int, gy: int) -> int:
    h = _tile_hash(gx, gy)
    t = (h / 4294967295.0) * bg_weights_total  # [0,total)
    for i, cw in enumerate(bg_cum_weights):
        if t < cw:
            return i
    return len(bg_cum_weights) - 1

def get_tile_index(gx: int, gy: int) -> int:
    key = (gx, gy)
    idx = bg_tile_cache.get(key)
    if idx is None:
        idx = _pick_weighted_index_from_hash(gx, gy)
        bg_tile_cache[key] = idx
    return idx

# === タイル座標ユーティリティ ===
# スポーン時のタイル(0,0)の“ワールド左上”をアンカーとして保持する
SPAWN_ANCHOR_WX = 0
SPAWN_ANCHOR_WY = 0
SPAWN_TILE_GX = 0
SPAWN_TILE_GY = 0

def world_to_tile(wx, wy):
    """ワールド座標(px) → タイル座標(gx, gy) へ（現在の TILE_W/H を使用）"""
    return int(math.floor(wx / TILE_W)), int(math.floor(wy / TILE_H))

def recalc_spawn_tile_indices():
    """現在のタイルサイズに合わせてスポーン(0,0)のタイル座標を再計算"""
    global SPAWN_TILE_GX, SPAWN_TILE_GY
    SPAWN_TILE_GX = int(math.floor(SPAWN_ANCHOR_WX / TILE_W))
    SPAWN_TILE_GY = int(math.floor(SPAWN_ANCHOR_WY / TILE_H))

# --- 現在のズームに合わせてタイル再生成（正方形で統一） ---
TILE_MIN = 64              # 俯瞰(0.1)でも小さく見せたいなら 32 でも可
BASE_TILE_SCALE = 5.0      # 通常プレイ時の基準ズーム
TILE_SCALE = BASE_TILE_SCALE

def apply_tile_scale(scale: float):
    global TILE_SCALE, TILE_W, TILE_H
    global bg_seq, bg_cum_weights, bg_weights_total, bg_tile_cache

    TILE_SCALE = float(scale)

    # ★正方形サイズを決める（画面の短辺基準がおすすめ）
    base_len   = min(SCREEN_WIDTH, SCREEN_HEIGHT)
    TILE_SIZE  = max(TILE_MIN, int(base_len * TILE_SCALE))

    # ★幅・高さとも同じ（=正方形）
    TILE_W = TILE_SIZE
    TILE_H = TILE_SIZE

    # 並びはグリッド座標で決まるのでサイズ変更時はキャッシュを消す
    bg_tile_cache.clear()
    bg_seq, bg_cum_weights, bg_weights_total = load_bg_tiles(BG_TILES, TILE_W, TILE_H)
    recalc_spawn_tile_indices()   # ← 追加：ズーム切替後も(0,0)を同じ場所に保つ

# --- 初期生成（※ここで初めて呼ぶ） ---
apply_tile_scale(TILE_SCALE)
apply_tile_scale(TILE_SCALE)

# --- 2D連結描画 ---
def draw_bg_sequence_2d(surface, images, tile_w, tile_h, offset_x, offset_y):
    if not images:
        surface.fill((0, 0, 0)); return
    W, H = surface.get_width(), surface.get_height()
    start_x = - (int(offset_x) % tile_w)
    start_y = - (int(offset_y) % tile_h)
    grid_x0 = int(offset_x) // tile_w
    grid_y0 = int(offset_y) // tile_h
    y, gy = start_y, grid_y0
    while y < H:
        x, gx = start_x, grid_x0
        while x < W:
            idx = get_tile_index(gx, gy)   # 重み付きランダム＋キャッシュ
            surface.blit(images[idx], (x, y))
            x += tile_w; gx += 1
        y += tile_h; gy += 1

# 俯瞰マップのプレイヤー表示
def bg_offset_from_camera(cx, cy):
    """
    カメラ（=プレイヤー）を画面中央に置くとき、
    背景描画の offset_x/offset_y（= 画面左上のワールド座標）を返す。
    """
    return int(cx - SCREEN_WIDTH // 2), int(cy - SCREEN_HEIGHT // 2)

def draw_game(screen):
    global level_up_notice_rect

    # ★ プレイヤーを中心にした背景オフセットを取得
    bg_off_x, bg_off_y = bg_offset_from_camera(player_x, player_y)

    # 背景を先に描く（上書きしない）
    draw_bg_sequence_2d(screen, bg_seq, TILE_W, TILE_H, bg_off_x, bg_off_y)

    # プレイヤー
    screen.blit(player_image, (PLAYER_DRAW_X, PLAYER_DRAW_Y))

    # EXPアイテム
    for item in exp_items:
        draw_x = item["rect"].x - player_x + PLAYER_DRAW_X
        draw_y = item["rect"].y - player_y + PLAYER_DRAW_Y
        screen.blit(exp_image, (draw_x, draw_y))

    # Batteryアイテム
    for item in battery_items:
        draw_x = item["rect"].x - player_x + PLAYER_DRAW_X
        draw_y = item["rect"].y - player_y + PLAYER_DRAW_Y
        screen.blit(battery_image, (draw_x, draw_y))

    #敵
    for enemy in enemies:
        draw_x = enemy['x'] - player_x + PLAYER_DRAW_X
        draw_y = enemy['y'] - player_y + PLAYER_DRAW_Y
        if enemy.get('dying'):
            a = max(0, min(255, int(enemy['alpha'])))
            nearest = min(ENEMY_FADE_LEVELS, key=lambda v: abs(v - a))
            img = enemy_fade_images[nearest]
        else:
            img = enemy_image
        screen.blit(img, (draw_x, draw_y))

    # shortwave
    for wave in shortwaves:
        rect = wave["image"].get_rect(center=(wave["x"] - player_x + PLAYER_DRAW_X,
                                              wave["y"] - player_y + PLAYER_DRAW_Y))
        screen.blit(wave["image"], rect)

    # laser
    for laser in lasers:
        draw_x = laser["rect"].x - player_x + PLAYER_DRAW_X
        draw_y = laser["rect"].y - player_y + PLAYER_DRAW_Y
        screen.blit(laser["image"], (draw_x, draw_y))

    # ダメージテキスト
    for dt in damage_texts:
        font = jp_font(20)
        color = (255, 255, 0) if dt["crit"] else (255, 50, 50)
        dmg_surf = font.render(dt["text"], True, color)
        draw_x = dt["x"] - player_x + PLAYER_DRAW_X
        draw_y = dt["y"] - player_y + PLAYER_DRAW_Y
        screen.blit(dmg_surf, (draw_x, draw_y))

    # --- レベルアップ待機通知（クリック可能） ---
    if 'level_up_pending' in globals() and level_up_pending:
        notice_font = jp_font(50)
        notice = notice_font.render("level up available", True, (255, 215, 0))
        x = int(SCREEN_WIDTH / 2 - 120)   # ←あなたの元の位置そのまま
        y = SCREEN_HEIGHT - 60

        # 当たり判定用のRectを保存
        level_up_notice_rect = notice.get_rect(topleft=(x, y))
        screen.blit(notice, level_up_notice_rect)

        # クリックしやすいように少し大きい枠を付けたい場合（任意）
        # pygame.draw.rect(screen, (255, 215, 0), level_up_notice_rect.inflate(12, 8), width=2)
    else:
        level_up_notice_rect = None

    # 残り時間

    time_font = jp_font(70)
    # 分と秒に分解
    minutes = remaining_time // 60
    seconds = remaining_time % 60

    # 表示形式（ゼロ埋め：01:05 など）
    remaining_time_text = time_font.render(f"{minutes:02d}:{seconds:02d}", True, (0, 0, 0))

    # --- 画面中央上に配置 ---
    text_rect = remaining_time_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 8))
    screen.blit(remaining_time_text, text_rect)

    
    # UI
    font = jp_font(30)
    hp_text = font.render(f"HP: {player_hp}/{player_max_hp}", True, (255, 0, 0))
    display_exp = min(exp, exp_to_next)
    level_text = font.render(f"Level: {level}  EXP: {display_exp}/{exp_to_next}", True, (0, 255, 0))
    battery_text = font.render(f"Battery: {battery}", True, (255, 255, 0))
    score_text = font.render(f"Score: {score}", True, (0, 255, 255))
    enemy_level_text = font.render(f"Enemy Lv: {enemy_level}", True, (255, 255, 255))
    coord_text = font.render(f"X: {int(player_x)}  Y: {int(player_y)}", True, (0, 0, 0)) 
    text_rect = coord_text.get_rect()
    text_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)

    screen.blit(hp_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(battery_text, (10, 90))
    screen.blit(score_text, (10, 130))
    screen.blit(enemy_level_text, (10, 170))
    screen.blit(coord_text, text_rect)

# ===============================
# ゲームリセット
# ===============================
def reset_game():
    global BG_RANDOM_SEED
    global player_x, player_y, player_hp, player_max_hp, base_attack, exp, level, exp_to_next, exp_rato, player_speed, player_defence, player_clitical_rato, player_clitical_damage, PLAYER_IFRAME_MAX, player_iframe, player_vx, player_vy
    global weapons, weapon_counter, lasers, laser_level, laser_timer, laser_cooldown, laser_duration, enemy_spawn_timer, score, start_ticks
    global enemies, enemy_base_hp, enemy_base_attack, enemy_speed, enemy_level, last_buff_time, ENEMY_RADIUS, ENEMY_SEP_ITER
    global damage_texts
    global exp_items, start_ticks, battery, battery_items, MAGNET_RADIUS, ITEM_HOMING_SPEED, SPAWN_ANCHOR_WX, SPAWN_ANCHOR_WY
    global shortwaves, Weapon_shortwave_image, shortwave_base_w, shortwave_base_h, initial_scale, shortwave_level, weapon_shortwave_cooldown, weapon_shortwave_duration, weapon_shortwave_timer
    global game_speed, game_time, goel_time, game_clear
    global LEVELUP_PICK_COUNT

    start_ticks = pygame.time.get_ticks()  # ← ゲーム開始時刻（ミリ秒）

    # --- スポーンタイルを(0,0)に固定し、プレイヤーはそのタイルの「中心」に置く ---
    # タイルの左上座標（アンカー）を記録
    SPAWN_TILE_GX = 0
    SPAWN_TILE_GY = 0
    SPAWN_ANCHOR_WX = SPAWN_TILE_GX * TILE_W
    SPAWN_ANCHOR_WY = SPAWN_TILE_GY * TILE_H
    recalc_spawn_tile_indices()  # 上のANCHORから(0,0)のタイル番号を再計算

    SPAWN_TILE_GX = 0; SPAWN_TILE_GY = 0
    SPAWN_ANCHOR_WX = SPAWN_TILE_GX * TILE_W
    SPAWN_ANCHOR_WY = SPAWN_TILE_GY * TILE_H
    recalc_spawn_tile_indices()
    player_x, player_y = center_of_tile(SPAWN_TILE_GX, SPAWN_TILE_GY)

    # タイル中心 = 左上 + (TILE_W/2, TILE_H/2)
    player_x = SPAWN_ANCHOR_WX + TILE_W // 2
    player_y = SPAWN_ANCHOR_WY + TILE_H // 2

    # マップのリセット
    bg_tile_cache.clear()
    BG_RANDOM_SEED = random.randint(0, 2**31 - 1)

    #ゲームスピード
    game_speed = 1.0

    #ゲーム内経過時間
    game_time = 0   # ゲーム内時間（秒単位で管理）

    #生存目標時間(秒)
    goel_time = 600 #10分
    game_clear = False

    # レベルアップ選択肢の選択回数を初期化
    LEVELUP_PICK_COUNT = {i: 0 for i in range(8)}  # ← 追加（1プレイ内カウントをリセット）

    # --- 「そのプレイの」ステータスはベース値 + 永続ボーナスで初期化する ---
    base_attack = persistent_attack_bonus
    player_speed = persistent_speed_bonus
    player_max_hp = persistent_maxhp_bonus
    player_hp = player_max_hp
    exp_rato = persistent_exp_bonus

    #プレイヤ基礎ステータス（power upで使わない)
    player_defence = 0
    player_clitical_rato = 0.05
    player_clitical_damage = 2
    #プレイヤー被弾後無敵時間
    PLAYER_IFRAME_MAX = 30  # 30フレーム ≒ 0.5秒（60FPS）
    player_iframe = 0
    #ノックバック速度
    player_vx = 0.0
    player_vy = 0.0

    # --- 経験値・レベルの初期化 ---
    exp = 0
    level = 1
    exp_to_next = 10

    # --- アイテム吸い寄せ範囲 ---
    MAGNET_RADIUS = 50          # プレイヤー周りの当たり判定（半径）
    ITEM_HOMING_SPEED = 6.0      # アイテムが吸い込まれるときの基準速度（px/フレーム）

    weapons = []  # すべての攻撃オブジェクトを入れる共通リスト
    weapon_counter = 0
    enemies = []
    shortwaves = []
    shortwave_level = 1
    weapon_shortwave_timer = 0
    weapon_shortwave_duration = 30   # ← 初期値にリセット（0.5秒くらい）
    weapon_shortwave_cooldown = 120   # 2秒に1回
    lasers = []   # レーザーのリスト
    laser_level = 1
    laser_timer = 0
    laser_cooldown = 360  # 6秒に1回（60FPS前提）
    laser_duration = 30   # 初期出現時間（0.5秒くらい）
    enemy_spawn_timer = 0
    score = 0
    start_ticks = pygame.time.get_ticks()
    last_buff_time = start_ticks
    damage_texts = []  # ダメージ表示リスト
    exp_items = []
    battery_items = []

    # 敵の初期能力
    enemy_base_hp = 1
    enemy_base_attack = 1
    enemy_speed = 1.0
    enemy_level = 1

    #敵のプロパティ（設定）
    # ← 追加：敵の当たり判定用の円半径（押し合いの基準）
    ENEMY_RADIUS = enemy_image.get_width() // 2
    # 押し戻しの反復回数（2回くらいで十分）
    ENEMY_SEP_ITER = 2
    
    # short wave初期化（レベル1サイズに縮小）
    initial_scale = 70 / shortwave_base_w   # ← 初期サイズを70pxにする場合
    Weapon_shortwave_image = pygame.transform.smoothscale(
        Weapon_shortwave_base,
        (int(shortwave_base_w * initial_scale), int(shortwave_base_h * initial_scale))
    )

#敵同士の当たり判定
def resolve_enemy_collisions(enemies):
    """
    敵同士が重ならないように半径 ENEMY_RADIUS の円同士として押し戻す。
    空間ハッシュで近傍だけをチェック。
    """
    if not enemies:
        return

    cell = ENEMY_RADIUS * 2  # 1マス=直径
    for _ in range(ENEMY_SEP_ITER):
        grid = {}
        # バケットに振り分け
        for idx, e in enumerate(enemies):
            cx = int(e['x'] // cell)
            cy = int(e['y'] // cell)
            grid.setdefault((cx, cy), []).append(idx)

        # 3x3 近傍セルだけチェック
        checked = set()
        for (cx, cy), indices in grid.items():
            for nx in (cx-1, cx, cx+1):
                for ny in (cy-1, cy, cy+1):
                    neigh = grid.get((nx, ny))
                    if not neigh:
                        continue
                    # このセル内の全ペア
                    for i in indices:
                        for j in neigh:
                            if j <= i:  # 同一 or 逆順はスキップ
                                continue
                            key = (i, j)
                            if key in checked:
                                continue
                            checked.add(key)

                            a = enemies[i]
                            b = enemies[j]
                            dx = b['x'] - a['x']
                            dy = b['y'] - a['y']
                            dist2 = dx*dx + dy*dy
                            min_d = ENEMY_RADIUS * 2

                            if dist2 == 0:
                                # 全く同座標 → ランダム微小オフセットで分離のきっかけ
                                off = 0.5
                                a['x'] -= off; a['y'] -= off
                                b['x'] += off; b['y'] += off
                                a['rect'].topleft = (int(a['x']), int(a['y']))
                                b['rect'].topleft = (int(b['x']), int(b['y']))
                                continue

                            if dist2 < (min_d * min_d):
                                dist = math.sqrt(dist2)
                                # めり込み量
                                pen = min_d - dist
                                # 法線（単位ベクトル）
                                nx_ = dx / dist
                                ny_ = dy / dist
                                # 半分ずつ押し戻す
                                push = pen * 0.5
                                a['x'] -= nx_ * push
                                a['y'] -= ny_ * push
                                b['x'] += nx_ * push
                                b['y'] += ny_ * push
                                # rect 更新
                                a['rect'].topleft = (int(a['x']), int(a['y']))
                                b['rect'].topleft = (int(b['x']), int(b['y']))

# 敵を出現させる
def spawn_enemy():
    if len(enemies) >= MAX_ENEMIES:
        return
    side = random.randint(0, 3)
    if side == 0:
        x = random.randint(0, SCREEN_WIDTH - enemy_image.get_width()) + player_x - SCREEN_WIDTH // 2
        y = player_y - SCREEN_HEIGHT // 2 - enemy_image.get_height()
    elif side == 1:
        x = random.randint(0, SCREEN_WIDTH - enemy_image.get_width()) + player_x - SCREEN_WIDTH // 2
        y = player_y + SCREEN_HEIGHT // 2
    elif side == 2:
        x = player_x - SCREEN_WIDTH // 2 - enemy_image.get_width()
        y = random.randint(0, SCREEN_HEIGHT - enemy_image.get_height()) + player_y - SCREEN_HEIGHT // 2
    else:
        x = player_x + SCREEN_WIDTH // 2
        y = random.randint(0, SCREEN_HEIGHT - enemy_image.get_height()) + player_y - SCREEN_HEIGHT // 2
    enemies.append({
        'rect': pygame.Rect(x, y, enemy_image.get_width(), enemy_image.get_height()),
        'x': x, 'y': y,
        'hp': enemy_base_hp,
        'atk': enemy_base_attack,
        'level': enemy_level, 
        'last_hits': {},
        'alpha': 255,       # フェードアウト用の透明度
        'dying': False      # フェードアウト中かどうか
    })

ENEMY_FADE_LEVELS = [255, 200, 150, 100, 50, 0]
enemy_fade_images = {}
for a in ENEMY_FADE_LEVELS:
    surf = enemy_image.copy()
    surf.set_alpha(a)
    enemy_fade_images[a] = surf

#武器のID
def next_weapon_id():
    global weapon_counter
    weapon_counter += 1
    return weapon_counter

GROW_FRAMES = 60.0      # 何フレームで最大まで膨らむか（速度は game_speed のみで変化）
BASE_MAX_SCALE = 6.0    # 最低の最大倍率
SCALE_PER_60F  = 1.0    # 寿命60f延長ごとに +1.0倍
GROW_PER_60F = 3.0
def spawn_shortwave():
    life_f = float(weapon_shortwave_duration)  # フレーム寿命
    wave = {
        "type": "shortwave",
        "x": player_x,
        "y": player_y,
        "rect": Weapon_shortwave_image.get_rect(center=(player_x, player_y)),
        "timer": life_f,                 # ← 残り寿命(フレーム)
        "lifetime_f": life_f,              # ← 生成時の寿命(フレーム)
        "damage": base_attack * 2,
        "id": next_weapon_id(),
        "image": Weapon_shortwave_image,
        "max_scale": 6.0                   # 上限スケール（お好みで）
    }
    shortwaves.append(wave)
    weapons.append(wave)

def laser_hits_point(laser, px, py, origin_x, origin_y):
    base_w, base_h = weapon_laser_image_base.get_size()  # 5x800
    half_w = base_w * 0.5

    ang = math.radians(laser['angle'])

    # ★ スプライトの縦基準に合わせた軸ベクトル
    dir_x = math.sin(ang)
    dir_y = -math.cos(ang)

    vx = px - origin_x
    vy = py - origin_y

    proj = vx * dir_x + vy * dir_y  # 原点(プレイヤー)から軸方向の距離

    # ★ 有効区間：プレイヤーから前方に 0..800px
    if 0 <= proj <= base_h:
        # 軸からの垂線距離
        perp_dist = abs(-dir_y * vx + dir_x * vy)
        return perp_dist <= half_w
    return False

def point_to_segment_distance(px, py, x1, y1, x2, y2):
    # 線分上の最近点を使う距離
    vx, vy = x2 - x1, y2 - y1
    wx, wy = px - x1, py - y1
    vv = vx*vx + vy*vy
    if vv <= 1e-9:
        # 長さゼロの保険
        dx, dy = px - x1, py - y1
        return math.hypot(dx, dy)
    t = max(0.0, min(1.0, (wx*vx + wy*vy) / vv))
    cx = x1 + t * vx
    cy = y1 + t * vy
    return math.hypot(px - cx, py - cy)

def clamp01(t: float) -> float:
    return 0.0 if t < 0.0 else (1.0 if t > 1.0 else t)

def segment_segment_distance(x1, y1, x2, y2, x3, y3, x4, y4) -> float:
    """2D線分 (x1,y1)-(x2,y2) と (x3,y3)-(x4,y4) の最短距離"""
    ux, uy = x2 - x1, y2 - y1
    vx, vy = x4 - x3, y4 - y3
    wx, wy = x1 - x3, y1 - y3

    a = ux*ux + uy*uy  # |u|^2
    b = ux*vx + uy*vy  # u·v
    c = vx*vx + vy*vy  # |v|^2
    d = ux*wx + uy*wy  # u·w
    e = vx*wx + vy*wy  # v·w
    D = a*c - b*b

    if D > 1e-9:
        sc = clamp01((b*e - c*d) / D)
    else:
        sc = 0.0  # ほぼ平行

    # tc は sc に合わせて再計算
    tc = (b*sc + e) / c if c > 1e-9 else 0.0
    tc = clamp01(tc)

    # もう一度 sc を tc に合わせて微調整
    sc = (b*tc - d) / a if a > 1e-9 else 0.0
    sc = clamp01(sc)

    cx1, cy1 = x1 + sc*ux, y1 + sc*uy   # 線分1上の最接近点
    cx2, cy2 = x3 + tc*vx, y3 + tc*vy   # 線分2上の最接近点
    dx, dy = cx2 - cx1, cy2 - cy1
    return math.hypot(dx, dy)

def spawn_laser():
    global lasers, weapons
    # レベルごとの本数を計算（3レベルごとに1本追加）
    num_lasers = 1 + (level // 3)
    laser_angle = random.randint(0, 359)
    
    for i in range(num_lasers):  # ← レベル分÷3本レーザー生成
        angle_offset = i * (360 // num_lasers) + laser_angle  # 均等配置
        laser = {
            "type": "laser",
            "x": player_x,
            "y": player_y,
            "rect": weapon_laser_image_base.get_rect(center=(player_x, player_y)),
            "timer": laser_duration / game_speed,
            "rot_timer": 30 / game_speed,
            "angle": angle_offset,
            "damage": base_attack, 
            "id": next_weapon_id()
        }
        lasers.append(laser)
        weapons.append(laser)



# ===============================
# レベルアップ処理
# ===============================
#レベルアップ選択肢抽選
def roll_level_choices():
    """上限未到達のプールから重複なしで最大3つを抽選"""
    global current_level_choices
    pool = available_choices()
    if not pool:
        current_level_choices = []
        return
    k = min(3, len(pool))
    current_level_choices = random.sample(pool, k)

def get_level_choice_rects():
    """current_level_choices の枚数に応じて、中央揃えでRectを返す"""
    w, h = CHOICE_IMG_W, CHOICE_IMG_H
    n = len(current_level_choices)
    total_w = n * w + (n - 1) * LEVEL_CHOICE_GAP if n > 0 else 0
    start_x = SCREEN_WIDTH // 2 - total_w // 2
    y = SCREEN_HEIGHT // 2 - h // 2

    rects = []
    for i in range(n):
        x = start_x + i * (w + LEVEL_CHOICE_GAP)
        rects.append(pygame.Rect(x, y, w, h))
    return rects

#レベルアップの強化
def level_up(choice_id):
    global exp, exp_to_next, level
    global base_attack, player_speed, player_clitical_rato, player_clitical_damage
    global player_max_hp, player_hp, player_defence
    global shortwave_level, laser_level, weapon_shortwave_duration, laser_duration, level_up_pending
    global exp_rato, MAGNET_RADIUS, weapon_shortwave_cooldown, current_level_choices
    global LEVELUP_PICK_COUNT, current_level_choices

        # 念のため：上限到達なら何もしない
    if LEVELUP_PICK_COUNT.get(choice_id, 0) >= CHOICE_CAPS.get(choice_id, 0):
        # ここに来た場合は表示側の漏れ。安全に抜ける。
        current_level_choices = []
        # 次のレベルが連続で溜まっている場合は再抽選
        if exp >= exp_to_next:
            pool = available_choices()
            if pool:
                level_up_pending = True
                roll_level_choices()
            else:
                level_up_pending = False
        else:
            level_up_pending = False
        return

    # 必要分だけ消費（超過分は保持）
    exp -= exp_to_next
    level += 1
    exp_to_next = int(exp_to_next * 1.5)

    # ベースの上昇（共通の少量アップ）
    base_attack += 1
    player_max_hp += 10
    player_hp = min(player_hp + 10, player_max_hp)

    # ---- 候補ごとの効果（0..6）----
    if choice_id == 0:
        # Shortwave持続アップ
        weapon_shortwave_duration = int(weapon_shortwave_duration * 1.5)
        shortwave_level += 1
    elif choice_id == 1:
        # Laser持続アップ
        laser_duration = int(laser_duration * 1.5)
        laser_level += 1
    elif choice_id == 2:
        # EXP倍率アップ
        exp_rato += 0.5
    elif choice_id == 3:
        # 攻撃力アップ
        base_attack += 2
    elif choice_id == 4:
        #　防御力アップ
        player_defence += 10
    elif choice_id == 5:
        # クリティカル率アップ
        player_clitical_rato += 0.05
    elif choice_id == 6:
        player_clitical_damage += 1
    elif choice_id == 7:
        MAGNET_RADIUS += 100

    # --- まだ次のレベルにも届いているなら、保留継続 ---
    if exp >= exp_to_next:
        level_up_pending = True
        roll_level_choices()   # 次の3候補を再抽選（test.py の仕様を維持）
    else:
        level_up_pending = False
        current_level_choices = []

    LEVELUP_PICK_COUNT[choice_id] = LEVELUP_PICK_COUNT.get(choice_id, 0) + 1

# レベルアップ選択肢の説明
CHOICE_INFO = {
    0: {"title": "Shortwave Duration ↑", "lines": ["ショートウェーブの持続時間を1.5倍にします。", "広がって当たり判定が長く残るのでDPSが安定。", "現在のショートウェーブレベル: {shortwave_level}"]},
    1: {"title": "Laser Duration ↑", "lines": ["レーザーの持続時間を1.5倍にします。", "回転中の当たり判定時間が延びて総合ダメージ増。", "現在のレーサーレベル: {laser_level}"]},
    2: {"title": "EXP Rate ↑", "lines": ["取得EXP倍率を+0.5します。", "以後のレベルアップペースが上がります。"]},
    3: {"title": "Base Attack ↑", "lines": ["基礎攻撃力を+2します。", "全武器ダメージに効果的。"]},
    4: {"title": "Defense ↑", "lines": ["防御力を+10します。", "被ダメージを軽減して生存力↑。"]},
    5: {"title": "Critical Rate ↑", "lines": ["クリティカル率を+5%します。", "運が絡むが期待ダメージ上昇。"]},
    6: {"title": "Critical Damage ↑", "lines": ["クリティカル倍率を+1します。", "クリティカル時の伸びが大きい。"]},
    7: {"title": "Magnet Radius ↑", "lines": ["アイテム吸引半径を+100します。", "取りこぼし減でテンポ良く育ちます。"]},
}



# ===============================
# 初期化
# ===============================
game_time = 0
real_time = 0

battery = 0
player_speed = 5
ENEMY_SPAWN_INTERVAL = 30
MAX_ENEMIES = 250

# プログラム開始時にセーブデータを読み込む
load_game_data()

# フラグリスト
running = True
in_base = False
paused = False
game_over = False
game_clear = False
game_start = True
power_up_screen = False
delete_data = False
# レベルアップ待ちフラグ
level_up_pending = False
# レベルアップ時選択肢説明の開始フラグ
choice_waiting = False
selected_choice_idx = None
overlooking = False

# === ノックバック設定 ===
KNOCKBACK_IMPULSE = 14.0   # 1回のヒットで与える押し返し量（好みで 10〜20）
KNOCKBACK_DECAY   = 0.88   # 毎フレームの減衰（0.85〜0.93 くらいが無難）

# 速度（ノックバック用ベクトル）
player_vx = 0.0
player_vy = 0.0

# 被弾後の無敵（i-frame）
PLAYER_IFRAME_MAX = 30     # 60FPSで約0.5秒
player_iframe = 0

# === Base（待機ルーム）用：プレイヤーは画面中央固定。動くのは“世界” ===
BASE_SPEED = 5
base_world_x = 0.0   # ワールド座標（背景側が動くので、こっちが増減）
base_world_y = 0.0

# Base 背景スクロール量
base_bg_scroll_x = 0.0
base_bg_scroll_y = 0.0
BASE_BG_AUTO_VX = 0.4   # 自動でゆっくり流れる速度
BASE_BG_AUTO_VY = 0.2
BASE_BG_PARALLAX = 0.3  # 入力に対するパララックス寄与（0〜1）

# -----------------------------
# Power Up のコスト設定
# -----------------------------
POWERUP_COST_ATTACK = 20
POWERUP_COST_SPEED  = 15
POWERUP_COST_HP     = 30
POWERUP_COST_EXP    = 100

# レベルアップ選択UIの表示位置オフセット（マイナスで左・上）
LEVEL_CHOICE_GAP = 24          # 画像の間隔（px）

#レベルアップ通知テキスト当たり判定
level_up_notice_rect = None

# 俯瞰モード時に表示するプレイヤーアイコンのピクセルサイズ
OVERLOOK_PLAYER_PX = 20

# -----------------------------
# Power Up 関数
# -----------------------------
def power_up_attack():
    global persistent_attack_bonus, base_attack, battery
    if battery >= POWERUP_COST_ATTACK:
        battery -= POWERUP_COST_ATTACK
        persistent_attack_bonus += 1
    else:
        print("バッテリー不足！")

def power_up_speed():
    global persistent_speed_bonus, player_speed, battery
    if battery >= POWERUP_COST_SPEED:
        battery -= POWERUP_COST_SPEED
        persistent_speed_bonus += 1
    else:
        print("バッテリー不足！")

def power_up_hp():
    global persistent_maxhp_bonus, battery
    if battery >= POWERUP_COST_HP:
        battery -= POWERUP_COST_HP
        persistent_maxhp_bonus += 10
    else:
        print("バッテリー不足！")

def power_up_exp():
    global persistent_exp_bonus, exp_rato, battery
    if battery >= POWERUP_COST_EXP:
        battery -= POWERUP_COST_EXP
        persistent_exp_bonus += 0.01
    else:
        print("バッテリー不足！")

# ===============================
# メインループ
# ===============================
while running:
    if game_start:
        # スタート画面の背景
        screen.fill(BLACK)
        screen.blit(game_start_image, (
            SCREEN_WIDTH // 2 - game_start_image.get_width() // 2,
            SCREEN_HEIGHT // 2 - game_start_image.get_height() // 2
        ))

        # スタートボタン
        start_rect = game_start_button.get_rect(center=(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4))
        screen.blit(game_start_button, start_rect)

        # パワーアップボタン（スタートボタンの下に配置）
        power_rect = power_up_button.get_rect(center=(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4 + 100))
        screen.blit(power_up_button, power_rect)

        data_delete_rect = data_delete_button.get_rect(center=(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4 + 200))
        screen.blit(data_delete_button, data_delete_rect)

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESCキーで終了
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    # reset_game() は呼ばず、まず base へ入る
                    game_start = False
                    in_base = True
                    # ワールド原点に戻す
                    base_world_x = 0.0
                    base_world_y = 0.0
                elif power_rect.collidepoint(event.pos):
                    power_up_screen = True
                    game_start = False
                elif data_delete_rect.collidepoint(event.pos):
                    delete_data = True
                    game_start = False

        # --- ここでフレーム終了 ---
        pygame.display.flip()
        clock.tick(60)
        continue   # ← while running の先頭に戻る

    # ===== Base（待機ルーム） =====
    if in_base:
    # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    in_base = False
                    game_start = True
                if event.key == pygame.K_h:
                    base_world_x = 0
                    base_world_y = 0

        # 入力（ワールド座標を更新：右に進む=世界を左へ流すのと同義）
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += BASE_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= BASE_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += BASE_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= BASE_SPEED

        base_world_x += dx
        base_world_y += dy

        # 到達チェック：ワールド座標(100,100) に“中央の自分”が重なったら開始
        if abs(base_world_x - 100) <= 20 and abs(base_world_y - 100) <= 20:
            reset_game()
            in_base = False

        # ===== 描画 =====
        # 背景をワールドオフセットでタイル描画（offsetが増えると左に流れる）
        draw_tiled_bg(screen, bg_image, base_world_x, base_world_y)

        # 目印：ワールド(100,100)の地点を画面上に投影して描く
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        target_screen_x = int(center_x + (100 - base_world_x))
        target_screen_y = int(center_y + (100 - base_world_y))
        pygame.draw.circle(screen, (255, 0, 0), (target_screen_x, target_screen_y), 8, 2)

        # プレイヤーは常に中央に描画（向きだけ入力で変える）
        if dx > 0:
            player_image_draw = pygame.transform.rotate(player_original, 270)
        elif dx < 0:
            player_image_draw = pygame.transform.rotate(player_original, 90)
        elif dy > 0:
            player_image_draw = pygame.transform.rotate(player_original, 180)
        elif dy < 0:
            player_image_draw = player_original
        else:
            player_image_draw = player_image

        screen.blit(
            player_image_draw,
            (center_x - player_original.get_width() // 2,
             center_y - player_original.get_height() // 2)
        )

        # デバッグ表示（任意）：いまのワールド座標
        font = jp_font(24)
        screen.blit(font.render(f"World Pos: ({int(base_world_x)}, {int(base_world_y)})", True, (0,0,0)), (10, 10))
        screen.blit(font.render("Go to (100,100) to START", True, (0,0,0)), (10, 40))

        pygame.display.flip()
        clock.tick(60)
        continue

    if power_up_screen:
        # 背景を表示
        screen.blit(power_up_back, (0, 0))

        # --- 強化候補ボタンを3つ（画像版） ---
        upgrade1_rect = attack_button.get_rect(center=(SCREEN_WIDTH // 2, 250))
        upgrade2_rect = speed_button.get_rect(center=(SCREEN_WIDTH // 2, 350))
        upgrade3_rect = hp_button.get_rect(center=(SCREEN_WIDTH // 2, 450))
        upgrade4_rect = exp_button.get_rect(center=(SCREEN_WIDTH // 2, 550))

        screen.blit(attack_button, upgrade1_rect)
        screen.blit(speed_button, upgrade2_rect)
        screen.blit(hp_button, upgrade3_rect)
        screen.blit(exp_button, upgrade4_rect)

        # --- Backボタン（下に追加） ---
        back_rect = back_button.get_rect(center=(SCREEN_WIDTH // 2, 650))
        screen.blit(back_button, back_rect)

        # --- イベント処理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESCキーで終了
                    power_up_screen = False
                    save_game_data() #avedata.jsonに保存する
                    game_start = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if upgrade1_rect.collidepoint(event.pos):
                    power_up_attack()   # 強化だけ行う（画面はそのまま）
                elif upgrade2_rect.collidepoint(event.pos):
                    power_up_speed()
                elif upgrade3_rect.collidepoint(event.pos):
                    power_up_hp()
                elif upgrade4_rect.collidepoint(event.pos):
                    power_up_exp()
                elif back_rect.collidepoint(event.pos):
                    power_up_screen = False
                    save_game_data() #avedata.jsonに保存する
                    game_start = True   # ← Backボタンでスタート画面に戻る

        label_font = jp_font(40)
        value_color = (0, 0, 0)  # 黒（ボタン背景が明るい想定）

        #所持しているバッテリーを表示
        battery_text = label_font.render(f"Battery: {battery}", True, (0, 0, 0))
        screen.blit(battery_text, (150, 100))

        # 各ボタンの右側に "+値" を表示
        pad_x = 16  # ボタンの右端からの余白
        def draw_bonus_value(rect, value):
            surf = label_font.render(f"+{value}", True, value_color)
            pos = (rect.right + pad_x, rect.centery - surf.get_height() // 2)
            screen.blit(surf, pos)

        draw_bonus_value(upgrade1_rect, persistent_attack_bonus)   # Base Attack の現在値
        draw_bonus_value(upgrade2_rect, persistent_speed_bonus)    # Player Speed の現在値
        draw_bonus_value(upgrade3_rect, persistent_maxhp_bonus)    # Player HP の現在値（HPは合計加算値）
        draw_bonus_value(upgrade4_rect, persistent_exp_bonus)

        pygame.display.flip()
        clock.tick(60)
        continue

    if delete_data:
        # 背景（スタート画面）を表示
        screen.blit(game_start_image, (
            SCREEN_WIDTH // 2 - game_start_image.get_width() // 2,
            SCREEN_HEIGHT // 2 - game_start_image.get_height() // 2
        ))


        # 確認ダイアログを中央に
        confirm_rect = delete_confirmation.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(delete_confirmation, confirm_rect)

        # Yes/No ボタンをダイアログの下に横並び配置
        spacing = 20
        buttons_y = confirm_rect.bottom - 100
        yes_rect = yes_button.get_rect(right=SCREEN_WIDTH // 2 - spacing // 2, top=buttons_y)
        no_rect  = no_button.get_rect(left =SCREEN_WIDTH // 2 + spacing // 2, top=buttons_y)

        screen.blit(yes_button, yes_rect)
        screen.blit(no_button, no_rect)

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESCでスタート画面に戻る（削除しない）
                    delete_data = False
                    game_start = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_rect.collidepoint(event.pos):
                    # 削除実行 → リセット → スタート画面へ
                    delete_save_data()
                    delete_data = False
                    game_start = True
                elif no_rect.collidepoint(event.pos):
                    # キャンセル → スタート画面へ
                    delete_data = False
                    game_start = True

        pygame.display.flip()
        clock.tick(60)
        continue  # ← 他の処理へ落ちないように

    if not game_over and not game_clear:
        if paused:
            # --- イベント処理（pause中もキーを受け付ける） ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # レベルアップ選択待ち中は、F/ESCを優先して処理
                    if level_up_pending and choice_waiting:
                        if event.key == pygame.K_f and selected_choice_idx is not None:
                            choice_id = current_level_choices[selected_choice_idx]
                            level_up(choice_id)
                            choice_waiting = False
                            selected_choice_idx = None
                            # レベルアップ確定後もポーズ継続でOK（必要なら paused=False にしても良い）
                            continue
                        elif event.key == pygame.K_ESCAPE:
                            # 選択のキャンセル（ポーズは維持）
                            choice_waiting = False
                            selected_choice_idx = None
                            continue

                    # ↑待ち中ではない通常のキー
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                    elif event.key == pygame.K_p:
                        paused = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if level_up_pending:
                        rects = get_level_choice_rects()

                        if not choice_waiting:
                            # まだ説明モーダルを出していない：選択肢クリックで説明を開く
                            for idx, r in enumerate(rects):
                                if r.collidepoint(event.pos):
                                    choice_waiting = True
                                    selected_choice_idx = idx
                                    break
                        else:
                            # 説明モーダル表示中（choice_waiting == True）
                            clicked_any = False
                            for idx, r in enumerate(rects):
                                if r.collidepoint(event.pos):
                                    clicked_any = True
                                    if idx == selected_choice_idx:
                                        # 同じ選択肢をもう一回クリック → 確定
                                        choice_id = current_level_choices[selected_choice_idx]
                                        level_up(choice_id)
                                        choice_waiting = False
                                        selected_choice_idx = None
                                        # （必要なら）ポーズを閉じたければ下を有効化
                                        # paused = False
                                    else:
                                        # 別の選択肢をクリック → 説明を切替
                                        selected_choice_idx = idx
                                    break

                            if not clicked_any:
                                # モーダルの外側クリックで閉じる（モーダル内なら何もしない）
                                box_w, box_h = 560, 280
                                box_rect = pygame.Rect(
                                    SCREEN_WIDTH // 2 - box_w // 2,
                                    SCREEN_HEIGHT // 2 - box_h // 2 + 250,
                                    box_w, box_h
                                )
                                if not box_rect.collidepoint(event.pos):
                                    choice_waiting = False
                                    selected_choice_idx = None

            # --- ゲーム画面（通常の見た目）をまず描画 ---
            draw_game(screen)

            # --- pause用の白半透明オーバーレイ ---
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            screen.blit(overlay, (0, 0))

            # リアルの経過時間を会得
            real_time = (pygame.time.get_ticks() - start_ticks) // 1000

            # --- ステータスUI（大きめフォント） ---
            font = jp_font(40)
            hp_text = font.render(f"HP: {player_hp}/{player_max_hp}", True, (0, 0, 0))
            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            display_exp = min(exp, exp_to_next)
            level_text = font.render(f"Level: {level}  EXP: {display_exp}/{exp_to_next}", True, (0, 0, 0))
            time_text = font.render(f"Time: {int(game_time)}", True, (0, 0, 0))
            real_time_text = font.render(f"Real Time: {real_time}", True, (0, 0, 0))
            enemy_level_text = font.render(f"Enemy Lv: {enemy_level}", True, (0, 0, 0))
            battery_text = font.render(f"Battery: {battery}", True, (0, 0, 0))
            speed_text = font.render(f"Game Speed: {game_speed:.1f}", True, (0, 0, 0))
            base_attack_text = font.render(f"base attack: {base_attack}", True, (0, 0, 0))
            clitical_rato_text = font.render(f"critical rato: {player_clitical_rato * 100} %", True, (0, 0, 0))
            clitical_damage_text = font.render(f"critical damage: × {player_clitical_damage}", True, (0, 0, 0))
            coord_text = font.render(f"X: {player_x}  Y: {player_y}", True, (0, 0, 0))
            text_rect = coord_text.get_rect()
            text_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)

            screen.blit(hp_text, (10, 10))
            screen.blit(level_text, (10, 50))
            screen.blit(battery_text, (10, 90))
            screen.blit(score_text, (10, 130))
            screen.blit(enemy_level_text, (10, 170))
            screen.blit(time_text, (10, 210))
            screen.blit(real_time_text, (10, 250))
            screen.blit(speed_text, (10, 290))

            screen.blit(base_attack_text, (10, 700))
            screen.blit(clitical_rato_text, (10, 740))
            screen.blit(clitical_damage_text, (10, 780))

            screen.blit(coord_text, text_rect)

            # --- レベルアップの選択UI（pause時のみ可視） ---
            if level_up_pending:
                sel_font = jp_font(50)
                tip = sel_font.render("Choose one to level up", True, (0, 0, 0))
                tip_pos = (SCREEN_WIDTH // 2 - tip.get_width() // 2,  # 見出しは正中に
                           SCREEN_HEIGHT // 2 - choice_imgs[0].get_height() // 2 - 60)
                screen.blit(tip, tip_pos)

                rects = get_level_choice_rects()
                for i, choice_id in enumerate(current_level_choices):
                    img = choice_imgs[choice_id]         # ← スケール済み画像
                    screen.blit(img, rects[i])           # ← Rectにピッタリ置く（topleft一致）
                    pygame.draw.rect(screen, (0, 0, 0), rects[i], width=4)  # 枠線も同じRectに
                if choice_waiting and selected_choice_idx is not None:

                    # 枠
                    box_w, box_h = 560, 280
                    box_rect = pygame.Rect(
                        SCREEN_WIDTH//2 - box_w//2,
                        SCREEN_HEIGHT//2 - box_h//2 + 250,
                        box_w, box_h
                    )
                    pygame.draw.rect(screen, (255, 255, 255), box_rect)
                    pygame.draw.rect(screen, (0, 0, 0), box_rect, width=4)

                    info_font = jp_font(32)
                    para_font = jp_font(20)
                    hint_font = jp_font(15)

                    # 選択肢IDから説明を取得
                    choice_id = current_level_choices[selected_choice_idx]
                    info = CHOICE_INFO.get(choice_id, {"title":"Unknown", "lines":["説明が未設定です"]})

                    # テンプレート内の {shortwave_level} を置き換える
                    formatted_lines = [
                        line.format(
                            shortwave_level=shortwave_level,
                            laser_level=laser_level
                            ) 
                            for line in info["lines"]]
                    
                    # タイトル
                    title_surf = info_font.render(info["title"], True, (0, 0, 0))
                    screen.blit(title_surf, (box_rect.centerx - title_surf.get_width()//2, box_rect.y + 24))

                    # 説明複数行
                    y = box_rect.y + 80
                    for line in formatted_lines:
                        line_surf = para_font.render(line, True, (0, 0, 0))
                        screen.blit(line_surf, (box_rect.x + 24, y))
                        y += 36

                    # 操作ヒント（任意）
                    hint = hint_font.render("同じ画像をもう一度クリックで決定 / ESCでキャンセル / Fキーでも決定可", True, (60, 60, 60))
                    screen.blit(hint, (box_rect.centerx - hint.get_width()//2, box_rect.bottom - 40))

                
            pygame.display.flip()
            clock.tick(60)
            continue

        # ===== 俯瞰モード（背景＋タイルID＋クリックで座標表示） =====
        if overlooking:
            # 俯瞰中は現在タイルスケール / 基準スケール が「縮小率」
            scale_ratio = TILE_SCALE / BASE_TILE_SCALE  # 例: 0.1 / 5.0 = 1/50

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_o):
                        apply_tile_scale(BASE_TILE_SCALE)
                        overlooking = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # “縮小後”オフセット + 画面座標 を、逆比率でワールドに戻す
                    bg_off_x_scaled = int((player_x - SCREEN_WIDTH // 2) * scale_ratio)
                    bg_off_y_scaled = int((player_y - SCREEN_HEIGHT // 2) * scale_ratio)

                    wx = int((bg_off_x_scaled + event.pos[0]) / scale_ratio)
                    wy = int((bg_off_y_scaled + event.pos[1]) / scale_ratio)

                    gx, gy = world_to_tile(wx, wy)
                    rel_x = gx - SPAWN_TILE_GX
                    rel_y = gy - SPAWN_TILE_GY
                    last_clicked_label = f"Clicked tile: ({rel_x}, {rel_y})"
                    last_clicked_ttl   = 120
                    print(last_clicked_label)

            # ★縮小したオフセットで背景を描く（1回だけ）
            bg_off_x_scaled = int((player_x - SCREEN_WIDTH // 2) * scale_ratio)
            bg_off_y_scaled = int((player_y - SCREEN_HEIGHT // 2) * scale_ratio)
            draw_bg_sequence_2d(screen, bg_seq, TILE_W, TILE_H, bg_off_x_scaled, bg_off_y_scaled)

            # プレイヤーアイコンは中央固定（重複描画しない）
            mini_player = pygame.transform.smoothscale(player_original, (OVERLOOK_PLAYER_PX, OVERLOOK_PLAYER_PX))
            screen.blit(mini_player, (SCREEN_WIDTH // 2 - OVERLOOK_PLAYER_PX // 2,
                                      SCREEN_HEIGHT // 2 - OVERLOOK_PLAYER_PX // 2))

            # ▼ ここからID描画（縮小オフセットを使う！）
            W, H = SCREEN_WIDTH, SCREEN_HEIGHT
            start_x = - (int(bg_off_x_scaled) % TILE_W)
            start_y = - (int(bg_off_y_scaled) % TILE_H)
            grid_x0 = int(bg_off_x_scaled) // TILE_W
            grid_y0 = int(bg_off_y_scaled) // TILE_H

            id_font = jp_font(14)
            y, gy = start_y, grid_y0
            while y < H:
                x, gx = start_x, grid_x0
                while x < W:
                    rel_x = gx - SPAWN_TILE_GX
                    rel_y = gy - SPAWN_TILE_GY
                    txt = id_font.render(f"{rel_x},{rel_y}", True, (0, 0, 0))
                    screen.blit(txt, (x + 6, y + 6))
                    pygame.draw.rect(screen, (0, 0, 0), (x, y, TILE_W, TILE_H), 1)
                    x += TILE_W; gx += 1
                y += TILE_H; gy += 1

            # 直近クリック表示（任意）
            try:
                if last_clicked_ttl > 0:
                    tip_font = jp_font(22)
                    tip = tip_font.render(last_clicked_label, True, (0, 0, 0))
                    screen.blit(tip, (10, SCREEN_HEIGHT - 40))
                    last_clicked_ttl -= 1
            except NameError:
                last_clicked_label = ""
                last_clicked_ttl = 0

            pygame.display.flip()
            clock.tick(60)
            continue



        #ゲーム内経過時間会得
        delta_time = 1 / 60.0   # 1フレームあたりの秒数（60FPS前提）
        game_time += delta_time * game_speed
        #リアルの経過時間会得
        real_time = (pygame.time.get_ticks() - start_ticks) // 1000
        #残り時間会得
        remaining_time = (goel_time - int(game_time))

        # 0になったら一度だけクリア遷移
        if remaining_time == 0 and not game_clear:
            game_clear = True

        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESCキーで終了
                    running = False
                elif event.key == pygame.K_DOWN:  # ↓キーでスピードダウン
                    if game_speed > 0.5:
                        game_speed = max(0.1, game_speed - 0.5)   # 0.5ずつ下がる
                    elif game_speed <= 0.5:
                        game_speed = 0.1   # 0.1にする
                elif event.key == pygame.K_UP:    # ↑キーでスピードアップ
                    if game_speed >= 0.5:
                        game_speed = min(5.0, game_speed + 0.5)   # 0.5ずつ上がる
                    elif game_speed < 0.5:
                        game_speed = 0.5   # 0.5にする
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_o:
                    if not overlooking:
                        # 1/50にしたいなら基準の1/50へ
                        apply_tile_scale(BASE_TILE_SCALE / 50.0)
                        overlooking = True
                    else:
                        apply_tile_scale(BASE_TILE_SCALE)
                        overlooking = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
            # 「level up available」の文字が押されたらポーズを開く
                if level_up_pending and level_up_notice_rect and level_up_notice_rect.collidepoint(event.pos):
                    paused = True

        # キー入力
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_d]:
            dx += player_speed * game_speed
        if keys[pygame.K_a]:
            dx -= player_speed * game_speed
        if keys[pygame.K_s]:
            dy += player_speed * game_speed
        if keys[pygame.K_w]:
            dy -= player_speed * game_speed

        # ノックバックの減衰（毎フレーム）
        player_vx *= KNOCKBACK_DECAY
        player_vy *= KNOCKBACK_DECAY

        # 無敵時間カウント
        if player_iframe > 0:
            player_iframe -= 1

        # 移動
        player_x += dx + player_vx
        player_y += dy + player_vy
        player_rect = pygame.Rect(
            player_x - player_image.get_width() // 2,
            player_y - player_image.get_height() // 2,
            player_image.get_width(),
            player_image.get_height()
        )

        # 向き変更
        if dx > 0:
            player_image = pygame.transform.rotate(player_original, 270)
        elif dx < 0:
            player_image = pygame.transform.rotate(player_original, 90)
        elif dy > 0:
            player_image = pygame.transform.rotate(player_original, 180)
        elif dy < 0:
            player_image = player_original

        # 敵生成
        enemy_spawn_timer += 1 * game_speed
        if enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL:
            spawn_enemy()
            spawn_enemy()
            enemy_spawn_timer = 0

        # short wave発動
        weapon_shortwave_timer += 1 * game_speed
        if weapon_shortwave_timer >= weapon_shortwave_cooldown:
            spawn_shortwave()
            weapon_shortwave_timer = 0

        # laser発動
        laser_timer += 1 * game_speed
        if laser_timer >= laser_cooldown:
            spawn_laser()
            laser_timer = 0

        # laser更新
        new_weapons = []
        lasers_to_keep = []
        for laser in lasers:
            laser["timer"] -= 1 * game_speed

            # 回転処理
            if laser["rot_timer"] > 0:
                laser["rot_timer"] -= 1
                laser["angle"] += 3 * game_speed
            else:
                laser["angle"] += 3 * game_speed

            # --- オフセット回転 ---
            base_w, base_h = weapon_laser_image_base.get_size()

            # 元画像の「根元位置」 = 下端中央から画像中心までのベクトル
            origin_offset = pygame.math.Vector2(0, -base_h // 2)

            # 回転させて、プレイヤー位置に足す
            offset_rotated = origin_offset.rotate(laser["angle"])
            cx = player_x + offset_rotated.x
            cy = player_y + offset_rotated.y

            # 回転画像を生成
            rotated_image = pygame.transform.rotate(weapon_laser_image_base, -laser["angle"])
            rect = rotated_image.get_rect(center=(cx, cy))

            laser["image"] = rotated_image
            laser["rect"] = rect

            # ★レーザー線分の端点を保存（判定用）
            ang = math.radians(laser["angle"])
            dir_x = math.sin(ang)   # 縦基準の画像なので (sinθ, -cosθ)
            dir_y = -math.cos(ang)
            laser["p0"] = (player_x, player_y)  # 根元（プレイヤー位置）
            laser["p1"] = (player_x + dir_x * base_h, player_y + dir_y * base_h)  # 先端

            if laser["timer"] > 0:
                lasers_to_keep.append(laser)
                new_weapons.append(laser)   # weapons に残す

        lasers = lasers_to_keep
        # weapons の laser を更新
        weapons = [w for w in weapons if w["type"] != "laser"] + new_weapons      
        # 敵の移動と衝突判定
        for enemy in enemies:
            # 直前中心位置を保存（トンネリング対策用）
            enemy['prev_cx'] = enemy['rect'].centerx
            enemy['prev_cy'] = enemy['rect'].centery

            # プレイヤー中心へ追尾（player_x, player_y は中心座標）
            target_x = player_x
            target_y = player_y
            enemy_center_x = enemy['x'] + enemy_image.get_width() // 2
            enemy_center_y = enemy['y'] + enemy_image.get_height() // 2

            dx_enemy = target_x - enemy_center_x
            dy_enemy = target_y - enemy_center_y
            dist = (dx_enemy**2 + dy_enemy**2)**0.5
            if dist > 0:
                enemy['x'] += (dx_enemy / dist) * enemy_speed * game_speed
                enemy['y'] += (dy_enemy / dist) * enemy_speed * game_speed
                enemy['rect'].x = int(enemy['x'])
                enemy['rect'].y = int(enemy['y'])

        # 全員動かし終わってから1回だけ、重なり解消
        resolve_enemy_collisions(enemies)

        # 次に、敵ごとに武器との当たり判定とHP処理
        enemies_to_keep = []
        for enemy in enemies:
            # 武器との衝突処理（レーザーは掃引判定）
            for weapon in weapons:
                if weapon.get('timer', 0) <= 0:
                    continue

                if weapon['type'] == 'laser':
                    # レーザー線分
                    (lx1, ly1) = weapon['p0']
                    (lx2, ly2) = weapon['p1']

                    # 敵の「前フレーム中心」→「今フレーム中心」の線分
                    e0x = enemy.get('prev_cx', enemy['rect'].centerx)  # 初回は現在値で代用
                    e0y = enemy.get('prev_cy', enemy['rect'].centery)
                    e1x = enemy['rect'].centerx
                    e1y = enemy['rect'].centery

                    # “太さ”はレーザー半幅 + 敵半径（カプセル同士）
                    laser_half_w = weapon_laser_image_base.get_size()[0] * 0.5  # 見た目半幅
                    enemy_r = ENEMY_RADIUS
                    threshold = laser_half_w + enemy_r

                    dist = segment_segment_distance(e0x, e0y, e1x, e1y, lx1, ly1, lx2, ly2)
                    hit = (dist <= threshold)
                else:
                    hit = enemy['rect'].colliderect(weapon['rect'])

                if not hit:
                    continue

                # --- 連続ヒット抑制（timerは減る値なので prev - now を比較） ---
                weapon_id = weapon['id']
                if weapon_id in enemy['last_hits']:
                    prev = enemy['last_hits'][weapon_id]
                    now  = weapon['timer']
                    if (prev - now) < 30:   # 30フレ以内はスキップ
                        continue
                enemy['last_hits'][weapon_id] = weapon['timer']

                # --- ダメージ ---
                dmg = weapon['damage']
                crit = False
                if random.random() < player_clitical_rato:
                    dmg *= player_clitical_damage
                    crit = True

                enemy['hp'] -= dmg
                damage_texts.append({
                    "text": str(dmg),
                    "x": enemy['rect'].centerx,
                    "y": enemy['rect'].y,
                    "timer": 30,
                    "crit": crit
                })
                # ダメージテキスト間引き
                if len(damage_texts) > 100:
                    del damage_texts[:len(damage_texts) - 100]

                break  # この敵は今フレーム1回で打ち切り

            # プレイヤーと接触（敵1体ごとに判定）
            if player_rect.colliderect(enemy['rect']):
                if player_iframe <= 0:
                    # ダメージ
                    dmg = max(0, enemy['atk'] - player_defence)
                    player_hp -= dmg
                    player_iframe = PLAYER_IFRAME_MAX
            
                    # ノックバック：敵中心→プレイヤー中心 方向へ押し返す
                    ex, ey = enemy['rect'].centerx, enemy['rect'].centery
                    dxk = player_x - ex
                    dyk = player_y - ey
                    dist = math.hypot(dxk, dyk) or 1.0
                    nx, ny = dxk / dist, dyk / dist

                    # インパルス（好みで game_speed を掛けると体感一定に）
                    impulse = KNOCKBACK_IMPULSE  # * game_speed でもOK
                    player_vx += nx * impulse
                    player_vy += ny * impulse

                # 生存中の敵は残す
                if enemy['hp'] > 0:
                    enemies_to_keep.append(enemy)
                continue

            # 生存チェック／ドロップ
            if enemy['hp'] > 0:
                enemies_to_keep.append(enemy)
            else:
                if not enemy.get("dying"):
                    enemy["dying"] = True
                    score += 1
                    battery += 1
                    exp += 1 * exp_rato
                    exp_spawn_chance = random.randint(0, 10)
                    if exp_spawn_chance < enemy["level"]:
                        exp_items.append({
                            "rect": exp_image.get_rect(center=enemy['rect'].center),
                            "value": int(enemy["level"] * exp_rato)
                        })
                    if random.random() < 0.2:
                        battery += 5
                        battery_items.append({
                            "rect": battery_image.get_rect(center=enemy['rect'].center),
                            "value": 5
                        })

                # レベルアップ（自動処理はあなたの元ロジックのまま必要ならここに）
                if exp >= exp_to_next and not level_up_pending:
                    pool = available_choices()
                    if pool:
                        level_up_pending = True
                        roll_level_choices()
                    else:
                        while exp >= exp_to_next and not available_choices():
                            exp -= exp_to_next
                            level += 1
                            exp_to_next = int(exp_to_next * 1.5)
                            base_attack += 1
                            player_max_hp += 10
                            player_hp = min(player_hp + 10, player_max_hp)
                        level_up_pending = False
                        current_level_choices = []

        # 最後に入れ替え
        enemies = enemies_to_keep

        # ==============================
        # アイテムの吸い込み（マグネット）と回収
        # ==============================
        # プレイヤー矩形（ワールド座標）
        player_rect = player_image.get_rect(center=(player_x, player_y))

        # 「当たり判定の円」に近い動作をRectで近似（inflateで拡大）
        magnet_rect = player_rect.inflate(MAGNET_RADIUS * 2, MAGNET_RADIUS * 2)

        # --- EXPアイテム ---
        exp_keep = []
        for item in exp_items:
            # 既存セーブや過去生成分への安全策
            item.setdefault("homing", False)
            item.setdefault("speed", ITEM_HOMING_SPEED)

            # マグネット判定に入ったら吸い込み開始
            if not item["homing"] and magnet_rect.colliderect(item["rect"]):
                item["homing"] = True
        
            # 吸い込み中はプレイヤーへ向かって移動
            if item["homing"]:
                ix, iy = item["rect"].center
                dx = player_x - ix
                dy = player_y - iy
                dist = math.hypot(dx, dy) + 1e-6

                # 近いほど少し加速（気持ちよく吸い込まれる感じ）
                speed = item["speed"] * game_speed * (2.0 if dist < 120 else 1.5)

                nx = ix + dx / dist * speed
                ny = iy + dy / dist * speed
                item["rect"].center = (nx, ny)

            # 最後に回収判定（通常の接触）
            if player_rect.colliderect(item["rect"]):
                exp += item["value"]
                # ここで消える＝keepしない
            else:
                exp_keep.append(item)
        exp_items = exp_keep

        # --- Batteryアイテム ---
        bat_keep = []
        for item in battery_items:
            item.setdefault("homing", False)
            item.setdefault("speed", ITEM_HOMING_SPEED)
        
            if not item["homing"] and magnet_rect.colliderect(item["rect"]):
                item["homing"] = True
        
            if item["homing"]:
                ix, iy = item["rect"].center
                dx = player_x - ix
                dy = player_y - iy
                dist = math.hypot(dx, dy) + 1e-6
                speed = item["speed"] * game_speed * (2.0 if dist < 120 else 1.5)
                nx = ix + dx / dist * speed
                ny = iy + dy / dist * speed
                item["rect"].center = (nx, ny)

            if player_rect.colliderect(item["rect"]):
                battery += item["value"]
            else:
                bat_keep.append(item)
        battery_items = bat_keep

        # 経過時間による敵強化（30秒ごと）
        current_ticks = pygame.time.get_ticks()
        if (current_ticks - last_buff_time) >= 30000 / game_speed:
            enemy_base_hp *= 2
            enemy_base_attack *= 2
            enemy_level += 1
            last_buff_time = current_ticks

        #=======================================
        # --- 描画 ---
        #=======================================
        # --- 敵の更新 ---
        enemies_to_keep = []
        for enemy in enemies:
            if enemy['dying']:
                enemy['alpha'] -= 25 * game_speed
                if enemy['alpha'] <= 0:
                    continue  # 完全に消えたら残さない
            enemies_to_keep.append(enemy)
        enemies = enemies_to_keep

        for wave in shortwaves[:]:
            step = game_speed
            wave["timer"] -= step
            if wave["timer"] <= 0:
                weapons[:] = [w for w in weapons if w.get('id') != wave['id']]
                shortwaves.remove(wave)
                continue

            # ★ 必ず lifetime_f を使う（spawn時に入れている前提）
            life_f = max(1.0, float(wave["lifetime_f"]))

            # 生成からの経過フレーム（timer は step=game_speed で減っているので、拡大は game_speed だけに連動）
            elapsed_f = life_f - wave["timer"]

            # ★ 最大サイズなし：経過フレームに比例して拡大（clamp しない）
            # 例）GROW_PER_60F = 1.0 → 60f で +1.0倍、120f で +2.0倍 … と増える
            scale_factor = 1.0 + (elapsed_f / 60.0) * GROW_PER_60F

            base_w, base_h = Weapon_shortwave_image.get_size()
            new_w = max(1, int(base_w * scale_factor))
            new_h = max(1, int(base_h * scale_factor))
            scaled_img = pygame.transform.smoothscale(Weapon_shortwave_image, (new_w, new_h))

            fade_tail_f = min(30.0, life_f * 0.2)
            if wave["timer"] < fade_tail_f:
                alpha = int(255 * (wave["timer"] / fade_tail_f))
            else:
                alpha = 255
            scaled_img.set_alpha(alpha)

            wave["image"] = scaled_img
            wave["rect"]  = scaled_img.get_rect(center=(wave["x"], wave["y"]))

        # --- ダメージテキスト更新 ---
        for dt in damage_texts[:]:
            dt["y"] -= 1
            dt["timer"] -= 1
            if dt["timer"] <= 0:
                damage_texts.remove(dt)
        #darw_game関数を呼び出す
        draw_game(screen)
        pygame.display.flip()
        clock.tick(60)

        # --- Game Over判定 ---
        if player_hp <= 0:
            game_over = True
            save_game_data()#savedataに保存
            # このフレームはここまでにして、次ループで game_over=True の分岐へ移る
            continue
    elif game_clear:
        screen.fill(BLACK)
        screen.blit(game_clear_image, (
            SCREEN_WIDTH // 2 - game_clear_image.get_width() // 2,
            SCREEN_HEIGHT // 2 - game_clear_image.get_height() // 2
        ))
        font = jp_font(50)
        time_text = font.render(f"Survival Time: {game_time} s", True, (255, 255, 255))
        real_time_text = font.render(f"Real Time: {real_time}", True, (200, 200, 200))
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))

        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 160))
        screen.blit(real_time_text, (SCREEN_WIDTH // 2 - real_time_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))

        # --- Restartボタン ---
        restart_rect = restart_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 250))
        screen.blit(restart_button, restart_rect)

        pygame.display.flip()

        # イベント処理（Game Over画面用）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    reset_game()
                    game_over = False
                    game_start = True
        # Game Over画面はここで1フレーム終わり。ループ継続。
        # 画面更新
        pygame.display.flip()
        continue


    else:
        # ---------------------------
        # Game Over画面（game_over == True）
        # ---------------------------
        screen.fill(BLACK)
        screen.blit(game_over_image, (
            SCREEN_WIDTH // 2 - game_over_image.get_width() // 2,
            SCREEN_HEIGHT // 2 - game_over_image.get_height() // 2
        ))

        font = jp_font(50)
        time_text = font.render(f"Survival Time: {game_time} s", True, (255, 255, 255))
        real_time_text = font.render(f"Real Time: {real_time}", True, (200, 200, 200))
        score_text = font.render(f"Score: {score}", True, (255, 255, 0))

        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 160))
        screen.blit(real_time_text, (SCREEN_WIDTH // 2 - real_time_text.get_width() // 2, SCREEN_HEIGHT // 2 + 200))

        # --- Restartボタン ---
        restart_rect = restart_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 250))
        screen.blit(restart_button, restart_rect)

        pygame.display.flip()

        # イベント処理（Game Over画面用）
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(event.pos):
                    reset_game()
                    game_over = False
                    game_start = True
        # Game Over画面はここで1フレーム終わり。ループ継続。
        # 画面更新
        pygame.display.flip()
        continue

pygame.quit()