import pytmx
import pygame
from os import path
import os
import sys
from settings import *
from random import random, choice

"""
Карта должна содержать минимум эти слои.
0. ground - layer tiles
1. spawn_players - layer tiles
2. spawn_bots - layer tiles
3. eagle - object

Также могут быть использованы:
walls - objects
trees - layer - tiles
"""

MAPDIR = 'data\\maps\\'
WORLDIMG_DIR = 'world\\'
DIR_FOR_TANKS_IMG = 'tanks_texture\\'
WIDTH, HEIGHT = 950, 750
MAP_SIZE = 650
OFFSET = 50
FPS = 60

TILE_FOR_PLAYERS = 16
TILE_FOR_MOBS = 17

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
monitor_size = [pygame.display.Info().current_w,
                pygame.display.Info().current_h]
background = pygame.Surface((WIDTH, HEIGHT))

# Загрузка всей игровой графики
# img_dir = path.join(path.dirname(__file__),
#                     'E:/')
# powerup_images = dict()
# powerup_images['shield'] = \
#     pygame.image.load(path.join(img_dir,
#                                 'E:/Game on Python/SpaceShooterRedux'
#                                 '/PNG/Power-ups/shield_gold.png')).convert()
# powerup_images['gun'] = \
#     pygame.image.load(path.join(img_dir, 'E:/Game on Python/'
#                                          'SpaceShooterRedux/PNG/'
#                                          'Power-ups/bolt_gold.png')).convert()
#
# background = \
#     pygame.image.load(path.join(img_dir,
#                                 'Backgrounds/darkPurple.png')).convert()
# background = pygame.transform.scale(background, (WIDTH, HEIGHT))
# background_rect = background.get_rect(center=(WIDTH // 2, HEIGHT // 2))
#
# player_img = pygame.image.load(path.join(img_dir,
#                                          "PNG/playerShip1_red.png")).convert()
# player_mini_img = pygame.transform.scale(player_img, (35, 29))
# player_mini_img.set_colorkey(BLACK)
# # pictures for meteors
# meteor_list = []
# for m_i in ["PNG/Meteors/meteorBrown_med1.png",
#             "PNG/Meteors/meteorBrown_big1.png",
#             "PNG/Meteors/meteorGrey_med1.png"]:
#     meteor_list.append(pygame.image.load(path.join(img_dir, m_i)).convert())
#
# # pictures for bullet
# bullet_img = \
#     pygame.image.load(path.join(img_dir,
#                                 "PNG/Lasers/laserRed16.png")).convert()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def convert_coords(x, tile_size):
    return x[0] * tile_size + OFFSET, x[1] * tile_size + OFFSET, x[2]


class Player(pygame.sprite.Sprite):
    images = {
        '1_t0': 't_y.png', '1_l0': 't_y_l.png', '1_r0': 't_y_r.png',
        '1_b0': 't_y_b.png',
        '1_t1': 't_y1.png', '1_l1': 't_y1_l.png', '1_r1': 't_y1_r.png',
        '1_b1': 't_y1_b.png',
        '2_t0': 't_g.png', '2_l0': 't_g_l.png', '2_r0': 't_g_r.png',
        '2_b0': 't_g_b.png',
        '2_t1': 't_g1.png', '2_l1': 't_g1_l.png', '2_r1': 't_g1_r.png',
        '2_b1': 't_g1_b.png',
    }

    def __init__(self, game, coords, tile_size, player):
        super().__init__()
        self.game = game
        self.type_tanks = 't1'
        self.player = player
        self.side = 't'
        self.move_trigger = False

        self.TILE_SIZE = tile_size
        self.image = None
        self.mask = None
        self.load_tanks_image()

        self.coords = coords
        self.rect = self.image.get_rect()
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

        self.speed = 2
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.bullet = None

        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()

    def load_tanks_image(self):
        self.move_trigger = not self.move_trigger
        image = load_image(f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{self.images[f"{self.player}_{self.side}{int(self.move_trigger)}"]}'
                           if self.player == 1 else
                           f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{self.images[f"{self.player}_{self.side}{int(self.move_trigger)}"]}')
        self.image = pygame.transform.scale(image, (self.TILE_SIZE -
                                                    self.TILE_SIZE // 8,
                                                    self.TILE_SIZE -
                                                    self.TILE_SIZE // 8))
        s = pygame.Surface((self.image.get_rect().width,
                            self.image.get_rect().height), pygame.SRCALPHA)
        s.fill(pygame.color.Color('black'))
        self.mask = pygame.mask.from_surface(s)

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def move_collide(self, side: str, speed=(0, 0)):
        self.side = side
        self.load_tanks_image()
        self.rect = self.rect.move(speed[0], speed[1])
        c = pygame.sprite.spritecollide(self, self.game.wall_group, False,
                                        pygame.sprite.collide_mask)
        c1 = pygame.sprite.spritecollide(self, self.game.all_sprites, False,
                                         pygame.sprite.collide_mask)
        # TODO обработка столкновений с другими игроками и тд
        """За обработку столкновений с пулями отвечает сама пуля"""
        if len(c1) != 1:
            print(c1)
        if c or self.game.map.check_collide(self.rect):
            self.rect = self.rect.move(-speed[0], -speed[1])

    def move(self, keystate, obj):
        # print(obj['up'])
        if keystate[pygame.key.key_code(obj['up'])]:
            self.move_collide('t', (0, -self.speed))
        elif keystate[pygame.key.key_code(obj['down'])]:
            self.move_collide('b', (0, self.speed))
        elif keystate[pygame.key.key_code(obj['left'])]:
            self.move_collide('l', (-self.speed, 0))
        elif keystate[pygame.key.key_code(obj['right'])]:
            self.move_collide('r', (self.speed, 0))

    def update(self, *args):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        keystate = pygame.key.get_pressed()
        if self.player == 1:
            obj = PLAYER1
        else:
            obj = PLAYER2

        self.move(keystate, obj)
        if keystate[pygame.key.key_code(obj['shoot'])]:
            self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.bullet is None or not self.bullet.alive():
                bullet = Bullet(self.rect, self.side, self.game, self)
                bullet.add(self.game.all_sprites, self.game.bullets)
                self.bullet = bullet

    def compare_rect_with_bot(self, rect: pygame.rect.Rect):
        if rect.x <= self.rect.x <= rect.x + rect.width\
                or rect.y <= self.rect.y <= rect.y + rect.width:
            return True
        return False


class Bullet(pygame.sprite.Sprite):
    images = {
        't': 'b.png',
        'l': 'b_l.png',
        'r': 'b_r.png',
        'b': 'b_b.png'
    }

    def __init__(self, rect_tank, side: str, game, who_shoot):
        super().__init__()
        self.who_shoot = who_shoot
        self.game = game
        self.image = load_image(f'{DIR_FOR_TANKS_IMG}'
                                f'bullet\\{self.images[side]}')
        k = (rect_tank.width // 4) // self.image.get_rect().width
        self.image = pygame.transform.scale(self.image,
                                            (self.image.get_rect().width * k,
                                             self.image.get_rect().height * k))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.side = side
        self.speed = 5
        self.speedy, self.speedx = 0, 0
        self.set_rect(rect_tank)

    def update(self):
        self.rect = self.rect.move(self.speedx, self.speedy)
        # удалить спрайт, если он заходит за верхнюю часть экрана
        if self.game.map.check_collide(self.rect):
            self.kill()
        # TODO столкновне с другими пулями, игроками
        c = pygame.sprite.spritecollideany(self, self.game.all_sprites)
        if c is not None:
            if c in self.game.wall_group and c.isWall:
                coord_collide = pygame.sprite.collide_mask(c, self)
                if coord_collide is not None:
                    if c.isBroken:
                        c.change_yourself(coord_collide)
                    self.kill()
            if c in self.game.player_group:
                # TODO сделать уменьшение жизни у игрока и анимацию попадания
                self.kill()
            if c in self.game.bullets and c is not self:
                if self.who_shoot.__class__ != c.who_shoot.__class__:
                    self.kill()
                    c.kill()
            if c in self.game.mobs_group and \
                    self.who_shoot.__class__ == Player:
                c.kill()
                self.kill()
            if c == self.game.eagle:
                c.eagle_break()
                self.kill()

    def set_rect(self, rect_tank):
        if self.side == 't':
            self.rect.bottom = rect_tank.top
            self.rect.centerx = rect_tank.centerx
            self.speedy = -self.speed
        if self.side == 'l':
            self.rect.right = rect_tank.left
            self.rect.centery = rect_tank.centery
            self.speedx = -self.speed
        if self.side == 'r':
            self.rect.left = rect_tank.right
            self.rect.centery = rect_tank.centery
            self.speedx = self.speed
        if self.side == 'b':
            self.rect.top = rect_tank.bottom
            self.rect.centerx = rect_tank.centerx
            self.speedy = self.speed


class Wall(pygame.sprite.Sprite):
    type_wall = {
        3: 'wall_RT.png',
        4: 'wall_RD.png',
        5: 'wall_LT.png',
        6: 'wall_LD.png',
        7: 'wall_T.png',
        8: 'wall_R.png',
        9: 'wall_L.png',
        10: 'wall_D.png',
        11: 'wall_1.png',
        18: 'wall_b1.png',
        19: 'wall_b2.png',
        20: 'wall_b3.png',
        21: 'wall_b4.png',
        22: 'wall_h1.png',
        23: 'wall_h2.png',
        2: 'water.png',
        13: 'metall_wall.png'
    }  # key(id) from Tiled Edit

    def __init__(self, x, y, id, tile_size):
        super().__init__()
        self.isBroken = True if id not in [2, 13] else False
        self.isWall = True if id not in [2] else False

        self.tile_size = tile_size
        self.image = self.mask = self.id = None
        self.reload_mask(id)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def reload_mask(self, set_id):
        self.id = set_id
        self.image = load_image(f'{WORLDIMG_DIR}{self.type_wall[self.id]}')
        self.image = pygame.transform.scale(self.image,
                                            (self.tile_size, self.tile_size))
        self.mask = pygame.mask.from_surface(self.image)

    def change_yourself(self, coords):
        x, y = coords
        max_s = self.tile_size              # 50
        half_s = max_s // 2 - max_s // 10 - 2  # 20
        half_s2 = half_s + max_s // 5 + 4      # 30
        if self.id == 11:
            if half_s <= x <= half_s2:
                if 0 <= y <= half_s:
                    self.reload_mask(7)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(10)
            elif 0 <= x <= half_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(9)
                elif 0 <= y <= half_s:
                    self.reload_mask(5)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(6)
            elif half_s2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(8)
                elif 0 <= y <= half_s:
                    self.reload_mask(3)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(4)
        elif self.id == 5:
            if half_s <= x <= half_s2:
                if half_s2 <= y <= max_s:
                    self.reload_mask(19)
            if max_s // 2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(18)
                elif 0 <= y <= half_s:
                    self.reload_mask(7)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(22)
            if 0 <= x <= max_s // 2 <= y <= max_s:
                self.reload_mask(9)
        elif self.id == 3:
            if half_s <= x <= half_s2 <= y <= max_s:
                self.reload_mask(21)
            if 0 <= x <= max_s // 2:
                if half_s <= y <= half_s2:
                    self.reload_mask(20)
                if 0 <= y <= half_s:
                    self.reload_mask(7)
                if half_s2 <= y <= max_s:
                    self.reload_mask(23)
            if max_s // 2 <= x <= max_s and max_s // 2 <= y <= max_s:
                self.reload_mask(8)
        elif self.id == 6:
            if half_s2 >= x >= half_s >= y >= 0:
                self.reload_mask(20)
            if half_s2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.reload_mask(21)
                elif 0 <= y <= half_s:
                    self.reload_mask(23)
            if 0 <= x <= half_s and 0 <= y <= max_s // 2:
                self.reload_mask(9)
            if max_s // 2 <= x <= max_s and max_s // 2 <= y <= max_s:
                self.reload_mask(10)
        elif self.id == 4:
            if half_s2 >= x >= half_s >= y >= 0:
                self.reload_mask(18)
            if 0 <= x <= max_s // 2 <= y <= max_s:
                self.reload_mask(10)
            if 0 <= x <= half_s:
                if half_s <= y <= max_s // 2:
                    self.reload_mask(19)
                elif 0 <= y <= half_s:
                    self.reload_mask(22)
            if max_s >= x >= max_s // 2 >= y >= 0:
                self.reload_mask(8)
        elif self.id == 10:
            if 0 <= y <= max_s // 2:
                if half_s <= x <= half_s2:
                    self.kill()
                elif 0 <= x <= half_s:
                    self.reload_mask(19)
                elif half_s2 <= x <= max_s:
                    self.reload_mask(21)
        elif self.id == 7:
            if max_s // 2 <= y <= max_s:
                if half_s <= x <= half_s2:
                    self.kill()
                elif 0 <= x <= half_s:
                    self.reload_mask(20)
                elif half_s2 <= x <= max_s:
                    self.reload_mask(18)
        elif self.id == 9:
            if max_s // 2 <= x <= max_s:
                if half_s <= y <= half_s2:
                    self.kill()
                elif 0 <= y <= half_s:
                    self.reload_mask(20)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(19)
        elif self.id == 8:
            if 0 <= x <= max_s // 2:
                if half_s <= y <= half_s2:
                    self.kill()
                elif 0 <= y <= half_s:
                    self.reload_mask(18)
                elif half_s2 <= y <= max_s:
                    self.reload_mask(21)
        elif self.id == 22:
            if 50 >= x >= 25 >= y >= 0:
                self.reload_mask(18)
            if 0 <= x <= 25 <= y <= 50:
                self.reload_mask(19)
        elif self.id == 23:
            if 50 >= x >= 25 and 25 <= y <= 50:
                self.reload_mask(21)
            if 0 <= x <= 25 and 0 <= y <= 25:
                self.reload_mask(20)
        else:
            self.kill()

class EmptyBot(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)

class Bot(pygame.sprite.Sprite):
    images = {
        't0': 't_w.png',
        'l0': 't_w_l.png',
        'r0': 't_w_r.png',
        'b0': 't_w_b.png',
        't1': 't_w1.png',
        'l1': 't_w1_l.png',
        'r1': 't_w1_r.png',
        'b1': 't_w1_b.png'
    }

    def __init__(self, game, coords, tile_size, type_bot: str, number_tank):
        super().__init__(game.mobs_group, game.all_sprites)
        self.game = game
        self.type_tanks = type_bot
        self.side = 't'
        self.available_side = ['t', 'l', 'b', 'r']
        self.move_trigger = False

        self.TILE_SIZE = tile_size
        self.image = None
        self.mask = None
        self.load_tanks_image()

        self.coords = coords
        self.rect = self.image.get_rect()
        self.rect.x = self.coords[0]
        self.rect.y = self.coords[1]

        self.speed = 2
        self.speedx = 0
        self.speedy = 0
        self.lives = 1
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.bullet = None

        self.shoot_delay = 200
        self.last_shot = pygame.time.get_ticks()

        self.start_time = pygame.time.get_ticks()
        self.change_side_timer = 2000
        self.target = None
        self.target_poz = [None, None]
        self.target_delay = 2000
        self.target_st = pygame.time.get_ticks()

    def setTarget(self, target):
        self.target = target

    def load_tanks_image(self):
        self.move_trigger = not self.move_trigger
        image = load_image(f'{DIR_FOR_TANKS_IMG}{self.type_tanks}\\'
                           f'{self.images[f"{self.side}{int(self.move_trigger)}"]}')
        self.image = pygame.transform.scale(image, (self.TILE_SIZE -
                                                    self.TILE_SIZE // 8,
                                                    self.TILE_SIZE -
                                                    self.TILE_SIZE // 8))
        s = pygame.Surface((self.image.get_rect().width,
                            self.image.get_rect().height), pygame.SRCALPHA)
        s.fill(pygame.color.Color('black'))
        self.mask = pygame.mask.from_surface(s)

    def hide(self):
        # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)

    def set_speedxy(self):
        speeds = {'r': [self.speed, 0],
                  'l': [-self.speed, 0],
                  't': [0, -self.speed],
                  'b': [0, self.speed]}
        self.speedx, self.speedy = speeds[self.side]

    def get_side(self, direction):
        if direction == 1:
            index = self.available_side.index(self.side)
            if index == len(self.available_side) - 1:
                return self.available_side[0]
            return self.available_side[index + 1]
        elif direction == -1:
            index = self.available_side.index(self.side)
            if index == len(self.available_side) - 1:
                return self.available_side[-1]
            return self.available_side[index - 1]

    def change_side(self, custom=False):
        anti_side = {"r": 'l', 'l': 'r', 't': 'b', 'b': 't'}
        if custom:
            if random() > 0.5:
                self.side = self.get_side(direction=1)
            else:
                self.side = self.get_side(direction=-1)
            return

        if random() < 0.20:  # 0.25
            self.side = anti_side[self.side]
        else:
            if random() < 0.5:  # 0.5
                self.side = anti_side[self.side]
            else:
                if random() > 0.5:
                    self.side = self.get_side(direction=1)
                else:
                    self.side = self.get_side(direction=-1)
        self.set_speedxy()

    def move_collide(self, side: str, speed=(0, 0)):
        self.side = side
        self.load_tanks_image()
        self.rect = self.rect.move(speed[0], speed[1])
        c = pygame.sprite.spritecollide(self, self.game.wall_group, False,
                                        pygame.sprite.collide_mask)
        c1 = pygame.sprite.spritecollide(self, self.game.all_sprites, False,
                                         pygame.sprite.collide_mask)
        if len(c1) != 1:
            print(c1)
        if c or self.game.map.check_collide(self.rect):
            self.rect = self.rect.move(-speed[0], -speed[1])
            if self.target is None:
                self.change_side()

    def has_path(self, x1, y1, x2, y2):
        INF = 1000
        x1 -= OFFSET
        x2 -= OFFSET
        y1 -= OFFSET
        y2 -= OFFSET
        x, y = x1 * self.game.map.width // MAP_SIZE, \
               y1 * self.game.map.height // MAP_SIZE
        distance = [[INF] * self.game.map.width
                    for _ in range(self.game.map.height)]
        distance[y][x] = 0
        prev = [[None] * self.game.map.width
                for _ in range(self.game.map.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), \
                          (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                rect = EmptyBot(next_x * MAP_SIZE // self.game.map.width +
                                OFFSET,
                                next_y * MAP_SIZE // self.game.map.height +
                                OFFSET,
                                self.rect.width, self.rect.height)
                if 0 <= next_x < self.game.map.width and \
                        0 <= next_y < self.game.map.height \
                        and self.is_free(rect) and \
                        distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))

        x, y = x2 * self.game.map.width // MAP_SIZE, \
               y2 * self.game.map.height // MAP_SIZE
        if distance[y][x] == INF or (x1, y1) == (x2, y2):
            return False, (x1, y1)
        while prev[y][x] != (x1, y1):
            if prev[y][x] is not None:
                x, y = prev[y][x]
            else:
                break
        return True, (x * MAP_SIZE // self.game.map.width + OFFSET,
                      y * MAP_SIZE // self.game.map.height + OFFSET)

    def is_free(self, rect):
        for i in self.game.wall_group:
            if not i.isBroken:
                if pygame.sprite.spritecollideany(i,
                                                  pygame.sprite.Group(rect)) \
                        is not None:
                    return False
        return True

    def get_nearest_players_pos(self):
        def hypot(x1, y1, x2, y2):
            return (abs(x1 - x2) + abs(y1 - y2)) ** 0.5
        lens = {}
        for i in self.game.player_group:
            lens[hypot(i.rect.x, i.rect.y, self.rect.x, self.rect.y)] = i
        pl = lens[min(list(lens.keys()))]
        return pl.rect.x, pl.rect.y

    def set_side(self, coords):
        x, y = coords
        if x < self.rect.x:
            self.side = 'l'
        elif x > self.rect.x:
            self.side = 'r'
        elif y < self.rect.y:
            self.side = 't'
        elif y > self.rect.y:
            self.side = 'b'

    def move(self):
        def just_drive():
            self.set_speedxy()
            now = pygame.time.get_ticks()
            self.move_collide(self.side, (self.speedx, self.speedy))
            if now - self.start_time > self.change_side_timer:
                self.change_side(custom=True)
                self.start_time = now

        if self.target is None:
            just_drive()
        if self.target == 'players':
            if (self.target_poz[0] is None and self.target_poz[1] is None) \
                or (self.rect.x <= self.target_poz[0] + self.speed and
                    self.rect.y <= self.target_poz[1] + self.speed):
                nex_pos = self.has_path(self.rect.x, self.rect.y,
                                        *self.get_nearest_players_pos())
                if nex_pos[0]:
                    self.target_poz = nex_pos[1]
                else:
                    self.target_poz = [None, None]
            now = pygame.time.get_ticks()
            if now - self.target_st > self.target_delay:
                self.target_st = now
                if None not in self.target_poz:

                    print(self.rect, self.target_poz)
                    self.rect.x = self.target_poz[0]
                    self.rect.y = self.target_poz[0]
                    return
                    # self.move_collide(self.side, (self.speedx, self.speedx))
                    # self.set_side(self.target_poz)
                    # self.set_speedxy()
                    # self.move_collide(self.side, (self.speedx, self.speedx))
            else:
                just_drive()
        if self.target == 'eagle':
            just_drive()

    def update(self):
        self.move()
        self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.bullet is None or not self.bullet.alive():
                # 1 / 32
                # TODO при пересечении с орлом стрелять по нему
                if random() < 1 / 10 or self.compare_rect():
                    bullet = Bullet(self.rect, self.side, self.game, self)
                    bullet.add(self.game.all_sprites, self.game.bullets)
                    self.bullet = bullet

    def compare_rect(self):
        # TODO Дописать проверку при пересечении с орлом
        for i in self.game.player_group:
            if i.compare_rect_with_bot(self.rect):
                return True
        return False

    def kill(self):
        super().kill()


class BotManager:
    def __init__(self, game):
        self.game = game
        self.player_count = 1 if self.game.player1 is not None \
            else 2 if self.game.player2 is not None else 0
        if self.player_count == 0:
            raise Exception('Недостаточно игроков')
        import mobs_count
        try:
            self.bot_comb = mobs_count.count[self.game.level]
        except KeyError:
            raise KeyError('Комбинация ботов не найдена')

        self.respawn_time = (190 - game.level * 4 - (
                self.player_count - 1) * 60) * 10
        self.start_time = -self.respawn_time

        self.period_timer = pygame.time.get_ticks()
        self.first_period = self.respawn_time // 8 * 20
        self.second_period = self.first_period * 2 * 20
        self.third_period = 2560 + self.second_period
        print(self.first_period)

        self.global_count_bots = sum(self.bot_comb)
        self.real_time_counter = [0, 't1']
        self.types_tanks = ['t1', 't2', 't3', 't4']
        self.visible_bots = 4 if self.player_count == 1 else 6
        self.free_tiles_for_spawn = self.game.TILES_FOR_MOBS

    def update(self):
        now = pygame.time.get_ticks()
        if len(self.game.mobs_group) <= 0 and self.global_count_bots <= 0:
            self.game.isGameOver = True
            self.game.game_over()

        if not self.game.isGameOver and \
                now - self.start_time > self.respawn_time and \
                len(self.game.mobs_group) < 4 and self.global_count_bots > 0:
            Bot(self.game, self.get_tile(),
                self.game.TILE_SIZE, self.get_type_tank(),
                sum(self.bot_comb) - self.global_count_bots)
            self.start_time = now

        if self.first_period < now - self.period_timer < self.second_period:
            self.setTarget_for_bots('players')
        elif self.second_period < now - self.period_timer \
                < self.third_period:
            self.setTarget_for_bots('eagle')
        elif now - self.period_timer > self.third_period:
            self.setTarget_for_bots(None)
            self.period_timer = now

        self.game.mobs_group.update()

    def get_type_tank(self):
        self.global_count_bots -= 1
        self.real_time_counter[0] += 1
        if self.real_time_counter[0] \
                > self.bot_comb[self.types_tanks.index(self.real_time_counter[
                                                           1])]:
            self.real_time_counter[0] = 0
            self.real_time_counter[1] = self.types_tanks[
                self.types_tanks.index(self.real_time_counter[1]) + 1]

        return self.real_time_counter[1]

    def get_tile(self):
        from random import choice
        return choice(self.free_tiles_for_spawn)

    def setTarget_for_bots(self, target):
        for i in self.game.mobs_group:
            i.setTarget(target)


class Map:
    def __init__(self, path, map_size):
        self.map = pytmx.load_pygame(path)
        self.TILE_SIZE = map_size // self.map.width
        self.width = self.map.width
        self.height = self.map.height
        self.koeff = self.map.tilewidth / self.TILE_SIZE

        self.rect = pygame.rect.Rect((OFFSET, OFFSET),
                                     (MAP_SIZE, MAP_SIZE))
        self.layers = list(self.map.layernames.keys())
        self.checking_layers()

    def checking_layers(self):
        for i in ['ground', 'spawn_players', 'spawn_bots', 'eagle']:
            if not self.check_(i):
                raise Exception(f'В карте не обнаружены необходимые слои: {i}')

    def get_tile_image(self, x, y, layer):
        image = self.map.get_tile_image(x, y, layer)
        if image is not None:
            image = pygame.transform.scale(image,
                                           (self.TILE_SIZE, self.TILE_SIZE))
            return image

    def get_objects(self, name):
        return self.map.layernames[name]

    def get_tile_id(self, gid):
        return self.map.tiledgidmap[gid]

    def get_tiled_by_id(self, id):
        return list(map(lambda x: convert_coords(x, self.TILE_SIZE),
                        self.map.get_tile_locations_by_gid(
            list(self.map.tiledgidmap.values()).index(id) + 1)))

    def render_layer(self, screen, layer_name):
        if layer_name not in self.layers:
            return
        layer = self.layers.index(layer_name)
        for x in range(self.width):
            for y in range(self.height):
                image = self.get_tile_image(x, y, layer)
                if image is not None:
                    screen.blit(image, (
                        x * self.TILE_SIZE + OFFSET,
                        y * self.TILE_SIZE + OFFSET))

    def check_(self, name):
        return name in self.map.layernames

    def check_collide(self, rect: pygame.rect.Rect):
        if rect.y < self.rect.y or rect.x < self.rect.x \
                or rect.right > self.rect.right \
                or rect.bottom > self.rect.bottom:
            return True
        return False


class Eagle(pygame.sprite.Sprite):
    images = {
        'normal': 'eagle.png',
        'broken': 'eagle_broken.png'
    }

    def __init__(self, game, x, y, tile_size):
        super().__init__(game.all_sprites)
        self.TILE_SIZE = tile_size
        self.image = load_image(f'{WORLDIMG_DIR}{self.images["normal"]}')
        self.image = pygame.transform.scale(self.image, (self.TILE_SIZE,
                                                         self.TILE_SIZE))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = x
        self.rect.y = y
        self.game = game
        self.isBroken = False

    def eagle_break(self):
        self.image = load_image(f'{WORLDIMG_DIR}\\{self.images["broken"]}')
        self.image = pygame.transform.scale(self.image, (self.TILE_SIZE,
                                                         self.TILE_SIZE))
        self.mask = pygame.mask.from_surface(self.image)
        self.isBroken = True


class Game:
    def __init__(self, type_game, number_level):
        self.map = Map(f'{MAPDIR}map{number_level}.tmx', MAP_SIZE)
        self.map_object = self.map.map
        self.TILE_SIZE = self.map.TILE_SIZE
        self.type_game = type_game
        self.level = number_level

        self.isGameOver = False

        self.all_sprites = pygame.sprite.Group()
        self.mobs_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.wall_group = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.eagle = self.createEagle()

        # Создаем спрайты стен
        self.createWalls()

        # для игроков ДОЛЖНО быть минимум и максимум 2
        # доступные клетки для спавна (В ДАННЫЙ МОМЕНТ УЧИТЫВАЕТСЯ
        # РЕЖИМ ЛИШЬ ТОЛЬКО НА 2 ЧЕЛОВЕК МАКСИМУМ)
        self.TILES_FOR_PLAYERS = self.map.get_tiled_by_id(TILE_FOR_PLAYERS)
        self.TILES_FOR_MOBS = self.map.get_tiled_by_id(TILE_FOR_MOBS)
        # print(self.TILES_FOR_PLAYERS)

        self.player1 = None
        self.player2 = None
        if type_game == 1 or type_game == 2:
            self.player1 = Player(self, self.TILES_FOR_PLAYERS[0],
                                  self.TILE_SIZE, player=1)
            if type_game == 2:
                self.player2 = Player(self, self.TILES_FOR_PLAYERS[1],
                                      self.TILE_SIZE, player=2)
        elif type_game == 3:
            raise Exception('Онлайн еще не готов')
        else:
            raise Exception('Неверный тип игры')
        if self.player1 is not None:
            self.player1.add(self.player_group, self.all_sprites)
        if self.player2 is not None:
            self.player2.add(self.player_group, self.all_sprites)
        self.bot_manager = BotManager(self)

    def createWalls(self):
        if not self.map.check_('walls'):
            return
        for i in self.map.get_objects('walls'):
            x, y = i.x / self.map.koeff + OFFSET, i.y / self.map.koeff + OFFSET
            wall = Wall(x, y, self.map.get_tile_id(i.gid), self.TILE_SIZE)
            wall.add(self.all_sprites, self.wall_group)

    def createEagle(self):
        tile = self.map.get_objects('eagle')[0]
        x, y = tile.x / self.map.koeff + OFFSET, tile.y / self.map.koeff + OFFSET
        return Eagle(self, x, y, self.TILE_SIZE)

    def update(self, events=None):
        if self.eagle.isBroken:
            self.game_over()
        self.player_group.update()
        self.bullets.update()
        self.bot_manager.update()

    def render(self):
        # Отрисовка по слоям.
        """
        Карта может содержать подобные слои.
        0. ground
        1. spawn_players
        2. spawn_bots
        3. trees
        4. eagle
        5. walls
        """
        # Отрисовка земли
        self.map.render_layer(screen, 'ground')
        # render player and bullet and mobs
        self.all_sprites.draw(screen)
        # Отрисовка деревьев
        self.map.render_layer(screen, 'trees')

    def game_over(self):
        print('game_over')
        # quit()


fullscreen = False


if __name__ == '__main__':
    clock = pygame.time.Clock()
    running = True
    game = Game(2, 1)
    while running:
        screen.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    screen = pygame.display.set_mode((event.w, event.h),
                                                     pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                # print(pygame.key.name(event.key))
                if event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(monitor_size,
                                                         pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode(
                            (screen.get_width(), screen.get_height()),
                            pygame.RESIZABLE)
        game.update()
        game.render()

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
