import pygame

from cash_display import CashDisplay
from composter import Composter
from doctor import Doctor
from field import Field
from hand import Deck, Hand
import math

from image_manager import ImageManager
import constants as c
from store import Store


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))

    def next_frame(self):
        return Frame(self.game)


class GameFrame(Frame):
    def __init__(self, game):
        super().__init__(game)

    def load(self):
        self.field = Field(self)
        self.deck = Deck()
        self.discard = Deck()
        self.discard.cards = []
        self.hand = Hand(self.deck, self)
        self.doctor = Doctor(self)

        self.shake_amp = 0
        self.since_shake = 999

        self.cash = 0
        self.lifetime_cash = 0
        self.cash_display = CashDisplay(self)
        self.moon = 0

        self.background = ImageManager.load("assets/images/background.png")

        self.composter = Composter(self)
        self.store = Store(self)



    def shake(self, amp=15):
        self.since_shake = 0
        self.shake_amp = amp

    def update(self, dt, events):
        self.since_shake += dt
        self.shake_amp *= 0.002**dt
        if self.shake_amp > 0:
            self.shake_amp -= 10*dt
            if self.shake_amp < 0:
                self.shake_amp = 0

        self.doctor.update(dt, events)

        self.composter.update(dt, events)

        self.hand.update(dt, events)
        self.field.update(dt, events)
        self.cash_display.update(dt, events)
        self.store.update(dt, events)

        if not self.hand.cards and self.store.target == c.UP:
            self.store.lower()
            self.field.collect_cash()

    def next_day(self):
        self.store.raise_up()
        self.hand.draw_from_deck(5)
        self.field.next_day()
        if self.moon == 1:
            self.doctor.add_dialog([
                "Ah! The soil, once rich and dark, has lost some of its vigor.",
                "It should be fine for now, but watch it keenly. Overusing one patch of soil may lessen its usefulness.",
                "To replenish the soil, simply |leave |it |fallow for a season. That is, don't grow any crops there.",
                "Our trust is in you, stranger. May you find smiles in the dark.",
            ])

    def add_shake(self, offset):
        y = offset[1] + self.shake_amp * math.cos(self.since_shake * 36)
        x = y * 0.1
        return x, y

    def draw(self, surface, offset=(0, 0)):

        offset = self.add_shake(offset)

        surface.blit(self.background, (c.WINDOW_WIDTH//2 - self.background.get_width()//2 + offset[0], c.WINDOW_HEIGHT//2 - self.background.get_height()//2 + offset[1]))

        self.field.draw(surface, offset)
        self.hand.draw(surface, offset)
        self.cash_display.draw(surface, offset=(0, 0))
        self.composter.draw(surface, offset)

        self.store.draw(surface, offset=(offset))

        self.doctor.draw(surface, (0, 0))

    def next_frame(self):
        return Frame(self.game)