import os
import sys
import pygame
import random


pygame.init()
WIDTH = 700
HEIGHT = 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))

FPS = 60

K_JUMP = pygame.K_SPACE
K_LAY = pygame.K_LSHIFT
DINO_SPEED_Y = 11
DINO_VECTOR_Y = 0.5

DINO_SIZE = (55, 60)
DINO_SIZE_LAY = (63, 40)
CACTUS_SIZE = (40, 55)
DED_MOROZ_SIZE = (112, 60)


def terminate():
    pygame.quit()
    sys.exit()


def restart():
    global dino, place1, place2, spawn_distance, game_speed

    for sprite in all_sprites:
        sprite.kill()
    dino = Dino()
    place1 = Place(0)
    place2 = Place(699)
    spawn_distance = 0
    game_speed = 250


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
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


class Dino(pygame.sprite.Sprite):
    images = [pygame.transform.scale(load_image('dino1.png', -1), DINO_SIZE),
              pygame.transform.scale(load_image('dino2.png', -1), DINO_SIZE),
              pygame.transform.scale(load_image('dino3.png', -1), DINO_SIZE),
              pygame.transform.scale(load_image('dino2.png', -1), DINO_SIZE)]
    die_img = pygame.transform.scale(load_image('dino_die.png', -1), DINO_SIZE)
    jump_img = pygame.transform.scale(load_image('dino_jump.png', -1), DINO_SIZE)
    down_images = [pygame.transform.scale(load_image('dino_lay1.png', -1), DINO_SIZE_LAY),
                   pygame.transform.scale(load_image('dino_lay2.png', -1), DINO_SIZE_LAY)]
    jump_sound = pygame.mixer.Sound('data/jump.mp3')
    jump_sound.set_volume(0.5)
    death_sound = pygame.mixer.Sound('data/death.mp3')
    death_sound.set_volume(0.5)

    def __init__(self):
        super().__init__(dino_group, all_sprites)
        self.image = Dino.images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = 100, 190
        self.score = 0
        self.frame = 0
        self.vy = 0
        self.vector_y = DINO_VECTOR_Y
        self.state = 'run'

    def update(self):
        global game_speed

        if self.state != 'die' and self.frame % 4 == 1:
            self.score += 1

        self.frame += 1
        if self.frame == 12:
            self.frame = 0
        if self.state == 'run':
            self.image = Dino.images[self.frame // 3]
        elif self.state == 'lay':
            self.image = Dino.down_images[self.frame // 6]
        self.mask = pygame.mask.from_surface(self.image)

        if self.state == 'jump':
            self.rect.y -= self.vy
            self.vy -= self.vector_y
            if self.rect.y >= 190:
                self.vy = 0
                self.rect.y = 190
                self.state = 'run'
                self.image = Dino.images[0]
                self.frame = 0
                create_particles((130, 251))
                self.vector_y = DINO_VECTOR_Y

        die_flag = False
        for cactus in cactus_group:
            if pygame.sprite.collide_mask(self, cactus):
                die_flag = True
        for ded in ded_moroz_group:
            if pygame.sprite.collide_mask(self, ded):
                die_flag = True
        if die_flag:
            Dino.death_sound.play()
            game_speed = 0
            self.state = 'die'
            self.image = Dino.die_img
            self.frame = 0
            with open('data/statistics.txt', 'a') as file:
                file.write(f'{str(self.score)}\n')
            death_screen()

    def event(self, event):
        if event.type == pygame.KEYDOWN and event.key == K_JUMP and self.state != 'jump' and self.state != 'die':
            self.vy = DINO_SPEED_Y
            self.state = 'jump'
            self.image = Dino.jump_img
            self.rect.y = 190
            Dino.jump_sound.play()
        elif event.type == pygame.KEYDOWN and event.key == K_LAY and self.state != 'jump' and self.state != 'die':
            self.state = 'lay'
            self.image = Dino.down_images[0]
            self.rect.y = 210
        elif event.type == pygame.KEYDOWN and event.key == K_LAY and self.state == 'jump':
            self.vector_y = DINO_VECTOR_Y * 2
        elif event.type == pygame.KEYUP and event.key == K_LAY and self.state == 'jump':
            self.vector_y = DINO_VECTOR_Y
        elif event.type == pygame.KEYUP and event.key == K_LAY and self.state == 'lay':
            self.state = 'run'
            self.image = Dino.images[0]
            self.rect.y = 190
        self.frame = 0


class Cactus(pygame.sprite.Sprite):
    images = [pygame.transform.scale(load_image('snowman1.png', -1), CACTUS_SIZE),
              pygame.transform.scale(load_image('snowman2.png', -1), CACTUS_SIZE),
              pygame.transform.scale(load_image('tree1.png', -1), CACTUS_SIZE),
              pygame.transform.scale(load_image('tree2.png', -1), CACTUS_SIZE),
              pygame.transform.scale(load_image('snow.png', -1), CACTUS_SIZE)]

    def __init__(self, shift):
        super().__init__(cactus_group, all_sprites)
        self.image = Cactus.images[random.randint(0, len(Cactus.images) - 1)]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = 700 + shift, 195
        self.v = game_speed

    def update(self):
        self.v = game_speed
        self.rect.x -= self.v / FPS
        if self.rect.x <= -25:
            self.kill()


class Dedmoroz(pygame.sprite.Sprite):
    images = [pygame.transform.scale(load_image('ded_moroz1.png', -1), DED_MOROZ_SIZE),
              pygame.transform.scale(load_image('ded_moroz2.png', -1), DED_MOROZ_SIZE),
              pygame.transform.scale(load_image('ded_moroz3.png', -1), DED_MOROZ_SIZE),
              pygame.transform.scale(load_image('ded_moroz2.png', -1), DED_MOROZ_SIZE)]

    def __init__(self, shift):
        super().__init__(ded_moroz_group, all_sprites)
        self.image = Dedmoroz.images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = 700 + shift, random.choice([200, 150, 125])
        self.v = game_speed + 20
        self.frame = 0

    def update(self):
        self.v = game_speed + 20
        self.frame += 1
        if self.frame == 20:
            self.frame = 0
        self.image = Dedmoroz.images[self.frame // 5]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x -= self.v / FPS


class Place(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('place.png'), (WIDTH + 50, 50))

    def __init__(self, x):
        super().__init__(place_border, all_sprites)
        self.image = Place.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = x, 250
        self.v = game_speed

    def update(self):
        self.v = game_speed
        self.rect.x -= self.v / FPS
        if self.rect.x <= -699:
            self.rect.x = 700


class Particle(pygame.sprite.Sprite):
    img = [pygame.transform.scale(load_image("particle1.png"), (6, 6)),
           pygame.transform.scale(load_image("particle2.png"), (3, 3)),
           pygame.transform.scale(load_image("particle3.png"), (3, 3))]

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(Particle.img)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = 1

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.y >= 250:
            self.kill()


def create_particles(position):
    particle_count = 20
    vx = range(int(-game_speed // 60 - 5), int(-game_speed // 60 + 5))
    vy = range(-10, -5)
    for _ in range(particle_count):
        Particle(position, random.choice(vx), random.choice(vy))


def statistics_screen():
    screen.fill('#CCCCCC')
    screen.fill('#FFFFFF', (100, 50, 500, 200))

    with open('data/statistics.txt', 'r') as file:
        stat = list(map(int, file.read().split('\n')[:-1]))
        max_score = max(stat)
        min_score = min(stat)
        sum_score = sum(stat)
        count_games = len(stat)
        av_score = sum_score / count_games

    statistics_text = ["Статистика игрока:",
                       "Лучший результат: {}".format(max_score),
                       "Худший результат: {}".format(min_score),
                       "Средний результат: {}".format(av_score),
                       "Всего набрано: {}".format(sum_score),
                       "Попыток сделано: {}".format(count_games)]

    font = pygame.font.Font(None, 30)
    text_coord = 55
    for line in statistics_text:
        string_rendered = font.render(line, 1, "#000000")
        stat_rect = string_rendered.get_rect()
        text_coord += 10
        stat_rect.top = text_coord
        stat_rect.x = 110
        text_coord += stat_rect.height
        screen.blit(string_rendered, stat_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    intro_text = ["Cristmas Dino                    Свободный режим                   Уровни", "",
                  "Управление:",
                  "SPACE - прыжок",
                  "LSHIFT - нагнуться"]
    draw_flag = True

    while True:
        if draw_flag:
            screen.fill('#000000')
            fon = load_image('fon.jpg')
            screen.blit(fon, (0, 0))

            font = pygame.font.Font(None, 30)
            text_coord = 50
            for line in intro_text:
                string_rendered = font.render(line, 1, "#000000")
                intro_rect = string_rendered.get_rect()
                text_coord += 10
                intro_rect.top = text_coord
                intro_rect.x = 10
                text_coord += intro_rect.height
                screen.blit(string_rendered, intro_rect)

            screen.fill('#FFFFFF', (315, 100, 100, 100))
            screen.fill('#FFFFFF', (565, 100, 100, 100))
            statistics_img = pygame.transform.scale(load_image('statistics.png', -1), (30, 30))
            screen.blit(statistics_img, (660, 10))

            draw_flag = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and 315 <= event.pos[0] <= 415 and 100 <= event.pos[1] <= 200:
                restart()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and 660 <= event.pos[0] <= 700 and 0 <= event.pos[1] <= 40:
                statistics_screen()
                draw_flag = True
        pygame.display.flip()
        clock.tick(FPS)


def death_screen():
    with open('data/statistics.txt', 'r') as file:
        max_score = max(map(int, file.read().split('\n')[:-1]))

    all_sprites.draw(screen)

    death_text = ["Счёт:",
                  str(dino.score),
                  "Лучший счёт:",
                  str(max_score),
                  "В меню (ESC)",
                  "Возродиться (SPACE)"]

    font = pygame.font.Font(None, 30)
    text_coord = 20
    for line in death_text:
        string_rendered = font.render(line, 1, "#AA0000")
        death_rect = string_rendered.get_rect()
        text_coord += 10
        death_rect.top = text_coord
        death_rect.x = 260
        text_coord += death_rect.height
        screen.blit(string_rendered, death_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                start_screen()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                restart()
                return
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    game_speed = 250

    running = True
    all_sprites = pygame.sprite.Group()
    dino_group = pygame.sprite.Group()
    cactus_group = pygame.sprite.Group()
    ded_moroz_group = pygame.sprite.Group()
    place_border = pygame.sprite.Group()

    clock = pygame.time.Clock()

    dino = Dino()
    place1 = Place(0)
    place2 = Place(699)
    spawn_distance = 0
    count_spawn = 0
    type_spawn = 0

    start_screen()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                dino.event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                start_screen()

        if spawn_distance <= 0:
            if dino.score <= 300:
                type_spawn = 1
            else:
                type_spawn = random.randint(1, 4)
            if type_spawn < 4:
                count_spawn = random.randint(5, 15) // 5
                for i in range(count_spawn):
                    _ = Cactus(i * 20)
            elif type_spawn == 4:
                k = 40 if spawn_distance <= 65 else 0
                _ = Dedmoroz(k)
            spawn_distance = random.randint(50 // (game_speed // 500 + 1), 120 // (game_speed // 250))

        screen.fill('#55DDFF')

        game_speed += 0.04
        spawn_distance -= 1

        all_sprites.update()
        all_sprites.draw(screen)

        font = pygame.font.Font(None, 20)
        score = font.render(str(dino.score), 1, "#000000")
        score_rect = score.get_rect()
        score_rect.top = 10
        score_rect.x = 650
        screen.blit(score, score_rect)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
