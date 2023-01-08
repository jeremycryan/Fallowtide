import random
import time

import pygame

from image_manager import ImageManager
import constants as c

class Doctor:

    def __init__(self, frame):
        self.frame = frame

        self.showing = 0
        self.target = 1
        self.shade = pygame.Surface((c.WINDOW_SIZE))
        self.shade.fill((0, 0, 0))

        self.sounds = [
            pygame.mixer.Sound(f"assets/sounds/voice_{n}.ogg") for n in [1, 2, 3, 4, 5, 6, 7]
        ]
        for sound in self.sounds:
            sound.set_volume(0.15)
        self.advance_sound = pygame.mixer.Sound("assets/sounds/advance_dialog.wav")
        self.advance_sound.set_volume(0.05)

        self.lines = []
        self.since_start_line = 0
        self.since_blep = 999

        self.doctor_surf = ImageManager.load("assets/images/doctor.png")
        self.dialog_background = pygame.surface.Surface((c.WINDOW_WIDTH, 350))
        self.dialog_background.fill((0, 0, 0))

        self.name_surf = ImageManager.load("assets/images/doctor_name.png")

        self.dialog_font = pygame.font.Font("assets/fonts/segoeui.ttf", 30)
        self.letters = {letter: self.dialog_font.render(letter, 1, (255, 255, 255)) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.,?!|- "}
        self.red_letters = {letter: self.dialog_font.render(letter, 1, (255, 50, 50)) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.,?!|- "}

        self.lines = [
            "Welcome, stranger. May tomorrow's sky look down on you with merciful eyes.",
            "Per your contract, you will be tending to this small plot of land for the village of Fallowtide.",
            "The upcoming harvests of are immense importance to us. We have dozens of villagers. Livestock. Specific... traditions.",
            "All of them rely on the crops grown here. And of course, we will compensate you generously.",
            "To start, |select |a |crop and place it in an |open |area |of |soil.",
        ]

    def update(self, dt, events):
        self.since_start_line += dt
        self.since_blep += dt
        if self.blocking() and self.since_blep > 0.2 and not self.ready_for_next_line():
            self.since_blep = 0
            random.choice(self.sounds).play()
        if self.target > self.showing:
            self.showing += dt * 3
            if self.showing > self.target:
                self.showing = self.target
        elif self.target < self.showing:
            self.showing -= dt*5
            if self.showing < self.target:
                self.showing = self.target

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.target == 1 and self.ready_for_next_line():
                        self.next_line()

    def draw(self, surface, offset=(0, 0)):

        if self.showing == 0:
            return

        self.shade.set_alpha(128 * self.showing)
        surface.blit(self.shade, (0, 0))

        self.dialog_background.set_alpha(220 * self.showing)
        surface.blit(self.dialog_background, (0, c.WINDOW_HEIGHT - self.dialog_background.get_height()))

        x = 550
        y = 700
        self.name_surf.set_alpha(150 * self.showing)
        surface.blit(self.name_surf, (x, y))


        cps = c.CPS
        chars_showing = self.since_start_line * cps
        text = self.current_line()
        words = text.split() if text else []
        max_width = 900
        x0 = 550
        y0 = 800
        x = x0
        y = y0
        drawn = 0
        for word in words:
            width = sum([self.letters[letter].get_width() for letter in word])
            if x + width > x0 + max_width:
                x = x0
                y += 35
            red = False
            for letter in word:
                if letter == "|":
                    red = True
                    continue
                self.letters[letter].set_alpha(255 * self.showing)
                if not red:
                    surface.blit(self.letters[letter], (x, y))
                else:
                    surface.blit(self.red_letters[letter], (x, y))
                drawn += 1
                x += self.letters[letter].get_width()
                if drawn >= chars_showing:
                    break
            if drawn >= chars_showing:
                break
            x += self.letters[" "].get_width()
            drawn += 1

        surf = ImageManager.load("assets/images/click_to_continue.png")
        x = c.WINDOW_WIDTH//2 - surf.get_width()//2
        y = c.WINDOW_HEIGHT - surf.get_height() - 25
        if self.ready_for_next_line() and time.time()%1 < 0.5:
            surface.blit(surf, (x, y))




        x = -self.doctor_surf.get_width() + self.doctor_surf.get_width()*self.showing**0.5
        y = c.WINDOW_HEIGHT - self.doctor_surf.get_height()
        surface.blit(self.doctor_surf, (x, y))

    def ready_for_next_line(self):
        cps = c.CPS
        chars_showing = self.since_start_line * cps
        current_line = self.current_line()
        if current_line and chars_showing > len(current_line):
            return True

    def blocking(self):
        return self.showing != 0

    def add_dialog(self, lines):
        self.lines += lines
        if not self.target == 1:
            self.target = 1
            self.since_start_line = 0

    def current_line(self):
        if not self.lines:
            return None
        return self.lines[0]

    def next_line(self):
        if len(self.lines):
            self.lines.pop(0)
            self.since_start_line = 0
        if not self.lines:
            self.target = 0
        else:
            self.advance_sound.play()