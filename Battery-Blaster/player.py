import pygame
import os

ASSET_DIR = os.path.join("assets", "sprites", "player")
UI_DIR = os.path.join("assets", "ui")   # <-- your ui folder

class Player:
    def __init__(self, x, y, max_charge=3, max_health=3):
        self.x = x
        self.y = y
        self.w = 56
        self.h = 72
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

        # movement
        self.vel = 5
        self.jump_vel = -12
        self.gravity = 0.6
        self.vy = 0
        self.on_ground = True
        self.jump_count = 0
        self.facing_right = True

        # charge (battery system)
        self.charge = 0
        self.max_charge = max_charge

        # health system
        self.max_health = max_health
        self.health = max_health
        self.heart_full = None
        self.heart_empty = None
        self.heart_size = (32, 32)

        # animations
        self.anim = {"idle": [], "run": [], "jump": [], "attack": []}
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_rate = 6
        self.state = "idle"

        # pre-load UI images
        self._load_ui()
        self.load_assets()

    def _load_ui(self):
        try:
            full_path = os.path.join(UI_DIR, "heart_full.png")
            empty_path = os.path.join(UI_DIR, "heart_empty.png")
            battery_path = os.path.join(UI_DIR, "battery.png")

            if os.path.exists(full_path):
                img = pygame.image.load(full_path).convert_alpha()
                self.heart_full = pygame.transform.scale(img, self.heart_size)
            if os.path.exists(empty_path):
                img = pygame.image.load(empty_path).convert_alpha()
                self.heart_empty = pygame.transform.scale(img, self.heart_size)

            # load battery icon once
            if os.path.exists(battery_path):
                bimg = pygame.image.load(battery_path).convert_alpha()
                self.battery_img = pygame.transform.scale(bimg, (28, 28))
            else:
                self.battery_img = None
        except Exception as e:
            print("UI load error:", e)
            if not self.heart_full:
                surf = pygame.Surface(self.heart_size)
                surf.fill((255, 0, 0))
                self.heart_full = surf
            if not self.heart_empty:
                surf = pygame.Surface(self.heart_size)
                surf.fill((100, 100, 100))
                self.heart_empty = surf
            self.battery_img = None

    def load_assets(self):
        # load animations (if you have separate folders)
        for key in self.anim.keys():
            folder = os.path.join(ASSET_DIR, key)
            if os.path.isdir(folder):
                files = sorted([f for f in os.listdir(folder) if f.endswith((".png", ".webp"))])
                for f in files:
                    path = os.path.join(folder, f)
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.scale(img, (self.w, self.h))
                        self.anim[key].append(img)
                    except Exception as e:
                        print("Player sprite load error:", path, e)

        # fallback idle frame
        if not self.anim["idle"]:
            surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            surf.fill((0, 200, 200))
            self.anim["idle"].append(surf)

    def apply_gravity(self):
        if not self.on_ground:
            self.vy += self.gravity
            self.y += self.vy
            if self.y >= 300:
                self.y = 300
                self.vy = 0
                self.on_ground = True
                self.jump_count = 0

    def jump(self):
        if self.on_ground or self.jump_count < 2:
            self.vy = self.jump_vel
            self.on_ground = False
            self.jump_count += 1
            self.state = "jump"

    def update_state(self, moving):
        if not self.on_ground:
            self.state = "jump"
        else:
            self.state = "run" if moving else "idle"

    def update(self, keys):
        moving = False
        if keys[pygame.K_LEFT]:
            self.x -= self.vel
            self.facing_right = False
            moving = True
        if keys[pygame.K_RIGHT]:
            self.x += self.vel
            self.facing_right = True
            moving = True

        # clamp screen
        self.x = max(0, min(800 - self.w, self.x))

        self.update_state(moving)
        self.apply_gravity()
        self.rect.topleft = (self.x, self.y)

        # animation timer
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.frame_timer = 0
            if self.anim.get(self.state):
                self.frame_idx = (self.frame_idx + 1) % len(self.anim[self.state])

    def take_damage(self):
        """Call this when colliding with enemy"""
        if self.health > 0:
            self.health -= 1

    def is_dead(self):
        return self.health <= 0

    def add_charge(self):
        """Call this when collecting a battery"""
        if self.charge < self.max_charge:
            self.charge += 1

    def use_charge(self, amount=1):
        """Consume charge for shooting. Returns True if enough charge."""
        if self.charge >= amount:
            self.charge -= amount
            return True
        return False

    def draw_health(self, surf, width):
        # Draw hearts on top-right corner
        if self.heart_full and self.heart_empty:
            # draw from right to left
            padding = 12
            for i in range(self.max_health):
                img = self.heart_full if i < self.health else self.heart_empty
                x = width - (i + 1) * (self.heart_size[0] + padding) - 10
                y = 10
                surf.blit(img, (x, y))

    def draw_battery(self, surf):
        # Draw battery icons top-left
        if self.battery_img:
            for i in range(self.charge):
                x = 10 + i * (self.battery_img.get_width() + 6)
                y = 10
                surf.blit(self.battery_img, (x, y))
        else:
            # fallback small rects
            for i in range(self.charge):
                pygame.draw.rect(surf, (0, 200, 255), (10 + i*20, 10, 14, 14))

    def draw(self, surf):
        # draw player
        frames = self.anim.get(self.state)
        if frames:
            img = frames[self.frame_idx % len(frames)]
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            surf.blit(img, (self.x, self.y))
        else:
            pygame.draw.rect(surf, (0, 200, 200), (self.x, self.y, self.w, self.h))
