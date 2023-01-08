import sys

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


class WinFrame:
    def __init__(self, game):
        self.game = game
        self.done = False
        pygame.mixer.music.fadeout(1000)

    def load(self):
        self.surf = ImageManager.load("assets/images/win.png")
        self.age = 0
        self.pre_age = 0
        self.music_playing = False


    def update(self, dt, events):
        self.pre_age += dt
        if self.pre_age > 4:
            self.age += dt
            if not self.music_playing:
                self.music_playing = True
                pygame.mixer.music.load("assets/sounds/end_music.ogg")
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.5)

            if self.age > 2:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            pygame.quit()
                            sys.exit()

    def draw(self, surface, offset=(0, 0)):
        self.surf.set_alpha(min(255, self.age * 500))
        surface.fill((0, 0, 0))
        surface.blit(self.surf, (0, 0))
        if self.age > 2:
            if self.age % 1 < 0.5:
                enter = ImageManager.load("assets/images/enter_to_close.png")
                surface.blit(enter, (c.WINDOW_WIDTH//2 - enter.get_width()//2, c.WINDOW_HEIGHT - enter.get_height()))

    def next_frame(self):
        return GameFrame(self.game)


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

        self.music = pygame.mixer.music.load("assets/sounds/music.ogg")
        pygame.mixer.music.play(-1)

        self.payment_sound = pygame.mixer.Sound("assets/sounds/payment.ogg")
        self.paper_sound = pygame.mixer.Sound("assets/sounds/paper.ogg")
        self.paper_sound.set_volume(0.4)

        self.cant = pygame.mixer.Sound("assets/sounds/cant.ogg")
        self.cant.set_volume(0.25)

        self.has_said_compost_hint = False

        self.skulls = 0
        self.doomshade = pygame.Surface(c.WINDOW_SIZE)
        self.end_shade = pygame.Surface(c.WINDOW_SIZE)
        self.end_shade.fill((0, 0, 0))
        self.ending = False
        self.end_shade_alpha = 0
        self.next_frame_obj = None


    def make_sacrifice(self):
        if self.skulls == 0:
            self.doctor.add_dialog([
                "The ritual has begun. Rejoice, for you are among the worthy few!",
                "Our blood will water the great tree of the new beginning.",
                "|Seven are needed, and from our sacrifice the old seven will rise again.",
                "Life from death, death from life.",
                "|Finish |what |you |started, |Stranger.",
            ])
        self.skulls += 1

        if self.skulls >= 7:
            self.fadeout()

    def fadeout(self):
        self.ending = True
        pygame.mixer.music.fadeout(1000)



    def shake(self, amp=15):
        self.since_shake = 0
        self.shake_amp = amp

    def update(self, dt, events):
        if self.ending:
            self.end_shade_alpha += dt * 255
            if self.end_shade_alpha >= 255:
                self.done = True
                self.end_shade_alpha = 255
                self.next_frame_obj = WinFrame(self.game)

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
            self.payment_sound.play()

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
        if self.moon >= 3 and not self.doctor.lines and not self.has_said_compost_hint:
            self.has_said_compost_hint = True
            self.doctor.add_dialog([
                "Hail, stranger.",
                "You may have noticed already, but there is a |composter available near your plot. It might look closer to a wood chipper or meat grinder. Don't worry about that.",
                "Placing |crop |cards in the composter will give you |mulch, which can restore depleted soil.",
                "It may also be necessary to compost crops that you are unable to fit on your land for the season.",
                "Life from death, death from life."
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
        self.composter.draw(surface, offset)

        if self.skulls > 0:
            r = 255
            g = max(0, 255 - 24*self.skulls)
            b = max(0, 255 - 24*self.skulls)
            self.doomshade.fill((r, g, b))
            surface.blit(self.doomshade, (0, 0), special_flags=pygame.BLEND_MULT)

        self.cash_display.draw(surface, offset=(0, 0))
        self.store.draw(surface, offset=(offset))

        self.doctor.draw(surface, (0, 0))

        if self.ending:
            self.end_shade.set_alpha(self.end_shade_alpha)
            surface.blit(self.end_shade, (0, 0))

    def next_frame(self):
        return self.next_frame_obj