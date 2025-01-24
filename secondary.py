#импортирование всех библиотек
import pygame
import random
import copy
import os

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
        screen.blit(image, ((self.width//2+1)*self.cell_size + self.left, (self.height//2+1)*self.cell_size + self.top))

    #функция для перемещения вверх
    def move_down(self):
        for i in range(len(game_map)-1):
            for j in range(len(game_map[i])):
                game_map[i][j] = game_map[i+1][j]
        for i in range(len(game_map[-1])):
            game_map[-1][i] = generate_cell(all_cell)
        return(game_map)

    def move_up(self):
        for i in range(len(game_map)-1, 0, -1):
            for j in range(len(game_map[i])):
                game_map[i][j] = game_map[i-1][j]
        for i in range(len(game_map[0])):
            game_map[0][i] = generate_cell(all_cell)
        return(game_map)

    def move_right(self):
        for i in range(len(game_map)):
            for j in range(len(game_map[i]) - 1):
                game_map[i][j] = game_map[i][j + 1]
        for i in range(len(game_map)):
            game_map[i][-1] = generate_cell(all_cell)
        return(game_map)

    def move_left(self):
        for i in range(len(game_map)):
            for j in range(len(game_map[i])-1, 0, -1):
                game_map[i][j] = game_map[i][j - 1]
        for i in range(len(game_map)):
            game_map[i][0] = generate_cell(all_cell)
        return(game_map)

#класс с клетками
class map_cell:
#имя в дебаге, имя в игре, обозначение на карте, шанс выпадения
    def __init__(self, name, game_name, img, color, chance, x = None, y = None):
        self.name = name
        self.game_name = game_name
        self.img = img
        self.color = color
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
        'floor': ('пол', './imgs/floor.png', 1, 300),
        'chest_1': ('сундук', './imgs/chest.png', 1, 303),
        'puddle': ('лужа', './imgs/puddle.png', 1, 310),
        'tree': ('дерево', './imgs/tree.png', 1, 330),
        'chest_2': ('каменный сундук', './imgs/stone-chest.png', 2, 335)
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

#генератор клетки
def generate_cell(all_cell):
    #ставит рандомно переменную, которая считается для создания клетки
    generate_number = random.randint(0, list(all_cell.values())[-1][3])
    
    for i in list(all_cell.keys()):
        if generate_number <= all_cell[i][3]:
            obj = map_cell(i, *all_cell[i])
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
            all_items_rechance.append(item(*all_items[i]))
            all_items_rechance[i].chance = in_chest_1[i]
    if subject_to_chance == 'chest_2':
        for i in range(len(all_items)):
            all_items_rechance.append(item(*all_items[i]))
            all_items_rechance[i].chance = in_chest_2[i]
            

    generate_number = random.randint(0, all_items_rechance[-1].chance)
    
    for i in range(len(all_items_rechance)):
        if generate_number <= all_items_rechance[i].chance:
            obj = item(*all_items[i])
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

#карта игры
game_map = []

#загрузка данными клеток
def generate_game_map(width, height):
    game_map = []
    for i in range(height):
        game_map.append([])
        for j in range(width):
            game_map[i].append(generate_cell(all_cell))
    return(game_map)

#функция открытия инвентаря
def open_inventory(inventory):
    for i in range(height_map-1):
        if len(inventory) < i:
            pass
        else:
            if inventory[i].preuse == True:
                win.addstr(i+1, 1, inventory[i].designation, curses.A_BOLD)
            else:
                win.addstr(i+1, 1, inventory[i].designation)
        if len(inventory) < i + height_map:
            pass
        else:
            if inventory[i + height_map - 1].preuse == True:
                win.addstr(i+1, width_map // 3 * 2 - 1, inventory[i + height_map - 1].designation, curses.A_BOLD)
            else:
                win.addstr(i+1, width_map // 3 * 2 - 1, inventory[i + height_map - 1].designation)
        win.addstr(height_map - 1, width_map // 2, "gold "+str(gold))
        win.addstr(height_map, width_map // 2, "point "+str(points))
        win.refresh()

def select_item(inventory):
    global preused_item
    open_inventory(inventory)
    for i in inventory:
        i.preuse = False
    inventory[preused_item].preuse = True
    key = win.getch()
    while True:
        key = win.getch()
        if key == ord('i'):
            return(None)
            break
        if key == ord('w'):
            for i in range(len(inventory)):
                if inventory[i].preuse == True:
                    if i == 0:
                        break
                    else:
                        inventory[i].preuse = False
                        inventory[i-1].preuse = True
                        break
        if key == ord('s'):
            for i in range(len(inventory)):
                if inventory[i].preuse == True:
                    if i == len(inventory) - 1:
                        break
                    else:
                        inventory[i].preuse = False
                        inventory[i+1].preuse = True
                        break
        if key == ord('e'):
            for i in range(len(inventory)):
                if inventory[i].preuse == True:
                    return(i)
                    break
        if key == ord('f'):
            key = win.getch()
            while key != ord('f'):
                key = win.getch()
                for i in range(len(inventory)):
                    if inventory[i].preuse == True:
                        used_item = i
                        break
                win.clear()
                win.addstr(1, 1, inventory[used_item].game_name)
                win.addstr(3, 0, inventory[used_item].description)
                win.addstr(height_map, 0, 'число использований - ' + str(inventory[used_item].count_used))
        for i in range(len(inventory)):
            if inventory[i].count_used <= 0:
                if inventory[i].preuse == True:
                    inventory[i] = copy.copy(void_in_inventory)
                    inventory[i].preuse = True
                else:
                    inventory[i] = copy.copy(void_in_inventory)
        win.clear()
        open_inventory(inventory)
        win.timeout(100)

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

#инвентарь и его заполнение
inventory = []

for i in range(max_inventory):
    inventory.append(copy.copy(void_in_inventory))

is_space = False

#инициальзация экрана
pygame.init()
pygame.display.set_caption('main')
#высота и ширина карты
screen = pygame.display.set_mode(size)

running = True
fps = 60
clock = pygame.time.Clock()
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
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.K_s:
                    if game_map[height_map // 2 + 2][width_map // 3 + 4 + 1].name == 'tree':
                        game_map[height_map // 2 + 2][width_map // 3 + 4 + 1] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        move_down(game_map)
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water
                if event.type == pygame.K_w:
                    if game_map[height_map // 2][width_map // 3 + 4 + 1].name == 'tree':
                        game_map[height_map // 2][width_map // 3 + 4 + 1] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        move_up(game_map)
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water
                if event.type == pygame.K_a:
                    if game_map[height_map // 2 + 1][width_map // 3 + 4].name == 'tree':
                        game_map[height_map // 2 + 1][width_map // 3 + 4] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        move_left(game_map)
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water
                if event.type == pygame.K_d:
                    if game_map[height_map // 2 + 1][width_map // 3 + 4 + 2].name == 'tree':
                        game_map[height_map // 2 + 1][width_map // 3 + 4 + 2] = copy.copy(broken_tree)
                        hungry -= loss_hungry
                        water -= loss_water
                    else:
                        move_right(game_map)
                        points += 1
                        if hungry > 0 and water > 0:
                            health_regeneration_timer += 1
                        if hungry <= 0:
                            health_degeneration_timer_for_hungry += 1
                        if water <= 0:
                            health_degeneration_timer_for_water += 1
                        hungry -= loss_hungry
                        water -= loss_water

        #взаимодействие с миром
        if board.board[board.height // 2 + 1][board.width // 2 + 1].name == 'broken_tree':
            for i in range(len(inventory)):
                if inventory[i].name == 'void_in_inventory':
                    first_space_in_inventory = i
                    is_space = True
                    break
            if is_space == True:
                board.board[board.height // 2 + 1][board.width // 2 + 1] = map_cell('floor', *all_cell['floor'])
                board.board[board.height // 2 + 1][board.width // 2 + 1].x = width_map // 2 + 1
                board.board[board.height // 2 + 1][board.width // 2 + 1].y = height_map // 2 + 1
                inventory[first_space_in_inventory] = item('wood', *all_items['wood'])
                points += 3
                is_space = False
            else:
                pass
        if board.board[board.height // 2 + 1][board.width // 2 + 1].name == 'chest_1':
            for i in range(len(inventory)):
                if inventory[i].name == 'void_in_inventory':
                    first_space_in_inventory = i
                    is_space = True
                    break
            if is_space == True:
                board.board[board.height // 2 + 1][board.width // 2 + 1] = map_cell('floor', *all_cell['floor'])
                board.board[board.height // 2 + 1][board.width // 2 + 1].x = width_map // 2
                board.board[board.height // 2 + 1][board.width // 2 + 1].y = height_map // 2
                inventory[first_space_in_inventory] = generate_item(all_items, 'chest_1')
                points += 5
                gold += random.randint(20, 120)
                is_space = False
            else:
                pass
        if board.board[board.height // 2 + 1][board.width // 2 + 1].name == 'chest_2':
            for i in range(len(inventory)):
                if inventory[i].name == 'void_in_inventory':
                    first_space_in_inventory = i
                    is_space = True
                    break
            if is_space == True:
                board.board[board.height // 2 + 1][board.width // 2 + 1] = map_cell('floor', *all_cell['floor'])
                board.board[board.height // 2 + 1][board.width // 2 + 1].x = width_map // 2
                board.board[board.height // 2 + 1][board.width // 2 + 1].y = height_map // 2
                inventory[first_space_in_inventory] = generate_item(all_items, 'chest_2')
                points += 20
                gold += random.randint(60, 360)
                is_space = False
            else:
                pass
        if board.board[board.height // 2 + 1][board.width // 2 + 1].name == 'puddle':
                board.board[board.height // 2 + 1][board.width // 2 + 1] = map_cell('floor', *all_cell['floor'])
                board.board[board.height // 2 + 1][board.width // 2 + 1].x = width_map // 2
                board.board[board.height // 2 + 1][board.width // 2 + 1].y = height_map // 2
                points -= 1
                water += 2

        #вывод карты с игроком
        board.render(screen)

        #загрузка экрана
        screen.fill((0, 0, 0))
        clock.tick(fps)
        pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

#вывод статов
#нужно вывести количество очков и gold на экран проигрыша

pygame.quit()