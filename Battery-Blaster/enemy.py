import pygame
import random
import os

EN_DIR = os.path.join("assets", "sprites", "enemies")

class Enemy:
    def __init__(self, x, y, speed=4):
        self.x = x
        self.y = y
        self.w = 48
        self.h = 48
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

        self.frames = []
        self.frame_idx = 0
        self.frame_timer = 0
        self.frame_rate = 8

        self.load_assets()

    def load_assets(self):
        if os.path.isdir(EN_DIR):
            files = sorted([f for f in os.listdir(EN_DIR) if f.endswith((".png", ".webp"))])
            for f in files:
                try:
                    img = pygame.image.load(os.path.join(EN_DIR, f)).convert_alpha()
                    img = pygame.transform.scale(img, (self.w, self.h))
                    self.frames.append(img)
                except Exception as e:
                    print("Enemy load error:", f, e)
        if not self.frames:
            surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            surf.fill((200, 50, 50))
            self.frames.append(surf)

    def update(self):
        self.x -= self.speed
        self.rect.topleft = (self.x, self.y)
        self.frame_timer += 1
        if self.frame_timer >= self.frame_rate:
            self.frame_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

    def draw(self, surf):
        surf.blit(self.frames[self.frame_idx], (self.x, self.y))

def spawn_enemy(width, height):
    y = random.randint(260, 320)  # near ground
    x = width + 50
    speed = random.uniform(3.5, 6.0)
    return Enemy(x, y, speed)
