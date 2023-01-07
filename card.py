import constants as c
import pygame
import math

class Card:

    title_font = None

    def __init__(self, crop, x = c.WINDOW_WIDTH + c.CARD_WIDTH//2, shape=None, orientation=c.UP):
        # Orientation up means the card is played on a ^ tile rather than a v tile.
        # Shape is tuple of tuples --- inner tuples are relative coordinates (0, 0) is hovered tile
        self.orientation = orientation
        self.crop = crop
        self.shape = shape if shape is not None else ((0, 0),)
        self.value = c.TILE_PRICES[crop] * len(shape)
        self.pulled = 0
        self.x = x
        self.target_x = 0
        self.hovered = True
        self.selected = False
        self.hand = None

        if Card.title_font == None:
            Card.title_font = pygame.font.Font("assets/fonts/alagard.ttf", 35)

        self.surf = self.get_surf()

    def is_hovered(self, x, y):
        if (abs(x) < c.CARD_WIDTH//2):
            if (y < c.CARD_HEIGHT//2 + 50 and y > -c.CARD_HEIGHT//2):
                return True
        return False

    def get_surf(self):
        surf = pygame.Surface((c.CARD_WIDTH, c.CARD_HEIGHT))
        surf.fill((255, 255, 255))
        title = Card.title_font.render(c.CARD_NAMES[self.crop], 1, (0, 0, 0))
        surf.blit(title, (surf.get_width()//2 - title.get_width()//2, 16))
        self.draw_shape(surf, offset=(0, 0))
        return surf

    def draw_shape(self, surface, offset=(0, 0)):
        x = surface.get_width()//2 + offset[0]
        y = surface.get_height()//2 + offset[1]

        min_x = min([xy[0] for xy in self.shape])
        min_y = min([xy[1] for xy in self.shape])
        max_x = max([xy[0] for xy in self.shape])
        max_y = max([xy[1] for xy in self.shape])

        width = max_x - min_x
        height = max_y - min_y

        x0 = x - (width) * c.CARD_SHAPE_WIDTH//4
        y0 = y - (height) * c.CARD_SHAPE_WIDTH//2

        for xy in self.shape:
            shape_width = c.CARD_SHAPE_WIDTH
            orientation = c.UP if ((self.orientation == c.UP) + xy[0] + xy[1])%2==1 else c.DOWN
            xs = x0 + shape_width//2 * (xy[0] - min_x)
            yoff = shape_width/6
            if orientation == c.DOWN:
                yoff *= -1
            ys = y0 + (shape_width - 4) * (xy[1] - min_y) + yoff
            points = [((shape_width - c.CARD_SHAPE_SPACING) * x, (shape_width - c.CARD_SHAPE_SPACING) * y) for (x, y) in ((0, -1/math.sqrt(3)), (0.5, 0.5/math.sqrt(3)), (-0.5, 0.5/math.sqrt(3)))]
            if orientation == c.DOWN:
                points = [(x, -y) for (x, y) in points]
            points = [(x + xs, y + ys) for (x, y) in points]
            if xy == (0, 0):
                pygame.draw.polygon(surface, (85, 85, 85), points)
            else:
                pygame.draw.polygon(surface, (128, 128, 128), points)

    def can_be_played_on_tile(self, field, x, y):
        if x < 0 or y < 0 or y > len(field.tiles) - 1 or x > len(field.tiles[0]) - 1:
            return False
        tile = field.tiles[y][x]
        if self.orientation != c.EITHER:
            if tile.orientation != self.orientation:
                return False
        return True


    def update(self, dt, events):
        dx = self.target_x - self.x
        change = dx * dt * 10
        if change > abs(dx):
            change *= abs(dx)/change
        if abs(dx) > 2:
            self.x += dx * dt * 10
        else:
            self.x = self.target_x

        if self.selected:
            dp = 1.2 - self.pulled
            self.pulled += dp * 10*dt
            if abs(self.pulled - 1.2) < 0.01:
                self.pulled = 1.2
        elif self.hovered:
            dp = 1 - self.pulled
            self.pulled += dp * 10*dt
            if abs(self.pulled - 1) < 0.01:
                self.pulled = 1
        else:
            dp = 0 - self.pulled
            self.pulled += dp * 10*dt
            if self.pulled < 0:
                self.pulled = 0

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.hovered and not self.selected:
                        self.select()
                    elif self.hovered:
                        self.unselect()

    def get_apparent_position(self):
        x = self.x
        y = c.WINDOW_HEIGHT - self.pulled * c.CARD_HEIGHT * 0.45
        return x, y

    def draw(self, surface, offset=(0, 0)):
        x, y = self.get_apparent_position()
        x += -c.CARD_WIDTH//2 + offset[0]
        y += -c.CARD_HEIGHT//2
        surface.blit(self.surf, (x, y))

    def start_hover(self):
        if not self.hovered:
            self.hovered = True

    def stop_hover(self):
        if self.hovered:
            self.hovered = False

    def select(self):
        if self.selected != True:
            self.selected = True
        if self.hand:
            for card in self.hand.cards:
                if card is not self:
                    card.unselect()

    def unselect(self):
        if self.selected:
            self.selected = False