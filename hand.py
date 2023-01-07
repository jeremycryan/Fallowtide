import pygame

from card import Card
import constants as c


class Deck:
    def __init__(self):
        self.cards = []


class Hand(Deck):
    def __init__(self, draw_from, frame):
        super().__init__()
        self.deck = draw_from

        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0)), orientation=c.UP))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0), (-1, 0), (1, 1), (0, 1), (-1, 1)), orientation=c.UP))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0)), orientation=c.UP))
        self.cards.append(Card(c.WHEAT, shape=((0, 0), (1, 0)), orientation=c.UP))

        self.shade = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        self.shade.fill((0, 0, 0))
        self.shade_alpha = 0

        self.frame = frame

        for card in self.cards:
            card.hand = self

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

    def selected_card(self):
        for card in self.cards:
            if card.selected:
                return card
        return None

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
            if hovered and not found:
                card.start_hover()
                found = True
            else:
                card.stop_hover()

    def update_targets(self, dt, events):
        total = len(self.cards)
        x0 = c.WINDOW_WIDTH//2 - (total - 1) * c.CARD_WIDTH//2 - (total-2) * c.CARD_SPACING
        for i, card in enumerate(self.cards):
            card.target_x = x0
            x0 += c.CARD_WIDTH + c.CARD_SPACING