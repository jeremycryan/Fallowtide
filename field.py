from image_manager import ImageManager
import pygame
import constants as c
import math
import random

from particle import MulchParticle, BloodParticle


class Field:
    def __init__(self, frame):
        self.width = 11
        self.height = 4
        self.tiles = [[Tile(x=x, y=y) for x in range(self.width)] for y in range(self.height)]

        tile_surf = ImageManager.load("assets/images/placeholder_tile.png")
        self.tile_width = tile_surf.get_width()
        self.tile_height = tile_surf.get_height()

        self.yoff = -110
        self.frame = frame

        self.has_seen_barren = False

        Crop.initialize_crop_locations()

    def update(self, dt, events):
        mpos = pygame.mouse.get_pos()
        x0 = c.WINDOW_WIDTH//2 - (self.width - 1) * self.tile_width / 4
        y0 = c.WINDOW_HEIGHT//2 - (self.height - 1) * self.tile_height / 2 + self.yoff
        found = False
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                px = x0 + x*self.tile_width/2
                py = y0 + y*self.tile_height
                dx = mpos[0] - px
                dy = mpos[1] - py
                if tile.hovered_by(dx, dy) and not found:
                    tile.hovered = True
                    found = True
                else:
                    tile.hovered = False
        self.check_for_clicks(dt, events)
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                tile.update(dt, events)


    def check_for_clicks(self, dt, events):
        if self.frame.doctor.blocking():
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    hovered_tile = self.hovered_tile()
                    if not hovered_tile:
                        return

                    selected_card = self.frame.hand.selected_card()
                    if not selected_card:
                        return

                    if not self.shape_placement_valid(selected_card.shape, selected_card.orientation):
                        self.frame.shake(5)
                        self.frame.cant.play()
                        return

                    self.place_here()

    def place_here(self):
        hovered_tile = self.hovered_tile()
        selected_card = self.frame.hand.selected_card()
        if not hovered_tile or not selected_card:
            return

        should_nudge = self.should_nudge(selected_card.shape, selected_card.orientation)

        crop = selected_card.crop
        for x, y in selected_card.shape:
            x = x + hovered_tile.x
            y = y + hovered_tile.y
            if should_nudge:
                x -= 1
            crop_object = Crop(crop, self.tiles[y][x])
            if crop_object.crop_type not in (c.BLOOD, c.MULCH):
                self.tiles[y][x].contents.append(crop_object)


        if crop == c.BLOOD:
            shape = ((1, 0), (-1, 0), (2, 0), (-2, 0), (0, -1), (-1, -1), (1, -1), (1, 1), (0, 1), (-1, 1))
            if hovered_tile.orientation == c.UP:
                shape += ((-2, 1), (2, 1))
            else:
                shape += ((-2, -1), (2, -1))
            for x, y in shape:
                x0 = x
                y0 = y
                if (x0 + y0 + (hovered_tile.orientation == c.UP)) % 2 == 1:
                    y0 += 1/6
                else:
                    y0 -= 1/6
                dist = math.sqrt(x0**2 + y0**2)

                x = x + hovered_tile.x
                y = y + hovered_tile.y
                if should_nudge:
                    x -= 1
                if y < 0 or x < 0:
                    continue
                try:
                    tile = self.tiles[y][x]
                    crop_object = Crop(crop, tile, delay=dist*0.25)
                except IndexError:
                    continue
                if crop_object.crop_type not in (c.BLOOD, c.MULCH):
                    self.tiles[y][x].contents.append(crop_object)



        self.frame.shake(15)
        self.frame.hand.use_selected()

    def draw(self, surf, offset=(0, 0)):
        x0 = c.WINDOW_WIDTH//2 - (self.width - 1) * self.tile_width / 4
        y0 = c.WINDOW_HEIGHT//2 - (self.height - 1) * self.tile_height / 2 + self.yoff
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                px = x0 + x*self.tile_width/2
                py = y0 + y*self.tile_height
                tile.draw(surf, offset=(px + offset[0], py + offset[1]))

        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile.orientation != c.DOWN:
                    continue
                px = x0 + x * self.tile_width / 2
                py = y0 + y * self.tile_height
                tile.draw_contents(surf, offset=(px + offset[0], py + offset[1]))
            for x, tile in enumerate(row):
                if tile.orientation != c.UP:
                    continue
                px = x0 + x * self.tile_width / 2
                py = y0 + y * self.tile_height
                tile.draw_contents(surf, offset=(px + offset[0], py + offset[1]))

    def hovered_tile(self):
        for row in self.tiles:
            for tile in row:
                if tile.hovered:
                    return tile
        return None

    def should_nudge(self, shape, orientation):
        hovered_tile = self.hovered_tile()
        if not hovered_tile:
            return False
        if orientation is not c.EITHER and orientation != hovered_tile.orientation:
            return True
        return False

    def shape_placement_valid(self, shape, orientation):
        hovered_tile = self.hovered_tile()
        if not hovered_tile:
            return False

        if self.frame.hand.selected_card():
            if self.frame.hand.selected_card().crop in (c.GOAT, c.CULTIST):
                return False

        nudge_x = 0
        if self.should_nudge(shape, orientation):
            nudge_x = -1

        for x, y in shape:
            x += hovered_tile.x + nudge_x
            y += hovered_tile.y
            if x < 0 or x > self.width - 1:
                return False
            if y < 0 or y > self.height - 1:
                return False
            tile = self.tiles[y][x]
            if tile.empty:
                return False
            if (tile.state == c.BARREN) and (not self.frame.hand.selected_card or not self.frame.hand.selected_card().crop in (c.BLOOD, c.MULCH)):
                return False
            if len(tile.contents):
                return False
        return True

    def draw_shape_highlights(self, shape, orientation, surface, offset=(0, 0)):
        hovered_tile = self.hovered_tile()
        if not hovered_tile:
            return
        x0 = c.WINDOW_WIDTH//2 - (self.width - 1) * self.tile_width / 4
        y0 = c.WINDOW_HEIGHT//2 - (self.height - 1) * self.tile_height / 2 + self.yoff

        nudge_x = 0
        if orientation is not c.EITHER and orientation != hovered_tile.orientation:
            nudge_x = -1

        valid = self.shape_placement_valid(shape, orientation)

        for x, y in shape:
            x += hovered_tile.x + nudge_x
            y += hovered_tile.y
            if x < 0 or x > self.width - 1:
                continue
            if y < 0 or y > self.height - 1:
                continue
            tile = self.tiles[y][x]
            if tile.empty:
                continue
            px = x0 + x * self.tile_width / 2
            py = y0 + y * self.tile_height
            tile.draw_highlight(surface, (px + offset[0], py + offset[1]), valid=valid)

    def collect_cash(self):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile.contents:
                    for crop in tile.contents:
                        crop_type = crop.crop_type

                        cash = c.TILE_PRICES[crop_type]
                        self.frame.cash += cash
                        self.frame.lifetime_cash += cash

    def next_day(self):
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                if tile.contents:
                    tile.reduce(1)
                    if c.FELLWEED in [crop.crop_type for crop in tile.contents]:
                        tile.state = c.BARREN
                    if not self.has_seen_barren and tile.state == c.BARREN:
                        self.frame.doctor.add_dialog([
                            "Alas, some of your soil has become |barren. As long as the ground is dry and cracked, crops will be unable to grow there.",
                            "Despair not! This is best avoided, but not beyond fixing.",
                            "If you |leave |that |soil |empty for a season, it may become fertile once more.",
                        ])
                        self.has_seen_barren = True
                    tile.contents = []
                else:
                    tile.fallow()
        self.frame.moon += 1


class Tile:
    def __init__(self, contents=None, x=0, y=0):
        self.contents = [] if contents is None else contents
        self.empty = False
        self.state = c.HEALTHY
        if (x < 3 or x > 7) and (y == 0 or y == 3):
            self.empty = True
        self.x = x
        self.y = y
        self.orientation = c.UP

        self.healthy_surf = ImageManager.load("assets/images/placeholder_tile.png")
        self.surf = self.healthy_surf
        self.used_surf = ImageManager.load("assets/images/used_soil.png")
        self.barren_surf = ImageManager.load("assets/images/barren_soil.png")
        self.surfs = {
            c.BARREN: self.barren_surf,
            c.USED: self.used_surf,
            c.HEALTHY: self.surf,
        }
        self.highlight_surf = ImageManager.load("assets/images/tile_highlight.png")
        self.bad_highlight_surf = ImageManager.load("assets/images/tile_bad_highlight.png")
        self.vertical_offset = 0
        if (x + y)%2 != c.UP:
            self.orientation = c.DOWN
            self.vertical_offset *= -1
            for key in self.surfs:
                self.surfs[key] = pygame.transform.flip(self.surfs[key], False, True)
            self.highlight_surf = pygame.transform.flip(self.highlight_surf, False, True)
            self.bad_highlight_surf = pygame.transform.flip(self.bad_highlight_surf, False, True)
        self.hovered = False

        self.particles = []

    def update(self, dt, events):
        if self.empty:
            return
        for item in self.contents:
            item.update(dt, events)
        for particle in self.particles[:]:
            particle.update(dt, events)
            if particle.dead:
                self.particles.remove(particle)

    def hovered_by(self, x, y):
        if self.empty:
            return False

        if self.orientation == c.DOWN:
            y *= -1

        x += self.surf.get_width()//2
        y += self.surf.get_height()//2
        if x < 0 or x > self.surf.get_width()-1:
            return
        if y < 0 or y > self.surf.get_height()-1:
            return
        color = self.surf.get_at((int(x), int(y)))
        if color[3] > 0:
            return True

    def draw(self, surf, offset=(0,0)):
        x = offset[0] - self.surf.get_width()//2
        y = offset[1] - self.surf.get_height()//2 + self.vertical_offset
        if self.empty:
            return
        surf.blit(self.surfs[self.state], (x, y))

        for particle in self.particles:
            particle.draw(surf, offset)

    def draw_contents(self, surf, offset=(0, 0)):
        for item in self.contents:
            item.draw(surf, offset)

    def draw_highlight(self, surf, offset=(0, 0), valid=True):
        x = offset[0] - self.surf.get_width()//2
        y = offset[1] - self.surf.get_height()//2 + self.vertical_offset
        if self.empty:
            return
        if valid:
            surf.blit(self.highlight_surf, (x, y))
        else:
            surf.blit(self.bad_highlight_surf, (x, y))

    def reduce(self, amt=1):
        if amt > 1:
            self.state = c.BARREN
            return
        if self.state == c.USED:
            self.state = c.BARREN
            return
        if self.state == c.HEALTHY:
            self.state = c.USED
            return

    def fallow(self):
        if self.state == c.BARREN:
            self.state = c.USED
        else:
            self.state = c.HEALTHY

class Crop:
    WHEAT_LOCATIONS = None
    FENNEL_LOCATIONS = None

    @staticmethod
    def initialize_crop_locations():
        points = []
        wheat_key = ImageManager.load("assets/images/wheat_spawn_key.png")
        for x in range(wheat_key.get_width()):
            for y in range(wheat_key.get_height()):
                if wheat_key.get_at((x, y)) == (0, 0, 0, 255):
                    px = x-wheat_key.get_width()//2
                    py = y + wheat_key.get_width()//math.sqrt(3) - wheat_key.get_width()
                    points.append((px, py))
        Crop.WHEAT_LOCATIONS = tuple(points)

        fennel_key = ImageManager.load("assets/images/fennel_spawn.png")
        points = []
        for x in range(fennel_key.get_width()):
            for y in range(fennel_key.get_height()):
                if fennel_key.get_at((x, y)) == (0, 0, 0, 255):
                    px = x-fennel_key.get_width()//2
                    py = y + fennel_key.get_width()//math.sqrt(3) - fennel_key.get_width()
                    points.append((px, py))
        Crop.FENNEL_LOCATIONS = tuple(points)
        pass

    def __init__(self, crop_enum, tile, delay=0.0):
        self.crop_type = crop_enum

        self.surf = ImageManager.load("assets/images/wheat.png")
        if self.crop_type == c.FENNEL:
            self.surf = ImageManager.load("assets/images/fennel.png")
        if tile.orientation == c.DOWN:
            self.surf = pygame.transform.flip(self.surf, False, True)
        self.orientation = tile.orientation

        self.pieces = []
        self.add_pieces()

        if self.crop_type == c.MULCH:
            tile.state = c.HEALTHY
            tile.particles.append(MulchParticle(tile))

        if self.crop_type == c.BLOOD:
            #tile.state = c.HEALTHY
            tile.particles.append(BloodParticle(tile, delay))
        pass

    def add_pieces(self):
        if self.crop_type in (c.MULCH, c.BLOOD):
            return
        locations = Crop.WHEAT_LOCATIONS
        if self.crop_type == c.FENNEL:
            locations = Crop.FENNEL_LOCATIONS
        if self.orientation != c.UP:
            locations = tuple([(x, -y) for (x, y) in locations])
        for x, y in locations:
            self.pieces.append(CropPiece(self, (x, y)))
        self.pieces.sort(key=lambda p: p.y)

    def update(self, dt, events):
        for piece in self.pieces:
            piece.update(dt, events)


    def draw(self, surface, offset=(0, 0)):
        x = offset[0] - self.surf.get_width()//2
        y = offset[1] - self.surf.get_height()//2
        #surface.blit(self.surf, (x, y))
        for piece in self.pieces:
            piece.draw(surface, offset)


class CropPiece:
    def __init__(self, crop, position):
        self.crop = crop
        self.x, self.y = position # position of center of rectangle
        self.draw_x = self.x

        self.period = 3 + random.random() * 0.5
        self.age = random.random() * self.period
        self.sway_amplitude = 50
        self.update(0.01, [])

        self.surf = ImageManager.load("assets/images/wheat_strand.png")
        if self.crop.crop_type == c.FENNEL:
            self.surf = ImageManager.load("assets/images/fennel.png")
        if self.crop.crop_type == c.FELLWEED:
            self.surf = ImageManager.load("assets/images/fellweed.png")

    def update(self, dt, events):
        self.age += dt
        self.angle = math.cos(self.age * math.pi * 2 / self.period) * self.sway_amplitude
        if self.sway_amplitude > 8:
            self.sway_amplitude *= 0.2**dt
            self.sway_amplitude -= 10 * dt
        self.draw_x = -self.angle * 0.8 + self.x

    def draw(self, surf, offset=(0, 0)):
        my_surf = pygame.transform.rotate(self.surf, self.angle)
        surf.blit(my_surf, (offset[0] + self.draw_x - my_surf.get_width()//2, offset[1] + self.y - my_surf.get_height() + 5))