import pygame, sys, os, random
from player import Player
from enemy import spawn_enemy
from utils import load_highscore, save_highscore

# ---------- Init ----------
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("[WARN] Mixer init failed:", e)

WIDTH, HEIGHT = 800, 450
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battery Blaster")
CLOCK = pygame.time.Clock()
FPS = 60
FONT = pygame.font.SysFont("Arial", 24)

# ---------- Assets ----------
BG_IMG = None
bg_path = os.path.join("assets", "bg", "layer1.png")
if os.path.exists(bg_path):
    BG_IMG = pygame.image.load(bg_path).convert()
    BG_IMG = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))

# Sounds
def try_load_sound(p):
    try:
        return pygame.mixer.Sound(p) if os.path.exists(p) else None
    except:
        return None

JUMP_SFX    = try_load_sound(os.path.join("assets", "sounds", "jump.wav"))
BATTERY_SFX = try_load_sound(os.path.join("assets", "sounds", "battery.wav"))
FIRE_SFX    = try_load_sound(os.path.join("assets", "sounds", "fire.wav"))

# Music (optional)
music_path = os.path.join("assets", "sounds", "bg_music.mp3")
if os.path.exists(music_path):
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("[MUSIC] failed:", e)

# ---------- Gameplay constants ----------
MAX_CHARGE = 3

# ---------- Projectile class ----------
class Projectile:
    def __init__(self, x, y, direction=1):
        self.image = pygame.Surface((12, 4), pygame.SRCALPHA)
        self.image.fill((255, 220, 60))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12 * direction

    def update(self):
        self.rect.x += self.speed
        return 0 < self.rect.right and self.rect.left < WIDTH

    def draw(self, surf):
        surf.blit(self.image, self.rect)

# ---------- Battery (uses UI folder) ----------
class Battery:
    def __init__(self, x, y):
        img_path = os.path.join("assets", "ui", "battery.png")   # <--- uses assets/ui
        if os.path.exists(img_path):
            self.image = pygame.image.load(img_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (28, 28))
        else:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            self.image.fill((0, 200, 255))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 4

    def update(self):
        self.rect.x -= self.speed
        return self.rect.right > 0

    def draw(self, surf):
        surf.blit(self.image, self.rect)

# ---------- Particles ----------
particles = []
def add_particles(x, y, color=(255, 255, 0)):
    for _ in range(6):
        particles.append([x, y,
                          random.randint(-3, 3),
                          random.randint(-3, 3),
                          random.randint(3, 6),
                          color])

def update_particles():
    global particles
    out = []
    for p in particles:
        p[0] += p[2]; p[1] += p[3]
        p[4] -= 0.15
        if p[4] > 0:
            out.append(p)
    particles = out[-300:]

def draw_particles(surf):
    for p in particles:
        pygame.draw.circle(surf, p[5], (int(p[0]), int(p[1])), max(1, int(p[4])))

# ---------- Main loop ----------
def main():
    clock = CLOCK
    run = True

    player = Player(100, 300, max_charge=MAX_CHARGE)
    enemies = []
    projectiles = []
    batteries = []

    enemy_timer = 0
    battery_timer = 0
    score = 0
    highscore = load_highscore()

    menu = True
    game_over = False

    while run:
        dt = clock.tick(FPS)

        # ----- MENU -----
        if menu:
            if BG_IMG:
                WIN.blit(BG_IMG, (0, 0))
            else:
                WIN.fill((10, 10, 30))
            title = FONT.render("Battery Blaster ⚡", True, (255, 255, 0))
            press = FONT.render("Press SPACE to Start", True, (255, 255, 255))
            WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
            WIN.blit(press, (WIDTH // 2 - press.get_width() // 2, 200))
            update_particles()
            draw_particles(WIN)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    menu = False
            continue

        # ----- EVENTS -----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if player.jump_count < 2:
                        player.jump()
                        if JUMP_SFX: JUMP_SFX.play()
                elif event.key == pygame.K_SPACE:
                    # shoot only if player has charge
                    if player.use_charge(1):
                        # projectile spawns from player's center and goes direction
                        direction = 1 if player.facing_right else -1
                        px = player.x + player.w//2 + (10 * direction)
                        py = player.y + player.h//2
                        projectiles.append(Projectile(px, py, direction))
                        if FIRE_SFX: FIRE_SFX.play()

        keys = pygame.key.get_pressed()

        # ----- SPAWN -----
        enemy_timer += 1
        if enemy_timer > max(50, 100 - score//5):
            enemies.append(spawn_enemy(WIDTH, HEIGHT))
            enemy_timer = 0

        battery_timer += 1
        if battery_timer > 180:
            by = random.randint(180, 300)
            batteries.append(Battery(WIDTH + 20, by))
            battery_timer = 0

        # ----- UPDATE -----
        player.update(keys)

        for e in enemies[:]:
            e.update()
            if e.rect.right < 0:
                enemies.remove(e)
                score += 1

        for p in projectiles[:]:
            if not p.update():
                projectiles.remove(p)

        for b in batteries[:]:
            if not b.update():
                batteries.remove(b)

        # Collisions: projectile vs enemy
        for e in enemies[:]:
            for p in projectiles[:]:
                if e.rect.colliderect(p.rect):
                    add_particles(e.x + e.w//2, e.y + e.h//2, (255, 60, 60))
                    try:
                        enemies.remove(e)
                        projectiles.remove(p)
                    except ValueError:
                        pass
                    score += 10
                    break

        # Collisions: player vs battery
        for b in batteries[:]:
            if player.rect.colliderect(b.rect):
                batteries.remove(b)
                player.add_charge()
                if BATTERY_SFX: BATTERY_SFX.play()

        # Collisions: player vs enemy
        for e in enemies[:]:
            if player.rect.colliderect(e.rect):
                # remove enemy on contact
                try:
                    enemies.remove(e)
                except ValueError:
                    pass
                player.take_damage()
                add_particles(player.x + player.w//2, player.y + player.h//2, (255, 80, 80))
                if player.is_dead():
                    game_over = True

        # ----- DRAW -----
        if BG_IMG:
            WIN.blit(BG_IMG, (0, 0))
        else:
            WIN.fill((10, 10, 30))

        for e in enemies:
            e.draw(WIN)
        for b in batteries:
            b.draw(WIN)
        for p in projectiles:
            p.draw(WIN)
        player.draw(WIN)

        # HUD
        player.draw_health(WIN, WIDTH)
        player.draw_battery(WIN)

        score_txt  = FONT.render(f"Score: {score}", True, (255, 255, 255))
        high_txt   = FONT.render(f"High: {highscore}", True, (180, 180, 180))
        WIN.blit(score_txt, (10, HEIGHT - 60))
        WIN.blit(high_txt, (10, HEIGHT - 30))

        update_particles()
        draw_particles(WIN)

        if game_over:
            over = FONT.render("GAME OVER! Press R to Restart", True, (255, 60, 60))
            WIN.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 10))
            pygame.display.update()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                if score > highscore:
                    save_highscore(score)
                    highscore = score
                return main()
            continue

        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
