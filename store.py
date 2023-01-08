import random

import pygame

from card import Card
from image_manager import ImageManager
from particle import RectParticle, CardParticle
from primitives import Pose
import constants as c

import math
import time


class Store:

    def __init__(self, frame):
        self.frame = frame
        self.extended = 0
        self.position = self.get_position()
        self.target = c.UP
        self.background = ImageManager.load("assets/images/shop_background.png")
        self.title_font = pygame.font.Font("assets/fonts/matura.ttf", 75)
        self.subtitle_font = pygame.font.Font("assets/fonts/alagard.ttf", 35)
        self.buy_for_font = pygame.font.Font("assets/fonts/alagard.ttf", 24)
        self.cost_font = pygame.font.Font("assets/fonts/alagard.ttf", 35)
        self.card_highlight = ImageManager.load("assets/images/card_highlight.png")

        self.mode = c.BUY

        self.cards = []
        self.costs = []

        self.particles = []

        self.card_shade = pygame.Surface((c.CARD_WIDTH, c.CARD_HEIGHT))
        self.card_shade.fill((0, 0, 0))
        self.card_shade.set_alpha(164)

        self.store_has_appeared = False
        self.destroy_screen_has_appeared = False

    def add_cards_for_sale(self):
        for i in range(3):
            self.cards.append(self.get_shop_card())

    def get_cards_to_remove(self):
        for i in range(3):
            card = random.choice(self.frame.discard.cards + self.frame.deck.cards)
            while card in self.cards:
                card = random.choice(self.frame.discard.cards + self.frame.deck.cards)
            self.cards.append(card)

    def get_position(self):
        x = c.WINDOW_WIDTH//2
        y = c.WINDOW_HEIGHT//2 - c.WINDOW_HEIGHT * (1 - self.extended)**2
        return Pose((x, y), 0)

    def draw(self, surface, offset=(0, 0)):
        if self.extended == 0:
            for particle in self.particles:
                particle.draw(surface, (0, 0))
            return

        position = self.get_position()

        surface.blit(self.background, (position.x - c.WINDOW_WIDTH//2 + offset[0], position.y - c.WINDOW_HEIGHT//2 + offset[1]))

        # draw title
        title_text = "Buy a card" if self.mode == c.BUY else "Destroy a card"
        title = self.title_font.render(title_text, 1, (255, 255, 255))
        y = position.y - c.WINDOW_HEIGHT//4 - title.get_height()//2 + offset[1] - 70
        x = c.WINDOW_WIDTH//2 - title.get_width()//2 + offset[0]
        surface.blit(title, (x, y))

        # draw subtitle
        title_text = "New cards are added to your deck" if self.mode == c.BUY else "Trashed cards are gone forever"
        title = self.subtitle_font.render(title_text, 1, (255, 255, 255))
        y = position.y - c.WINDOW_HEIGHT//5 + 8 - title.get_height()//2 + offset[1] - 70
        x = c.WINDOW_WIDTH//2 - title.get_width()//2 + offset[0]
        surface.blit(title, (x, y))

        # draw cards
        for i, card in enumerate(self.cards):
            surf = card.get_surf(red=(self.mode == c.REMOVE))
            x = c.WINDOW_WIDTH//2 + 300 * (i-1) - surf.get_width()//2 + offset[0] + math.sin(time.time()*3 + i*1.5)*8
            y = -(i==1)*50 - surf.get_height()//2 + offset[1] + position.y + 100 + math.cos(time.time()*3 + i*1.5) * 8
            surface.blit(surf, (x, y))

            cost_color = 255, 255, 255
            if card.get_shop_cost() > self.frame.cash and self.mode == c.BUY:
                surface.blit(self.card_shade, (x, y))
                cost_color = 96, 96, 96
            else:
                if i == self.card_index_hovered():
                    surface.blit(self.card_highlight, (x-5, y-5))

            cost = card.get_shop_cost()
            cost_text = self.cost_font.render(f"{cost}", 1, (cost_color))
            currency_symbol = ImageManager.load("assets/images/coin3.png").copy()
            buy_for_text = "Buy for" if self.mode == c.BUY else "Trash this card"

            if self.mode == c.REMOVE:
                cost_color = cost_color[0], 50, 50
            buy_for = self.buy_for_font.render(buy_for_text, 1, (cost_color))
            if card.get_shop_cost() > self.frame.cash and self.mode == c.BUY:
                currency_symbol.blit(self.card_shade, (0, 0))

            x0 = c.WINDOW_WIDTH // 2 + 300 * (i - 1) + offset[0]
            y0 = -(i == 1) * 50 + offset[1] + position.y - 175

            x = x0 - buy_for.get_width()//2
            y = y0 - buy_for.get_height()//2
            if self.mode == c.REMOVE:
                y += 45
            surface.blit(buy_for, (x, y + 7))

            if self.mode == c.BUY:
                y0 += 40
                x = x0
                y = y0
                x -= (currency_symbol.get_width() + 5 + cost_text.get_width())//2
                surface.blit(currency_symbol, (x, y - currency_symbol.get_height()//2), special_flags=pygame.BLEND_ADD)
                x += currency_symbol.get_width() + 5
                surface.blit(cost_text, (x, y-cost_text.get_height()//2))

        pass

        # draw skip button
        if self.mode == c.BUY:
            button = ImageManager.load("assets/images/next_season.png")
            button_hover = ImageManager.load("assets/images/next_season_hover.png")

            x = c.WINDOW_WIDTH//2 + 600 - button.get_width()
            y = c.WINDOW_HEIGHT * 1//3 + 115 - button.get_height() + position.y
            to_draw = button
            if self.next_season_hovered():
                to_draw = button_hover
            surface.blit(to_draw, (x - button.get_width()//2, y - button.get_height()//2), special_flags=pygame.BLEND_ADD)

        for particle in self.particles:
            particle.draw(surface, (0, 0))

    def next_season_hovered(self):
        position = self.get_position()
        if self.mode == c.BUY:
            button = ImageManager.load("assets/images/next_season.png")
            x = c.WINDOW_WIDTH//2 + 600 - button.get_width()
            y = c.WINDOW_HEIGHT * 1//3 + 115 - button.get_height() + position.y
            mpos = pygame.mouse.get_pos()
            if mpos[0] > x - button.get_width()//2 and mpos[0] < x + button.get_width()//2 and mpos[1] > y - button.get_height()//2 and mpos[1] < y + button.get_height()//2:
                return True

    def card_position_from_index(self, idx):
        position = self.get_position()
        for i, card in enumerate(self.cards):
            x = c.WINDOW_WIDTH//2 + 300 * (i-1) + math.sin(time.time()*3 + i*1.5)*8
            y = -(i==1)*50+ position.y + 50 + math.cos(time.time()*3 + i*1.5) * 8

            if i == idx:
                return x, y

    def card_index_hovered(self):
        if not self.cards:
            return None
        position = self.get_position()
        for i, card in enumerate(self.cards):
            surf = card.get_surf()
            x = c.WINDOW_WIDTH//2 + 300 * (i-1) - surf.get_width()//2 + math.sin(time.time()*3 + i*1.5)*8
            y = -(i==1)*50 - surf.get_height()//2 + position.y + 50 + math.cos(time.time()*3 + i*1.5) * 8

            mpos = pygame.mouse.get_pos()
            if mpos[0] > x and mpos[0] < x + c.CARD_WIDTH and mpos[1] > y and mpos[1] < y + c.CARD_HEIGHT:
                return i
        return None


    def get_shop_card(self):
        options = []

        multiplier = 1.6


        if self.frame.lifetime_cash < 2000 * multiplier:
            shape, orientation = random.choice(c.MEDIUM_SHAPES)
            options.append(Card(c.WHEAT, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 900  * multiplier and self.frame.lifetime_cash < 4000  * multiplier:
            shape, orientation = random.choice(c.LARGE_SHAPES)
            options.append(Card(c.WHEAT, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 1600  * multiplier and self.frame.lifetime_cash < 8000  * multiplier:
            shape, orientation = random.choice(c.SMALL_SHAPES)
            options.append(Card(c.FENNEL, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 3200  * multiplier and self.frame.lifetime_cash < 15000  * multiplier:
            shape, orientation = random.choice(c.MEDIUM_SHAPES)
            options.append(Card(c.FENNEL, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 6400  * multiplier and self.frame.lifetime_cash < 25000  * multiplier:
            shape, orientation = random.choice(c.LARGE_SHAPES)
            options.append(Card(c.FENNEL, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 9000  * multiplier and self.frame.lifetime_cash < 50000  * multiplier:
            shape, orientation = random.choice(c.SMALL_SHAPES)
            options.append(Card(c.FELLWEED, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 12000  * multiplier and self.frame.lifetime_cash < 100000  * multiplier:
            shape, orientation = random.choice(c.MEDIUM_SHAPES)
            options.append(Card(c.FELLWEED, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 24000 * multiplier:
            shape, orientation = random.choice(c.LARGE_SHAPES)
            options.append(Card(c.FELLWEED, shape=shape, orientation=orientation))

        if self.frame.lifetime_cash > 10000 * multiplier:
            options.append(Card(c.GOAT, shape=((0, 0),), orientation=c.EITHER))

        if not options:
            options.append(Card(c.WHEAT, shape=((0, 0),), orientation=c.UP))

        if self.frame.lifetime_cash > 30000 * multiplier:
            return Card(c.CULTIST, shape=((0, 0),), orientation=c.EITHER)

        new_card = random.choice(options)
        return new_card

    def lower(self):
        self.target = c.DOWN
        self.cards = []
        self.mode = c.BUY
        self.add_cards_for_sale()

        if not self.store_has_appeared:
            self.store_has_appeared = True
            self.frame.doctor.add_dialog([
                "Excellent harvest this month, stranger. You have been compensated accordingly.",
                "Every season, you will have the opportunity to spend your earnings on |better |crop |cards.",
                "More efficient planting, more profits for you. And more offerings for the residents of Fallowtide.",
                "|Choose |an |upgrade to add it to your deck, or save your gold for later if you prefer."
            ])

    def raise_up(self):
        self.target = c.UP

    def toggle(self):
        if self.target == c.UP:
            self.lower()
        else:
            self.raise_up()

    def update(self, dt, events):
        if self.extended < 1:
            doctor_extended = self.frame.doctor.showing
            extended = max(doctor_extended, self.extended)
            pygame.mixer.music.set_volume(1 - 0.85*extended)

        speed = 3
        if self.target == c.DOWN:
            self.extended += speed*dt
            if self.extended > 1:
                self.extended = 1
        else:
            self.extended -= speed*dt
            if self.extended < 0:
                self.extended = 0

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.frame.doctor.blocking():
                    continue
                if event.button == 1:
                    hovered = self.card_index_hovered()
                    if hovered != None:
                        self.click_card(hovered)
                    elif self.next_season_hovered() and self.mode == c.BUY:
                        self.frame.doctor.advance_sound.play()
                        self.frame.next_day()

        for particle in self.particles[:]:
            particle.update(dt, events)
            if particle.dead:
                self.particles.remove(particle)


    def click_card(self, idx):
        if self.mode == c.BUY:
            self.try_buy(idx)
        else:
            self.try_destroy(idx)

    def try_destroy(self, idx):
        if len(self.cards) <= idx:
            return

        card = self.cards[idx]
        if card in self.frame.discard.cards:
            self.frame.discard.cards.remove(card)
        elif card in self.frame.deck.cards:
            self.frame.deck.cards.remove(card)
        self.frame.shake(15)

        pos = self.card_position_from_index(idx)
        for i in range(120):
            x = pos[0] + random.random() * c.CARD_WIDTH - c.CARD_WIDTH//2
            y = pos[1] + random.random() * c.CARD_HEIGHT - c.CARD_HEIGHT//2
            self.particles.append(CardParticle((x, y), (x - pos[0], y - pos[1])))
        self.particles.append(RectParticle((pos)))

        self.frame.next_day()
        self.frame.paper_sound.play()

    def try_buy(self, idx):
        if len(self.cards) <= idx:
            return

        card = self.cards[idx]
        if self.frame.cash < card.get_shop_cost():
            self.frame.shake(8)
            self.frame.cant.play()
            return

        self.frame.paper_sound.play()
        self.frame.cash -= card.get_shop_cost()
        self.frame.discard.cards.append(card)
        self.cards = []
        self.mode = c.REMOVE
        self.get_cards_to_remove()
        self.frame.shake(15)

        pos = self.card_position_from_index(idx)
        for i in range(120):
            x = pos[0] + random.random() * c.CARD_WIDTH - c.CARD_WIDTH//2
            y = pos[1] + random.random() * c.CARD_HEIGHT - c.CARD_HEIGHT//2
            self.particles.append(CardParticle((x, y), (x - pos[0], y - pos[1])))
        self.particles.append(RectParticle((pos)))
        if not self.destroy_screen_has_appeared:
            self.destroy_screen_has_appeared = True
            self.frame.doctor.add_dialog([
                "Every time you purchase a new crop, you have a chance to destroy an old one.",
                "Just like in the larger world, death brings new life, and life death.",
                "Select a card here to |permanently |remove |it |from |your |deck.",
            ])
