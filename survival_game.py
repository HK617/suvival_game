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
# プレイヤー当たり判定（描画と無関係の固定Hitbox）
PLAYER_COLL_W = 30
PLAYER_COLL_H = 30

# 見た目中心と当たり判定中心の補正（+で右/下へ移動）
# ※プレイヤーの赤枠が「左上」に寄って見えるなら、正の値を入れる
HITBOX_OFFSET_X = 0
HITBOX_OFFSET_Y = 0

# プレイヤー描画位置（常に中央）
PLAYER_DRAW_X = SCREEN_WIDTH // 2 - player_original.get_width() // 2
PLAYER_DRAW_Y = SCREEN_HEIGHT // 2 - player_original.get_height() // 2

# ミニマップ用のプレイヤーアイコン
MINIMAP_ICON_PX = 16  # お好みで 12〜24 あたり
player_icon_img = pygame.image.load("player_icon.png").convert_alpha()
player_icon = pygame.transform.smoothscale(player_icon_img, (MINIMAP_ICON_PX, MINIMAP_ICON_PX))

# 敵画像
enemy_image = pygame.image.load("SG_enemy(level1).png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (30, 30))

# EXPアイテム
exp_image = pygame.image.load("exp.png").convert_alpha()
exp_image = pygame.transform.scale(exp_image, (20, 20))

# Batteryアイテム
battery_image = pygame.image.load("battery.png").convert_alpha()
battery_image = pygame.transform.scale(battery_image, (20, 20))

#建築物
# Portal
portal_img = pygame.image.load("portal.png").convert_alpha()
portal_img = pygame.transform.smoothscale(portal_img, (128, 160))
PORTAL_W, PORTAL_H = portal_img.get_size()
# ---- 壁ブロック（100x100）----
BLOCK_SIZE = 50 #ブロックの大きさ
block_img = pygame.image.load("block1.png").convert_alpha()
block_img = pygame.transform.smoothscale(block_img, (BLOCK_SIZE, BLOCK_SIZE))

# ★ ドア画像（閉/開）を読み込んで同サイズに揃える
door_closed_img = pygame.image.load("close_door.png").convert_alpha()
door_closed_img = pygame.transform.smoothscale(door_closed_img, (BLOCK_SIZE, BLOCK_SIZE))
door_open_img = pygame.image.load("open_door.png").convert_alpha()
door_open_img  = pygame.transform.smoothscale(door_open_img,  (BLOCK_SIZE, BLOCK_SIZE))
# ★ ドアの最大HP
DOOR_MAX_HP = 200

# 画像コード（短縮保存用）
IMG_CODE = {"block1.png": "0", "close_door.png": "1", "open_door.png": "2"}
CODE_IMG = {v: k for k, v in IMG_CODE.items()}
# ★ ブロック画像レジストリ
BLOCK_IMAGES = {
    "block1.png":    block_img,
    "close_door.png": door_closed_img,
    "open_door.png":  door_open_img,
}

# スポーンを囲うブロック群（ワールド座標のRectを保持）
border_blocks = []

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
# マップ永続化用
EXPLORED_TILES = set()  # {(gx, gy), ...} を保持（保存時はリストに変換）

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
    global BG_RANDOM_SEED, EXPLORED_TILES
    global SAVED_BLOCKS_LAYOUT   # ★ 追加

    SAVED_BLOCKS_LAYOUT = None   # デフォルト

    pad, psp, pmh, pexp, bat = 1, 5, 10, 1, 0
    seed_default = BG_RANDOM_SEED

    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)

                persistent_attack_bonus = int(data.get("persistent_attack_bonus", pad))
                persistent_speed_bonus  = int(data.get("persistent_speed_bonus",  psp))
                persistent_maxhp_bonus  = int(data.get("persistent_maxhp_bonus",  pmh))
                persistent_exp_bonus    = float(data.get("persistent_exp_bonus",  pexp))
                battery                 = int(data.get("battery",                  bat))
                BG_RANDOM_SEED          = int(data.get("bg_seed", seed_default))

                # explored_tiles（既存）
                explored_data = data.get("explored_tiles", "")
                EXPLORED_TILES = set()
                if isinstance(explored_data, str):
                    for token in explored_data.split(";"):
                        token = token.strip()
                        if not token:
                            continue
                        gx_str, gy_str = token.split(",")
                        EXPLORED_TILES.add((int(gx_str), int(gy_str)))
                elif isinstance(explored_data, list):
                    for pair in explored_data:
                        if isinstance(pair, (list, tuple)) and len(pair) == 2:
                            gx, gy = pair
                            EXPLORED_TILES.add((int(gx), int(gy)))

                # ★ 新規: ブロック配置（短縮・互換）
                blocks_compact = data.get("blocks_compact")
                blocks_data    = data.get("blocks")

                SAVED_BLOCKS_LAYOUT = None
                if isinstance(blocks_compact, str) and blocks_compact:
                    SAVED_BLOCKS_LAYOUT = decode_blocks(blocks_compact)

                print("セーブデータを読み込みました。")

            except json.JSONDecodeError:
                persistent_attack_bonus = pad
                persistent_speed_bonus  = psp
                persistent_maxhp_bonus  = pmh
                persistent_exp_bonus    = pexp
                battery                 = bat
                BG_RANDOM_SEED          = seed_default
                EXPLORED_TILES          = set()
                SAVED_BLOCKS_LAYOUT     = None
                print("セーブファイルが壊れています。初期値で続行します。")
    else:
        persistent_attack_bonus = pad
        persistent_speed_bonus  = psp
        persistent_maxhp_bonus  = pmh
        persistent_exp_bonus    = pexp
        battery                 = bat
        BG_RANDOM_SEED          = seed_default
        EXPLORED_TILES          = set()
        SAVED_BLOCKS_LAYOUT     = None
        print("セーブファイルが見つかりません。初期値で開始します。")


# ===============================
# セーブデータの保存
# ===============================
def save_game_data():
    # 探索済みを "gx,gy;..." へ
    explored_str = ";".join(f"{gx},{gy}" for gx, gy in EXPLORED_TILES)

    # ★ ブロック保存（超短縮）
    try:
        blocks_compact = encode_blocks(border_blocks)
    except Exception:
        blocks_compact = ""

    data = {
        "persistent_attack_bonus": persistent_attack_bonus,
        "persistent_speed_bonus":  persistent_speed_bonus,
        "persistent_maxhp_bonus":  persistent_maxhp_bonus,
        "persistent_exp_bonus":    persistent_exp_bonus,
        "battery":                 battery,
        "bg_seed":                 BG_RANDOM_SEED,
        "explored_tiles":          explored_str,
        "blocks_compact":          blocks_compact,
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        print("セーブデータを保存しました。")

# ===============================
# セーブデータの削除
# ===============================
def delete_save_data():
    global persistent_attack_bonus, persistent_speed_bonus, persistent_maxhp_bonus, persistent_exp_bonus, battery
    global BG_RANDOM_SEED, EXPLORED_TILES

    # 永続データを初期化
    persistent_attack_bonus = 1
    persistent_speed_bonus  = 5
    persistent_maxhp_bonus  = 10
    persistent_exp_bonus    = 1
    battery = 0

    # 探索済みクリア
    EXPLORED_TILES.clear()

    # マップシードを振り直し → ぜんぶの背景キャッシュを空に
    BG_RANDOM_SEED = random.randint(0, 2**31 - 1)
    clear_all_bg_caches()

    # 新しいシード・空の探索履歴で保存
    save_game_data()

    # ゲーム状態リセット（reset_game は seed をいじらない）
    reset_game()

# マップ情報の削除
def clear_all_bg_caches():
    """背景タイルのキャッシュを全てクリア（通常・ミニマップ・ズーム別）"""
    # 通常/ミニマップの既定コンテキスト
    for name in ("bg_ctx", "bg_ctx_normal", "bg_ctx_mini"):
        ctx = globals().get(name)
        if isinstance(ctx, dict):
            cache = ctx.get("cache")
            if isinstance(cache, dict):
                cache.clear()
    # ズームごとのミニマップ用コンテキスト
    if "MINIMAP_CTXS" in globals():
        for ctx in MINIMAP_CTXS.values():
            if isinstance(ctx, dict):
                cache = ctx.get("cache")
                if isinstance(cache, dict):
                    cache.clear()
    # ミニマップのラベル（座標表示）のグリッドキャッシュも念のため
    if "LABEL_GRID_CACHE" in globals() and isinstance(LABEL_GRID_CACHE, dict):
        LABEL_GRID_CACHE.clear()

# ベース帰還
def enter_base_from_game():
    """メインゲームから待機ルーム(in_base)へ安全に戻す"""
    global in_base, paused, overlooking, game_start, game_over, game_clear
    global enemies, weapons, lasers, shortwaves, exp_items, battery_items
    global base_world_x, base_world_y, base_bg_scroll_x, base_bg_scroll_y


        # ★ 存在しないときに備えて安全に初期化
    if 'enemies' not in globals(): enemies = []
    if 'weapons' not in globals(): weapons = []
    if 'lasers' not in globals(): lasers = []
    if 'shortwaves' not in globals(): shortwaves = []
    if 'exp_items' not in globals(): exp_items = []
    if 'battery_items' not in globals(): battery_items = []

    base_bg_scroll_x = 0.0
    base_bg_scroll_y = 0.0

    # 画面遷移フラグ
    in_base = True
    paused = False
    overlooking = False
    game_start = False
    game_over = False
    game_clear = False

    # 動的オブジェクトをクリア
    enemies.clear()
    weapons.clear()
    lasers.clear()
    shortwaves.clear()
    exp_items.clear()
    battery_items.clear()

    # ベースの背景スクロール位置も合わせてリセット
    base_bg_scroll_x = 0.0
    base_bg_scroll_y = 0.0

# ===============================
# ゲーム描画
# ===============================
#===========背景の表示============
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

def base_world_to_screen(wx, wy):
    """ベースのワールド座標 → 画面座標
    ワールド: 上=+Y / スクリーン: 上=-Y なので、Yだけ符号が反転する
    """
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    sx = cx + int(wx - base_world_x)
    sy = cy - int(wy - base_world_y)   # ★ ここがポイント（マイナス）
    return sx, sy


# === 2D背景　===
def prepare_bg(tiles, tile_w, tile_h, preserve_aspect=True, placeholder_alpha=255):
    """
    背景タイルの読み込みと重み付け初期化（透明対応）
    - 透過画像OK（convert_alpha）
    - preserve_aspect=True なら縦横比を保持し、余白は透明でパディング
    """
    images, cum, total = [], [], 0.0

    for path, w in tiles:
        # --- 透過対応で読み込み ---
        try:
            img = pygame.image.load(path).convert_alpha()
        except pygame.error:
            # アルファ付きのプレースホルダ
            img = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
            img.fill((40, 40, 40, placeholder_alpha))
            pygame.draw.rect(img, (80, 80, 80, placeholder_alpha), (0, 0, tile_w, tile_h), 6)

        # --- リサイズ（縦横比を保つ/保たない を選択） ---
        if preserve_aspect:
            w0, h0 = img.get_width(), img.get_height()
            if w0 == 0 or h0 == 0:
                # 破損時の保険
                fitted = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
            else:
                scale = min(tile_w / w0, tile_h / h0)
                new_w = max(1, int(w0 * scale))
                new_h = max(1, int(h0 * scale))
                scaled = pygame.transform.smoothscale(img, (new_w, new_h))
                fitted = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)  # 透明背景
                fitted.blit(scaled, ((tile_w - new_w) // 2, (tile_h - new_h) // 2))
            img = fitted
        else:
            if img.get_size() != (tile_w, tile_h):
                img = pygame.transform.smoothscale(img, (tile_w, tile_h))

        images.append(img)

        # --- 重みを累積 ---
        total += max(0.0, float(w))
        cum.append(total)

    # すべての重みが0以下のとき等確率に
    if total <= 0:
        cum = [i + 1 for i in range(len(images))]
        total = float(len(images))

    return {"images": images, "cum": cum, "total": total, "cache": {}}

def draw_bg(surface, ctx, offset_x, offset_y, seed):
    """背景をオフセット付きで描画"""
    imgs, cum, total, cache = ctx["images"], ctx["cum"], ctx["total"], ctx["cache"]
    if not imgs:
        surface.fill((0,0,0)); return
    W, H = surface.get_width(), surface.get_height()
    tw, th = imgs[0].get_width(), imgs[0].get_height()

    start_x = - (int(offset_x) % tw)
    start_y = - (int(offset_y) % th)
    gx0 = int(offset_x) // tw
    gy0 = int(offset_y) // th

    def tile_index(gx, gy):
        key = (gx, gy)
        if key in cache: return cache[key]
        h = ((gx * 1836311903) ^ (gy * 2971215073) ^ seed) & 0xffffffff
        t = (h / 4294967295.0) * total
        for i, cw in enumerate(cum):
            if t < cw:
                cache[key] = i
                return i
        cache[key] = len(cum) - 1
        return cache[key]

    y, gy = start_y, gy0
    while y < H:
        x, gx = start_x, gx0
        while x < W:
            surface.blit(imgs[tile_index(gx, gy)], (x, y))
            x += tw; gx += 1
        y += th; gy += 1

# ワールドの中心座標を特定
def center_of_tile(gx: int, gy: int, tile_w: int, tile_h: int):
    """タイル (gx, gy) の“中心”ワールド座標を返す"""
    return gx * tile_w + tile_w // 2, gy * tile_h + tile_h // 2

# === スポーン中心（ワールド座標）を保持 ===
SPAWN_CENTER_WX = None
SPAWN_CENTER_WY = None

def _rel_axis_to_tile(delta: float) -> int:
    """
    スポーン中心からの片軸距離 delta(px) を「タイル数」に変換。
    ルール:
      |delta| < 5000      -> 0
       delta >= +5000     -> 1 + ((delta - 5000) // 10000)
       delta <= -5000     -> -1 - (((-delta) - 5000) // 10000)
    """
    if delta >= 5000:
        return 1 + int((delta - 5000) // 10000)
    elif delta <= -5000:
        return -1 - int(((-delta) - 5000) // 10000)
    else:
        return 0

def spawn_rel_tile(wx: float, wy: float) -> tuple[int, int]:
    """ワールド座標→スポーン基準タイル座標 (gx, gy)"""
    dx = wx - SPAWN_CENTER_WX
    dy = wy - SPAWN_CENTER_WY
    return _rel_axis_to_tile(dx), _rel_axis_to_tile(dy)

def world_to_tile(wx: float, wy: float, tile_w: int = None, tile_h: int = None):
    """
    ワールド中心(5000,5000)がタイル(0,0)の中心になるタイル座標計算
    """
    tw = TILE_W if tile_w is None else tile_w
    th = TILE_H if tile_h is None else tile_h
    gx = int(math.floor((wx - 5000) / tw))
    gy = int(math.floor((wy - 5000) / th))
    return gx, gy

# ==== 全体マップ =====
def enter_minimap():
    """縮小マップ表示へ切り替え（再ビルドなし）"""
    global overlooking, TILE_W, TILE_H, bg_ctx, minimap_cam_x, minimap_cam_y
    overlooking = True
    minimap_cam_x = 0.0
    minimap_cam_y = 0.0
    TILE_W, TILE_H = MINIMAP_TILE_W, MINIMAP_TILE_H
    bg_ctx = bg_ctx_mini

def exit_minimap():
    """縮小マップ表示を解除（再ビルドなし）"""
    global overlooking, TILE_W, TILE_H, bg_ctx, minimap_cam_x, minimap_cam_y
    overlooking = False
    minimap_cam_x = 0.0
    minimap_cam_y = 0.0
    TILE_W, TILE_H = NORMAL_TILE_W, NORMAL_TILE_H
    bg_ctx = bg_ctx_normal

def build_minimap_label_layer(base_gx, base_gy, cols, rows, tw, th,
                              center_lgx, center_lgy, ix_center, iy_center):
    """
    画面に映る描画タイル (base_gx.., base_gy..) に対して、
    「画面中央の論理タイル (center_lgx, center_lgy)」からの差分で
    スポーン基準タイル座標ラベルを描く。
    """
    global LABEL_FONT
    if LABEL_FONT is None:
        LABEL_FONT = jp_font(14)

    surf = pygame.Surface((cols * tw, rows * th), pygame.SRCALPHA)

    for j in range(rows):
        gy_iter = base_gy + j
        y = j * th
        for i in range(cols):
            gx_iter = base_gx + i
            x = i * tw

            # 画面中央の“描画タイル index”との差分で論理タイル座標を求める
            label_gx = center_lgx + (gx_iter - ix_center)
            label_gy = center_lgy + (gy_iter - iy_center)

            label = f"({label_gx},{label_gy})"
            shadow = LABEL_FONT.render(label, True, (0, 0, 0))
            text   = LABEL_FONT.render(label, True, (255, 255, 255))
            surf.blit(shadow, (x + 1, y + 1))
            surf.blit(text,   (x,     y))

            # （任意）グリッド線
            pygame.draw.rect(surf, (0, 0, 0), (x, y, tw, th), 1)

    return surf

# ===== ミニマップズーム設定 =====
MINIMAP_ZOOM_SIZES = [50, 75, 100, 150, 200, 300]  # 1タイルのピクセルサイズ候補
minimap_zoom_i = MINIMAP_ZOOM_SIZES.index(100)     # 既定=100px/タイル

# ズームごとの背景コンテキストをキャッシュ
MINIMAP_CTXS = {}

def set_minimap_zoom_index(new_i: int):
    """ズームインデックスを反映して、TILE_W/H と bg_ctx を切替"""
    global minimap_zoom_i, TILE_W, TILE_H, bg_ctx, LABEL_GRID_CACHE
    minimap_zoom_i = max(0, min(len(MINIMAP_ZOOM_SIZES) - 1, new_i))
    size = MINIMAP_ZOOM_SIZES[minimap_zoom_i]

    # コンテキストが無ければ生成してキャッシュ
    if size not in MINIMAP_CTXS:
        MINIMAP_CTXS[size] = prepare_bg(BG_TILES, size, size)

    # このフレームから使う解像度に切替
    TILE_W = TILE_H = size
    bg_ctx = MINIMAP_CTXS[size]

    # ラベルレイヤーはサイズ依存なのでクリア
    LABEL_GRID_CACHE.clear()

# ==== マップ移動 ======
# ===== ミニマップ手動パン =====
MINIMAP_PAN_SPEED_PX = 12   # 1フレームの移動量（Shiftで×3）
minimap_cam_x = 0.0         # ミニマップ内カメラのXオフセット（px）
minimap_cam_y = 0.0         # ミニマップ内カメラのYオフセット（px）


#=============建築物の描画====================
def build_spawn_border(cx, cy, half=300, block_hp=100):
    rects = []
    s = BLOCK_SIZE
    left   = cx - half
    right  = cx + half - s
    top    = cy - half
    bottom = cy + half - s

    def _push(x, y):
        rects.append({"rect": pygame.Rect(int(x), int(y), s, s),
                      "hp": block_hp, "max_hp": block_hp})

    # 上下辺
    x = left
    while x <= right + 1:
        _push(x, top)
        _push(x, bottom)
        x += s
    # 左右辺
    y = top + s
    while y <= bottom - 1:
        _push(left,  y)
        _push(right, y)
        y += s
    return rects

def rect_collides_any(r, rects):
    """r が rects のどれかと衝突していれば True"""
    for br in rects:
        rect = br["rect"] if isinstance(br, dict) and "rect" in br else br
        if r.colliderect(rect):
            return True
    return False

# HPバーの描画
def draw_hp_bar(surf, x, y, w, h, hp, max_hp, back=(60,60,60), fill=(0,200,0), border=(0,0,0)):
    hp = max(0, min(hp, max_hp))
    # 背景
    pygame.draw.rect(surf, back, (x, y, w, h))
    # 中身
    fw = int(w * (hp / max_hp)) if max_hp > 0 else 0
    if fw > 0:
        pygame.draw.rect(surf, fill, (x, y, fw, h))
    # 枠
    pygame.draw.rect(surf, border, (x, y, w, h), 1)

# デバックモードの表示
# 敵のスポーン範囲の表示
def get_current_spawn_tile_rect():
    """プレイヤーがいる“論理タイル”内で、敵をランダムサンプルしている矩形（ワールド座標）を返す"""
    w, h = enemy_image.get_width(), enemy_image.get_height()

    pgx, pgy = spawn_rel_tile(player_x, player_y)   # 現在のタイル番号
    tile_cx, tile_cy = center_of_tile(pgx, pgy, TILE_W, TILE_H)

    tile_left   = tile_cx - TILE_W // 2
    tile_right  = tile_cx + TILE_W // 2
    tile_top    = tile_cy - TILE_H // 2
    tile_bottom = tile_cy + TILE_H // 2

    # 敵スプライトが収まる内側（spawn_enemy と同じ）
    left   = int(tile_left   + w * 0.5)
    right  = int(tile_right  - w * 0.5)
    top    = int(tile_top    + h * 0.5)
    bottom = int(tile_bottom - h * 0.5)
    return pygame.Rect(left, top, right - left, bottom - top)

# 建築物の保存
def make_block_from_xy(x, y, img="block1.png", hp=100, collidable=True, door_state=None):
    """保存データ→実体化 / 既定作成用の共通フォーマット"""
    b = {
        "rect": pygame.Rect(int(x), int(y), BLOCK_SIZE, BLOCK_SIZE),
        "img": img,
        "collidable": bool(collidable),
        "door_state": door_state,  # None / "closed" / "open"
        "hp": int(hp),
        "max_hp": int(hp),
    }
    # ドアはHP不要にする（飾り）
    if b["door_state"] is not None:
        b["hp"] = b["max_hp"] = 0
    return b


def encode_blocks(blocks):
    """
    ブロック群を超短い文字列に圧縮:
      1エントリ = "x,y,t[,hp]"
      ・t は 0=壁, 1=閉ドア, 2=開ドア
      ・hp は“既定値”なら省略（壁=100, 閉ドア=DOOR_MAX_HP, 開ドア=0）
      ・エントリ区切りは ';'
    """
    parts = []
    for br in blocks:
        r = br["rect"]
        x, y = r.x, r.y
        img = br.get("img", "block1.png")
        t = IMG_CODE.get(img, "0")

        hp = int(br.get("hp", 100))
        default_hp = 100 if t == "0" else (DOOR_MAX_HP if t == "1" else 0)

        if hp == default_hp:
            parts.append(f"{x},{y},{t}")
        else:
            parts.append(f"{x},{y},{t},{hp}")
    return ";".join(parts)


def decode_blocks(compact: str):
    """
    encode_blocks で作った文字列をブロック配列に戻す。
    collidable/door_state は img & hp から自動導出。
    """
    if not compact:
        return []

    out = []
    for entry in compact.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        fields = entry.split(",")
        # x,y,t[,hp]
        if len(fields) < 3:
            continue
        x = int(fields[0]); y = int(fields[1]); t = fields[2]
        img = CODE_IMG.get(t, "block1.png")

        # 既定HP
        default_hp = 100 if t == "0" else (DOOR_MAX_HP if t == "1" else 0)
        hp = int(fields[3]) if len(fields) >= 4 else default_hp

        # 派生プロパティ
        if t == "1" and hp > 0:
            door_state = "closed"
            collidable = True
        elif t == "2":
            door_state = "open"
            collidable = False
        else:
            door_state = None
            collidable = (hp > 0)

        out.append({
            "rect": pygame.Rect(int(x), int(y), BLOCK_SIZE, BLOCK_SIZE),
            "img": img,
            "collidable": collidable,
            "door_state": door_state,
            "hp": hp,
            "max_hp": hp if door_state is None else (DOOR_MAX_HP if door_state == "closed" else 0),
        })
    return out


def default_border_blocks_with_door(cx, cy, half=500, hp=100):
    raw = build_spawn_border(cx, cy, half=half, block_hp=hp)
    for br in raw:
        br["img"] = "block1.png"
        br["collidable"] = True
        br["door_state"] = None

    # 中央下に最も近いブロックをドアに
    target_x, target_y = cx, cy + half - BLOCK_SIZE // 2
    door_idx = min(
        range(len(raw)),
        key=lambda i: (raw[i]["rect"].centerx - target_x) ** 2 + (raw[i]["rect"].centery - target_y) ** 2
    )
    raw[door_idx]["img"] = "close_door.png"
    raw[door_idx]["door_state"] = "closed"

    # ★ ここを変更：閉じている間はHPあり＆衝突あり（開いたらHPゼロ化＆衝突OFFにする）
    raw[door_idx]["hp"] = DOOR_MAX_HP
    raw[door_idx]["max_hp"] = DOOR_MAX_HP
    raw[door_idx]["collidable"] = True
    return raw


def draw_game(screen):
    global level_up_notice_rect

    # 変更後（ここがポイント）
    bg_off_x = int(player_x - PLAYER_DRAW_X)
    bg_off_y = int(player_y - PLAYER_DRAW_Y)

    # --- 背景を最初に描く（上書きしない）---
    draw_bg(screen, bg_ctx, bg_off_x, bg_off_y, BG_RANDOM_SEED)

    # === ブロック描画（画像） ===
    for br in border_blocks:
        r = br["rect"]
        screen_rect = r.move(-bg_off_x, -bg_off_y)

        # ★ 画像は個々の設定に従う
        img_key = br.get("img", "block1.png")
        img = BLOCK_IMAGES.get(img_key, block_img)
        screen.blit(img, screen_rect.topleft)

        # ★ ドアや非衝突ブロックはHPバーを出さない
        if br.get("collidable", True) and br.get("max_hp", 0) > 0:
            bw = r.w
            bar_w, bar_h = bw, 6
            bar_x = screen_rect.x
            bar_y = screen_rect.y - (bar_h + 2)
            draw_hp_bar(screen, bar_x, bar_y, bar_w, bar_h, br.get("hp", 0), br.get("max_hp", 0), fill=(200,80,80))


    # （デバッグ）当たり判定の枠を表示したいとき
    # pygame.draw.rect(screen, (255, 0, 0), screen_rect, 1)
        # --- デバッグ: 当たり判定の可視化 ---
    if DEBUG_COLLISION_DRAW:
        if DEBUG_COLLISION_DRAW:
            for br in border_blocks:
                r = br["rect"]
                rr = pygame.Rect(int(r.x - bg_off_x), int(r.y - bg_off_y), r.w, r.h)
                pygame.draw.rect(screen, (0,255,0), rr, 2)

        # プレイヤーの矩形（赤）
        screen_cx = player_x - bg_off_x
        screen_cy = player_y - bg_off_y
        pr = pygame.Rect(
            int(screen_cx - PLAYER_COLL_W // 2 + HITBOX_OFFSET_X),
            int(screen_cy - PLAYER_COLL_H // 2 + HITBOX_OFFSET_Y),
            PLAYER_COLL_W, PLAYER_COLL_H
        )
        pygame.draw.rect(screen, (255, 0, 0), pr, 2)

        # 敵の当たり判定（黄色）
        for en in enemies:
            if 'rect' not in en:
                continue
            er = en['rect']
            # ワールド→画面
            er_screen = pygame.Rect(
                int(er.x - bg_off_x),
                int(er.y - bg_off_y),
                er.w, er.h
            )
            pygame.draw.rect(screen, (255, 215, 0), er_screen, 2)  # Yellow

            # 中心マーカー（任意：見やすくするため）
            cx = er_screen.centerx
            cy = er_screen.centery
            pygame.draw.line(screen, (255, 215, 0), (cx - 6, cy), (cx + 6, cy), 1)
            pygame.draw.line(screen, (255, 215, 0), (cx, cy - 6), (cx, cy + 6), 1)
        
        # --- 敵スポーン範囲の可視化（F1デバッグ時） ---
        spawn_rect_world = get_current_spawn_tile_rect()
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # サンプリング領域（赤）
        sr_screen = pygame.Rect(
            spawn_rect_world.x - bg_off_x,
            spawn_rect_world.y - bg_off_y,
            spawn_rect_world.w,
            spawn_rect_world.h
        )
        pygame.draw.rect(overlay, (255, 0, 0, 60), sr_screen)       # 塗り
        pygame.draw.rect(overlay, (255, 0, 0, 180), sr_screen, 2)   # 枠

        # ポータル禁止半径（青）
        portals = list_portals()
        PORTAL_SAFE_RADIUS = max(PORTAL_W, PORTAL_H) // 2 + 100
        for p in portals:
            px, py = p["rect"].center
            cx = int(px - bg_off_x)
            cy = int(py - bg_off_y)
            pygame.draw.circle(overlay, (0, 128, 255, 50), (cx, cy), PORTAL_SAFE_RADIUS)
            pygame.draw.circle(overlay, (0, 128, 255, 160), (cx, cy), PORTAL_SAFE_RADIUS, 2)

        # 合成
        screen.blit(overlay, (0, 0))

        # ラベル（下部に表示）
        help_font = jp_font(20)
        txt = help_font.render("F1: Debug ON  （赤=スポーン範囲 / 青=ポータル禁止半径）", True, (0,0,0))
        screen.blit(txt, (10, SCREEN_HEIGHT - 70))


    # プレイヤー
    # プレイヤー画像の中心を常に画面中央に置く
    player_draw_x = SCREEN_WIDTH // 2 - player_image.get_width() // 2 - 15
    player_draw_y = SCREEN_HEIGHT // 2 - player_image.get_height() // 2 - 15
    screen.blit(player_image, (player_draw_x, player_draw_y))

    # === プレイヤーHPバー ===
    pw, ph = player_image.get_width(), player_image.get_height()
    # 直前の blit に使った player_draw_x / player_draw_y をそのまま使う
    bar_w, bar_h = max(40, pw), 7
    bar_x = player_draw_x + (pw - bar_w) // 2
    bar_y = player_draw_y - (bar_h + 4)
    draw_hp_bar(screen, bar_x, bar_y, bar_w, bar_h, player_hp, player_max_hp, fill=(0, 180, 255))


    if overlooking:
        pygame.draw.circle(screen, (255, 0, 0), (PLAYER_DRAW_X + 15, PLAYER_DRAW_Y + 15), 6)

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

    # どこか上（関数外でもOK）で一度だけ定義
    ENEMY_MAX_HP_DEFAULT = 50

    # 敵
    for enemy in enemies:
        # ---- HPの初期化（未設定キーがあっても落ちないよう保険）----
        enemy.setdefault('hp', 50)                 # 好きな初期値でOK
        enemy.setdefault('max_hp', enemy['hp'])    # maxが無ければ今のhpを上限として扱う

        # ---- 画像の選択 ----
        if enemy.get('dying'):
            a = max(0, min(255, int(enemy['alpha'])))
            nearest = min(ENEMY_FADE_LEVELS, key=lambda v: abs(v - a))
            img = enemy_fade_images[nearest]
        else:
            img = enemy_image

        # ---- 位置（ワールド→画面）----s
        # 敵の位置は左上基準（enemy['x'],['y']）なので、そのままオフセット
        draw_x = int(enemy['x'] - bg_off_x)
        draw_y = int(enemy['y'] - bg_off_y)
        screen.blit(img, (draw_x, draw_y))

        # ---- HPの初期化（未設定の個体のみ）----
        if 'hp' not in enemy:
            enemy['max_hp'] = ENEMY_MAX_HP_DEFAULT
            enemy['hp'] = enemy['max_hp']

        # ---- HPバー（敵の頭上）----
        # enemy['rect'] が左上基準の当たり判定Rectであることを前提
        er = enemy.get('rect')
        if er is None:
            # 念のため保険：rectが無い個体は画像サイズから仮Rectを作る
            er = pygame.Rect(int(enemy['x']), int(enemy['y']),
                         img.get_width(), img.get_height())
            enemy['rect'] = er

        er_screen = er.move(-bg_off_x, -bg_off_y)
        bar_w, bar_h = er.w, 5
        bar_x = er_screen.x
        bar_y = er_screen.y - (bar_h + 2)
        draw_hp_bar(screen, bar_x, bar_y, bar_w, bar_h,
                    enemy['hp'], enemy['max_hp'], fill=(255, 215, 0))


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
    # ここで自前計算（グローバルは参照するだけ）
    minutes = max(0, int((goel_time - int(game_time)) // 60))
    seconds = max(0, int((goel_time - int(game_time)) % 60))

    # 表示形式（ゼロ埋め：01:05 など）
    remaining_time_text = time_font.render(f"{minutes:02d}:{seconds:02d}", True, (0, 0, 0))

    # --- 画面中央上に配置 ---
    text_rect = remaining_time_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 8))
    screen.blit(remaining_time_text, text_rect)

    
    # UI
    font = jp_font(30)
    hp_text = font.render(f"HP: {player_hp}/{player_max_hp}", True, (255, 0, 0))
    display_exp = min(int(exp), int(exp_to_next))
    level_text = font.render(f"Level: {level}  EXP: {display_exp}/{exp_to_next}", True, (0, 255, 0))
    battery_text = font.render(f"Battery: {battery}", True, (255, 255, 0))
    score_text = font.render(f"Score: {score}", True, (0, 255, 255))
    enemy_level_text = font.render(f"Enemy Lv: {enemy_level}", True, (255, 255, 255))
    coord_text = font.render(f"X: {int(player_x - 5000)}  Y: {int(player_y - 5000)}", True, (0, 0, 0)) 
    text_rect = coord_text.get_rect()
    text_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)

    screen.blit(hp_text, (10, 10))
    screen.blit(level_text, (10, 50))
    screen.blit(battery_text, (10, 90))
    screen.blit(score_text, (10, 130))
    screen.blit(enemy_level_text, (10, 170))
    screen.blit(coord_text, text_rect)

        # === タイル座標の表示（新規） ===
    gx, gy = spawn_rel_tile(player_x, player_y)
    tile_text = font.render(f"Tile: ({gx}, {gy})", True, (50, 50, 50))
    tile_text_rect = tile_text.get_rect()
    tile_text_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 40)
    screen.blit(tile_text, tile_text_rect)

    # ★ 探索済みタイルに追加（重複は set なので気にしない）
    EXPLORED_TILES.add((gx, gy))

    # === 初期スポーン地点(タイル0,0の中心=SPAWN_CENTER_WX/WY)にポータルを描く ===
    portal_draw_x = SPAWN_CENTER_WX - player_x + PLAYER_DRAW_X
    portal_draw_y = SPAWN_CENTER_WY - player_y + PLAYER_DRAW_Y
    screen.blit(portal_img, (int(portal_draw_x - PORTAL_W // 2), int(portal_draw_y - PORTAL_H // 2)))

# ===============================
# 敵のアルゴリズム
# ===============================
# --- スリープ挙動パラメータ ---
BLOCK_SAFE_DIST         = 2000   # ブロックまでの最短距離がこれ以下なら“眠らない”
BLOCK_WAKE_DIST_HYST    = 1900   # 起床のブロック距離（ヒステリシス）
MIN_DIST_FROM_BLOCKS = 1000  # ブロックからの最小距離（px）
R_MIN                   = 1500   # 敵の保険スポーン距離（px）

def enemy_center(enemy):
    cx = enemy['x'] + enemy['rect'].w * 0.5
    cy = enemy['y'] + enemy['rect'].h * 0.5
    return cx, cy

def dist_blocks_min(cx, cy):
    """敵中心→最も近いブロック距離"""
    return min_distance_to_blocks(cx, cy, border_blocks)

def in_same_player_tile(cx, cy):
    """敵中心がプレイヤーと同じ“論理タイル”にいるか？"""
    pgx, pgy = spawn_rel_tile(player_x, player_y)
    egx, egy = spawn_rel_tile(cx, cy)
    return (pgx == egx) and (pgy == egy)

def enemy_should_sleep(cx, cy):
    """眠る条件：
       - プレイヤーと同一タイルなら眠らない
       - ブロックまでの最短距離が BLOCK_SAFE_DIST 以下なら眠らない
       - それ以外なら眠る
    """
    if in_same_player_tile(cx, cy):
        return False
    if dist_blocks_min(cx, cy) <= BLOCK_SAFE_DIST:
        return False
    return True  # どちらにも当てはまらない → 眠る

def enemy_should_wake(cx, cy):
    """起床条件：
       - プレイヤーと同じタイルに入った
       - またはブロックに近づいた（距離 < BLOCK_WAKE_DIST_HYST）
    """
    if in_same_player_tile(cx, cy):
        return True
    if dist_blocks_min(cx, cy) < BLOCK_WAKE_DIST_HYST:
        return True
    return False

def sleep_enemy(enemy):
    enemy['sleep'] = True
    enemy['ai_disabled'] = True

def wake_enemy(enemy):
    enemy['sleep'] = False
    enemy['ai_disabled'] = False

# ===============================
# 建築物のアルゴリズム
# ===============================
# --- portals（将来複数OK） ---
PORTALS = []  # 各要素: {"rect": pygame.Rect(...)}
def list_portals():
    return PORTALS

# ===============================
# ゲームリセット
# ===============================
def reset_game():
    global BG_RANDOM_SEED
    global player_x, player_y, SPAWN_CENTER_WX, SPAWN_CENTER_WY, player_hp, player_max_hp, base_attack, exp, level, exp_to_next, exp_rato, player_speed, player_defence, player_clitical_rato, player_clitical_damage, PLAYER_IFRAME_MAX, player_iframe, player_vx, player_vy
    global weapons, weapon_counter, lasers, laser_level, laser_timer, laser_cooldown, laser_duration, enemy_spawn_timer, score, start_ticks
    global enemies, enemy_base_hp, enemy_base_attack, enemy_speed, enemy_level, last_buff_time, ENEMY_RADIUS, ENEMY_SEP_ITER, LABEL_FONT, LABEL_GRID_CACHE
    global damage_texts
    global exp_items, start_ticks, battery, battery_items, MAGNET_RADIUS, ITEM_HOMING_SPEED
    global shortwaves, Weapon_shortwave_image, shortwave_base_w, shortwave_base_h, initial_scale, shortwave_level, weapon_shortwave_cooldown, weapon_shortwave_duration, weapon_shortwave_timer
    global game_speed, game_time, goel_time, game_clear
    global LEVELUP_PICK_COUNT
    global border_blocks, PORTALS

    start_ticks = pygame.time.get_ticks()  # ← ゲーム開始時刻（ミリ秒）

    player_x, player_y = center_of_tile(0, 0, TILE_W, TILE_H)
    SPAWN_CENTER_WX, SPAWN_CENTER_WY = player_x, player_y

    # ★ ブロック配置：savedataにあればそれを使い、無ければ既定形＋ドアを作る
    if 'SAVED_BLOCKS_LAYOUT' in globals() and SAVED_BLOCKS_LAYOUT:
        border_blocks = SAVED_BLOCKS_LAYOUT
    else:
        border_blocks = default_border_blocks_with_door(SPAWN_CENTER_WX, SPAWN_CENTER_WY, half=500, hp=100)
        # 初回に既定配置を保存しておく（以後はロードで再現される）
        try:
            save_game_data()
        except Exception:
            pass

    # ★ここでPORTALSを更新（いまは1個）
    PORTALS = [{
        "rect": pygame.Rect(
            SPAWN_CENTER_WX - PORTAL_W // 2,
            SPAWN_CENTER_WY - PORTAL_H // 2,
            PORTAL_W, PORTAL_H
        )
    }]

    LABEL_FONT = jp_font(14)   # ← ここで再初期化
    LABEL_GRID_CACHE = {}      # ← キャッシュは空でOK

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
        # バケットに振り分け
        for idx, e in enumerate(enemies):
            if e.get('sleep'):    # ★眠りは空間ハッシュに入れない
                continue
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
                            if a.get('sleep') or b.get('sleep'):  # ★眠りは動かさない
                                continue
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
def point_rect_distance(px, py, r: pygame.Rect):
    """点(px,py)と矩形rのユークリッド距離（0なら接触/内部）"""
    # 矩形外なら外側の最近点まで、内部なら0
    dx = 0.0
    if px < r.left:
        dx = r.left - px
    elif px > r.right:
        dx = px - r.right

    dy = 0.0
    if py < r.top:
        dy = r.top - py
    elif py > r.bottom:
        dy = py - r.bottom

    if dx == 0.0 and dy == 0.0:
        return 0.0
    return (dx*dx + dy*dy) ** 0.5

def min_distance_to_blocks(px, py, blocks):
    """点と複数ブロックとの最小距離"""
    if not blocks:
        return float('inf')
    dmin = float('inf')
    for b in blocks:
        # bがRectそのものか、オブジェクトにrectを持つかの両対応
        r = b if isinstance(b, pygame.Rect) else b.get('rect', None)
        if r is None:
            continue
        d = point_rect_distance(px, py, r)
        if d < dmin:
            dmin = d
    return dmin

# 敵のスポーン位置
def segment_intersects_rect(x1, y1, x2, y2, r: pygame.Rect) -> bool:
    """線分(x1,y1)-(x2,y2)が矩形rと交差するか（境界含む）"""
    # 1) 端点どちらかが矩形内なら「交差」とみなす
    if r.collidepoint(x1, y1) or r.collidepoint(x2, y2):
        return True

    # 2) 矩形の4辺と線分の交差をチェック
    x3, y3, x4, y4 = r.left, r.top, r.right, r.top       # 上辺
    if _seg_seg_intersect(x1, y1, x2, y2, x3, y3, x4, y4): return True
    x3, y3, x4, y4 = r.right, r.top, r.right, r.bottom   # 右辺
    if _seg_seg_intersect(x1, y1, x2, y2, x3, y3, x4, y4): return True
    x3, y3, x4, y4 = r.left, r.bottom, r.right, r.bottom # 下辺
    if _seg_seg_intersect(x1, y1, x2, y2, x3, y3, x4, y4): return True
    x3, y3, x4, y4 = r.left, r.top, r.left, r.bottom     # 左辺
    if _seg_seg_intersect(x1, y1, x2, y2, x3, y3, x4, y4): return True

    return False

def _seg_seg_intersect(x1,y1,x2,y2, x3,y3,x4,y4) -> bool:
    """2線分が交差しているか（共線の重なりや端点接触もTrue）"""
    def ccw(ax,ay, bx,by, cx,cy):
        return (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)
    d1 = ccw(x1,y1,x2,y2,x3,y3)
    d2 = ccw(x1,y1,x2,y2,x4,y4)
    d3 = ccw(x3,y3,x4,y4,x1,y1)
    d4 = ccw(x3,y3,x4,y4,x2,y2)
    # 一般の交差
    if (d1*d2 < 0) and (d3*d4 < 0):
        return True
    # 共線＆重なり（境界含む）
    def between(a,b,c):  # c が [min(a,b), max(a,b)] にいる？
        return min(a,b) <= c <= max(a,b)
    if d1 == 0 and between(x1,x2,x3) and between(y1,y2,y3): return True
    if d2 == 0 and between(x1,x2,x4) and between(y1,y2,y4): return True
    if d3 == 0 and between(x3,x4,x1) and between(y3,y4,y1): return True
    if d4 == 0 and between(x3,x4,x2) and between(y3,y4,y2): return True
    return False

def crosses_wall_to_portal(cx, cy, portals, blocks, crossings_required=1) -> bool:
    """
    候補点(cx,cy)→各ポータル中心への線分が、ブロック矩形と少なくとも
    crossings_required 回交差するか？（どれか1つのポータルに対して満たせばOK）
    """
    for p in portals:
        pr = p["rect"]
        px, py = pr.center
        hits = 0
        for b in blocks:
            br = b["rect"] if isinstance(b, dict) else (b if isinstance(b, pygame.Rect) else None)
            if br is None: 
                continue
            if segment_intersects_rect(cx, cy, px, py, br):
                hits += 1
                if hits >= crossings_required:
                    return True
    return False

def spawn_enemy():
    if len(enemies) >= MAX_ENEMIES:
        return

    w, h = enemy_image.get_width(), enemy_image.get_height()

    # ① プレイヤーがいる“論理タイル”の中心→そのタイルの左上/右下（ワールド座標）を計算
    pgx, pgy = spawn_rel_tile(player_x, player_y)   # プレイヤーがいるタイル(±5000/10000ルール)
    tile_cx, tile_cy = center_of_tile(pgx, pgy, TILE_W, TILE_H)
    tile_left   = tile_cx - TILE_W // 2
    tile_right  = tile_cx + TILE_W // 2
    tile_top    = tile_cy - TILE_H // 2
    tile_bottom = tile_cy + TILE_H // 2

    # ② タイル内でランダムサンプリング（中心=候補点）→ブロックから1000以上＆非衝突なら採用
    # === 敵を出現させる ===
    MAX_TRIES = 300
    portals = list_portals()  # ★ 現在登録されているポータル（1個または複数）
    PORTAL_SAFE_RADIUS = max(PORTAL_W, PORTAL_H) // 2 + 100  # ポータル保護距離(px)

    for _ in range(MAX_TRIES):
        # タイル内のランダム座標
        cx = random.uniform(tile_left + w * 0.5, tile_right - w * 0.5)
        cy = random.uniform(tile_top + h * 0.5, tile_bottom - h * 0.5)

        # 敵の矩形
        x = int(cx - w * 0.5)
        y = int(cy - h * 0.5)
        rect = pygame.Rect(x, y, w, h)
    
        # --- 条件チェック ---

        # ① ブロックと重ならない
        if rect_collides_any(rect, border_blocks):
            continue

        # ② ブロックから1000px以上離す（中心で判定）
        if min_distance_to_blocks(cx, cy, border_blocks) < MIN_DIST_FROM_BLOCKS:
            continue

        # ③ ポータルに近すぎない（保護距離）
        too_close_to_portal = False
        for p in portals:
            px, py = p["rect"].center
            if math.hypot(cx - px, cy - py) < PORTAL_SAFE_RADIUS:
                too_close_to_portal = True
                break
        if too_close_to_portal:
            continue

        # ④ 壁の“外側”のみ許可（ポータル中心へ線を引いたとき壁を最低1回跨ぐ）
        if not crosses_wall_to_portal(cx, cy, portals, border_blocks, crossings_required=1):
            continue

        # --- ここまで通れば採用 ---
        enemies.append({
            'rect': rect,
            'x': x, 'y': y,
            'hp': enemy_base_hp, 'max_hp': enemy_base_hp,
            'atk': enemy_base_attack,
            'level': enemy_level,
            'last_hits': {},
            'alpha': 255,
            'dying': False,
        })
        return  # 1体湧かせたら終了

    # 200回試しても見つからなければ、今回は湧かせない
    return


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

#プレイヤーの向きを初期化
player_image_draw = player_image

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
# メインゲーム中のESC確認ダイアログ表示フラグ
confirm_gameover = False  

DEBUG_COLLISION_DRAW = False

# === Base（待機ルーム）用デバッグ表示 ===
DEBUG_BASE_DRAW = False

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

# === 背景の初期化 ===
TILE_W = 10000
TILE_H = 10000
# ミニマップ用のプレイヤー表示サイズ（px）
OVERLOOK_PLAYER_PX = 14

# ミニマップのラベル用フォント（起動時に設定）
LABEL_FONT = None
if LABEL_FONT is None:
    LABEL_FONT = jp_font(14)

# ミニマップのラベルグリッドをキャッシュ
# key = (base_gx, base_gy, cols, rows, tw, th)
LABEL_GRID_CACHE = {}

# 追加：通常タイル/ミニマップ用タイルの定数
NORMAL_TILE_W, NORMAL_TILE_H = 10000, 10000
MINIMAP_TILE_W, MINIMAP_TILE_H = 100, 100
#タイルの出現確率
BG_TILES = [("bg1.png", 6), ("bg2.png", 3), ("bg3.png", 1)]
BG_RANDOM_SEED = 1337

# 背景コンテキストの生成（その後でOK）
bg_ctx_normal = prepare_bg(BG_TILES, NORMAL_TILE_W, NORMAL_TILE_H)
bg_ctx_mini   = prepare_bg(BG_TILES, MINIMAP_TILE_W, MINIMAP_TILE_H)
bg_ctx = bg_ctx_normal

# プログラム開始時にセーブデータを読み込む
load_game_data()

MINIMAP_CTXS[100] = bg_ctx_mini

# （任意）初回ウォームアップ
_tmp = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
draw_bg(_tmp, bg_ctx_normal, 0, 0, BG_RANDOM_SEED)
draw_bg(_tmp, bg_ctx_mini,   0, 0, BG_RANDOM_SEED)
del _tmp
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
                    base_world_x = 0
                    base_world_y = 0
                    # ワールド原点に戻す
                    enter_base_from_game() 
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
                elif event.key == pygame.K_F1:
                    DEBUG_BASE_DRAW = not DEBUG_BASE_DRAW

        # 入力（ワールド座標を更新：右に進む=世界を左へ流すのと同義）
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += BASE_SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= BASE_SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy -= BASE_SPEED
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy += BASE_SPEED

        # ---- ここから当たり判定（ブロック矩形＋開始円） ----
        # 1) 目標物の定義（ワールド座標）
        BLOCK_CX, BLOCK_CY = 0, 190   # 透明ブロックの中心
        BLOCK_W, BLOCK_H   = 128, 120
        PROMPT_CX, PROMPT_CY = 0, 120 # プロンプト円の中心
        PROMPT_R = 20

        # 2) 軸分離でシンプルに衝突を止める（X→Yの順に適用）
        prev_x, prev_y = base_world_x, base_world_y
        nx = base_world_x + dx
        ny = base_world_y + dy

        # プレイヤー矩形サイズ（画像から）
        p_w = player_original.get_width()
        p_h = player_original.get_height()

        # 透明ブロックの pygame.Rect（左上起点）
        block_rect = pygame.Rect(
            int(BLOCK_CX - BLOCK_W // 2),
            int(BLOCK_CY - BLOCK_H // 2),
            BLOCK_W, BLOCK_H
        )

        # --- X軸移動の衝突 ---
        test_rect_x = pygame.Rect(int(nx - p_w/2), int(prev_y - p_h/2), p_w, p_h)
        if test_rect_x.colliderect(block_rect):
            nx = prev_x  # X方向は進ませない

        # --- Y軸移動の衝突 ---
        test_rect_y = pygame.Rect(int(nx - p_w/2), int(ny - p_h/2), p_w, p_h)
        if test_rect_y.colliderect(block_rect):
            ny = prev_y  # Y方向は進ませない

        # 確定
        base_world_x, base_world_y = nx, ny

        # 3) プロンプト判定（円内なら表示）
        dx_c = base_world_x - PROMPT_CX
        dy_c = base_world_y - PROMPT_CY
        show_start_prompt = (dx_c*dx_c + dy_c*dy_c) <= (PROMPT_R * PROMPT_R)

        # ★ 追加：ワールド座標(500,500) 到達で Power Up 画面を開く
        if abs(base_world_x - 500) <= 20 and abs(base_world_y - 0) <= 20:
            power_up_screen = True
            in_base = False

        # ===== 描画 =====
        # 背景をワールドオフセットでタイル描画（offsetが増えると左に流れる）
        draw_tiled_bg(screen, bg_image, base_world_x, -base_world_y)

         # 目印：(100,180)  ← 表示位置も合わせる
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        px, py = base_world_to_screen(0, 180)
        screen.blit(portal_img, (px - PORTAL_W // 2, py - PORTAL_H // 2))

        mx, my = base_world_to_screen(500, 0)
        pygame.draw.circle(screen, (0, 128, 255), (mx, my), 8, 2)

        # プレイヤーは常に中央に描画（向きだけ入力で変える）
        if dx > 0:
            player_image_draw = pygame.transform.rotate(player_original, 270)
        elif dx < 0:
            player_image_draw = pygame.transform.rotate(player_original, 90)
        elif dy > 0:
            player_image_draw = player_original
        elif dy < 0:
            player_image_draw = pygame.transform.rotate(player_original, 180)

        screen.blit(
            player_image_draw,
            (center_x - player_original.get_width() // 2,
             center_y - player_original.get_height() // 2)
        )

        # ★ 「プレイを開始しますか？」の案内とFキーで開始
        if show_start_prompt:
            tip_font = jp_font(28)
            tip = tip_font.render("プレイを開始しますか？（Fキー）", True, (0, 0, 0))
            tip_x = SCREEN_WIDTH // 2 - tip.get_width() // 2
            tip_y = SCREEN_HEIGHT // 2 + player_original.get_height() // 2 + 40
            screen.blit(tip, (tip_x, tip_y))

            if keys[pygame.K_f]:
                reset_game()
                in_base = False


        # デバッグ表示（任意）：いまのワールド座標
        font = jp_font(24)
        screen.blit(font.render(f"World Pos: ({int(base_world_x)}, {int(base_world_y)})", True, (0,0,0)), (10, 10))
        screen.blit(font.render("ポータル下で Fキー で開始", True, (0,0,0)), (10, 40))

                # ★ 追加: Base用デバッグ可視化
        if DEBUG_BASE_DRAW:
            # 画面中心（プレイヤー描画位置は常にここ）
            cx = SCREEN_WIDTH // 2
            cy = SCREEN_HEIGHT // 2

            # プレイヤーの当たり判定（見た目基準。Baseでは画像と同じ大きさでOK）
            p_w = player_original.get_width()
            p_h = player_original.get_height()
            player_rect_screen = pygame.Rect(cx - p_w // 2, cy - p_h // 2, p_w, p_h)
            pygame.draw.rect(screen, (255, 0, 0), player_rect_screen, 2)  # 赤: プレイヤー

            # 透明ブロック（ワールド定義）
            BLOCK_CX, BLOCK_CY = 0, 190
            BLOCK_W, BLOCK_H   = 128, 120
            left = BLOCK_CX - BLOCK_W // 2
            top  = BLOCK_CY - BLOCK_H // 2
            sx, sy = base_world_to_screen(left, top)
            block_rect_screen = pygame.Rect(sx, sy, BLOCK_W, BLOCK_H)
            pygame.draw.rect(screen, (0, 255, 0), block_rect_screen, 2)  # 緑: 透明ブロック

            # ポータル矩形（画像基準）
            portal_left  = 0 - PORTAL_W // 2
            portal_top   = 180 - PORTAL_H // 2
            psx, psy = base_world_to_screen(portal_left, portal_top)
            portal_rect_screen = pygame.Rect(psx, psy, PORTAL_W, PORTAL_H)
            pygame.draw.rect(screen, (0, 0, 255), portal_rect_screen, 2)  # 青: ポータル

            # 開始プロンプト円（Fキー判定位置）
            PROMPT_CX, PROMPT_CY = 0, 120
            PROMPT_R = 20
            pcx, pcy = base_world_to_screen(PROMPT_CX, PROMPT_CY)
            pygame.draw.circle(screen, (0, 128, 255), (pcx, pcy), PROMPT_R, 2)  # 水色: 開始円

            # 原点十字（任意）
            ox, oy = base_world_to_screen(0, 0)
            pygame.draw.line(screen, (200, 0, 200), (ox - 10, oy), (ox + 10, oy), 2)
            pygame.draw.line(screen, (200, 0, 200), (ox, oy - 10), (ox, oy + 10), 2)

            # 軽い注記
            info_font = jp_font(18)
            screen.blit(info_font.render("F2: Base Debug ON", True, (0, 0, 0)), (10, 70))
            screen.blit(info_font.render("Red=Player  Green=Block  Blue=Portal  Cyan=StartCircle", True, (0, 0, 0)), (10, 92))


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
                if event.key == pygame.K_ESCAPE:  # ESCでベースに戻る
                    save_game_data()
                    power_up_screen = False
                    base_world_x -= 50
                    base_world_y = 0
                    enter_base_from_game()
                    continue
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
                        save_game_data()
                        power_up_screen = False
                        base_world_x -= 50
                        base_world_y = 0
                        enter_base_from_game()
                        continue

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
#================
#メインゲーム
#================
    if not game_over and not game_clear:
        # === ESC確認ダイアログ（メインゲーム中のみ） ===
        if confirm_gameover:
            # 背景に現状のゲーム画面を描く
            draw_game(screen)

            # 半透明の暗幕
            dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 160))
            screen.blit(dim, (0, 0))

            spacing = 60  # ボタン間隔
            buttons_y = SCREEN_HEIGHT // 2 + 40
            yes_rect = yes_button.get_rect(right=SCREEN_WIDTH // 2 - spacing // 2, top=buttons_y)
            no_rect  = no_button.get_rect(left =SCREEN_WIDTH // 2 + spacing // 2, top=buttons_y)
            screen.blit(yes_button, yes_rect)
            screen.blit(no_button,  no_rect)

            # 追加で文字を重ねてわかりやすく（画像にテキストが無い場合）
            try:
                font = jp_font(36)
                msg  = font.render("ゲームを終了して GAME OVER にしますか？", True, (255,255,255))
                screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 - 60))
            except:
                pass

            # ここ専用のイベント処理（ゲームは停止）
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                        # キャンセル
                        confirm_gameover = False
                    elif event.key == pygame.K_y or event.key == pygame.K_RETURN:
                        # 確定→ゲームオーバーへ
                        save_game_data()
                        confirm_gameover = False
                        game_over = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_rect.collidepoint(event.pos):
                        save_game_data()
                        confirm_gameover = False
                        game_over = True
                    elif no_rect.collidepoint(event.pos):
                        confirm_gameover = False

            pygame.display.flip()
            clock.tick(60)
            continue  # このフレームは他の更新を行わない
        if paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # ===== ミニマップ（俯瞰）中の入力 =====
                if overlooking:
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_o, pygame.K_ESCAPE, pygame.K_p):
                            exit_minimap()
                            paused = False
                            continue
                        # ズームイン / ズームアウト（＋／−、テンキー対応）
                        if event.key in (pygame.K_EQUALS, pygame.K_UP):
                            set_minimap_zoom_index(minimap_zoom_i + 1)
                            continue
                        if event.key in (pygame.K_MINUS, pygame.K_DOWN):
                            set_minimap_zoom_index(minimap_zoom_i - 1)
                            continue
                    elif event.type == pygame.MOUSEWHEEL:
                        if event.y > 0:
                            set_minimap_zoom_index(minimap_zoom_i + 1)
                        elif event.y < 0:
                            set_minimap_zoom_index(minimap_zoom_i - 1)
                    # === ここを追加：W/A/S/D でミニマップ内をパン ===
                    keys = pygame.key.get_pressed()
                    spd = MINIMAP_PAN_SPEED_PX
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        spd *= 3  # Shiftで高速パン

                    if keys[pygame.K_w]:
                        minimap_cam_y -= spd
                    if keys[pygame.K_s]:
                        minimap_cam_y += spd
                    if keys[pygame.K_a]:
                        minimap_cam_x -= spd
                    if keys[pygame.K_d]:
                        minimap_cam_x += spd
                    # 俯瞰中は通常pause処理に進まない
                    continue

                # ===== ここから通常の pause 中キー処理 =====
                if event.type == pygame.KEYDOWN:
                    # レベルアップ説明モーダル中の決定/キャンセル
                    if level_up_pending and choice_waiting:
                        if event.key == pygame.K_f and selected_choice_idx is not None:
                            choice_id = current_level_choices[selected_choice_idx]
                            level_up(choice_id)
                            choice_waiting = False
                            selected_choice_idx = None
                            continue
                        elif event.key == pygame.K_ESCAPE:
                            choice_waiting = False
                            selected_choice_idx = None
                            continue
                        # 通常のpause中（俯瞰でない時）も O で俯瞰へ入る
                    if event.key == pygame.K_o and not overlooking:
                        enter_minimap()
                        continue

                    # 通常のpause解除
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        paused = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if level_up_pending:
                        rects = get_level_choice_rects()
                        if not choice_waiting:
                            for idx, r in enumerate(rects):
                                if r.collidepoint(event.pos):
                                    choice_waiting = True
                                    selected_choice_idx = idx
                                    break
                        else:
                            clicked_any = False
                            for idx, r in enumerate(rects):
                                if r.collidepoint(event.pos):
                                    clicked_any = True
                                    if idx == selected_choice_idx:
                                        choice_id = current_level_choices[selected_choice_idx]
                                        level_up(choice_id)
                                        choice_waiting = False
                                        selected_choice_idx = None
                                    else:
                                        selected_choice_idx = idx
                                    break
                            if not clicked_any:
                                box_w, box_h = 560, 280
                                box_rect = pygame.Rect(
                                    SCREEN_WIDTH // 2 - box_w // 2,
                                    SCREEN_HEIGHT // 2 - box_h // 2 + 250,
                                    box_w, box_h
                                )
                                if not box_rect.collidepoint(event.pos):
                                    choice_waiting = False
                                    selected_choice_idx = None

            # ===== 俯瞰モード（背景＋スポーン基準タイル座標ラベル＋player.png） =====
            if overlooking:
            
                # ミニマップ時は TILE_W/H = 100,100 の想定
                tw, th = TILE_W, TILE_H

                # 1) プレイヤーがいる「スポーン基準タイル番号」
                lgx, lgy = spawn_rel_tile(player_x, player_y)

                # 2) そのタイルの「左上」を画面中央に置く（微パララックスは使わない）
                bg_off_x = int(lgx * tw - (SCREEN_WIDTH  // 2) + minimap_cam_x)
                bg_off_y = int(lgy * th - (SCREEN_HEIGHT // 2) + minimap_cam_y)

                # 背景のみ描画
                draw_bg(screen, bg_ctx, bg_off_x, bg_off_y, BG_RANDOM_SEED)

                # === 探索済みタイルを薄く塗る ===
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                for gx, gy in EXPLORED_TILES:
                    # タイル左上の座標を算出（背景と同じロジック）
                    tile_screen_x = gx * TILE_W - bg_off_x
                    tile_screen_y = gy * TILE_H - bg_off_y
                    # 半透明の矩形を描く
                    pygame.draw.rect(overlay, (0, 255, 0, 80), (tile_screen_x, tile_screen_y, TILE_W, TILE_H))
                # まとめて描画
                screen.blit(overlay, (0, 0))

                # 4) 画面に見えている“描画タイル”のインデックス（divmodで安定化）
                qx, rx = divmod(int(bg_off_x), tw)   # qx = base_gx,  rx = 0..tw-1
                qy, ry = divmod(int(bg_off_y), th)   # qy = base_gy,  ry = 0..th-1
                base_gx, base_gy = qx, qy
                start_x, start_y = -rx, -ry

                # 画面の“左上”に映っている論理タイル（lgx/lgy はプレイヤーの論理タイル）
                left_lgx = lgx + ((bg_off_x - lgx * tw) // tw)
                left_lgy = lgy + ((bg_off_y - lgy * th) // th)

                # プレイヤーがいる“論理タイル”（±5000/10000ルール）
                center_lgx, center_lgy = spawn_rel_tile(player_x, player_y)

                # ラベル式  label = center_lg + (gx_iter - ix_center) を崩さず、
                # 画面左上タイルのラベルが left_lg になるように ix_center を再定義
                ix_center = base_gx - (left_lgx - center_lgx)
                iy_center = base_gy - (left_lgy - center_lgy)

                # 画面で必要なタイル枚数（端のはみ出し用に +2）
                cols = SCREEN_WIDTH  // tw + 2
                rows = SCREEN_HEIGHT // th + 2

                # キャッシュキーに中心情報も入れる（中心タイルが変わったら作り直す）
                key = (base_gx, base_gy, cols, rows, tw, th, center_lgx, center_lgy, ix_center, iy_center)
                layer = LABEL_GRID_CACHE.get(key)
                if layer is None:
                    layer = build_minimap_label_layer(base_gx, base_gy, cols, rows, tw, th,
                                      center_lgx, center_lgy, ix_center, iy_center)
                    LABEL_GRID_CACHE[key] = layer

                screen.blit(layer, (start_x, start_y))

                # --- プレイヤーアイコンを「そのタイル内の実位置」に置く ---
                # いま描いているタイル解像度（ミニマップ時は tw=th=100）
                scale_px_per_world = tw / 10000.0  # 10000ワールド単位 → twピクセル

                # プレイヤーがいるスポーン基準タイル番号（すでに lgx, lgy があります）
                # lgx, lgy = spawn_rel_tile(player_x, player_y) は上で計算済み

                # そのタイルの「左上」が画面上のどこか（bg_off_x/y を使って直接求める）
                tile_screen_x = lgx * tw - bg_off_x
                tile_screen_y = lgy * th - bg_off_y

                # スポーン中心からの相対距離（ワールド単位）
                dx = player_x - SPAWN_CENTER_WX
                dy = player_y - SPAWN_CENTER_WY

                # タイル内オフセット（0〜10000）：
                # 左端 = -5000 + 10000*lgx なので、残差 = delta - 左端
                rx_world = dx + 5000 - 10000 * lgx
                ry_world = dy + 5000 - 10000 * lgy
                # 念のためはみ出し防止（四捨五入誤差対策）
                rx_world = max(0, min(9999, rx_world))
                ry_world = max(0, min(9999, ry_world))

                # ピクセルに変換（ミニマップのタイル内位置）
                off_x_px = int(rx_world * scale_px_per_world)
                off_y_px = int(ry_world * scale_px_per_world)

                # 画面上の実描画位置（アイコンの中心を載せたいので半分引く）
                icon_x = int(tile_screen_x + off_x_px - player_icon.get_width()  / 2)
                icon_y = int(tile_screen_y + off_y_px - player_icon.get_height() / 2)

                screen.blit(player_icon, (icon_x, icon_y))

                # ヒント
                hint_font = jp_font(22)
                hint = hint_font.render("O または ESC で閉じる", True, (0, 0, 0))
                screen.blit(hint, (20, 20))

                zfont = jp_font(16)
                zoom_info = zfont.render(f"Zoom: {TILE_W}px/tile", True, (0,0,0))
                screen.blit(zoom_info, (20, 48))

                pygame.display.flip()
                clock.tick(60)
                continue

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
            display_exp = min(int(exp), int(exp_to_next))
            level_text = font.render(f"Level: {level}  EXP: {display_exp}/{exp_to_next}", True, (0, 0, 0))
            time_text = font.render(f"Time: {int(game_time)}", True, (0, 0, 0))
            real_time_text = font.render(f"Real Time: {real_time}", True, (0, 0, 0))
            enemy_level_text = font.render(f"Enemy Lv: {enemy_level}", True, (0, 0, 0))
            battery_text = font.render(f"Battery: {battery}", True, (0, 0, 0))
            speed_text = font.render(f"Game Speed: {game_speed:.1f}", True, (0, 0, 0))
            base_attack_text = font.render(f"base attack: {base_attack}", True, (0, 0, 0))
            clitical_rato_text = font.render(f"critical rato: {player_clitical_rato * 100} %", True, (0, 0, 0))
            clitical_damage_text = font.render(f"critical damage: × {player_clitical_damage}", True, (0, 0, 0))
            coord_text = font.render(f"X: {player_x - 5000}  Y: {player_y - 5000}", True, (0, 0, 0))
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
                if event.key == pygame.K_ESCAPE:  # ESCで確認ダイアログを開く
                    confirm_gameover = True
                    continue
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
                    # Oでミニマップを開く／閉じる
                    if not paused:
                        paused = True
                        enter_minimap()     # ★ これが肝
                    else:
                        if overlooking:
                            # 既に俯瞰中なら閉じる
                            exit_minimap()
                            paused = False
                        else:
                            # ポーズ中かつ俯瞰でない → 俯瞰に入る
                            enter_minimap()
                if event.key == pygame.K_F1:
                    DEBUG_COLLISION_DRAW = not DEBUG_COLLISION_DRAW

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
        prev_x, prev_y = player_x, player_y

        # ---- X軸
        nx = prev_x + dx + player_vx
        test_rect_x = pygame.Rect(int(nx - PLAYER_COLL_W/2), int(prev_y - PLAYER_COLL_H/2), PLAYER_COLL_W, PLAYER_COLL_H)
        for br in border_blocks:
            if not br.get("collidable", True):
                continue
            if test_rect_x.colliderect(br["rect"]):
                # ★ 閉じたドアに当たったら即オープンして通す
                if br.get("door_state") == "closed":
                    br["door_state"] = "open"
                    br["img"] = "open_door.png"
                    br["collidable"] = False
                    br["hp"] = br["max_hp"] = 0  # 開いたらHP表示なし
                    try:
                        save_game_data()
                    except Exception:
                        pass
                    # ドアを開いたのでブロックとしては「当たり扱いしない」
                    continue
                # 通常の壁は止める
                nx = prev_x
                break

        # ---- Y軸
        ny = prev_y + dy + player_vy
        test_rect_y = pygame.Rect(int(nx - PLAYER_COLL_W/2), int(ny - PLAYER_COLL_H/2), PLAYER_COLL_W, PLAYER_COLL_H)
        for br in border_blocks:
            if not br.get("collidable", True):
                continue
            if test_rect_y.colliderect(br["rect"]):
                # ★ 閉じたドアに当たったら即オープンして通す
                if br.get("door_state") == "closed":
                    br["door_state"] = "open"
                    br["img"] = "open_door.png"
                    br["collidable"] = False
                    br["hp"] = br["max_hp"] = 0
                    try:
                        save_game_data()
                    except Exception:
                        pass
                    continue
                ny = prev_y
                break

        # 確定
        player_x, player_y = nx, ny
        
        # 最終的なプレイヤー判定Rect（他の衝突にもこれを使う）
        player_rect = pygame.Rect(
            int(player_x - PLAYER_COLL_W // 2),
            int(player_y - PLAYER_COLL_H // 2),
            PLAYER_COLL_W, PLAYER_COLL_H
        )
        # ★ ドア（閉）に触れたら“開く”：画像差し替え＆衝突OFF → ついでに保存
        door_opened = False
        for br in border_blocks:
            if br.get("door_state") == "closed" and player_rect.colliderect(br["rect"]):
                br["door_state"] = "open"
                br["img"] = "open_door.png"
                br["collidable"] = False
                br["hp"] = br["max_hp"] = 0
                door_opened = True
        if door_opened:
            try:
                save_game_data()
            except Exception:
                pass


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

        # 敵の移動と衝突判定（ブロックにも当たる）
        for enemy in enemies:
            # --- スリープ／ウェイク判定（最初にやる） ---
            cx_enemy, cy_enemy = enemy_center(enemy)

            if enemy.get('sleep'):
                # 眠っている → 起床条件を満たすまで完全スキップ（座標維持）
                if not enemy_should_wake(cx_enemy, cy_enemy):
                    # 位置・描画・HPバーは draw 側でそのまま出る（座標は固定）
                    enemy['prev_cx'] = enemy['rect'].centerx
                    enemy['prev_cy'] = enemy['rect'].centery
                    continue
                else:
                    # 起こす
                    wake_enemy(enemy)
            else:
                # 起きている → 眠る条件ならこのフレームは何もせず眠る
                if enemy_should_sleep(cx_enemy, cy_enemy):
                    sleep_enemy(enemy)
                    enemy['prev_cx'] = enemy['rect'].centerx
                    enemy['prev_cy'] = enemy['rect'].centery
                    continue

            # 直前中心位置（レーザー掃引やノックバック等で使う）
            enemy['prev_cx'] = enemy['rect'].centerx
            enemy['prev_cy'] = enemy['rect'].centery

            # 追尾ベクトル（enemy['x'],['y'] は左上基準）
            ex_prev, ey_prev = enemy['x'], enemy['y']
            cx_enemy = ex_prev + enemy['rect'].w * 0.5
            cy_enemy = ey_prev + enemy['rect'].h * 0.5

            dx_enemy = player_x - cx_enemy
            dy_enemy = player_y - cy_enemy
            dist = math.hypot(dx_enemy, dy_enemy)
            if dist > 0:
                step_x = (dx_enemy / dist) * enemy_speed * game_speed
                step_y = (dy_enemy / dist) * enemy_speed * game_speed
            else:
                step_x = step_y = 0.0

            # --- X軸移動の衝突 ---
            nx = ex_prev + step_x
            test_rect_x = pygame.Rect(int(nx), int(ey_prev), enemy['rect'].w, enemy['rect'].h)
            hit_block = False
            hit_block_br = None
            for br in border_blocks:
                if not br.get("collidable", True):
                    continue
                if test_rect_x.colliderect(br["rect"]):
                    nx = ex_prev
                    hit_block = True
                    hit_block_br = br
                    break


            # 敵の --- Y軸移動の衝突 ---
            ny = ey_prev + step_y
            test_rect_y = pygame.Rect(int(nx), int(ny), enemy['rect'].w, enemy['rect'].h)
            for br in border_blocks:
                if not br.get("collidable", True):   # ★ これを追加
                    continue
                if test_rect_y.colliderect(br["rect"]):
                    ny = ey_prev
                    hit_block = True
                    hit_block_br = br
                    break

            # 確定
            enemy['x'], enemy['y'] = nx, ny
            enemy['rect'].x = int(nx)
            enemy['rect'].y = int(ny)

            # === ★ ブロックに当たっている場合の攻撃処理（1秒に1回） ===
            if hit_block and hit_block_br is not None:
                now = pygame.time.get_ticks()
                last_attack = enemy.get("last_block_attack", 0)
                if now - last_attack >= 2000:  # 2秒(2000ms)おき
                    enemy["last_block_attack"] = now
                    dmg = max(1, int(enemy.get('atk', 1)))  # その時の攻撃力を使用（保険で最低1）
                    hit_block_br["hp"] -= dmg

                    if hit_block_br["hp"] <= 0:
                        try:
                            border_blocks.remove(hit_block_br)
                        except ValueError:
                            pass
                        
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

            # ★既存の敵にも攻撃力を反映したい場合（任意）
            for e in enemies:
                e['atk'] *= 2

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
                    save_game_data()
                    base_world_x = 0
                    base_world_y = 0
                    enter_base_from_game()  
                    game_over = False
        # Game Over画面はここで1フレーム終わり。ループ継続。
        # 画面更新
        pygame.display.flip()
        continue

pygame.quit()