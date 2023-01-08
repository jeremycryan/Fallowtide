import random

import pygame

from card import Card
import constants as c
from particle import CardParticle, RectParticle


class Deck:
    def __init__(self):
        self.cards = []

        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0)), orientation=c.UP))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0)), orientation=c.DOWN))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (0, -1)), orientation=c.DOWN))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0)), orientation=c.UP))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0)), orientation=c.DOWN))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (0, -1)), orientation=c.DOWN))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (0, -1), (1, 0), (-1, 0)), orientation=c.DOWN))
        self.cards.append(Card(c.WHEAT, shape=((1, 0), (0, 0), (0, -1), (1, -1)), orientation=c.DOWN))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0), (1, -1), (0, -1)), orientation=c.UP))
        # for i in range(3):
        #     self.cards.append(Card(c.MULCH, shape=((0, 0),), orientation=c.EITHER))
        # for i in range(3):
        #     self.cards.append(Card(c.BLOOD, shape=((0, 0),), orientation=c.EITHER))

        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)


class Hand():
    def __init__(self, draw_from, frame):
        self.cards = []

        self.has_played_card = False
        self.has_played_fennel = False
        self.deck = draw_from
        self.draw_from_deck(5)

        self.shade = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        self.shade.fill((0, 0, 0))
        self.shade_alpha = 0

        self.frame = frame

        self.particles = []

        self.plant_sound = pygame.mixer.Sound("assets/sounds/plant_sound.ogg")

        for card in self.cards:
            card.hand = self

    def draw_from_deck(self, amt=1):
        for i in range(amt):
            if not len(self.deck.cards):
                self.deck.cards = self.frame.discard.cards
                self.frame.discard.cards = []
                random.shuffle(self.deck.cards)
            new_card = self.deck.cards.pop()
            new_card.hand = self
            new_card.selected = False
            new_card.x = c.WINDOW_WIDTH + c.CARD_WIDTH//2
            self.cards.append(new_card)

    def draw(self, surface, offset=(0, 0)):
        selected_card = self.selected_card()
        for card in self.cards:
            if card is selected_card:
                continue
            card.draw(surface, offset)
        if self.shade_alpha > 0:
            self.shade.set_alpha(self.shade_alpha)
            surface.blit(self.shade, (0, 0))

        selected_card = self.selected_card()
        if selected_card is not None:
            self.frame.field.draw_shape_highlights(selected_card.shape, selected_card.orientation, surface, offset)

        for card in self.cards:
            if card.pulled > 1 or card is selected_card:
                card.draw(surface, offset)

        for particle in self.particles:
            particle.draw(surface, offset)

    def selected_card(self):
        for card in self.cards:
            if card.selected:
                return card
        return None

    def use_selected(self):
        selected = self.selected_card()
        if selected and selected in self.cards:
            self.cards.remove(selected)
            if selected.crop not in (c.MULCH, c.BLOOD):
                self.frame.discard.cards.append(selected)

        for i in range(120):
            x = selected.x + random.random() * c.CARD_WIDTH - c.CARD_WIDTH//2
            y = selected.get_apparent_position()[1] + random.random() * c.CARD_HEIGHT - c.CARD_HEIGHT//2
            self.particles.append(CardParticle((x, y), (x - selected.x, y - selected.get_apparent_position()[1])))
        self.particles.append(RectParticle((selected.get_apparent_position())))
        self.plant_sound.play()

        if not self.has_played_card:
            self.has_played_card = True
            self.frame.doctor.add_dialog([
                "Very good. The crops have already taken root.",
                "You have only limited space in this plot. Keep that in mind as you |place |your |remaining |crops.",
                "I sense this will be a very beneficial relationship for both of us. Farewell for now."
            ])
        if not self.has_played_fennel and selected.crop == c.FENNEL:
            self.has_played_fennel = True
            self.frame.doctor.add_dialog([
                "Ah, I see you have expanded to a new crop.",
                "|Fennel is quite prized by the residents of Fallowtide. Prepared correctly, it can ward against unfriendly demons and spirits.",
                "In other situations, it may invite them.",
                "Regardless, its value is considerable, and we will pay you handsomely for its cultivation.",
                "Farewell for now. May you dream of fire and warm things.",
            ])

    def update(self, dt, events):
        for card in self.cards:
            card.update(dt, events)
        self.update_targets(dt, events)

        if self.selected_card() is not None:
            if self.shade_alpha < 128:
                self.shade_alpha += 1200*dt
                if self.shade_alpha > 128:
                    self.shade_alpha = 128
        else:
            if self.shade_alpha > 0:
                self.shade_alpha -= 1600*dt
                if self.shade_alpha < 0:
                    self.shade_alpha = 0

        mx, my = pygame.mouse.get_pos()
        found = False
        for card in self.cards:
            cx, cy = card.get_apparent_position()
            dx = mx - cx
            dy = my - cy
            hovered = card.is_hovered(dx, dy)
            if hovered and not found and not self.frame.doctor.blocking():
                card.start_hover()
                found = True
            else:
                card.stop_hover()

        for particle in self.particles[:]:
            particle.update(dt, events)
            if particle.dead:
                self.particles.remove(particle)

    def update_targets(self, dt, events):
        total = len(self.cards)
        x0 = c.WINDOW_WIDTH//2 - (total - 1) * c.CARD_WIDTH//2 - (total-2) * c.CARD_SPACING
        for i, card in enumerate(self.cards):
            card.target_x = x0
            x0 += c.CARD_WIDTH + c.CARD_SPACING