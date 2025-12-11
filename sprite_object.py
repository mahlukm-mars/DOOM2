import pygame as pg
from settings import *
import os
from collections import deque

class SpriteObject:
    def __init__(self, game, path = 'resources/sprites/static_sprites/candlebra.bmp', pos=(10.5, 3.5), scale=0.7, shift=0.27):
        self.game = game
        self.player = game.player
        self.x, self.y = pos
        self.image = pg.image.load(path).convert_alpha()
        self.IMAGE_WIDTH = self.image.get_width()
        self.HALF_WIDTH = self.image.get_width() // 2
        self.IMAGE_RATIO = self.IMAGE_WIDTH / self.image.get_height()
        self.dx, self.dy, self.theta, self.screen_x, self.distance, self.norm_distance = 0, 0, 0, 0, 1, 1   
        self.sprite_half_width = 0
        self.SPRITE_SCALE = scale
        self.SPRITE_HEIGHT_SHIFT = shift

    def get_sprite_projection(self):
        proj = SCREEN_DIST / self.norm_distance * self.SPRITE_SCALE
        proj_width, proj_height = proj * self.IMAGE_RATIO, proj

        image = pg.transform.scale(self.image, (proj_width, proj_height))

        self.sprite_half_width = proj_width // 2
        height_shift = proj_height * self.SPRITE_HEIGHT_SHIFT
        pos = self.screen_x - self.sprite_half_width, HALF_HEIGHT - proj_height // 2 + height_shift

        self.game.raycasting.objects_to_render.append((self.norm_distance, image, pos))

    def get_sprite(self):
        dx = self.x - self.player.x
        dy = self.y - self.player.y
        self.dx, self.dy = dx, dy
        self.theta = math.atan2(dy, dx)

        delta = self.theta - self.player.angle
        if (dx > 0 and self.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (NUM_RAYS // 2 + delta_rays) * SCALE

        self.distance = math.hypot(dx, dy)
        self.norm_distance = self.distance * math.cos(delta)
        if -self.HALF_WIDTH < self.screen_x < (WIDTH + self.HALF_WIDTH) and self.norm_distance > 0.5:
            self.get_sprite_projection()

    def update(self):
        self.get_sprite()

class AnimatedSprite(SpriteObject):
    def __init__(self, game, path='resources/sprites/animated_sprites/green_light/0.bmp', pos=(11.5, 3.5), scale=0.8, shift=0.15, animeted_time=120):
        super().__init__(game, path, pos, scale, shift)
        self.animeted_time = animeted_time
        self.path = path.rsplit('/', 1)[0]
        self.images = self.get_images(self.path)
        self.animeted_time_prev = pg.time.get_ticks()
        self.animated_trigger = False

    def update(self):
        super().update()
        self.check_animation_time()
        self.animate(self.images)

    def animate(self, images):
        if self.animated_trigger:
            images.rotate(-1)
            self.image = images[0]

    def check_animation_time(self):
        self.animated_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animeted_time_prev > self.animeted_time:
            self.animeted_time_prev = time_now
            self.animated_trigger = True

    def get_images(self, path):
        images = deque()
        # Sort files to ensure correct order (0.bmp, 1.bmp, 2.bmp, etc)
        for file_name in sorted(os.listdir(path)):
            if not file_name.endswith('.bmp') and not file_name.endswith('.png'):
                continue
            if os.path.isfile(os.path.join(path, file_name)):
                img = pg.image.load(os.path.join(path, file_name)).convert_alpha()
                images.append(img)
        return images