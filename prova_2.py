import pygame
import math
import heapq
import os
import threading
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(BASE_DIR, "mappe2", "lt_foundry_n.map")

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Algorithm")

# Parametri viewport fissi
VIEWPORT_WIDTH = WIDTH
VIEWPORT_HEIGHT = WIDTH
SCROLL_SPEED = 20
MIN_NODE_SIZE = 5  # Dimensione minima dei nodi in pixel

# Variabili globali
stop_requested = False
algorithm_running = False

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
        
        # Solo disegna se il nodo è visibile nel viewport
        if (-self.width <= draw_x <= VIEWPORT_WIDTH and 
            -self.height <= draw_y <= VIEWPORT_HEIGHT):
            pygame.draw.rect(win, self.color, (draw_x, draw_y, self.width, self.height))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        # Giù
        if self.row < self.tot_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row + 1][self.col])
        # Su
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row - 1][self.col])
        # Destra
        if self.col < self.tot_cols - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col + 1])
        # Sinistra
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
        # Controllo eventi pygame per evitare freeze
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
        
        # Disegna solo ogni N step per ridurre il flickering
        step_counter += 1
        if step_counter % 5 == 0:  # Disegna ogni 5 step
            draw_func()
            pygame.time.delay(10)  # Piccola pausa per vedere l'animazione
    
    return False

def load_map(map_path):
    """Carica una mappa da file"""
    try:
        with open(map_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        # Trova la linea "map"
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
        
        # Popola la griglia con gli ostacoli
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

def make_grid(rows, cols):
    """Crea una griglia di nodi con dimensioni uniformi ottimizzate"""
    import math
    
    # Calcola dimensioni che utilizzano il più possibile lo spazio disponibile
    exact_width = VIEWPORT_WIDTH / cols
    exact_height = VIEWPORT_HEIGHT / rows
    
    # Se i nodi sarebbero troppo piccoli, usa dimensione minima
    if exact_width >= MIN_NODE_SIZE and exact_height >= MIN_NODE_SIZE:
        # Per mappe piccole/medie, arrotonda per eccesso per riempire meglio
        if rows <= 80 and cols <= 80:
            node_width = math.ceil(exact_width)
            node_height = math.ceil(exact_height)
            
            # Se supera di poco, riduci di 1 (preferibilmente mantieni l'arrotondamento per eccesso)
            if cols * node_width > VIEWPORT_WIDTH + 10:  # Tolleranza di 10px
                node_width -= 1
            if rows * node_height > VIEWPORT_HEIGHT + 10:
                node_height -= 1
        else:
            # Per mappe più grandi, usa arrotondamento normale
            node_width = round(exact_width)
            node_height = round(exact_height)
        
        print(f"Debug: Griglia {rows}x{cols}")
        print(f"Debug: Dimensione esatta: {exact_width:.2f}x{exact_height:.2f}")
        print(f"Debug: Dimensione finale: {node_width}x{node_height}")
        print(f"Debug: Totale: {cols*node_width}x{rows*node_height} (viewport: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT})")
    else:
        # Per mappe molto grandi, usa dimensione minima
        node_width = MIN_NODE_SIZE
        node_height = MIN_NODE_SIZE
        print(f"Debug: Griglia molto grande {rows}x{cols}, usando dimensione minima {MIN_NODE_SIZE}")
    
    # Crea griglia con nodi uniformi
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(cols):
            node = Node(i, j, node_width, node_height, rows, cols)
            grid[i].append(node)
    
    return grid, node_width, node_height

def draw_grid(win, rows, cols, node_width, node_height, offset_x, offset_y):
    """Disegna la griglia"""
    # Linee orizzontali
    for i in range(rows + 1):
        y = i * node_height - offset_y
        if -1 <= y <= VIEWPORT_HEIGHT + 1:
            pygame.draw.line(win, GREY, (0, y), (VIEWPORT_WIDTH, y))
    
    # Linee verticali
    for j in range(cols + 1):
        x = j * node_width - offset_x
        if -1 <= x <= VIEWPORT_WIDTH + 1:
            pygame.draw.line(win, GREY, (x, 0), (x, VIEWPORT_HEIGHT))

def draw(win, grid, rows, cols, node_width, node_height, offset_x, offset_y):
    """Funzione di disegno principale"""
    win.fill(BACKGROUND)
    
    # Disegna solo i nodi visibili
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
    # Aggiusta per l'offset
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
    pygame.init()
    
    # Parametri iniziali
    ROWS, COLS = 50, 50
    grid, node_width, node_height = make_grid(ROWS, COLS)
    
    # Offset iniziali 
    total_width = COLS * node_width
    total_height = ROWS * node_height
    print(f"Debug main: viewport {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}, griglia totale {total_width}x{total_height}")
    print(f"Debug main: spazio inutilizzato: W={VIEWPORT_WIDTH-total_width}, H={VIEWPORT_HEIGHT-total_height}")
    
    # Calcolo offset per centratura
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
    
    # Disegno iniziale
    draw(WIN, grid, ROWS, COLS, node_width, node_height, offset_x, offset_y)
    
    clock = pygame.time.Clock()
    needs_redraw = False  # Flag per gestire il ridisegno
    
    while running:
        clock.tick(60)  # Limita FPS per stabilità
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_requested = True
                running = False
                break
            
            # Gestione tastiera
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not algorithm_running:
                    # Avvia algoritmo
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    
                    algorithm_running = True
                    stop_requested = False
                    draw_func = lambda: draw(WIN, grid, ROWS, COLS, node_width, node_height, offset_x, offset_y)
                    thread = threading.Thread(target=run_algorithm_thread, args=(draw_func, grid, start, end))
                    thread.daemon = True
                    thread.start()
                
                elif event.key == pygame.K_m and not algorithm_running:
                    # Carica mappa
                    result = load_map(MAP)
                    if result[0] is not None:
                        grid, ROWS, COLS, node_width, node_height = result
                        
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
                        
                        start = None
                        end = None
                        map_loaded = True
                        needs_redraw = True
                
                elif event.key == pygame.K_c and not algorithm_running:
                    # Reset con centratura
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
        
        # Gestione mouse continua (fuori dal loop eventi per catturare anche quando tieni premuto)
        if not algorithm_running:
            mouse_buttons = pygame.mouse.get_pressed()
            
            if mouse_buttons[0]:  # Tasto sinistro premuto
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
            
            elif mouse_buttons[2]:  # Tasto destro premuto
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
            
            # Gestione scroll continuo
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
        
        # Ridisegna solo quando necessario
        if needs_redraw:
            draw(WIN, grid, ROWS, COLS, node_width, node_height, offset_x, offset_y)
            needs_redraw = False
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()