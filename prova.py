import pygame
import math # mi serve per abs da usare nella euristica
import heapq   #frontiera
import os    # serve per il file

MAP = "mappe/arena2.map"

WIDTH =800 #larghzza finestra
WIN = pygame.display.set_mode((WIDTH,WIDTH))  #funzione che mi permette di creare la finestra princiaple di tipo surface con cui posso interagire
pygame.display.set_caption("A* Algotithm")  #imposto titolo della finestra

#definzione dei colori usati per l'interfaccia (colori in RGB)

EXPLORED = (236,204,124)
FRONTIER =(213,124,49) 
BACKGROUND = (255,255,255)
OBSTACLE =(0,0,0) 
PATH =(255,175,44)
START = (222,152,78) 
GREY = (128,128,128)
END = (217,101,39)

class Node:
    def __init__(self,row,col,width,tot_rows):  #costruttore della classe nodo
        self.row=row   #riga in cui si trova il nodo 
        self.col=col   # colonna in cui si trova il nodo    -> entrambi servono per la logica dell'algoritmo
        self.tot_rows=tot_rows   # num tot di righe e colonne della griglia
        self.width=width  #larghezza in pixel di ogni nodo
        self.x= row*width   #riga che indica la posizione grafica(in pixel) che serve a pygame 
        self.y=col*width    # colonna //
        self.color=BACKGROUND    
        self.neighbors = []
        
    def get_pos(self):  #ritorna la posizione del nodo
        return self.row, self.col

    def is_explored(self):
        return self.color == EXPLORED  # se il coloro è rosso singifica che è gia stato esplorato

    def is_in_frontier(self):
        return self.color == FRONTIER

    def is_obstacle(self):
        return self.color == OBSTACLE
    
    def is_start(self):
        return self.color == START
    
    def is_end(self):
        return self.color == END
    
    def reset(self):
        self.color =  BACKGROUND

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
# manhattan distance 
def h(p1,p2):   # punto 1 e punto 2  manathan distance
    x1,y1 = p1 # estrae i valori da p1 in nelle variabili
    x2,y2 = p2
    return abs(x1-x2) + abs(y1-y2)
'''
distanza euclidea 
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)
'''


def draw_path(parent,node,draw):
    while node in parent:
        node = parent[node]
        node.make_path()
        draw()

def algorithm(draw,grid,start,end):
    count = 0 # serve per i tie breaker
    frontier = []
    heapq.heappush(frontier,((0,count,start)))  # sto mettendo f(n) , count e start
    parent = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start]=0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start]=h(start.get_pos(), end.get_pos())

    frontier_track = {start}

    while frontier:
        for event in pygame.event.get():
            if event == pygame.QUIT:
                pygame.quit()

        node = heapq.heappop(frontier)[2]  
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
                    heapq.heappush(frontier,(f_score[neighbor],count,neighbor))
                    frontier_track.add(neighbor)
                    if neighbor != end:
                        neighbor.make_frontier()
        draw()

        if node != start:
            node.make_explored()
    return False   
        

def load_map(map_path,win_width):

    with open(map_path,"r", encoding = "utf-8") as f:
        lines = []
        for line in f:
            ln= line.strip() # pulisco la stringa all'inizio e alla fine da newline e carriage residuo
            if ln =="":
                continue
            lines.append(ln)
        map_idx = None # inizializzo a None nell'eventualità che ci sia un errore 
        for i,line in enumerate(lines):
            if line.strip().lower() == "map":
                map_idx=i+1  # i+1 perchè dalal riga dopo si comincia a definire la configurazione della mappa nel file map
                break
        if map_idx is None:
            print("Errore nel caricamento della mappa: manca la riga 'map")
            exit(1)

        map_lines = lines[map_idx:]
        rows = len(map_lines)
        col = len(map_lines[0])

        grid = make_grid(rows,win_width)

        for r, line in enumerate(map_lines):
            for c,ch in enumerate(line):
                node = grid[r][c]
                if ch != ".":
                    node.make_obstacle()
                    
    return grid, rows



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
    for i in range(rows+1):
        pygame.draw.line(win,GREY,(0,i*dim),(width,i*dim)) # disegna una linea orizzontale per ogni riga sulla superficie win di colore GREY dal punto iniziale (0,i*dim) al punto finale (width,i*dim)
    for j in range(rows+1):
        pygame.draw.line(win,GREY,(j*dim,0),(j*dim,width))

def draw (win,grid,rows,width): 
    win.fill(BACKGROUND)
    
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

def listener(win,width):
    ROWS = 50 #valore di default cambiabile
    grid= make_grid(ROWS,width) # creato la griglia come lista di liste

    start=None
    end=None
    run = True
    runnin_algorithm = False
    map_loaded = False
    while run:
        draw(win,grid,ROWS,width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if not runnin_algorithm:
                if pygame.mouse.get_pressed()[0]:     # get_pressed è una funzione che restituisce una tupla(True,false, true) o qualsiasi combainzione che ci dice che il puls. sinistro /centrale /destro sono stati cliccati  e mettendo [0] significa che mi sto interessando a quello sinistro
                    pos= pygame.mouse.get_pos()  
                    row,col = get_clicked_position(pos,ROWS,width) # chiamo funzione ausiliaria creata prima
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        node = grid[row][col]
                        if not start and node != end and not node.is_obstacle():
                            start = node
                            start.make_start()
                        elif not end and node != start and not node.is_obstacle():
                            end = node
                            end.make_end()
                        elif node!= end and node!=start and not map_loaded:
                            node.make_obstacle()
                elif pygame.mouse.get_pressed()[2]: # tasto destro cancella le cose
                    pos= pygame.mouse.get_pos()  
                    row,col = get_clicked_position(pos,ROWS,width) # chiamo funzione ausiliaria creata prima
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        node = grid[row][col]
                        if node == start:
                            start=None
                            node.reset()
                        elif node ==end:
                            end=None
                            node.reset()
                        elif not map_loaded and node.is_obstacle():
                            node.reset()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    runnin_algorithm=True
                    algorithm(lambda: draw(win,grid,ROWS,width), grid, start,end)                          
                if event.key == pygame.K_c:
                    start = None
                    end = None 
                    grid = make_grid(ROWS,width)
                    runnin_algorithm=False
                    map_loaded = False
                if event.key == pygame.K_m:
                    grid, ROWS = load_map(MAP,width)
                    start = None
                    end = None
                    map_loaded = True
                    
    pygame.quit()  #chiude la finestra una volta usciti dal while (solo quando run = false)

listener(WIN,WIDTH)