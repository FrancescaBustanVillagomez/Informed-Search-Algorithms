import pygame
import math
import heapq
import os
import threading
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(BASE_DIR, "mappe", "arena2.map")

WIDTH = 800
WIN = None  # Verrà inizializzato dopo
pygame.display.set_caption("A* Algorithm")

# Parametri viewport dinamici
VIEWPORT_WIDTH = WIDTH
VIEWPORT_HEIGHT = WIDTH
SCROLL_SPEED = 20
MIN_NODE_SIZE = 5

# Variabili globali
stop_requested = False
algorithm_running = False
is_fullscreen = False  # NUOVO: tracking modalità fullscreen
original_viewport_size = (WIDTH, WIDTH)  # NUOVO: salva dimensioni originali

# Colori
EXPLORED = (236, 204, 124)
FRONTIER = (213, 124, 49) 
BACKGROUND = (255, 255, 255)
OBSTACLE = (0, 0, 0) 
PATH = (255, 175, 44)
START = (222, 152, 78) 
GREY = (128, 128, 128)
END = (217, 101, 39)

class Node:
    def __init__(self, row, col, width, height, tot_rows, tot_cols):
        self.row = row
        self.col = col
        self.tot_rows = tot_rows
        self.tot_cols = tot_cols
        self.width = width
        self.height = height
        self.x = col * width
        self.y = row * height
        self.color = BACKGROUND
        self.neighbors = []
        
    def get_pos(self):
        return self.row, self.col

    def is_explored(self):
        return self.color == EXPLORED

    def is_in_frontier(self):
        return self.color == FRONTIER

    def is_obstacle(self):
        return self.color == OBSTACLE
    
    def is_start(self):
        return self.color == START
    
    def is_end(self):
        return self.color == END
    
    def reset(self):
        self.color = BACKGROUND

    def make_explored(self):
        self.color = EXPLORED
    
    def make_frontier(self):
        self.color = FRONTIER

    def make_obstacle(self):
        self.color = OBSTACLE
    
    def make_start(self):
        self.color = START
    
    def make_end(self):
        self.color = END
    
    def make_path(self):
        self.color = PATH

    def draw(self, win, offset_x, offset_y):
        draw_x = self.x - offset_x
        draw_y = self.y - offset_y
        
        if (-self.width <= draw_x <= VIEWPORT_WIDTH and 
            -self.height <= draw_y <= VIEWPORT_HEIGHT):
            pygame.draw.rect(win, self.color, (draw_x, draw_y, self.width, self.height))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.tot_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.tot_cols - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    """Euristica Manhattan distance"""
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def draw_path(parent, node, draw_func):
    """Ricostruisce e disegna il percorso trovato"""
    while node in parent:
        node = parent[node]
        if not node.is_start() and not node.is_end():
            node.make_path()
        draw_func()

def algorithm(draw_func, grid, start, end):
    """Algoritmo A*"""
    global stop_requested
    count = 0
    frontier = []
    heapq.heappush(frontier, (0, count, start))
    
    parent = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    
    frontier_track = {start}
    step_counter = 0
    
    while frontier and not stop_requested:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        current = heapq.heappop(frontier)[2]
        frontier_track.remove(current)
        
        if current == end:
            draw_path(parent, current, draw_func)
            end.make_end()
            start.make_start()
            return True
            
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            
            if temp_g_score < g_score[neighbor]:
                parent[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                
                if neighbor not in frontier_track:
                    count += 1
                    heapq.heappush(frontier, (f_score[neighbor], count, neighbor))
                    frontier_track.add(neighbor)
                    if neighbor != end:
                        neighbor.make_frontier()
        
        if current != start:
            current.make_explored()
        
        step_counter += 1
        if step_counter % 5 == 0:
            draw_func()
            pygame.time.delay(10)
    
    return False

def load_map(map_path):
    """Carica una mappa da file"""
    try:
        with open(map_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        map_idx = None
        for i, line in enumerate(lines):
            if line.lower() == "map":
                map_idx = i + 1
                break
        
        if map_idx is None:
            print("Errore: manca la riga 'map' nel file")
            return None, 0, 0, 0, 0
        
        map_lines = lines[map_idx:]
        rows = len(map_lines)
        cols = len(map_lines[0]) if map_lines else 0
        
        if rows == 0 or cols == 0:
            print("Errore: mappa vuota")
            return None, 0, 0, 0, 0
        
        grid, node_width, node_height = make_grid(rows, cols)
        
        for r, line in enumerate(map_lines):
            for c, ch in enumerate(line):
                if r < rows and c < cols:
                    node = grid[r][c]
                    if ch != ".":
                        node.make_obstacle()
        
        return grid, rows, cols, node_width, node_height
        
    except FileNotFoundError:
        print(f"Errore: file {map_path} non trovato")
        return None, 0, 0, 0, 0
    except Exception as e:
        print(f"Errore nel caricamento della mappa: {e}")
        return None, 0, 0, 0, 0

# NUOVO: Funzione per toggle fullscreen
def toggle_fullscreen(rows, cols, current_node_size):
    """Attiva/disattiva modalità fullscreen e ricalcola dimensioni"""
    global WIN, VIEWPORT_WIDTH, VIEWPORT_HEIGHT, is_fullscreen, original_viewport_size
    
    if not is_fullscreen:
        # Entra in fullscreen
        original_viewport_size = (VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        
        # Ottieni risoluzione schermo NATIVA (per HiDPI/Retina)
        # Usa flags per ottenere la risoluzione reale
        display_info = pygame.display.Info()
        screen_width = display_info.current_w
        screen_height = display_info.current_h
        
        # Per schermi HiDPI, pygame potrebbe dare valori scalati
        # Prova a usare la risoluzione desktop reale
        import ctypes
        try:
            # Windows
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            screen_width = user32.GetSystemMetrics(0)
            screen_height = user32.GetSystemMetrics(1)
            print(f"Debug: Risoluzione Windows nativa {screen_width}x{screen_height}")
        except:
            # Linux/Mac - usa pygame standard
            print(f"Debug: Risoluzione pygame {screen_width}x{screen_height}")
        
        VIEWPORT_WIDTH = screen_width
        VIEWPORT_HEIGHT = screen_height
        
        # Usa SCALED per supporto HiDPI automatico
        WIN = pygame.display.set_mode((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), 
                                       pygame.FULLSCREEN | pygame.SCALED)
        is_fullscreen = True
        
        print(f"Debug: Fullscreen attivato {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
        
        # Ricalcola dimensioni nodi per riempire lo schermo grande
        grid, node_width, node_height = make_grid(rows, cols)
        return grid, node_width, node_height
    else:
        # Esci da fullscreen
        VIEWPORT_WIDTH, VIEWPORT_HEIGHT = original_viewport_size
        WIN = pygame.display.set_mode((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
        is_fullscreen = False
        
        print(f"Debug: Fullscreen disattivato {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
        
        # Ripristina dimensioni originali
        grid, node_width, node_height = make_grid(rows, cols)
        return grid, node_width, node_height

def adjust_viewport_to_grid(rows, cols, node_size):
    """Adatta il viewport alla griglia se possibile"""
    global VIEWPORT_WIDTH, VIEWPORT_HEIGHT, WIN
    
    # Non ridimensionare se siamo in fullscreen
    if is_fullscreen:
        return False
    
    grid_width = cols * node_size
    grid_height = rows * node_size
    
    MAX_WINDOW_WIDTH = 1920
    MAX_WINDOW_HEIGHT = 1080
    MIN_WINDOW_SIZE = 400
    
    new_width = VIEWPORT_WIDTH
    new_height = VIEWPORT_HEIGHT
    
    if grid_width < VIEWPORT_WIDTH and grid_width >= MIN_WINDOW_SIZE:
        new_width = min(grid_width, MAX_WINDOW_WIDTH)
    
    if grid_height < VIEWPORT_HEIGHT and grid_height >= MIN_WINDOW_SIZE:
        new_height = min(grid_height, MAX_WINDOW_HEIGHT)
    
    if new_width != VIEWPORT_WIDTH or new_height != VIEWPORT_HEIGHT:
        VIEWPORT_WIDTH = new_width
        VIEWPORT_HEIGHT = new_height
        WIN = pygame.display.set_mode((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
        print(f"Debug: Viewport ridimensionato a {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
        return True
    
    return False

def make_grid(rows, cols):
    """Crea una griglia di nodi QUADRATI ottimizzata"""
    size_for_width = VIEWPORT_WIDTH / cols
    size_for_height = VIEWPORT_HEIGHT / rows
    exact_size = min(size_for_width, size_for_height)
    
    if exact_size < MIN_NODE_SIZE:
        node_size = MIN_NODE_SIZE
        print(f"Debug: Griglia molto grande {rows}×{cols}, usando dimensione minima {MIN_NODE_SIZE}")
    else:
        node_size_floor = math.floor(exact_size)
        node_size_ceil = math.ceil(exact_size)
        
        width_floor = cols * node_size_floor
        height_floor = rows * node_size_floor
        width_ceil = cols * node_size_ceil
        height_ceil = rows * node_size_ceil
        
        usage_floor_w = width_floor / VIEWPORT_WIDTH
        usage_floor_h = height_floor / VIEWPORT_HEIGHT
        usage_ceil_w = width_ceil / VIEWPORT_WIDTH
        usage_ceil_h = height_ceil / VIEWPORT_HEIGHT
        
        waste_floor = max(0, 1 - usage_floor_w) + max(0, 1 - usage_floor_h)
        waste_ceil = max(0, 1 - usage_ceil_w) + max(0, 1 - usage_ceil_h)
        
        overflow_floor = max(usage_floor_w, usage_floor_h)
        overflow_ceil = max(usage_ceil_w, usage_ceil_h)
        
        # FULLSCREEN: usa sempre ceil per massimizzare riempimento
        if is_fullscreen:
            node_size = node_size_ceil
            reason = f"FULLSCREEN: uso ceil per riempire (utilizzo {usage_ceil_w*100:.1f}% × {usage_ceil_h*100:.1f}%)"
        else:
            # Modalità normale: limiti conservativi
            MAX_OVERFLOW = 1.05
            MIN_USAGE = 0.90
            
            if overflow_ceil <= MAX_OVERFLOW and waste_floor - waste_ceil > 0.05:
                node_size = node_size_ceil
                reason = f"ceil per riempire meglio (spreco: floor={waste_floor*100:.1f}% vs ceil={waste_ceil*100:.1f}%)"
            elif overflow_ceil <= MAX_OVERFLOW and (usage_floor_w < MIN_USAGE or usage_floor_h < MIN_USAGE):
                node_size = node_size_ceil
                reason = f"ceil perché floor sottoutilizza ({usage_floor_w*100:.1f}% × {usage_floor_h*100:.1f}%)"
            else:
                node_size = node_size_floor
                if overflow_ceil > MAX_OVERFLOW:
                    reason = f"floor per evitare overflow (ceil→{overflow_ceil*100:.1f}%)"
                else:
                    reason = f"floor per sicurezza (utilizzo {usage_floor_w*100:.1f}% × {usage_floor_h*100:.1f}%)"
        
        print(f"Debug: {reason}")
    
    total_width = cols * node_size
    total_height = rows * node_size
    node_width = node_height = node_size
    
    usage_w = (total_width / VIEWPORT_WIDTH) * 100
    usage_h = (total_height / VIEWPORT_HEIGHT) * 100
    waste_w = max(0, VIEWPORT_WIDTH - total_width)
    waste_h = max(0, VIEWPORT_HEIGHT - total_height)
    
    aspect_ratio = max(cols/rows, rows/cols)
    print(f"Debug: Griglia {rows}×{cols} (aspect ratio: {aspect_ratio:.2f})")
    print(f"Debug: Dimensione calcolata: {exact_size:.2f}px → finale: {node_size}×{node_size}px")
    print(f"Debug: Totale griglia: {total_width}×{total_height} vs viewport {VIEWPORT_WIDTH}×{VIEWPORT_HEIGHT}")
    print(f"Debug: Utilizzo: {usage_w:.1f}% width, {usage_h:.1f}% height")
    print(f"Debug: Spreco: {waste_w}px width ({waste_w/VIEWPORT_WIDTH*100:.1f}%), {waste_h}px height ({waste_h/VIEWPORT_HEIGHT*100:.1f}%)")
    
    # Adatta viewport solo se non in fullscreen
    if not is_fullscreen:
        adjust_viewport_to_grid(rows, cols, node_size)
    
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            node = Node(i, j, node_width, node_height, rows, cols)
            grid[i].append(node)
    
    return grid, node_width, node_height

def draw_grid(win, rows, cols, node_width, node_height, offset_x, offset_y):
    """Disegna la griglia"""
    for i in range(rows + 1):
        y = i * node_height - offset_y
        if -1 <= y <= VIEWPORT_HEIGHT + 1:
            pygame.draw.line(win, GREY, (0, y), (VIEWPORT_WIDTH, y))
    
    for j in range(cols + 1):
        x = j * node_width - offset_x
        if -1 <= x <= VIEWPORT_WIDTH + 1:
            pygame.draw.line(win, GREY, (x, 0), (x, VIEWPORT_HEIGHT))

def draw(win, grid, rows, cols, node_width, node_height, offset_x, offset_y):
    """Funzione di disegno principale"""
    win.fill(BACKGROUND)
    
    start_row = max(0, offset_y // node_height)
    end_row = min(rows, (offset_y + VIEWPORT_HEIGHT) // node_height + 1)
    start_col = max(0, offset_x // node_width)
    end_col = min(cols, (offset_x + VIEWPORT_WIDTH) // node_width + 1)
    
    for i in range(start_row, end_row):
        for j in range(start_col, end_col):
            if i < rows and j < cols:
                grid[i][j].draw(win, offset_x, offset_y)
    
    draw_grid(win, rows, cols, node_width, node_height, offset_x, offset_y)
    pygame.display.update()

def get_clicked_position(pos, node_width, node_height, offset_x, offset_y):
    """Converte coordinate del mouse in posizione griglia"""
    x, y = pos
    world_x = x + offset_x
    world_y = y + offset_y
    
    row = world_y // node_height
    col = world_x // node_width
    return row, col

def run_algorithm_thread(draw_func, grid, start, end):
    """Esegue l'algoritmo in un thread separato"""
    global algorithm_running
    try:
        algorithm(draw_func, grid, start, end)
    finally:
        algorithm_running = False

def main():
    """Funzione principale"""
    global WIN, VIEWPORT_WIDTH, VIEWPORT_HEIGHT
    
    pygame.init()
    
    WIN = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("A* Algorithm")
    
    ROWS, COLS = 50, 50
    grid, node_width, node_height = make_grid(ROWS, COLS)
    
    total_width = COLS * node_width
    total_height = ROWS * node_height
    print(f"Debug main: viewport {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}, griglia totale {total_width}x{total_height}")
    print(f"Debug main: spazio inutilizzato: W={VIEWPORT_WIDTH-total_width}, H={VIEWPORT_HEIGHT-total_height}")
    
    if total_width < VIEWPORT_WIDTH:
        offset_x = -(VIEWPORT_WIDTH - total_width) // 2
        print(f"Debug: Centratura X, offset = {offset_x}")
    else:
        offset_x = 0
        
    if total_height < VIEWPORT_HEIGHT:
        offset_y = -(VIEWPORT_HEIGHT - total_height) // 2
        print(f"Debug: Centratura Y, offset = {offset_y}")  
    else:
        offset_y = 0
    
    global stop_requested, algorithm_running
    algorithm_running = False
    start = None
    end = None
    running = True
    map_loaded = False
    
    draw(WIN, grid, ROWS, COLS, node_width, node_height, offset_x, offset_y)
    
    clock = pygame.time.Clock()
    needs_redraw = False
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_requested = True
                running = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not algorithm_running:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    
                    algorithm_running = True
                    stop_requested = False
                    draw_func = lambda: draw(WIN, grid, ROWS, COLS, node_width, node_height, offset_x, offset_y)
                    thread = threading.Thread(target=run_algorithm_thread, args=(draw_func, grid, start, end))
                    thread.daemon = True
                    thread.start()
                
                # NUOVO: Toggle fullscreen con F11
                elif event.key == pygame.K_F11 and not algorithm_running:
                    # Salva stato start/end
                    old_start_pos = start.get_pos() if start else None
                    old_end_pos = end.get_pos() if end else None
                    
                    # Toggle fullscreen e ricalcola griglia
                    result = toggle_fullscreen(ROWS, COLS, node_width)
                    if result:
                        grid, node_width, node_height = result
                        
                        # Ripristina start/end
                        if old_start_pos:
                            r, c = old_start_pos
                            start = grid[r][c]
                            start.make_start()
                        else:
                            start = None
                            
                        if old_end_pos:
                            r, c = old_end_pos
                            end = grid[r][c]
                            end.make_end()
                        else:
                            end = None
                        
                        # Ricalcola offset per centratura
                        total_width = COLS * node_width
                        total_height = ROWS * node_height
                        
                        if total_width < VIEWPORT_WIDTH:
                            offset_x = -(VIEWPORT_WIDTH - total_width) // 2
                        else:
                            offset_x = 0
                            
                        if total_height < VIEWPORT_HEIGHT:
                            offset_y = -(VIEWPORT_HEIGHT - total_height) // 2
                        else:
                            offset_y = 0
                        
                        needs_redraw = True
                
                elif event.key == pygame.K_m and not algorithm_running:
                    result = load_map(MAP)
                    if result[0] is not None:
                        grid, ROWS, COLS, node_width, node_height = result
                        
                        total_width = COLS * node_width
                        total_height = ROWS * node_height
                        
                        if total_width < VIEWPORT_WIDTH:
                            offset_x = -(VIEWPORT_WIDTH - total_width) // 2
                        else:
                            offset_x = 0
                            
                        if total_height < VIEWPORT_HEIGHT:
                            offset_y = -(VIEWPORT_HEIGHT - total_height) // 2
                        else:
                            offset_y = 0
                        
                        start = None
                        end = None
                        map_loaded = True
                        needs_redraw = True
                
                elif event.key == pygame.K_c and not algorithm_running:
                    start = None
                    end = None
                    grid, node_width, node_height = make_grid(ROWS, COLS)
                    map_loaded = False
                    
                    total_width = COLS * node_width
                    total_height = ROWS * node_height
                    
                    if total_width < VIEWPORT_WIDTH:
                        offset_x = -(VIEWPORT_WIDTH - total_width) // 2
                    else:
                        offset_x = 0
                        
                    if total_height < VIEWPORT_HEIGHT:
                        offset_y = -(VIEWPORT_HEIGHT - total_height) // 2
                    else:
                        offset_y = 0
                    
                    needs_redraw = True
                
                # NUOVO: ESC per uscire da fullscreen
                elif event.key == pygame.K_ESCAPE and is_fullscreen:
                    old_start_pos = start.get_pos() if start else None
                    old_end_pos = end.get_pos() if end else None
                    
                    result = toggle_fullscreen(ROWS, COLS, node_width)
                    if result:
                        grid, node_width, node_height = result
                        
                        if old_start_pos:
                            r, c = old_start_pos
                            start = grid[r][c]
                            start.make_start()
                        else:
                            start = None
                            
                        if old_end_pos:
                            r, c = old_end_pos
                            end = grid[r][c]
                            end.make_end()
                        else:
                            end = None
                        
                        total_width = COLS * node_width
                        total_height = ROWS * node_height
                        
                        if total_width < VIEWPORT_WIDTH:
                            offset_x = -(VIEWPORT_WIDTH - total_width) // 2
                        else:
                            offset_x = 0
                            
                        if total_height < VIEWPORT_HEIGHT:
                            offset_y = -(VIEWPORT_HEIGHT - total_height) // 2
                        else:
                            offset_y = 0
                        
                        needs_redraw = True
        
        if not algorithm_running:
            mouse_buttons = pygame.mouse.get_pressed()
            
            if mouse_buttons[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, node_width, node_height, offset_x, offset_y)
                
                if 0 <= row < ROWS and 0 <= col < COLS:
                    node = grid[row][col]
                    
                    if not start and node != end and not node.is_obstacle():
                        start = node
                        start.make_start()
                        needs_redraw = True
                    elif not end and node != start and not node.is_obstacle():
                        end = node
                        end.make_end()
                        needs_redraw = True
                    elif node != end and node != start and not map_loaded and not node.is_obstacle():
                        node.make_obstacle()
                        needs_redraw = True
            
            elif mouse_buttons[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, node_width, node_height, offset_x, offset_y)
                
                if 0 <= row < ROWS and 0 <= col < COLS:
                    node = grid[row][col]
                    changed = False
                    
                    if node == start:
                        start = None
                        node.reset()
                        changed = True
                    elif node == end:
                        end = None
                        node.reset()
                        changed = True
                    elif not map_loaded and node.is_obstacle():
                        node.reset()
                        changed = True
                    
                    if changed:
                        needs_redraw = True
            
            keys = pygame.key.get_pressed()
            total_width = COLS * node_width
            total_height = ROWS * node_height
            
            if total_width > VIEWPORT_WIDTH:
                if keys[pygame.K_LEFT]:
                    new_offset_x = max(0, offset_x - SCROLL_SPEED)
                    if new_offset_x != offset_x:
                        offset_x = new_offset_x
                        needs_redraw = True
                if keys[pygame.K_RIGHT]:
                    new_offset_x = min(total_width - VIEWPORT_WIDTH, offset_x + SCROLL_SPEED)
                    if new_offset_x != offset_x:
                        offset_x = new_offset_x
                        needs_redraw = True
            
            if total_height > VIEWPORT_HEIGHT:
                if keys[pygame.K_UP]:
                    new_offset_y = max(0, offset_y - SCROLL_SPEED)
                    if new_offset_y != offset_y:
                        offset_y = new_offset_y
                        needs_redraw = True
                if keys[pygame.K_DOWN]:
                    new_offset_y = min(total_height - VIEWPORT_HEIGHT, offset_y + SCROLL_SPEED)
                    if new_offset_y != offset_y:
                        offset_y = new_offset_y
                        needs_redraw = True
        
        if needs_redraw:
            draw(WIN, grid, ROWS, COLS, node_width, node_height, offset_x, offset_y)
            needs_redraw = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()