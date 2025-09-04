import pygame

# --- Параметры ---
TILE_SIZE = 10  # Размер одного тайла в пикселях
GRID_WIDTH = 80  # Количество тайлов по ширине
GRID_HEIGHT = 43 # Количество тайлов по высоте
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Цвета (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Доступные тайлы (простые цвета для примера)
# Можно использовать изображения, но для простоты начнем с цветов
TILES = {
    "empty": GRAY,
    "wall": BLACK,
    "player": RED,
    "enemy": BLUE,
    "item": GREEN
}

# --- Инициализация ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tile Editor")

# Словарь для хранения состояния каждого тайла на сетке
# grid[y][x] = "tile_key"
# Поменяли местами GRID_WIDTH и GRID_HEIGHT при создании
grid = [["wall" for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Переменные для выбора тайла
current_tile_index = 0
tile_keys = list(TILES.keys()) # Список ключей доступных тайлов

# Переменные для отслеживания нажатия мыши
drawing = False

# --- Функции ---
def draw_grid():
    """Рисует сетку и тайлы"""
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile_key = grid[y][x]
            color = TILES.get(tile_key, GRAY) # Получаем цвет по ключу, или серый если нет

            # Рисуем сам тайл
            pygame.draw.rect(screen, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

            # Рисуем границы тайла
            pygame.draw.rect(screen, GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1) # Толщина 1 пиксель

def get_mouse_tile_pos():
    """Возвращает координаты тайла, над которым находится мышь"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if 0 <= mouse_x < SCREEN_WIDTH and 0 <= mouse_y < SCREEN_HEIGHT:
        return mouse_x // TILE_SIZE, mouse_y // TILE_SIZE
    return None, None

def export_grid_to_data():
    """Экспортирует текущую сетку в виде данных (список списков строк)"""
    # Транспонируем сетку перед экспортом
    transposed_grid = list(zip(*grid))  # Используем zip для транспонирования
    data = []
    for row in transposed_grid:
        data_row = []
        for tile_key in row:
            data_row.append(tile_key) # Добавляем ключ тайла
        data.append(data_row)
    return data

def display_tile_palette():
    """Отображает палитру доступных тайлов для выбора"""
    palette_x = SCREEN_WIDTH + 20 # Положение палитры справа от основной сетки
    palette_y_start = 20
    tile_palette_spacing = TILE_SIZE + 10 # Отступ между тайлами в палитре

    font = pygame.font.Font(None, 24) # Шрифт для подписей

    screen.blit(font.render("Choose Tile:", True, WHITE), (palette_x, palette_y_start - 30))

    for i, tile_key in enumerate(tile_keys):
        color = TILES[tile_key]
        rect = pygame.Rect(palette_x, palette_y_start + i * tile_palette_spacing, TILE_SIZE, TILE_SIZE)

        # Выделяем выбранный тайл
        if i == current_tile_index:
            pygame.draw.rect(screen, WHITE, rect, 3) # Белая рамка

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, GRAY, rect, 1) # Граница тайла

        # Добавляем подпись к тайлу
        text_surface = font.render(tile_key, True, WHITE)
        screen.blit(text_surface, (rect.right + 5, rect.centery - text_surface.get_height() // 2))


# --- Основной цикл ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # --- Обработка нажатий мыши ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Левая кнопка мыши
                # Проверяем, нажата ли кнопка выбора тайла в палитре
                palette_x_start = SCREEN_WIDTH + 20
                palette_y_start = 20
                tile_palette_spacing = TILE_SIZE + 10
                for i, tile_key in enumerate(tile_keys):
                    rect = pygame.Rect(palette_x_start, palette_y_start + i * tile_palette_spacing, TILE_SIZE, TILE_SIZE)
                    if rect.collidepoint(event.pos):
                        current_tile_index = i
                        drawing = False # Останавливаем рисование, пока не выберем тайл
                        break # Выходим из цикла, если кнопка найдена
                else: # Если нажатие было не на палитре
                    drawing = True # Начинаем рисовать

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Левая кнопка мыши
                drawing = False

        # --- Обработка перемещения мыши ---
        if event.type == pygame.MOUSEMOTION:
            if drawing:
                grid_x, grid_y = get_mouse_tile_pos()
                if grid_x is not None and grid_y is not None:
                    # Изменяем тайл только если он отличается, чтобы избежать лишних обновлений
                    if grid[grid_y][grid_x] != tile_keys[current_tile_index]:
                        grid[grid_y][grid_x] = tile_keys[current_tile_index]

        # --- Обработка прокрутки мыши (для выбора тайла) ---
        if event.type == pygame.MOUSEWHEEL:
            # Прокрутка вверх
            if event.y > 0:
                current_tile_index = (current_tile_index - 1) % len(tile_keys)
            # Прокрутка вниз
            elif event.y < 0:
                current_tile_index = (current_tile_index + 1) % len(tile_keys)

    # --- Отрисовка ---
    screen.fill(WHITE) # Очищаем экран
    draw_grid()
    display_tile_palette()

    # Отображаем выбранный тайл внизу экрана
    font = pygame.font.Font(None, 30)
    current_tile_key = tile_keys[current_tile_index]
    current_tile_color = TILES[current_tile_key]
    pygame.draw.rect(screen, current_tile_color, (10, SCREEN_HEIGHT - 40, 32, 32))
    pygame.draw.rect(screen, GRAY, (10, SCREEN_HEIGHT - 40, 32, 32), 2)
    screen.blit(font.render(f"Selected: {current_tile_key}", True, WHITE), (50, SCREEN_HEIGHT - 35))

    pygame.display.flip() # Обновляем экран

# --- Экспорт данных после закрытия окна ---
final_data = export_grid_to_data()
print("Exported Grid Data (list of lists of tile keys):")
for row in final_data:
    print(row)

pygame.quit()