#импортирование всех библиотек
import random
import curses
import copy

#высота и ширина карты
height_map = 17 // 2 * 2 + 1
width_map = 17 // 2 * 4 + 1

#инициальзация экрана
sc = curses.initscr()
#h, w = sc.getmaxyx()
win = curses.newwin(height_map + 2, width_map + 2, 0, 0)

win.keypad(1)
curses.curs_set(0)

curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)


#класс с клетками
class map_cell:
#имя в дебаге, имя в игре, обозначение на карте, шанс выпадения
    def __init__(self, name, game_name, designation, color, chance, x = None, y = None):
        self.name = name
        self.game_name = game_name
        self.designation = designation
        self.color = color
        self.chance = chance
        self.x = x
        self.y = y

#класс предмет
class item:
    def __init__(self, name, game_name, designation, description, count_used, heal_health, heal_hungry, heal_water, bonus_dmg, chance = None, preuse = False):
        self.name = name
        self.game_name = game_name
        self.designation = designation
        self.description = description
        self.count_used = count_used
        self.chance = chance
        self.preuse = preuse
        self.heal_health = heal_health
        self.heal_hungry = heal_hungry
        self.heal_water = heal_water
        self.bonus_dmg = bonus_dmg
#класс способность
class ability:
    def __init__(self, name, level, duration):
        self.name = name
        self.level = level    
        self.duration = duration
#класс эффект
class effect:
    def __init__(self, name, game_name, level, duration):
        self.name = name
        self.game_name = game_name
        self.level = level  
        self.duration = duration  
#класс сущность
class summon:
    def __init__(self, name, game_name, description, dmg, health, abilities = [], effects = []):
        self.name = name
        self.game_name = game_name
        self.description = description
        self.dmg = dmg
        self.health = health
        self.abilities = abilities
        self.effects = effects
    #функция атаки в сущности
    def attack(self, target):
        target.health -= self.dmg
        for i in range(len(self.abilities)):
            if self.abilities[i].name == 'poison_attack':
                target.effects.append(effect('poison', 'яд', self.abilities[i].level, self.abilities[i].duration))
        for i in range(len(target.abilities)):
            if target.abilities[i].name == 'shield':
                if self.dmg < target.abilities[i].level:
                    target.health += self.dmg
                else:
                    target.health += target.abilities[i].level
    #функция для обработки процессов
    def processing(self):
        deletted_effects = 0
        for i in range(len(self.effects)):
            if self.effects[i - deletted_effects].name == 'poison':
                self.effects[i - deletted_effects].duration -= 1
                self.health -= self.effects[i - deletted_effects].level
            if self.effects[i - deletted_effects].duration <= 0:
                deletted_effects += 1
                del self.effects[i - deletted_effects]

#функция для изменения цвета текста
def out_color(text, ncolor):
    if ncolor == 'red':
        col = "\033[31m{}"
    if ncolor == 'green':
        col = "\033[32m{}"
    if ncolor == 'yellow':
        col = "\033[33m{}"
    if ncolor == 'blue':
        col = "\033[34m{}"
    if ncolor == 'purple':
        col = "\033[35m{}"
    if ncolor == 'black':
        col = "\033[30m{}"
    return(col.format(text) + "\033[37m{}".format(''))
#Пример работы функции out_color
#возможные цвета red, green, yellow, blue, purple
#print(out_color('TEST 1', 'purple'))

all_cell = [
        ['floor', 'пол', ' ', 1, 300],
        ['chest_1', 'сундук', '𝌴', 1, 303],
        ['puddle', 'лужа', '◉', 1, 310],
        ['tree', 'дерево', '✱', 1, 330],
        ['grave', 'могила', '☖', 1, 334],
        ['chest_2', 'каменный сундук', '𝌴', 2, 335]
    ]

all_items = [
        ['bottle_of_water', 'бутыль воды', '◘', 'стелянная колба с жидкостью, на вид схожей с обычной водой', 1, 0, 0, 30, 0],
        ['popato', 'картошка', '⟳', 'сырая, полусгнившая картошка', 1, 1, 20, -10, 0],
        ['piece_of_glass', 'осколок стекла', '↾', 'осколок стекла. взять такой в руку будет больно...', 3, -1, 0, 0, 2],
        ['medic_pill', 'медицинская пилюля', 'o', 'таблетка, которая обычно помогает избавится от боли', 1, 10, 0, 0, 0],
        ['iron_sword', 'железный меч', 'Į', 'железный меч. Хлипкий, но все ещё полезно', 10, 0, 0, 0, 3],
        ['wood', 'бревно', '=', 'кусок дерева... ты что собрался ЭТО есть?', 1, -1, 5, 5, 1],
        ['big_piece_of_glass', 'кусок стекла', '⌔', 'кусочек стекла.', 3, -1, 0, 0, 5],
        ['vase_of_glass', 'стеклянная ваза', 'U', 'удобно собирать жидкости. даже пить из неё будто бы приятнее. жаль в ней даже воды нет...', 10, 0, 0, 0, 0],
        ['vase_of_glass_with_water', 'стеклянная ваза с водой', 'U','та же ваза, та же вода, но пить из неё - сущее удовольствие', 10, 0, 0, 50, 0],
        ['medic_water', 'медицинское лекарство', '◘', 'таблетка растворённая в воде может дать хорошие целебные свойства', 1, 15, 20, 30, 0,],
        ['vase_of_glass_with_medic_water', 'стеклянная ваза с лекарством', 'U','та же ваза, то же лекарство, но пить из неё - сущее удовольствие', 10, 10, 20, 20, 0],
        ['dinary0', 'дневник из лаборатории 0', 'D', 'дневник учёного Тимур. с одной стороны может пойти на бумагу, а с другой можно и почитать.\
некоторые страницы стёрлись от древности.{День ---. Сегодня ничего особенного не происходило. Кроме того, что после испытания газового раствора\
у меня в животе булькало}', 1, 0, 15, -5, 0],
        ['debug_monocle', 'монокль просвящения', 'i', '~ВЫСОКИЙ ПРЕДМЕТ~ Даёт вам силу углублённого исследования предмета из вашего инвентаря', 1, 0, 0, 0, 0]
    ]

all_summons = [
    ['zobmie', 'зомби', 'Чьи-то сгнившие останки, так ещё и двигающиеся. Даже трогать не хочется', 2, 7, [ability('poison_attack', 1, 2)], []]
]

all_crafts = [
    ['piece_of_glass', 'piece_of_glass', 'big_piece_of_glass'],
    ['big_piece_of_glass', 'big_piece_of_glass', 'vase_of_glass'],
    ['vase_of_glass', 'bottle_of_water', 'vase_of_glass_with_water'],
    ['bottle_of_water', 'medic_pill', 'medic_water'],
    ['vase_of_glass', 'medic_water', 'vase_of_glass_with_medic_water']]

void_in_inventory = item('void_in_inventory', 'Пусто', '-', 'отсек в вашем хранилище', 1, 0, 0, 0, 0)

#генератор клетки
def generate_cell(all_cell):
    #ставит рандомно переменную, которая считается для создания клетки
    generate_number = random.randint(0, all_cell[-1][4])
    
    for i in range(len(all_cell)):
        if generate_number <= all_cell[i][4]:
            obj = map_cell(*all_cell[i])
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

#вывод карты со всеми игровыми названиями, игровой вывод карты
def print_map(game_map):
#    game_map[len(game_map) // 2][len(game_map[len(game_map) // 2]) // 2] = main_player
    for i in range(len(game_map)):
        for j in range(len(game_map[i])):
            game_map[i][j].x = i
            game_map[i][j].y = j
            win.addch(game_map[i][j].x + 1, game_map[i][j].y + 1, game_map[i][j].designation, curses.color_pair(game_map[i][j].color))

#пример вывода для функции debug_map
#print_map(game_map)

#функция для перемещения вверх
def move_down(game_map):
    for i in range(len(game_map)-1):
        for j in range(len(game_map[i])):
            game_map[i][j] = game_map[i+1][j]
    for i in range(len(game_map[-1])):
        game_map[-1][i] = generate_cell(all_cell)
    return(game_map)

def move_up(game_map):
    for i in range(len(game_map)-1, 0, -1):
        for j in range(len(game_map[i])):
            game_map[i][j] = game_map[i-1][j]
    for i in range(len(game_map[0])):
        game_map[0][i] = generate_cell(all_cell)
    return(game_map)

def move_right(game_map):
    for i in range(len(game_map)):
        for j in range(len(game_map[i]) - 1):
            game_map[i][j] = game_map[i][j + 1]
    for i in range(len(game_map)):
        game_map[i][-1] = generate_cell(all_cell)
    return(game_map)

def move_left(game_map):
    for i in range(len(game_map)):
        for j in range(len(game_map[i])-1, 0, -1):
            game_map[i][j] = game_map[i][j - 1]
    for i in range(len(game_map)):
        game_map[i][0] = generate_cell(all_cell)
    return(game_map)

#список со всеми еденицами для заполнения клеток игры 1 - обозначение в дебаге 2 - название для вывода
#3 - обозначение на карте 4 - шанс выпадения на поле

#main_player не включаем в all_cell, т.к. он не должен спавниться произвольно
main_player = map_cell('player', 'игрок', '◯', 1, 0, width_map // 3 - 1, height_map)
broken_tree = map_cell('broken_tree', 'сломанное дерево', '✳', 1, 0)

#карта игры
game_map = []

#загрузка данными клеток
def generate_game_map(game_map):
    for i in range(height_map):
        game_map.append([])
        for j in range(width_map):
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
#функция создания битвы
def fight(player, target):
    global width_map, height_map, health, hungry, water, bonus_dmg, inventory, death_fight, max_health, max_hungry, max_water, preused_item
    #список действий на преактивации
    #1 - атаковать
    #2 - предметы
    #3 - исследовать    
    pre_acts = [True, False, False]
    end_fight = False
    win.clear()
    while end_fight != True:
        key = win.getch()
        win.addstr(1, width_map // 2, target.game_name)

        win.addstr(height_map - 2, 1, 'Союзное Здоровье - ' + str(player.health) + '   ')
        win.addstr(height_map, 1, 'Вражеское Здоровье - ' + str(target.health) + '   ')

        win.addch(3, width_map // 2, '◯')
        win.addch(4, (width_map // 2), '┤')
        win.addch(4, (width_map // 2) - 1, '╭')
        win.addch(5, (width_map // 2), '∏')

        if key == ord('a'):
            for i in range(len(pre_acts)):
                if pre_acts[i] == True:
                    if i == 0:
                        break
                    else:
                        pre_acts[i] = False
                        pre_acts[i-1] = True
                        break
        if key == ord('d'):
            for i in range(len(pre_acts)):
                if pre_acts[i] == True:
                    if i == len(pre_acts) - 1:
                        break
                    else:
                        pre_acts[i] = False
                        pre_acts[i+1] = True
                        break

        if key == ord('e'):
            for i in range(len(pre_acts)):
                if pre_acts[i] == True:
                    if i == 0:
                        player.dmg += bonus_dmg
                        player.processing()
                        target.processing()
                        player.attack(target)
                        target.attack(player)
                        player.dmg -= bonus_dmg
                        bonus_dmg = 0
                        break
                    if i == 1:
                        preused_item = 0
                        used_item = select_item(inventory)
                        if used_item != None:
                            preused_item = used_item
                            if inventory[used_item].name == 'debug_monocle':
                                while True:
                                    win.timeout(100)
                                    key = win.getch()
                                    if key == ord('i'):
                                        win.clear()
                                        break
                                    win.clear()
                                    win.addstr(1, width_map // 2, str(target.name) + ' ' + str(target.game_name))
                                    win.addstr(3, 0, target.description)
                                    win.addstr(height_map-3, 0, 'hp=' + str(target.health))
                                    win.addstr(height_map-3, 10, 'dmg:' + str(target.dmg))
                                    win.addstr(height_map-2, 0, 'abilities:' + str(target.abilities))
                                    win.addstr(height_map-2, 10, 'effects:' + str(target.effects))
                            main_player_in_fight.health += inventory[used_item].heal_health
                            hungry += inventory[used_item].heal_hungry
                            water += inventory[used_item].heal_water
                            bonus_dmg += inventory[used_item].bonus_dmg
                            if main_player_in_fight.health > max_health:
                                main_player_in_fight.health = max_health
                            if hungry > max_hungry:
                                hungry = max_hungry
                            if water > max_water:
                                water = max_water
                            if hungry < 0:
                                hungry = 0
                            if water < 0:
                                water = 0
                            inventory[used_item].count_used -= 1
                            for i in inventory:
                                i.preuse = False
                            inventory[used_item].preuse = True
                            player.processing()
                            target.processing()
                            target.attack(player)
                            win.clear()
                        else:
                            win.clear()
                    if i == 2:
                        inspect_flag = False
                        pre_inspect = [True, False]
                        win.clear()
                        while inspect_flag != True:
                            key = win.getch()
                            if key == ord('a'):
                                for i in range(len(pre_inspect)):
                                    if pre_inspect[i] == True:
                                        if i == 0:
                                            break
                                        else:
                                            pre_inspect[i] = False
                                            pre_inspect[i-1] = True
                                            break
                            if key == ord('d'):
                                for i in range(len(pre_inspect)):
                                    if pre_inspect[i] == True:
                                        if i == len(pre_inspect) - 1:
                                            break
                                        else:
                                            pre_inspect[i] = False
                                            pre_inspect[i+1] = True
                                            break
                            if key == ord('e'):
                                for i in range(len(pre_inspect)):
                                    if pre_inspect[i] == True and i == 0:
                                        win.clear()
                                        while True:
                                            key = win.getch()
                                            win.addstr(1, 1, player.game_name)
                                            win.addstr(3, 1, player.description)
                                            win.addstr(7, 1, 'Эффекты:')
                                            for i in range(len(player.effects)):
                                                win.addstr(i+8, 1, str(player.effects[i].game_name) + ' Уровень ' + str(player.effects[i].level) + '  Длительность ' + str(player.effects[i].duration))
                                            if key == ord('e'):
                                                inspect_flag = True
                                                win.clear()
                                                break
                                    if pre_inspect[i] == True and i == 1:
                                        win.clear()
                                        while True:
                                            key = win.getch()
                                            win.addstr(1, 1, target.game_name)
                                            win.addstr(3, 1, target.description)
                                            win.addstr(7, 1, 'Эффекты:')
                                            for i in range(len(target.effects)):
                                                win.addstr(i+8, 1, str(target.effects[i].game_name) + ' Уровень ' + str(target.effects[i].level) + '  Длительность ' + str(target.effects[i].duration))
                                            if key == ord('e'):
                                                inspect_flag = True
                                                win.clear()
                                                break
                            
                            if pre_inspect[0] == True:
                                win.addstr(8, 1, 'Игрок', curses.A_BOLD)
                            else:
                                win.addstr(8, 1, 'Игрок')
                            if pre_inspect[1] == True:
                                win.addstr(8, width_map // 2 + 6, 'Враг', curses.A_BOLD)
                            else:
                                win.addstr(8, width_map // 2 + 6, 'Враг')

        if pre_acts[0] == True:
            win.addstr(8, 1, 'Атаковать', curses.A_BOLD)
        else:
            win.addstr(8, 1, 'Атаковать')
        if pre_acts[1] == True:
            win.addstr(8, width_map // 2 + 6, 'Предметы', curses.A_BOLD)
        else:
            win.addstr(8, width_map // 2 + 6, 'Предметы')
        if pre_acts[2] == True:
            win.addstr(10, 1, 'Исследовать', curses.A_BOLD)
        else:
            win.addstr(10, 1, 'Исследовать')

        if player.health <= 0:
            health = 0
            end_fight = True
            death_fight = True
        if target.health <= 0:
            end_fight = True
            health = player.health

        win.timeout(100)

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

game_map = generate_game_map(game_map)

#загрузка в центральную клетку главного персонажа

#game_map[len(game_map) // 2][len(game_map[len(game_map) // 2]) // 2] = main_player

#debug_map(game_map)
#print_map(game_map)
#
#print('')
#
#print_map(move_up(game_map, all_cell))

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

dmg = 3
bonus_dmg = 0

gold = 0

points = 0

death_fight = False

#создание игрока для боя как сущность
main_player_in_fight = summon('player', 'игрок', 'Это вы!', dmg, health)

#инвентарь и его заполнение
inventory = []

for i in range(max_inventory):
    inventory.append(copy.copy(void_in_inventory))

print_map(game_map)

is_space = False

while end_game != True:
    win.border(0)
    win.timeout(100)

    key = win.getch()

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

    

    #проверка смерти игрока и обработка смерти
    if health <= 0 or death_fight == True:
        print_map(game_map)
        open_inventory(inventory)
        win.addch(main_player.x, main_player.y, main_player.designation)
        win.addstr(height_map - 2, width_map // 2, "gold "+str(gold))
        win.addstr(height_map - 1, width_map // 2, "point "+str(points))
        win.addstr(height_map, width_map // 2, "health "+str(health)+'/'+str(max_health))
        key = win.getch()
        while key != ord('q'):
            key = win.getch()

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
    
    if key == ord('s'):
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
    if key == ord('w'):
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
    if key == ord('a'):
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
    if key == ord('d'):
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

#        print('')
#        debug_map(game_map)
#        print('')
#подбор сундуков
    if game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].name == 'broken_tree':
        for i in range(len(inventory)):
            if inventory[i].name == 'void_in_inventory':
                first_space_in_inventory = i
                is_space = True
                break
        if is_space == True:
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1] = map_cell(*all_cell[0])
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].x = width_map // 3 + 3
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].y = height_map // 2
            inventory[first_space_in_inventory] = item(*all_items[5])
            points += 3
            is_space = False
        else:
            pass
    if game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].name == 'chest_1':
        for i in range(len(inventory)):
            if inventory[i].name == 'void_in_inventory':
                first_space_in_inventory = i
                is_space = True
                break
        if is_space == True:
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1] = map_cell(*all_cell[0])
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].x = width_map // 3 + 3
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].y = height_map // 2
            inventory[first_space_in_inventory] = generate_item(all_items, 'chest_1')
            points += 5
            gold += random.randint(20, 120)
            is_space = False
        else:
            pass
    if game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].name == 'chest_2':
        for i in range(len(inventory)):
            if inventory[i].name == 'void_in_inventory':
                first_space_in_inventory = i
                is_space = True
                break
        if is_space == True:
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1] = map_cell(*all_cell[0])
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].x = width_map // 3 + 3
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].y = height_map // 2
            inventory[first_space_in_inventory] = generate_item(all_items, 'chest_2')
            points += 20
            gold += random.randint(60, 360)
            is_space = False
        else:
            pass
    if game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].name == 'puddle':
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1] = map_cell(*all_cell[0])
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].x = width_map // 3 + 3
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].y = height_map // 2
            points -= 1
            water += 2

    #вывод карты с игроком
    print_map(game_map)
    win.addch(main_player.x, main_player.y, main_player.designation)

    if key == ord('i'):
        preused_item = 0
        while True:
            used_item = select_item(inventory)
            if used_item != None:
                preused_item = used_item
                health += inventory[used_item].heal_health
                hungry += inventory[used_item].heal_hungry
                water += inventory[used_item].heal_water
                bonus_dmg += inventory[used_item].bonus_dmg
                if inventory[used_item].name == 'debug_monocle':
                    preused_item = 0
                    used_item = 0
                    used_item = select_item(inventory)
                    if used_item != None:
                        while True:
                            win.timeout(100)
                            key = win.getch()
                            if key == ord('i'):
                                break
                            win.clear()
                            win.addstr(1, width_map // 2, str(inventory[used_item].name) + ' ' + str(inventory[used_item].game_name))
                            win.addstr(3, 0, inventory[used_item].description)
                            win.addstr(height_map-3, 0, 'hp+' + str(inventory[used_item].heal_health))
                            win.addstr(height_map-3, 10, 'water+' + str(inventory[used_item].heal_water))
                            win.addstr(height_map-2, 0, 'hungry+' + str(inventory[used_item].heal_hungry))
                            win.addstr(height_map-2, 10, 'bonus_dmg+' + str(inventory[used_item].bonus_dmg))
                            win.addstr(height_map, 0, 'число использований - ' + str(inventory[used_item].count_used))
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
    if key == ord('c'):
        pre_craft = [True, False, False]
        crafted_item = copy.copy(void_in_inventory)
        craft_item_1 = copy.copy(void_in_inventory)
        craft_item_2 = copy.copy(void_in_inventory)
        while True:
            key = win.getch()
            win.clear()
            if key == ord('c'):
                break

            if key == ord('a'):
                for i in range(len(pre_craft)):
                    if pre_craft[i] == True:
                        if i == 0:
                            break
                        else:
                            pre_craft[i] = False
                            pre_craft[i-1] = True
                            break
            if key == ord('d'):
                for i in range(len(pre_craft)):
                    if pre_craft[i] == True:
                        if i == len(pre_craft) - 1:
                            break
                        else:
                            pre_craft[i] = False
                            pre_craft[i+1] = True
                            break
            if key == ord('e') and pre_craft[2] != True:
                for i in inventory:
                    i.preuse = False
                inventory[0].preuse = True
                key = win.getch()
                while True:
                    key = win.getch()
                    if key == ord('i'):
                        if pre_craft[0] == True:
                            craft_item_1 = copy.copy(void_in_inventory)
                        if pre_craft[1] == True:
                            craft_item_2 = copy.copy(void_in_inventory)
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
                                used_item = i
                                break
                        if pre_craft[0] == True:
                            craft_item_1 = inventory[i]
                        if pre_craft[1] == True:
                            craft_item_2 = inventory[i]
                        for i in inventory:
                            i.preuse = False
                        inventory[used_item].preuse = True
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
                            win.addstr(1, width_map // 2, inventory[used_item].game_name)
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

                some_craft = False
                for i in range(len(all_crafts)):
                    if craft_item_1.name == all_crafts[i][0] and craft_item_2.name == all_crafts[i][1]:
                        some_craft = True
                        for j in range(len(all_items)):
                            if all_items[j][0] == all_crafts[i][2]:
                                crafted_item = copy.copy(item(*all_items[j]))
                if some_craft != True:
                    crafted_item = copy.copy(void_in_inventory)
            if key == ord('e') and pre_craft[2] == True and crafted_item.name != 'void_in_inventory':
                count_item = 2
                if craft_item_1.name == craft_item_2.name:
                    count_item = 0
                    for i in range(len(inventory)):
                        if inventory[i].name == craft_item_1.name:
                            count_item += 1
                if count_item >= 2:
                    for i in range(len(inventory)):
                        if inventory[i].name == craft_item_1.name:
                            inventory[i] = copy.copy(void_in_inventory)
                            craft_item_1 = copy.copy(void_in_inventory)
                            break
                    for i in range(len(inventory)):
                        if inventory[i].name == craft_item_2.name:
                            inventory[i] = copy.copy(void_in_inventory)
                            craft_item_2 = copy.copy(void_in_inventory)
                            break
                    for i in range(len(inventory)):
                        if inventory[i].name == void_in_inventory.name:
                            inventory[i] = copy.copy(crafted_item)
                            crafted_item = copy.copy(void_in_inventory)
                            break
            if pre_craft[0] == True:
                win.addstr(5, 1, 'основной', curses.A_BOLD)
                win.addch(6, 5, '┌', curses.A_BOLD)
                win.addch(6, 6, '─', curses.A_BOLD)
                win.addch(6, 7, '┐', curses.A_BOLD)
                win.addch(7, 7, '│', curses.A_BOLD)
                win.addch(7, 5, '│', curses.A_BOLD)
                win.addch(8, 5, '└', curses.A_BOLD)
                win.addch(8, 6, '─', curses.A_BOLD)
                win.addch(8, 7, '┘', curses.A_BOLD)
                win.addch(7, 6, craft_item_1.designation, curses.A_BOLD)
            else:
                win.addstr(5, 1, 'основной')
                win.addch(6, 5, '┌')
                win.addch(6, 6, '─')
                win.addch(6, 7, '┐')
                win.addch(7, 7, '│')
                win.addch(7, 5, '│')
                win.addch(8, 5, '└')
                win.addch(8, 6, '─')
                win.addch(8, 7, '┘')
                win.addch(7, 6, craft_item_1.designation)

            win.addch(7, 10, '╋')
            if pre_craft[1] == True:
                win.addstr(5, 11, 'побочный', curses.A_BOLD)
                win.addch(6, 12, '┌', curses.A_BOLD)
                win.addch(6, 13, '─', curses.A_BOLD)
                win.addch(6, 14, '┐', curses.A_BOLD)
                win.addch(7, 12, '│', curses.A_BOLD)
                win.addch(7, 14, '│', curses.A_BOLD)
                win.addch(8, 12, '└', curses.A_BOLD)
                win.addch(8, 13, '─', curses.A_BOLD)
                win.addch(8, 14, '┘', curses.A_BOLD)
                win.addch(7, 13, craft_item_2.designation, curses.A_BOLD)
            else:
                win.addstr(5, 11, 'побочный')
                win.addch(6, 12, '┌')
                win.addch(6, 13, '─')
                win.addch(6, 14, '┐')
                win.addch(7, 12, '│')
                win.addch(7, 14, '│')
                win.addch(8, 12, '└')
                win.addch(8, 13, '─')
                win.addch(8, 14, '┘')
                win.addch(7, 13, craft_item_2.designation)

            win.addch(7, 19, '➜')
            if pre_craft[2] == True:
                win.addstr(5, 22, 'итог', curses.A_BOLD)
                win.addch(6, 22, '┌', curses.A_BOLD)
                win.addch(6, 23, '─', curses.A_BOLD)
                win.addch(6, 24, '┐', curses.A_BOLD)
                win.addch(7, 22, '│', curses.A_BOLD)
                win.addch(7, 24, '│', curses.A_BOLD)
                win.addch(8, 22, '└', curses.A_BOLD)
                win.addch(8, 23, '─', curses.A_BOLD)
                win.addch(8, 24, '┘', curses.A_BOLD)
                win.addch(7, 23, crafted_item.designation, curses.A_BOLD)
            else:
                win.addstr(5, 22, 'итог')
                win.addch(6, 22, '┌')
                win.addch(6, 23, '─')
                win.addch(6, 24, '┐')
                win.addch(7, 22, '│')
                win.addch(7, 24, '│')
                win.addch(8, 22, '└')
                win.addch(8, 23, '─')
                win.addch(8, 24, '┘')
                win.addch(7, 23, crafted_item.designation)
            win.timeout(100) 

    if key == ord('q'):
        win.addstr(2, 2, "действительно ли вы хотите покинуть игру? Нажмите Y(Да) или N(Нет)")
        while key != ord('y') or key != ord('n'):
            key = win.getch()
            if key == ord('y'):
                end_game = True
                break
            if key == ord('n'):
                break
            win.timeout(100)
#вывод произваольного текста
#    win.addstr(2, 2, "текст")
#    win.refresh()

#использование цвета
#   curses.start_color()
#   curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) цвет 1; первый цвет это цвет символов, а второй цвет фона
#   curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE) цвет 2; первый цвет это цвет символов, а второй цвет фона
#    win.addstr(height_map - 2, 1, "hungry "+str(hungry)+'/'+str(max_hungry), curses.color_pair(1)) использование цвета 1
#    win.addstr(height_map - 1, 1, "water "+str(water)+'/'+str(max_water), curses.color_pair(2)) использование цвета 2


    #вывод статов
    win.addstr(height_map - 2, 1, "hungry "+str(hungry)+'/'+str(max_hungry))
    win.addstr(height_map - 1, 1, "water "+str(water)+'/'+str(max_water))
    win.addstr(height_map, 1, "health "+str(health)+'/'+str(max_health))

    if game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].name == 'grave':
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1] = map_cell(*all_cell[0])
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].x = width_map // 3 + 3
            game_map[height_map // 2 + 1][width_map // 3 + 4 + 1].y = height_map // 2
            points += 100
            water += 50
            hungry += 50
            main_player_in_fight.health = health
            main_player_in_fight.effects = []
            fight(main_player_in_fight, summon(*all_summons[0]))
            gold = random.randint(500, 3000)

sc.refresh()
curses.endwin()





