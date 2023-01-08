import pygame

from image_manager import ImageManager


class CashDisplay:
    def __init__(self, frame):
        self.symbol = ImageManager.load("assets/images/coin2.png")
        self.moon = ImageManager.load("assets/images/moon.png")
        self.frame = frame
        self.font = pygame.font.Font("assets/fonts/matura.ttf", 40)
        self.last_value = None
        self.visible_value = 0
        self.text = None
        self.back = ImageManager.load("assets/images/ui_back.png")

        self.slimback = pygame.transform.scale(self.back, (self.back.get_width(), self.back.get_height()//2))
        self.skull = ImageManager.load("assets/images/souls.png")

    def update(self, dt, events):
        if self.last_value is not None:
            dv = self.last_value - self.visible_value
            self.visible_value += dv * dt * 10
            if abs(self.visible_value - self.last_value) < 1:
                self.visible_value = self.last_value
        pass

    def draw(self, surface, offset=(0, 0)):

        surface.blit(self.back, (0, 50), special_flags=pygame.BLEND_MULT)
        x = 140
        y = 160
        surface.blit(self.symbol, (x, y-self.symbol.get_height()//2), special_flags=pygame.BLEND_ADD)
        if self.text is None or self.frame.cash != self.last_value:
            self.last_value = self.frame.cash

        self.text = self.font.render(f"{int(self.visible_value)}", 1, (255, 255, 255))
        x += self.symbol.get_width() + 20
        surface.blit(self.text, (x, y - self.text.get_height()//2))

        x = 140
        y = 100
        surface.blit(self.moon, (x, y-self.symbol.get_height()//2), special_flags=pygame.BLEND_ADD)
        text = self.font.render(f"Season {self.frame.moon}", 1, (255, 255, 255))
        x += self.moon.get_width() + 20
        surface.blit(text, (x, y - text.get_height()//2))

        if self.frame.skulls > 0:
            surface.blit(self.slimback, (0, 190), special_flags=pygame.BLEND_MULT)
            x = 140
            y = 220
            surface.blit(self.skull, (x, y-self.skull.get_height()//2), special_flags=pygame.BLEND_ADD)
            text = self.font.render(f"{self.frame.skulls}", 1, (255, 255, 255))
            x += self.skull.get_width() + 20
            surface.blit(text, (x, y-text.get_height()//2))