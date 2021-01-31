import sys
import os
import pygame
import random
import time

view = 'right'
view_bot = 'right'
pygame.init()
level_map_width, level_map_height = 26, 18
size = width, height = 1300, 900
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Миссия "Новый Год!"')
clock = pygame.time.Clock()
player = None

label_font = pygame.font.SysFont('mistral', 48)
label_font_looser = pygame.font.SysFont('mistral', 148)
label_font_menu = pygame.font.SysFont('mistral', 48)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
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


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
collection_items_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
protective_items_group = pygame.sprite.Group()
decorates_group = pygame.sprite.Group()
check_lose_items_group = pygame.sprite.Group()

tmp_m = []
fon = pygame.image.load('data/fon.jpg')
player_ = pygame.image.load("data/Terrain (16x16).png")
floor = pygame.image.load("data/box_2.0.png")
floor = pygame.transform.scale(floor, (50, 50))

tile_images = {
    'santa': load_image('santa.png'),
    'empty': floor
}

collection_items_images = {
    'coin': load_image('money.png'),
    'present': load_image('present.png'),
    'present_2': load_image('present_2.png'),
    'present_3': load_image('present_3.png'),
}

decorates_images = {
    'green_tree': load_image('green_tree.png'),
    'snow_tree': load_image('snow_tree.png'),
    'green_beaurf_tree': load_image('green_beaurf_tree.png'),
    'snow_beaurf_tree': load_image('snow_beaurf_tree.png'),
}

enemies_types = {
    'enemy_bot': load_image('Run (322x32).png'),
}

protective_items = {
    'sword': load_image('sword.png'),
    'last_heart': load_image('heart.png'),
}

check_lose_items = {
    'present_counter': load_image('present_counter.png')
}

player_image = load_image('Run (32x32).png')

tile_width = tile_height = 50
collections_items_width_plus, collections_items_height_plus = 10, 8
max_height = height // tile_height
max_width = width // tile_width


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Decorates(pygame.sprite.Sprite):
    def __init__(self, decorate_type, pos_x, pos_y):
        super().__init__(decorates_group, all_sprites)
        self.image = decorates_images[decorate_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class CheckLoseItems(pygame.sprite.Sprite):
    def __init__(self, check_lose_item_type, pos_x, pos_y):
        super().__init__(check_lose_items_group, all_sprites)
        self.image = check_lose_items[check_lose_item_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)


class CollectionItems(pygame.sprite.Sprite):
    def __init__(self, collection_item_type, pos_x, pos_y):
        super().__init__(collection_items_group, all_sprites)
        self.image = collection_items_images[collection_item_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + collections_items_width_plus, tile_height * pos_y + collections_items_height_plus)
        self.mask = pygame.mask.from_surface(self.image)


class ProtectiveItems(pygame.sprite.Sprite):
    def __init__(self, protective_item_type, pos_x, pos_y):
        super().__init__(protective_items_group, all_sprites)
        self.image = protective_items[protective_item_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(player_image, 12, 1, pos_x, pos_y)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (35, 35))
        self.pos = pos_x, pos_y
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows, pos_x, pos_y):
        self.rect = pygame.Rect(pos_x + 7, pos_y + 7, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, turn):
        global view
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (35, 35))
        if turn == 'left' or view == 'left' and turn != 'right':
            view = 'left'
            self.image = pygame.transform.flip(self.frames[self.cur_frame], 90, 0)
        elif turn == 'right' or view == 'right' and turn != 'left':
            view = 'right'
            self.image = self.frames[self.cur_frame]


class Enemies(pygame.sprite.Sprite):
    def __init__(self, enemy_type, pos_x, pos_y):
        super().__init__(enemies_group, all_sprites)
        self.frames = []
        self.cut_sheet(enemies_types[enemy_type], 12, 1, pos_x, pos_y)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.pos = (pos_x, pos_y)

    def cut_sheet(self, sheet, columns, rows, pos_x, pos_y):
        self.rect = pygame.Rect(pos_x + 7, pos_y + 7,
                                sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, turn_bot):
        global view_bot
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (35, 35))
        if turn_bot == 'left' or view_bot == 'left' and turn_bot != 'right':
            view_bot = 'left'
            self.image = pygame.transform.flip(self.frames[self.cur_frame], 90, 0)
        elif turn_bot == 'right' or view_bot == 'right' and turn_bot != 'left':
            view_bot = 'right'
            self.image = self.frames[self.cur_frame]


def generate_level_floor(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] in '.^;':
                Tile('empty', x, y)
            elif level[y][x] == '?':
                Tile('empty', x, y)
                Tile('santa', x + 0.3, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x * tile_width, y * tile_height)
    # возвращаем игрока и размер поля
    return new_player, x, y


def generate_level_collection_items(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == ';':
                CollectionItems(random.choice(list(collection_items_images.keys())), x, y)


def generate_level_enemies(level):
    new_bot, enemy_type, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] in '@.;':
                Tile('empty', x, y)
            elif level[y][x] == '^':
                Decorates('snow_tree', x, y)
            elif level[y][x] == '!':
                enemy_type = 'enemy_bot'
                Tile('empty', x, y)
                new_bot = Enemies(enemy_type, x * tile_width, y * tile_height)
    return new_bot, x, y


def generate_level_decorates(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '^':
                Decorates(random.choice(list(decorates_images.keys())), x, y)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def check_for_movement(move):
    x, y = player.pos[0] // tile_width, player.pos[1] // tile_height

    if move == 'up':
        if y > 0 and level_map[y - 1][x] in '.@!;':
            return True

    elif move == 'down':
        if y < max_height - 1 and level_map[y + 1][x] in '.@!;':
            return True

    elif move == 'left':
        if x > 0 and level_map[y][x - 1] in '.@!;':
            return True

    elif move == 'right':
        if x < max_width - 1 and level_map[y][x + 1] in '.@;!':
            return True

    return False


def select_level():
    screen.blit(fon, (0, 0))
    for i in range(1, 11):
        screen.blit(label_font.render(str(i), 1, (210, 200, 200)), (350 + 50 * i, 250))
    screen.blit(label_font.render(u'Назад', 1, (210, 200, 200)), (580, 650))


def new_game_f():
    intro_text = ["В этой игре ваша основная цель-",
                  "Собрать как можно больше подарков,",
                  "Чтобы спасти Новый Год.",
                  "Некоторые противники этого праздника",
                  "Решили его испортить.",
                  "Они ходят по карте",
                  "И при первой же возможности",
                  "Уничтожают подарки.",
                  "Не дайте им это сделать. Удачи!!!"]
    screen.blit(fon, (0, 0))
    text_coord = 580
    for line in intro_text:
        screen.blit(label_font.render(line, 1, (0, 0, 0)), (450, text_coord - 450))
        string_rendered = label_font.render(line, 1, (0, 0, 0))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        text_coord += intro_rect.height

    screen.blit(label_font.render(u'Назад', 1, (0, 0, 0)), (580, 650))


def menu():
    screen.blit(fon, (0, 0))
    screen.blit(label_font.render(u'Играть', 1, (210, 200, 200)), (585, 250))
    screen.blit(label_font.render(u'Об игре', 1, (210, 200, 200)), (565, 350))
    screen.blit(label_font.render(u'Выбор уровня', 1, (210, 200, 200)), (555, 450))
    screen.blit(label_font.render(u'Выход', 1, (210, 200, 200)), (585, 550))


def start_screen():
    screen.blit(fon, (0, 0))

    flag_select_level, flag_new_game = False, False

    menu()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if not flag_select_level and not flag_new_game:
                if event.type == pygame.MOUSEMOTION:
                    if 700 > event.pos[0] > 587 and 285 > event.pos[1] > 252:
                        screen.blit(label_font.render(u'Играть', 1, (63, 82, 119)), (585, 250))
                    elif 732 > event.pos[0] > 567 and 385 > event.pos[1] > 352:
                        screen.blit(label_font.render(u'Об игре', 1, (63, 82, 119)), (565, 350))
                    elif 782 > event.pos[0] > 537 and 495 > event.pos[1] > 442:
                        screen.blit(label_font.render(u'Выбор уровня', 1, (63, 82, 119)), (555, 450))
                    elif 700 > event.pos[0] > 587 and 585 > event.pos[1] > 552:
                        screen.blit(label_font.render(u'Выход', 1, (63, 82, 119)), (585, 550))
                    else:
                        menu()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 700 > event.pos[0] > 587 and 285 > event.pos[1] > 252:
                        return
                    elif 732 > event.pos[0] > 567 and 385 > event.pos[1] > 352:
                        new_game_f()
                        flag_new_game = True
                    elif 782 > event.pos[0] > 537 and 485 > event.pos[1] > 452:
                        select_level()
                        flag_select_level = True
                    elif 700 > event.pos[0] > 587 and 585 > event.pos[1] > 552:
                        quit()

            elif flag_select_level:
                if event.type == pygame.MOUSEMOTION:
                    if 662 > event.pos[0] > 582 and 685 > event.pos[1] > 652:
                        screen.blit(label_font.render(u'Назад', 1, (63, 82, 119)), (580, 650))
                    elif 425 >= event.pos[0] >= 352 \
                            and 290 >= event.pos[1] >= 252:
                        screen.blit(label_font.render(u'1', 1, (63, 82, 119)), (400, 250))
                    else:
                        select_level()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 662 > event.pos[0] > 582 and 685 > event.pos[1] > 652:
                        flag_select_level = False
                        menu()
                    elif 425 >= event.pos[0] >= 352 \
                            and 290 >= event.pos[1] >= 252:
                        return

            elif flag_new_game:
                if event.type == pygame.MOUSEMOTION:
                    if 662 > event.pos[0] > 582 \
                            and 685 > event.pos[1] > 652:
                        screen.blit(label_font.render(u'Назад', 1, (63, 82, 119)), (580, 650))
                    elif 512 >= event.pos[0] >= 467 \
                            and 380 >= event.pos[1] >= 352:
                        screen.blit(label_font.render(u'Да', 1, (63, 82, 119)), (465, 350))
                    elif 700 >= event.pos[0] >= 637 \
                            and 380 >= event.pos[1] >= 352:
                        screen.blit(label_font.render(u'Нет', 1, (63, 82, 119)), (635, 350))
                    else:
                        new_game_f()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 662 > event.pos[0] > 582 and 685 > event.pos[1] > 652 \
                            or (512 >= event.pos[0] >= 467
                                and 380 >= event.pos[1] >= 352) \
                            or (700 >= event.pos[0] >= 637
                                and 380 >= event.pos[1] >= 352):
                        flag_new_game = False
                        menu()

        pygame.display.flip()
        clock.tick(60)


def selection_menu_lose():
    screen.blit(fon, (0, 0))
    screen.blit(label_font_looser.render(u'Вы проиграли', 1, (210, 200, 200)), (335, 250))
    screen.blit(label_font_menu.render(u'В меню', 1, (210, 200, 200)), (565, 550))


def selection_menu_won():
    screen.blit(fon, (0, 0))
    screen.blit(label_font_looser.render(u'Вы выиграли', 1, (210, 200, 200)), (335, 250))
    screen.blit(label_font_menu.render(u'В меню', 1, (210, 200, 200)), (565, 550))


def won():
    screen.blit(fon, (0, 0))

    selection_menu_won()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.MOUSEMOTION:
                if 700 > event.pos[0] > 587 and 585 > event.pos[1] > 552:
                    screen.blit(label_font_menu.render(u'В меню', 1, (63, 82, 119)), (565, 550))
                else:
                    selection_menu_won()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if 700 > event.pos[0] > 587 and 585 > event.pos[1] > 552:
                    return

        pygame.display.flip()
        clock.tick(60)


def lose():
    screen.blit(fon, (0, 0))

    selection_menu_lose()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            if event.type == pygame.MOUSEMOTION:
                if 700 > event.pos[0] > 587 and 585 > event.pos[1] > 552:
                    screen.blit(label_font_menu.render(u'В меню', 1, (63, 82, 119)), (565, 550))
                else:
                    selection_menu_lose()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if 700 > event.pos[0] > 587 and 585 > event.pos[1] > 552:
                    return

        pygame.display.flip()
        clock.tick(60)


def robot_position(pos, level):
    global tmp_m, flag_m, list_of_pos, flag_c, fl, fl_2
    fl = True
    fl_2 = True
    for m in range(len(level)):
        for w in range(len(level[m])):
            if level[m][w] == ';' and (w, m) not in tmp and (w, m) not in tmp_m:
                tmp.append((w, m))
    if flag_c:
        random.shuffle(tmp)
        flag_c = False
    for k in tmp:
        list_of_pos = [k]
        break

    bot_pos = (pos[0] // tile_width, pos[1] // tile_height)
    while True:
        size_list_of_pos = len(list_of_pos)
        for i in range(len(list_of_pos)):
            if (list_of_pos[i][0] + 1, list_of_pos[i][1]) == bot_pos \
                    or (list_of_pos[i][0] - 1, list_of_pos[i][1]) == bot_pos \
                    or (list_of_pos[i][0], list_of_pos[i][1] - 1) == bot_pos \
                    or (list_of_pos[i][0], list_of_pos[i][1] + 1) == bot_pos:
                return (list_of_pos[i][0] * tile_width, list_of_pos[i][1] * tile_height)
            else:
                if list_of_pos[i][0] < max_width - 1:
                    if level[list_of_pos[i][1]][list_of_pos[i][0] + 1] == '.' \
                            and (list_of_pos[i][0] + 1, list_of_pos[i][1]) not in list_of_pos:
                        list_of_pos.append((list_of_pos[i][0] + 1, list_of_pos[i][1]))

                if list_of_pos[i][1] < max_height - 1:
                    if level[list_of_pos[i][1] + 1][list_of_pos[i][0]] == '.' \
                            and (list_of_pos[i][0], list_of_pos[i][1] + 1) not in list_of_pos:
                        list_of_pos.append((list_of_pos[i][0], list_of_pos[i][1] + 1))

                if list_of_pos[i][1] > 0 and level[list_of_pos[i][1] - 1][list_of_pos[i][0]] == '.' \
                        and (list_of_pos[i][0], list_of_pos[i][1] - 1) not in list_of_pos:
                    list_of_pos.append((list_of_pos[i][0], list_of_pos[i][1] - 1))

                if list_of_pos[i][0] > 0 and level[list_of_pos[i][1]][list_of_pos[i][0] - 1] == '.' \
                        and (list_of_pos[i][0] - 1, list_of_pos[i][1]) not in list_of_pos:
                    list_of_pos.append((list_of_pos[i][0] - 1, list_of_pos[i][1]))

        if size_list_of_pos == len(list_of_pos):
            return pos


def moving_the_robot(pos, level, turn):
    turn_bot_ = None
    if not turn is None:
        if (pos[0] % tile_width == 0
                and pos[1] % tile_height == 0):
            turn = None
        else:
            if turn[0] == 1:
                turn_bot_ = 'right'
            elif turn[0] == -1:
                turn_bot_ = 'left'
            elif turn[1] == 1:
                turn_bot_ = 'down'
            elif turn[1] == -1:
                turn_bot_ = 'up'
            bot.update(turn_bot=turn_bot_)
            bot.rect = bot.rect.move(2 * turn[0], 2 * turn[1])
            bot.pos = (bot.pos[0] + (2 * turn[0]), bot.pos[1] + (2 * turn[1]))
    else:
        new_pos = robot_position(pos, level)
        if new_pos[0] - bot.pos[0] > 0:
            w = 1
        elif new_pos[0] - bot.pos[0] < 0:
            w = -1
        else:
            w = 0

        if new_pos[1] - bot.pos[1] > 0:
            m = 1
        elif new_pos[1] - bot.pos[1] < 0:
            m = -1
        else:
            m = 0

        if w == 1:
            turn_bot_ = 'right'
        elif w == -1:
            turn_bot_ = 'left'
        elif m == 1:
            turn_bot_ = 'down'
        elif m == -1:
            turn_bot_ = 'up'

        bot.update(turn_bot=turn_bot_)
        bot.rect = bot.rect.move(2 * w, 2 * m)
        bot.pos = (bot.pos[0] + (2 * w), bot.pos[1] + (2 * m))
        turn = (w, m)

    return turn


if __name__ == '__main__':
    while True:
        fl = True
        fl_2 = True
        flag_c = True
        tmp = []
        list_of_pos = []
        tmp_m = []
        all_sprites = pygame.sprite.Group()
        tiles_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()
        collection_items_group = pygame.sprite.Group()
        enemies_group = pygame.sprite.Group()
        protective_items_group = pygame.sprite.Group()
        decorates_group = pygame.sprite.Group()
        check_lose_items_group = pygame.sprite.Group()

        start_screen()
        screen.fill((0, 0, 0))

        level_map = load_level('level1.txt')
        bot, level_x, level_y = generate_level_enemies(level_map)
        player, level_x, level_y = generate_level_floor(level_map)
        generate_level_collection_items(level_map)
        for i in range(1, 4):
            ProtectiveItems('sword', level_map_width - i, 0)
        for j in range(1, 4):
            CheckLoseItems('present_counter', level_map_width - j, 1)
        generate_level_decorates(level_map)

        running, turn, turn_enemy, res_, flag = True, None, None, None, True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            if enemies_group and collection_items_group:
                turn_enemy = moving_the_robot(bot.pos, level_map, turn_enemy)
            if not enemies_group:
                for y in range(len(level_map)):
                    for x in range(len(level_map[y])):
                        if level_map[y][x] == '!':
                            enemy_type = 'enemy_bot'
                            Tile('empty', x, y)
                            bot = Enemies(enemy_type, x * tile_width, y * tile_height)
            if not turn is None:
                if (player.pos[0] % tile_width == 0
                        and player.pos[1] % tile_height == 0):
                    turn = None
                else:
                    if turn == 'down':
                        player.update(turn='down')
                        player.rect = player.rect.move(0, 2)
                        player.pos = (player.pos[0], player.pos[1] + 2)
                        check_coin_x = player.pos[0] // 50
                        check_coin_y = player.pos[1] // 50

                    elif turn == 'up':
                        player.update(turn='up')
                        player.rect = player.rect.move(0, -2)
                        player.pos = (player.pos[0], player.pos[1] - 2)

                    elif turn == 'left':
                        player.update(turn='left')
                        player.rect = player.rect.move(-2, 0)
                        player.pos = (player.pos[0] - 2, player.pos[1])

                    elif turn == 'right':
                        player.update(turn='right')
                        player.rect = player.rect.move(2, 0)
                        player.pos = (player.pos[0] + 2, player.pos[1])

            else:
                key = pygame.key.get_pressed()

                if key[pygame.K_DOWN]:
                    if check_for_movement('down'):
                        turn = 'down'
                        player.update(turn='down')
                        player.rect = player.rect.move(0, 2)
                        player.pos = (player.pos[0], player.pos[1] + 2)

                elif key[pygame.K_UP]:
                    if check_for_movement('up'):
                        turn = 'up'
                        player.update(turn='up')
                        player.rect = player.rect.move(0, -2)
                        player.pos = (player.pos[0], player.pos[1] - 2)
                elif key[pygame.K_LEFT]:
                    if check_for_movement('left'):
                        turn = 'left'
                        player.update(turn='left')
                        player.rect = player.rect.move(-2, 0)
                        player.pos = (player.pos[0] - 2, player.pos[1])

                elif key[pygame.K_RIGHT]:
                    if check_for_movement('right'):
                        turn = 'right'
                        player.update(turn='right')
                        player.rect = player.rect.move(2, 0)
                        player.pos = (player.pos[0] + 2, player.pos[1])

                if player.pos == (800, 550):
                    if key[pygame.K_r]:
                        pygame.mixer.music.load('data/marry_christmas.ogg')
                        pygame.mixer.music.set_volume(1.3)
                        pygame.mixer.music.play()
                        time.sleep(4)
                        pygame.mixer.music.load('data/damage.mp3')
                        pygame.mixer.music.set_volume(0.1)
                        tmp_len = len(enemies_group)
                        for object_ in enemies_group:
                            object_.kill()
                        for _ in range(tmp_len):
                            pygame.mixer.music.play()
                            time.sleep(0.1)
                if tmp:
                    for j in range(len(tmp)):
                        if fl:
                            if tmp[j] == (player.pos[0] // 50, player.pos[1] // 50):
                                for object_ in collection_items_group:
                                    if pygame.sprite.collide_mask(player, object_):
                                        if isinstance(object_, CollectionItems):
                                            pygame.mixer.music.load(
                                                'data/collection_items_sound.ogg')
                                            tmp_m.append(tmp[j])
                                            del tmp[j]
                                            pygame.mixer.music.set_volume(0.1)
                                            pygame.mixer.music.play()
                                            object_.kill()
                                            flag_m = True
                                            if not collection_items_group:
                                                pygame.mixer.music.load('data/win.ogg')
                                                pygame.mixer.music.set_volume(1.5)
                                                pygame.mixer.music.play()
                                                running = False
                                                res_ = True
                                            fl = False
                if tmp:
                    for k in range(len(tmp)):
                        if fl_2:
                            if tmp[k] == (bot.pos[0] // 50, bot.pos[1] // 50):
                                for object_ in collection_items_group:
                                    if pygame.sprite.collide_mask(bot, object_):
                                        if isinstance(object_, CollectionItems):
                                            pygame.mixer.music.load(
                                                'data/bot_get_collection_item.ogg'
                                            )
                                            pygame.mixer.music.set_volume(0.1)
                                            pygame.mixer.music.play()
                                            object_.kill()
                                            tmp_m.append(tmp[k])
                                            del tmp[k]
                                            flag_m = True
                                            for x in check_lose_items_group:
                                                x.kill()
                                                break
                                            if not collection_items_group:
                                                pygame.mixer.music.load('data/win.ogg')
                                                pygame.mixer.music.set_volume(1.5)
                                                pygame.mixer.music.play()
                                                running = False
                                                res_ = True
                                            if not check_lose_items_group:
                                                pygame.mixer.music.load('data/game_over.ogg')
                                                pygame.mixer.music.play()
                                                running = False
                                                res_ = False
                                            fl_2 = False

                for object_ in enemies_group:
                    if pygame.sprite.collide_mask(player, object_):
                        if isinstance(object_, Enemies):
                            if protective_items_group and flag:
                                pygame.mixer.music.load('data/damage.mp3')
                                pygame.mixer.music.set_volume(0.1)
                                pygame.mixer.music.play()
                                for x in protective_items_group:
                                    x.kill()
                                    object_.kill()
                                    if len(protective_items_group) == 0 and flag:
                                        ProtectiveItems('last_heart', level_map_width - 1, 0)
                                        flag = False
                                    break
                            else:
                                player.kill()
                                for y in protective_items_group:
                                    y.kill()
                                    pygame.mixer.music.load('data/game_over.ogg')
                                    pygame.mixer.music.play()
                                    running = False
                                    res_ = False
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            collection_items_group.draw(screen)
            player_group.draw(screen)
            enemies_group.draw(screen)
            decorates_group.draw(screen)
            protective_items_group.draw(screen)
            check_lose_items_group.draw(screen)

            clock.tick(60)
            pygame.display.flip()

        screen.fill((0, 0, 0))
        if res_ is False:
            lose()
        else:
            won()

pygame.quit()
