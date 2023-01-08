##!/usr/bin/env python3
from image_manager import ImageManager
from primitives import GameObject, Pose
import pygame
import random
import constants as c


class Particle():
    def __init__(self):
        self.age = 0
        self.duration = None
        self.dead = False

    def get_alpha(self):
        return 255

    def get_scale(self):
        return 1

    def through(self, loading=1):
        """ Increase loading argument to 'frontload' the animation. """
        if self.duration is None:
            return 0
        else:
            return 1 - (1 - self.age / self.duration)**loading

    def update(self, dt, events):
        self.age += dt
        if self.duration and self.age > self.duration:
            self.destroy()

    def destroy(self):
        self.dead = True


class CardParticle(Particle):
    def __init__(self, position, direction):
        super().__init__()
        self.duration = 1.25
        self.position = Pose(position, 0)
        direction = Pose(direction, 0)
        self.velocity = direction.copy()
        self.velocity += Pose((random.random() * 25, random.random() * 25), 0)
        self.velocity *= random.random() * 2 + 2
        self.velocity.angle = random.random() * 1000 - 500
        self.surf = ImageManager.load("assets/images/tripart.png")
        self.base_scale = 1.25 - random.random() * 0.5
        self.age += random.random() * self.duration * 0.5


    def get_alpha(self):
        return 255 - 255*self.through(2)

    def get_scale(self):
        return self.base_scale * (1 - 0.5 * self.through())

    def update(self, dt, events):
        super().update(dt, events)
        self.position += self.velocity * dt
        self.velocity *= 0.1**dt

    def draw(self, surface, offset=(0, 0)):
        my_surf = pygame.transform.rotate(self.surf, angle=self.position.angle)
        my_surf = pygame.transform.scale(my_surf, (my_surf.get_width() * self.get_scale(), my_surf.get_height() * self.get_scale()))
        my_surf.set_alpha(self.get_alpha())
        x = offset[0] - my_surf.get_width()//2 + self.position.x
        y = offset[1] - my_surf.get_height()//2 + self.position.y
        surface.blit(my_surf, (x, y))



class RectParticle(Particle):
    def __init__(self, position):
        super().__init__()
        self.duration = 0.4
        self.position = Pose(position, 0)
        self.surf = pygame.Surface((c.CARD_WIDTH, c.CARD_HEIGHT))
        self.surf.fill((255, 255, 255))


    def get_alpha(self):
        return 255 - 255*self.through(2)

    def get_scale(self):
        return 1 + 0.75 * self.through(2)

    def update(self, dt, events):
        super().update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        my_surf = pygame.transform.scale(self.surf, (self.surf.get_width() * self.get_scale(), self.surf.get_height() * self.get_scale()))
        my_surf.set_alpha(self.get_alpha())
        x = offset[0] - my_surf.get_width()//2 + self.position.x
        y = offset[1] - my_surf.get_height()//2 + self.position.y
        surface.blit(my_surf, (x, y))


class MulchParticle(Particle):

    def __init__(self, tile):
        super().__init__()
        self.duration = 1
        self.position = Pose((0, 0), 0)
        self.surf = ImageManager.load_copy("assets/images/large_tripart.png")
        self.filter = self.surf.copy()
        self.filter.fill((255, 255, 255))
        if tile.orientation == c.DOWN:
            self.surf = pygame.transform.flip(self.surf, False, True)

    def get_alpha(self):
        return 255 - 255 * self.through(2)

    def get_color(self):
        r = 255 - 255 * self.through(2)
        g = 255
        b = 255 - 150 * self.through(2)
        return r, g, b

    def draw(self, surface, offset=(0, 0)):
        my_surf = pygame.transform.scale(self.surf, (self.surf.get_width() * self.get_scale(), self.surf.get_height() * self.get_scale()))
        my_surf.set_alpha(self.get_alpha())
        self.filter.fill(self.get_color())
        my_surf.blit(self.filter, (0, 0), special_flags=pygame.BLEND_MULT)
        x = offset[0] - my_surf.get_width()//2 + self.position.x
        y = offset[1] - my_surf.get_height()//2 + self.position.y
        surface.blit(my_surf, (x, y))


class BloodParticle(Particle):

    def __init__(self, tile, delay=0):
        super().__init__()
        self.age = -delay
        self.duration = 2
        self.position = Pose((0, 0), 0)
        self.surf = ImageManager.load_copy("assets/images/blood_rune.png")
        self.filter = self.surf.copy()
        self.filter.fill((255, 255, 255))
        if tile.orientation == c.DOWN:
            self.surf = pygame.transform.flip(self.surf, False, True)
        self.tile = tile

    def get_alpha(self):
        return min(255 - 255 * self.through(), self.through()*800)

    def get_color(self):
        if self.age < 0:
            return (255, 150, 150)
        r = 255
        g = 128 - 128 * self.through(2)
        b = 128 - 128 * self.through(2)
        return r, g, b

    def draw(self, surface, offset=(0, 0)):
        my_surf = pygame.transform.scale(self.surf, (self.surf.get_width() * self.get_scale(), self.surf.get_height() * self.get_scale()))
        self.filter.fill(self.get_color())
        my_surf.blit(self.filter, (0, 0), special_flags=pygame.BLEND_MULT)
        my_surf.set_alpha(self.get_alpha())
        x = offset[0] - my_surf.get_width()//2 + self.position.x
        y = offset[1] - my_surf.get_height()//2 + self.position.y
        surface.blit(my_surf, (x, y))

    def update(self, dt, events):
        super().update(dt, events)
        if self.through() > 0.15:
            self.tile.state = c.HEALTHY