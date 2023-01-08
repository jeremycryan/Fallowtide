import random

from card import Card
from image_manager import ImageManager
from particle import CardParticle, RectParticle
from primitives import Pose
import constants as c
import pygame
import math


class Composter:
    def __init__(self, frame):
        self.surf = ImageManager.load("assets/images/compost.png")
        self.highlight_surf = ImageManager.load("assets/images/compost_highlight.png")

        self.position = Pose((c.WINDOW_WIDTH - 250, 200), 0)
        self.frame = frame

        self.squish_amp = 0
        self.since_squish = 999

        self.brrrr = pygame.mixer.Sound("assets/sounds/grinder.ogg")

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_hovered() and self.frame.hand.selected_card():
                    self.compost(self.frame.hand.selected_card())
        pass
        self.since_squish += dt
        self.squish_amp *= 0.03**dt
        self.squish_amp -= 0.5*dt
        if self.squish_amp < 0:
            self.squish_amp = 0

    def compost(self, card):
        if card in self.frame.hand.cards:
            self.frame.hand.cards.remove(card)
            if card.crop in c.COMPOSTS_TO or card.crop == c.CULTIST:
                self.frame.discard.cards.append(card)

        selected = card
        for i in range(120):
            x = selected.x + random.random() * c.CARD_WIDTH - c.CARD_WIDTH//2
            y = selected.get_apparent_position()[1] + random.random() * c.CARD_HEIGHT - c.CARD_HEIGHT//2
            self.frame.hand.particles.append(CardParticle((x, y), (x - selected.x, y - selected.get_apparent_position()[1])))
        self.frame.hand.particles.append(RectParticle((selected.get_apparent_position())))

        self.frame.shake(10)
        self.blorp()
        self.brrrr.play()

        if card.crop == c.CULTIST:
            self.frame.make_sacrifice()

        if not card.crop in c.COMPOSTS_TO:
            return
        new_type = c.COMPOSTS_TO[card.crop]
        new_card = Card(new_type, shape=((0, 0),), orientation=c.EITHER)
        self.frame.hand.cards.append(new_card)
        new_card.hand = self.frame.hand


        pass

    def blorp(self):
        self.since_squish = 0
        self.squish_amp = 0.2

    def get_y_scale(self):
        scale = 1 + math.cos(self.since_squish * 25) * self.squish_amp
        return scale

    def draw(self, surface, offset=(0, 0)):

        surf_to_use = self.surf if (not self.is_hovered() or not self.frame.hand.selected_card()) else self.highlight_surf
        squish_surf = pygame.transform.scale(surf_to_use, (int(surf_to_use.get_width()/self.get_y_scale()), int(surf_to_use.get_height()*self.get_y_scale())))
        x = offset[0] + self.position.x - squish_surf.get_width()//2
        y = offset[1] + self.position.y - squish_surf.get_height()//2
        surface.blit(squish_surf, (x, y))
        pass

    def is_hovered(self):
        mpos = Pose(pygame.mouse.get_pos(), 0)
        diff = mpos - self.position
        if abs(diff.x) < self.surf.get_width()//2 and abs(diff.y) < self.surf.get_height()//2:
            return True
        return False