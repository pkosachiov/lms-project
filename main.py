#импортирование всех библиотек
import pygame
import random
import copy
import os
import pickle

class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = generate_game_map(width, height)
        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 50

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
    #обработка игровой карты
    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                self.board[i][j].x = i
                self.board[i][j].y = j
                image = pygame.transform.scale(load_image(self.board[i][j].img), (self.cell_size, self.cell_size))
                screen.blit(image, (j*self.cell_size + self.left, i*self.cell_size + self.top))
        image = pygame.transform.scale(load_image(main_player.img), (self.cell_size, self.cell_size))
        screen.blit(image, ((self.width//2)*self.cell_size + self.left, (self.height//2)*self.cell_size + self.top))

    #функция для перемещения вниз
    def move_down(self):
        for i in range(len(self.board)-1):
            for j in range(len(self.board[i])):
                self.board[i][j] = self.board[i+1][j]
        for i in range(len(self.board[-1])):
            self.board[-1][i] = generate_cell(all_cell, world)
        return(self.board)

    #функция для перемещения вверх
    def move_up(self):
        for i in range(len(self.board)-1, 0, -1):
            for j in range(len(self.board[i])):
                self.board[i][j] = self.board[i-1][j]
        for i in range(len(self.board[0])):
            self.board[0][i] = generate_cell(all_cell, world)
        return(self.board)

    #функция для перемещения вправо
    def move_right(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i]) - 1):
                self.board[i][j] = self.board[i][j + 1]
        for i in range(len(self.board)):
            self.board[i][-1] = generate_cell(all_cell, world)
        return(self.board)

    #функция для перемещения влево
    def move_left(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])-1, 0, -1):
                self.board[i][j] = self.board[i][j - 1]
        for i in range(len(self.board)):
            self.board[i][0] = generate_cell(all_cell, world)
        return(self.board)

#класс с клетками
class map_cell:
#имя в дебаге, имя в игре, обозначение на карте, шанс выпадения
    def __init__(self, name, game_name, img, chance, x = None, y = None):
        self.name = name
        self.game_name = game_name
        self.img = img
        self.chance = chance
        self.x = x
        self.y = y

#класс предмет
class item:
    def __init__(self, name, game_name, img, description, count_used, heal_health, heal_hungry, heal_water, chance = None, preuse = False):
        self.name = name
        self.game_name = game_name
        self.img = img
        self.description = description
        self.count_used = count_used
        self.chance = chance
        self.preuse = preuse
        self.heal_health = heal_health
        self.heal_hungry = heal_hungry
        self.heal_water = heal_water

#все клетки
all_cell = {
        'stone_floor': ('каменный пол', './imgs/stone_floor.png', (-1, 300)),
        'floor': ('пол', './imgs/floor.png', (300, -1)),
        'chest_1': ('сундук', './imgs/chest.png', (3, 10)),
        'puddle': ('лужа', './imgs/puddle.png', (7, -1)),
        'stone_puddle': ('подземная лужа', './imgs/stone_puddle.png', (-1, 10)),
        'tree': ('дерево', './imgs/tree.png', (20, -1)),
        'chest_2': ('каменный сундук', './imgs/stone-chest.png', (2, 5)),
        'luke': ('люк', './imgs/luke.png', (2, -1)),
        'stone_luke': ('подземная лужа', './imgs/stone_luke.png', (-1, 2))
        }

#все предметы
all_items = {
        'bottle_of_water': ('бутыль воды', './imgs/bottle_of_water.png', 'стелянная колба с жидкостью, на вид схожей с обычной водой', 1, 0, 0, 30),
        'popato': ('картошка', './imgs/popato.png', 'сырая, полусгнившая картошка', 1, 1, 20, -10),
        'piece_of_glass': ('осколок стекла', './imgs/piece_of_glass.png', 'осколок стекла. взять такой в руку будет больно...', 3, -1, 0, 0),
        'medic_pill': ('медицинская пилюля', './imgs/medic_pill.png', 'таблетка, которая обычно помогает избавится от боли', 1, 10, 0, 0),
        'wood': ('бревно', './imgs/wood.png', 'кусок дерева...', 1, -1, 5, 5),
        'big_piece_of_glass': ('кусок стекла', './imgs/big_piece_of_glass.png', 'кусочек стекла.', 3, -1, 0, 0),
        'vase_of_glass': ('стеклянная ваза', './imgs/vase_of_glass.png', 'удобно собирать жидкости. даже пить из неё будто бы приятнее. жаль в ней даже воды нет...', 10, 0, 0, 0),
        'vase_of_glass_with_water': ('стеклянная ваза с водой', './imgs/vase_of_glass_with_water.png','та же ваза, та же вода, но пить из неё - сущее удовольствие', 10, 0, 0, 50),
        'medic_water': ('медицинское лекарство', './imgs/medic_water.png', 'таблетка растворённая в воде может дать хорошие целебные свойства', 1, 15, 20, 30),
        'vase_of_glass_with_medic_water': ('стеклянная ваза с лекарством', './imgs/vase_of_glass_with_medic_water.png','та же ваза, то же лекарство, но пить из неё - сущее удовольствие', 10, 10, 20, 20)
}

#все крафты
all_crafts = (
    ('piece_of_glass', 'piece_of_glass', 'big_piece_of_glass'),
    ('big_piece_of_glass', 'big_piece_of_glass', 'vase_of_glass'),
    ('vase_of_glass', 'bottle_of_water', 'vase_of_glass_with_water'),
    ('bottle_of_water', 'medic_pill', 'medic_water'),
    ('vase_of_glass', 'medic_water', 'vase_of_glass_with_medic_water'))

#единица пустоты инвентаря
void_in_inventory = item('void_in_inventory', 'Пусто', './imgs/void_in_inventory.png', 'отсек в вашем хранилище', 1, 0, 0, 0)

#функция для загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        return None
    image = pygame.image.load(fullname)
    return image

#генератор клетки
def generate_cell(all_cell, world):
    #создает список шанса спавна
    chances = [(list(all_cell.keys())[0], all_cell[list(all_cell.keys())[0]][2][world])]
    for key in list(all_cell.keys())[1:]:
        chances.append((key, all_cell[key][2][world]+chances[-1][1]))
    #ставит рандомно переменную, которая считается для создания клетки
    generate_number = random.randint(0, chances[-1][1])

    for i in chances:
        if generate_number <= i[1]:
            obj = map_cell(i[0], *all_cell[i[0]])
            return(obj)
#генератор предмета
def generate_item(all_items, subject_to_chance):
    #ставит рандомно переменную, которая считается для создания предмета
    all_items_rechance = []
    #шансы спавнов вещей в сундуке 1 
    in_chest_1 = [50, 150, 170, 179, 180]
    in_chest_2 = [0, 0, 0, 70, 80, 80, 80, 80, 80, 80, 80, 90, 100]
    if len(in_chest_1) < len(all_items):
        max_chance = in_chest_1[-1]
        for i in range(len(all_items) - len(in_chest_1)):
            in_chest_1.append(max_chance)
    if len(in_chest_2) < len(all_items):
        max_chance = in_chest_2[-1]
        for i in range(len(all_items) - len(in_chest_2)):
            in_chest_2.append(max_chance)
    if subject_to_chance == 'chest_1':
        for i in range(len(all_items)):
            all_items_rechance.append(item(list(all_items.keys())[i], *list(all_items.values())[i]))
            all_items_rechance[i].chance = in_chest_1[i]
    if subject_to_chance == 'chest_2':
        for i in range(len(all_items)):
            all_items_rechance.append(item(list(all_items.keys())[i], *list(all_items.values())[i]))
            all_items_rechance[i].chance = in_chest_2[i]
            

    generate_number = random.randint(0, all_items_rechance[-1].chance)
    
    for i in range(len(all_items_rechance)):
        if generate_number <= all_items_rechance[i].chance:
            obj = item(list(all_items.keys())[i], *list(all_items.values())[i])
            return(obj)

#вывод карты со всеми дебаг названиями, дебаг вывод карты
def debug_map(game_map):
    for i in range(len(game_map)):
        print('')
        for j in range(len(game_map[i])):
            print(game_map[i][j].name, end = ' ')
#пример вывода для функции debug_map
#debug_map(game_map)

#список со всеми еденицами для заполнения клеток игры 1 - обозначение в дебаге 2 - название для вывода
#3 - обозначение на карте 4 - шанс выпадения на поле

#main_player не включаем в all_cell, т.к. он не должен спавниться произвольно
main_player = map_cell('player', 'игрок', './imgs/player.png', 1, 0)
broken_tree = map_cell('broken_tree', 'сломанное дерево', './imgs/broken_tree.png', 1, 0)

#функция загрузки игры
def load_game():
    if os.path.exists('./save_game.pickle'):
        with open('./save_game.pickle', 'rb') as f:
            saved_game = pickle.load(f)
            print(saved_game)
        return saved_game
    else:
        return None 

#функция сохранения игры
def save_game(board, health, hungry, water, inventory, world):
    data = [board, health, hungry, water, inventory, world]
    with open('./save_game.pickle', 'wb') as f:
        pickle.dump(data, f)

#загрузка данными клеток
def generate_game_map(width, height):
    game_map = []
    for i in range(height):
        game_map.append([])
        for j in range(width):
            game_map[i].append(generate_cell(all_cell, world))
    return(game_map)

def replace_interact(board):
    if world == 0:
        board.board[board.height // 2][board.width // 2] = map_cell('floor', *all_cell['floor'])
        board.board[board.height // 2][board.width // 2].x = board.width // 2
        board.board[board.height // 2][board.width // 2].y = board.height // 2
    elif world == 1:
        board.board[board.height // 2][board.width // 2] = map_cell('stone_floor', *all_cell['stone_floor'])
        board.board[board.height // 2][board.width // 2].x = board.width // 2
        board.board[board.height // 2][board.width // 2].y = board.height // 2

# функция открытия инвентаря
def open_inventory(inventory):

    for i in range(board.height):  # Проходим по строкам
        for j in range(board.width):  # Проходим по столбцам
            inv_index = i * board.width + j  # Индекс элемента инвентаря
            if inv_index < len(inventory):

                # Загружаем изображение для текущего объекта инвентаря
                image = pygame.transform.scale(load_image(inventory[inv_index].img),
                                               (board.cell_size, board.cell_size))
                screen.blit(image, (j * board.cell_size + board.left, i * board.cell_size + board.top))

                # Если элемент инвентаря должен быть использован, рисуем рамку вокруг
                if inventory[inv_index].preuse:
                    pygame.draw.rect(screen, (0, 0, 0),
                        (j * board.cell_size + board.left, i * board.cell_size + board.top,
                         board.cell_size, board.cell_size), 3 )

            # Отображаем информацию о золоте и очках
            text_surface = my_font.render(f"gold {gold}", False, (255, 255, 255))
            screen.blit(text_surface, (board.width * board.cell_size * 0.8 + board.left,
                                       board.height * board.cell_size + board.top - 30))

            text_surface = my_font.render(f"point {points}", False, (255, 255, 255))
            screen.blit(text_surface, (board.width * board.cell_size * 0.8 + board.left,
                                       board.height * board.cell_size + board.top - 60))

    # Рисуем изображение для основного игрока
    image = pygame.transform.scale(load_image(main_player.img), (board.cell_size, board.cell_size))
    screen.blit(image, ((board.width // 2) * board.cell_size + board.left,
                        (board.height // 2) * board.cell_size + board.top))

    pygame.display.flip()  # Обновляем экран

#выбор предмета
def select_item(inventory):
    global preused_item, end_game, running
    open_inventory(inventory)
    for i in inventory:
        i.preuse = False
    inventory[preused_item].preuse = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_game = True
                running = False
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i:
                    return(None)
                    break
                elif event.key == pygame.K_a:
                    for i in range(len(inventory)):
                        if inventory[i].preuse == True:
                            if i == 0:
                                break
                            else:
                                inventory[i].preuse = False
                                inventory[i-1].preuse = True
                                break
                elif event.key == pygame.K_d:
                    for i in range(len(inventory)):
                        if inventory[i].preuse == True:
                            if i == len(inventory) - 1:
                                break
                            else:
                                inventory[i].preuse = False
                                inventory[i+1].preuse = True
                                break
                elif event.key == pygame.K_e:
                    for i in range(len(inventory)):
                        if inventory[i].preuse == True:
                            return(i)
                            break
                elif event.key == pygame.K_f:
                    screen.fill((0, 0, 0))  # Очистка экрана
                    pressf = False
                    while not pressf:
                        for i in range(len(inventory)):
                            if inventory[i].preuse == True:
                                used_item = i
                                break

                        # Отображаем название предмета
                        text_surface = my_font.render(inventory[used_item].game_name, False, 
                                                      (255, 255, 255))
                        screen.blit(text_surface, (board.width * board.cell_size * 0.3 + board.left,
                                                   30 + board.top))

                        # Отображаем описание с переносом строк

                        x_pos = board.width * board.cell_size * 0.3 + board.left
                        y_pos = 80 + board.top

                        # Разбиваем описание на слова
                        words = inventory[used_item].description.split(' ')

                        line = ""
                        for word in words:
                            # Если в строке меньше 4 слов добавляем текущее слово
                            if len(line.split()) < 4:
                                line += ' ' + word if line else word
                            else:
                                # Если строка содержит 4 слова выводим ее и начинаем новую строку
                                text_surface = my_font.render(line, False, (255, 255, 255))
                                screen.blit(text_surface, (x_pos, y_pos))
                                y_pos += 32
                                line = word  # Начинаем новую строку с текущего слова

                        # Выводим оставшиеся слова в строке
                        if line:
                            text_surface = my_font.render(line, False, (255, 255, 255))
                            screen.blit(text_surface, (x_pos, y_pos))
                            y_pos += 32

                        # Отображаем количество использований
                        y_pos += 40
                        text_surface = my_font.render(f"Число использований: {inventory[used_item].count_used}", False,
                                                      (255, 255, 255))
                        screen.blit(text_surface, (x_pos, y_pos))

                        # Обработка событий
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                end_game = True
                                running = False
                                return None
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_f:
                                    screen.fill((0, 0, 0))
                                    board.render(screen)
                                    pressf = True

                        clock.tick(fps)
                        pygame.display.flip()
        for i in range(len(inventory)):
            if inventory[i].count_used <= 0:
                if inventory[i].preuse == True:
                    inventory[i] = copy.copy(void_in_inventory)
                    inventory[i].preuse = True
                else:
                    inventory[i] = copy.copy(void_in_inventory)
        open_inventory(inventory)
        clock.tick(fps)
        pygame.display.flip()


def display_stats(screen, my_font, health, hungry, water, max_health, max_hungry, max_water):
    # Отображение здоровья
    health_text = f"HP: {health}/{max_health}"
    health_surface = my_font.render(health_text, False, (255, 255, 255))
    screen.blit(health_surface, (10, 10))

    # Отображение еды
    hungry_text = f"Food: {hungry}/{max_hungry}"
    hungry_surface = my_font.render(hungry_text, False, (255, 255, 255))
    screen.blit(hungry_surface, (10, 50))

    # Отображение воды
    water_text = f"Water: {water}/{max_water}"
    water_surface = my_font.render(water_text, False, (255, 255, 255))
    screen.blit(water_surface, (10, 90))

world = 0

size = width, height = 15, 15

board = Board(width, height)

end_game = False

#стата игрока
max_health = 20
health = 20
health_regeneration = 1
health_regeneration_timer = 0
health_regeneration_timer_max = 5

max_hungry = 120
hungry = 120
loss_hungry = 2
health_degeneration_for_hungry = 1
health_degeneration_timer_for_hungry = 0
health_degeneration_timer_max_for_hungry = 5

max_water = 80
water = 80
loss_water = 1
health_degeneration_for_water = 1
health_degeneration_timer_for_water = 0
health_degeneration_timer_max_for_water = 5

max_inventory = 19

gold = 0

points = 0

#инициальзация шрифта
pygame.font.init()

my_font = pygame.font.SysFont('Comic Sans MS', 30)

#инвентарь и его заполнение
inventory = []

for i in range(max_inventory):
    inventory.append(copy.copy(void_in_inventory))

is_space = False



#инициальзация экрана
pygame.init()
pygame.display.set_caption('main')
#высота и ширина карты
screen = pygame.display.set_mode(list(map(lambda x: x*board.cell_size, size)))

screen.fill((0, 0, 0))

running = True
fps = 60
clock = pygame.time.Clock()

epilog = True

#загрузка сейва
game = load_game()
if game != None:
    board, health, hungry, water, inventory, world = load_game()

#начальный экран
while epilog:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_game = True
            running = False
            epilog = False
        elif event.type == pygame.KEYDOWN:
            epilog = False
    text = ["Ходить на w/a/s/d", "открыть инвентарь i", "применить предмет e", "осмотреть предмет f"]
    for i in range(len(text)):
        text_surface = my_font.render(text[i],
        False,
        (255, 255, 255))
        screen.blit(text_surface, (board.width*board.cell_size//3, board.height*board.cell_size//3+i*board.cell_size))
    pygame.display.flip()

while running:

    while not end_game:

        #пассивная регенерация
        if health_regeneration_timer >= health_regeneration_timer_max:
            health_regeneration_timer = 0
            health += health_regeneration
        if health_degeneration_timer_for_hungry >= health_degeneration_timer_max_for_hungry:
            health_degeneration_timer_for_hungry = 0
            health -= health_degeneration_for_hungry
        if health_degeneration_timer_for_water >= health_degeneration_timer_max_for_water:
            health_degeneration_timer_for_water = 0
            health -= health_degeneration_for_water

        #проверка смерти игрока
        if health <= 0:
            end_game = True

        #проверка на то, что больше ли стата чем её максимум
        if health > max_health:
            health = max_health
        if hungry > max_hungry:
            hungry = max_hungry
        if water > max_water:
            water = max_water
        if hungry < 0:
            hungry = 0
        if water < 0:
            water = 0

        for event in pygame.event.get():
            save_game(board, health, hungry, water, inventory, world)
            if event.type == pygame.QUIT:
                end_game = True
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    if board.board[board.height // 2 + 1][board.width // 2].name == 'tree':
                        board.board[board.height // 2 + 1][board.width // 2] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        board.move_down()
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water
                if event.key == pygame.K_w:
                    if board.board[board.height // 2 - 1][board.width // 2].name == 'tree':
                        board.board[board.height // 2 - 1][board.width // 2] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        board.move_up()
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water
                if event.key == pygame.K_a:
                    if board.board[board.height // 2][board.width // 2 - 1].name == 'tree':
                        board.board[board.height // 2][board.width // 2 - 1] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        board.move_left()
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water
                if event.key == pygame.K_d:
                    if board.board[board.height // 2][board.width // 2 + 1].name == 'tree':
                        board.board[board.height // 2][board.width // 2 + 1] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        board.move_right()
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water
                if event.key == pygame.K_i:
                    preused_item = 0
                    while True:
                        used_item = select_item(inventory)
                        if used_item != None:
                            preused_item = used_item
                            health += inventory[used_item].heal_health
                            hungry += inventory[used_item].heal_hungry
                            water += inventory[used_item].heal_water
                            if used_item != None:
                                inventory[used_item].count_used -= 1
                                for i in inventory:
                                    i.preuse = False
                                inventory[used_item].preuse = True

                                #проверка на то, что больше ли стата чем её максимум
                                if health > max_health:
                                    health = max_health
                                if hungry > max_hungry:
                                    hungry = max_hungry
                                if water > max_water:
                                    water = max_water
                                if hungry < 0:
                                    hungry = 0
                                if water < 0:
                                    water = 0
                        else:
                            break

        #взаимодействие с миром
        if board.board[board.height // 2][board.width // 2].name == 'broken_tree':
            for i in range(len(inventory)):
                if inventory[i].name == 'void_in_inventory':
                    first_space_in_inventory = i
                    is_space = True
                    break
            if is_space == True:
                replace_interact(board)
                inventory[first_space_in_inventory] = item('wood', *all_items['wood'])
                points += 3
                is_space = False
            else:
                pass
        if board.board[board.height // 2][board.width // 2].name == 'chest_1':
            for i in range(len(inventory)):
                if inventory[i].name == 'void_in_inventory':
                    first_space_in_inventory = i
                    is_space = True
                    break
            if is_space == True:
                replace_interact(board)
                inventory[first_space_in_inventory] = generate_item(all_items, 'chest_1')
                points += 5
                gold += random.randint(20, 120)
                is_space = False
            else:
                pass
        if board.board[board.height // 2][board.width // 2].name == 'chest_2':
            for i in range(len(inventory)):
                if inventory[i].name == 'void_in_inventory':
                    first_space_in_inventory = i
                    is_space = True
                    break
            if is_space == True:
                replace_interact(board)
                inventory[first_space_in_inventory] = generate_item(all_items, 'chest_2')
                points += 20
                gold += random.randint(60, 360)
                is_space = False
            else:
                pass
        if board.board[board.height // 2][board.width // 2].name == 'puddle':
            replace_interact(board)
            points -= 1
            water += 2
        if board.board[board.height // 2][board.width // 2].name == 'stone_puddle':
            replace_interact(board)
            points -= 10
            water += 20
            health -= 5
        if board.board[board.height // 2][board.width // 2].name == 'luke':
            points += 1000
            world = 1
            board.board = generate_game_map(width, height)
        if board.board[board.height // 2][board.width // 2].name == 'stone_luke':
            points += 1000
            world = 0
            board.board = generate_game_map(width, height)

        #вывод карты с игроком
        board.render(screen)

        # Отображаем статы игрока
        display_stats(screen, my_font, health, hungry, water, max_health, max_hungry, max_water)

        #загрузка экрана
        clock.tick(fps)
        pygame.display.flip()

    if os.path.exists('./save_game.pickle') and health <= 0:
        os.remove('./save_game.pickle')
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        screen.fill((0, 0, 0))
        text = ["ENDGAME!", f"gold {gold}", f"points {points}"]
        for i in range(len(text)):
            text_surface = my_font.render(text[i],
            False,
            (255, 255, 255))
            screen.blit(text_surface, (board.width*board.cell_size//3, board.height*board.cell_size//3+i*board.cell_size))
        pygame.display.flip()

#вывод статов
#нужно вывести количество очков и gold на экран проигрыша

pygame.quit()
