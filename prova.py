import pygame
import math # mi serve per abs da usare nella euristica
import heapq   #frontiera
import re
import os
from queue import PriorityQueue
MAP_PATH = "mappe/arena.map"
SCEN_PATH = "maps/arena.scen"

WIDTH =800 #larghzza finestra
WIN = pygame.display.set_mode((WIDTH,WIDTH))  #funzione che mi permette di creare la finestra princiaple di tipo surface con cui posso interagire
pygame.display.set_caption("A* Algotithm")  #imposto titolo della finestra

#definzione dei colori usati per l'interfaccia (colori in RGB)
RED = (255,0,0) # esplorati
GREEN =(0,255,0) # non ancora esplorati
BLUE = (0,0,255)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK =(0,0,0) # ostacolo
PURPLE =(128,0,128)  # percorso
ORANGE = (255,165,0) # inizio
GREY = (128,128,128)
TORQUOISE = (64,224,208) # fine

class Node:
    def __init__(self,row,col,width,tot_rows):  #costruttore della classe nodo
        self.row=row   #riga in cui si trova il nodo 
        self.col=col   # colonna in cui si trova il nodo    -> entrambi servono per la logica dell'algoritmo
        self.tot_rows=tot_rows   # num tot di righe e colonne della griglia
        self.width=width  #larghezza in pixel di ogni nodo
        self.x= row*width   #riga che indica la posizione grafica(in pixel) che serve a pygame 
        self.y=col*width    # colonna //
        self.color=WHITE    
        self.neighbors = []
        
    def get_pos(self):  #ritorna la posizione del nodo
        return self.row, self.col

    def is_explored(self):
        return self.color == RED  # se il coloro è rosso singifica che è gia stato esplorato

    def is_in_frontier(self):
        return self.color == GREEN

    def is_obstacle(self):
        return self.color == BLACK
    
    def is_start(self):
        return self.color == ORANGE
    
    def is_end(self):
        return self.color == TORQUOISE
    
    def reset(self):
        self.color =  WHITE

    def make_explored(self):
        self.color = RED
    
    def make_frontier(self):
        self.color = GREEN

    def make_obstacle(self):
        self.color = BLACK
    
    def make_start(self):
        self.color = ORANGE
    
    def make_end(self):
        self.color = TORQUOISE
    
    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win,self.color,(self.x,self.y,self.width,self.width))
    
    def update_neighbors(self,grid):
        self.neighbors=[]
        if self.row<self.tot_rows-1 and not grid[self.row+1][self.col].is_obstacle():  # sto controllando se non mi trovo all'ultima riga e se quindi il nodo sotto di me non sia un ostacolo per aggiungerlo
            self.neighbors.append(grid[self.row+1][self.col])

        if self.row>0 and not grid[self.row-1][self.col].is_obstacle():  
            self.neighbors.append(grid[self.row-1][self.col])

        if self.col<self.tot_rows-1 and not grid[self.row][self.col+1].is_obstacle():  
            self.neighbors.append(grid[self.row][self.col+1])

        if self.col>0 and not grid[self.row][self.col-1].is_obstacle():  
            self.neighbors.append(grid[self.row][self.col-1])
        


    def __lt__(self,other):   # definisco come confrontare in nodi (less_than) quindi self<other sempre falso ovvero non considerarmi mai minore dell'altro
        return False
def load_map(filename):
    with open(filename, "r") as f:
        lines = f.readlines()

    # salto le prime 4 righe di intestazione
    header = 4  
    rows = len(lines) - header
    cols = len(lines[header].strip())

    grid = make_grid(rows, WIDTH)  # usa già la tua funzione esistente

    for i in range(rows):
        line = lines[header + i].strip()
        for j, char in enumerate(line):
            node = grid[i][j]
            if char == "@":   # muro
                node.make_obstacle()
            # se vuoi supportare altri simboli:
            # elif char == "T": ... (terreno difficile)
    return grid
def load_scenario(filename):
    with open(filename, "r") as f:
        lines = f.readlines()[1:]  # salta la riga "version"

    scenarios = []
    for line in lines:
        parts = line.strip().split()
        start = (int(parts[4]), int(parts[5]))
        goal = (int(parts[6]), int(parts[7]))
        scenarios.append((start, goal))
    return scenarios



def h(p1,p2):   # punto 1 e punto 2  manathan distance
    x1,y1 = p1 # estrae i valori da p1 in nelle variabili
    x2,y2 = p2
    return abs(x1-x2) + abs(y1-y2)
def draw_path(parent,node,draw):
    while node in parent:
        node = parent[node]
        node.make_path()
        draw()

def algorithm(draw,grid,start,end):
    count = 0 # serve per i tie breaker
    frontier = PriorityQueue()
    frontier.put((0,count,start))  # sto mettendo f(n) , count e start
    parent = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start]=0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start]=h(start.get_pos(), end.get_pos())

    frontier_track = {start}

    while not frontier.empty():
        for event in pygame.event.get():
            if event == pygame.QUIT:
                pygame.quit()

        node = frontier.get()[2]   # il terzo valore della tupla nell'insieme che rappresenta il nodo
        frontier_track.remove(node)

        if node == end:
            draw_path(parent,node,draw)
            end.make_end()
            start.make_start()
            return True
        for neighbor in node.neighbors:
            temp_g_score = g_score[node]+1
            if temp_g_score < g_score[neighbor]: # ho trovato un path migliore
                parent[neighbor] = node
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score+h(neighbor.get_pos(), end.get_pos())

                if neighbor not in frontier_track:
                    count+=1
                    frontier.put((f_score[neighbor],count,neighbor))
                    frontier_track.add(neighbor)
                    if neighbor != end:
                        neighbor.make_frontier()
        draw()

        if node != start:
            node.make_explored()
    return False   
        




def make_grid(rows,width):  # num righe e colonne totali e larghezza totale della finestra in pixel
    grid=[] # griglia sarà una lista di liste  dove ogni grid[i] è un riga della griglia e grid[i][j] è un nodo/cella
    dim = width // rows # dimensione in pixel di ogni nodo   es. se finestra di 400 px e rows=20 ogni cella sarà 400//20 = 20px
    for i in range(rows):  # fai i numeri da 0 a rows-1
        grid.append([])  # aggiungo per ogni riga i una lista vuota che conterrà i nodi di quella riga
        for j in range(rows): # per ogni colonna j nella riga i 
            node=Node(i,j,dim,rows) # creo un nodo
            grid[i].append(node) # aggiungo il nodo alla riga i
    return grid

def draw_grid(win,rows,width):  # finestra su cui disegnare, num righe e colonne totali, larghezza totale di win
    dim= width // rows
    for i in range(rows):
        pygame.draw.line(win,GREY,(0,i*dim),(width,i*dim)) # disegna una linea orizzontale per ogni riga sulla superficie win di colore GREY dal punto iniziale (0,i*dim) al punto finale (width,i*dim)
        for j in range(rows):
            pygame.draw.line(win,GREY,(j*dim,0),(j*dim,width))

def draw (win,grid,rows,width): 
    win.fill(WHITE)
    
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win,rows,width)
    pygame.display.update()      

def get_clicked_position(pos,rows,width):  #pos è la posizione restituita da pygame in pixel 
    dim = width // rows
    x,y = pos # pos sono coordinate in pixel dove x indica la colonna (le ascisse) y la riga (le ordinate)-> pygame restituisce (x,y) io li ho invertiti per convenzioni perche in (x,y) 
    row= x // dim
    col = y // dim
    return  row,col




def load_map_file(map_path, window_width):
    """
    Legge un file .map (MovingAI) e ritorna una grid (lista di liste) e rows.
    - interpreta '.' come libero; tutto il resto come ostacolo ([@,#,T,...])
    - scala la griglia alla finestra: make_grid(rows, window_width)
    """
    with open(map_path, "r") as f:
        lines = [line.rstrip("\n") for line in f if line.strip() != ""]

    # trova l'indice della linea "map" (case-insensitive)
    map_idx = None
    for i, line in enumerate(lines):
        if line.strip().lower() == "map":
            map_idx = i + 1
            break
    if map_idx is None:
        raise ValueError("File .map non valido: manca la riga 'map'")

    # parse header per altezza/larghezza (se presenti)
    height = None
    width = None
    for line in lines[:map_idx]:
        parts = line.split()
        if parts[0].lower() == "height":
            height = int(parts[1])
        if parts[0].lower() == "width":
            width = int(parts[1])

    map_lines = lines[map_idx: map_idx + (height if height else len(lines) - map_idx)]
    rows = len(map_lines)
    if width is None:
        width = len(map_lines[0])

    # crea la griglia usando la tua funzione: ogni nodo dimensionato in base a window_width
    grid = make_grid(rows, window_width)

    # marca ostacoli: per ogni carattere nella mappa, se non '.' => ostacolo
    for r, line in enumerate(map_lines):
        for c, ch in enumerate(line):
            if c >= len(grid[r]):  # protezione se righe irregolari
                continue
            if ch != '.':
                grid[r][c].make_obstacle()
    return grid, rows

def load_scen_file(scen_path):
    """
    Legge un file .scen e ritorna una lista di tuple (start, goal) dove start=(x,y), goal=(x,y).
    Strategia robusta: per ogni riga estrai gli interi e prendi, se possibile, gli ultimi 4 come startX,startY,goalX,goalY.
    """
    scenarios = []
    with open(scen_path, "r") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    # normalmente la prima linea è 'version ...' -> la saltiamo se non contiene 4+ interi
    for ln in lines:
        nums = re.findall(r"-?\d+", ln)
        nums = [int(n) for n in nums]
        if len(nums) >= 4:
            # prendi gli ultimi 4 numeri come (startX,startY,goalX,goalY)
            sx, sy, gx, gy = nums[-4], nums[-3], nums[-2], nums[-1]
            scenarios.append(((sx, sy), (gx, gy)))
    return scenarios



def listener(win, width):
    # inizializzazione: default (sarà sovrascritto se carichi una map)
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None
    run = True

    while run:
        # prima gestiamo gli eventi: se QUIT -> esci subito senza chiamare draw
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            # click / tasti solo se non abbiamo già lanciato l'algoritmo
            if event.type == pygame.MOUSEBUTTONDOWN:
                # tasto sinistro
                if event.button == 1:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_position(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        node = grid[row][col]
                        if not start and node != end:
                            start = node
                            start.make_start()
                        elif not end and node != start:
                            end = node
                            end.make_end()
                        elif node != end and node != start:
                            node.make_obstacle()
                # tasto destro: resetta cella
                elif event.button == 3:
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_position(pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        node = grid[row][col]
                        node.reset()
                        if node == start:
                            start = None
                        if node == end:
                            end = None

            if event.type == pygame.KEYDOWN:
                # SPACE: avvia solo se start e end sono presenti
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                # C: reset griglia manuale
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

                # L: carica mappa + scenario (MAP_PATH, SCEN_PATH) e avvia primo scenario
                if event.key == pygame.K_l:
                    # controlla che i file esistano
                    if not os.path.exists(MAP_PATH):
                        print("MAP non trovato:", MAP_PATH)
                        continue
                    # carica la mappa e aggiorna grid/ROWS
                    try:
                        grid, ROWS = load_map_file(MAP_PATH, width)
                    except Exception as e:
                        print("Errore caricamento map:", e)
                        continue

                    # prova a caricare lo scenario
                    start = None
                    end = None
                    if os.path.exists(SCEN_PATH):
                        scenarios = load_scen_file(SCEN_PATH)
                        if len(scenarios) > 0:
                            (sx, sy), (gx, gy) = scenarios[0]  # prendi il primo scenario
                            # attenzione: sx,sy sono (x,y) => (colonna,riga)
                            # mappa: node = grid[row][col] => row = y, col = x
                            if 0 <= sy < ROWS and 0 <= sx < len(grid[0]) and 0 <= gy < ROWS and 0 <= gx < len(grid[0]):
                                start = grid[sy][sx]
                                end = grid[gy][gx]
                                start.make_start()
                                end.make_end()
                            else:
                                print("Coordinate start/goal fuori mappa:", (sx,sy), (gx,gy))
                        else:
                            print("Nessuno scenario trovato in:", SCEN_PATH)
                    else:
                        print("Nessun file .scen trovato, userà click per definire start/end")

                    # aggiorna vicini e avvia l'algoritmo se start/end validi
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    if start and end:
                        algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

        if not run:
            break

        # disegna solo se la finestra è aperta
        draw(win, grid, ROWS, width)

    pygame.quit()

listener(WIN,WIDTH)