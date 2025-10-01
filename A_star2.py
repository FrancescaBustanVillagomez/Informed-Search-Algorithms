import pygame
import math 
import heapq
import os
import threading
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # cartella in cui si trova questo file py
MAP = os.path.join(BASE_DIR, "mappe", "lgt101d.map")  # percorso completo per trovare la mappa
#MAP = "mappe/brc997d.map"
#MAP = "mappe/orz302d.map"
# Mappe piccole
#MAP = "den009d.map" 34*50
#MAP = "den201d.map " 37*37
#MAP = "den404d.map" 34*28
#MAP = "hrt002d.map" 50*49
#MAP = "isound1.map" 50*49
#MAP = "lak101d.map" 31*30 dalla 101 alla 105 poi 107-110
#MAP = "lgt101d.map" 28*44 da 101 a 105 e da 107 a 110

#mappe grandi
#MAP = "mappe2/lt_foundry_n.map" 92*109
#MAP = "lgt101d.map" 28*44
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Algorithm")

# Parametri viewport fissi
VIEWPORT_WIDTH = WIDTH    # dim della finestra visibile
VIEWPORT_HEIGHT  = WIDTH    # finestra sarà quadrata alla fine
SCROLL_SPEED = 20  # num di pixel spostati con le frecce
MIN_NODE_SIZE = 5  #dim minima dei nodi in pixel


# Variabili globali
stop_requested = False   # serve al thread 
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
    def __init__(self,row,col,width,height,tot_rows,tot_cols):  #costruttore della classe nodo
        self.row=row   #riga in cui si trova il nodo 
        self.col=col   # colonna in cui si trova il nodo    -> entrambi servono per la logica dell'algoritmo
        self.tot_rows=tot_rows   # num tot di righe e colonne della griglia
        self.tot_cols= tot_cols
        self.width=width  #larghezza in pixel di ogni nodo
        self.heigth = height
        self.x = col * width    
        self.y = row * height
        self.color=BACKGROUND    
        self.neighbors = []
        
    def get_pos(self):  #ritorna la posizione del nodo
        return self.row, self.col

    def is_explored(self):
        return self.color == EXPLORED  # se il colore è rosso singifica che è gia stato esplorato

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

    def draw(self, win, offset_x, offset_y):
        draw_x = self.x - offset_x
        draw_y = self.y - offset_y
        if(-self.width <= draw_x <= VIEWPORT_WIDTH and -self.y <= draw_y <= VIEWPORT_HEIGHT):
            pygame.draw.rect(win,self.color,(draw_x, draw_y,self.width,self.heigth))
        
        
    def update_neighbors(self,grid):
        self.neighbors=[]
        if self.row < self.tot_rows-1 and not grid[self.row+1][self.col].is_obstacle():  # sto controllando se non mi trovo all'ultima riga e se quindi il nodo sotto di me non sia un ostacolo per aggiungerlo
            self.neighbors.append(grid[self.row+1][self.col])

        if self.row>0 and not grid[self.row-1][self.col].is_obstacle():  
            self.neighbors.append(grid[self.row-1][self.col])

        if self.col<self.tot_cols-1 and not grid[self.row][self.col+1].is_obstacle():  
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
#ricostruisce e disegna il percorso trovato
def draw_path(parent,node,draw_func):
    while node in parent:
        node = parent[node]
        if not node.is_start() and not node.is_end():
            node.make_path()
        draw_func()

def algorithm(draw_func,grid,start,end):
    global stop_requested
    count = 0 # serve per i tie breaker
    frontier = []
    heapq.heappush(frontier,((0,count,start)))  # sto mettendo f(n) , count e start
    
    parent = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start]=0

    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start]=h(start.get_pos(), end.get_pos())

    frontier_track = {start}
    step_counter = 0 #disegna solo ogni 5 step

    while frontier and not stop_requested:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False   # algorithm non piu respondabile di chiusura di finestra 
        
        node = heapq.heappop(frontier)[2]  
        frontier_track.remove(node)

        if node == end:
            draw_path(parent,node,draw_func)
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
        draw_func()

        if node != start:
            node.make_explored()

        #diegno solo ogni N step per ridurre il flickering
        step_counter += 1
        if step_counter % 5 == 0:  # disegno ongi 5 step
            draw_func()
            pygame.time.delay(10)   #piccola pausa per vedere animazione

    return False   
        

def load_map(map_path):
    try:
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
                return None, 0, 0, 0, 0

            map_lines = lines[map_idx:]
            rows = len(map_lines)
            if map_lines:
                cols = len(map_lines[0])
            else:
                cols = 0

            if rows == 0 or cols == 0:
                print("Errore: mappa vuota")
                return None, 0, 0, 0, 0

            grid, node_width, node_height = make_grid(rows,cols)

            for r, line in enumerate(map_lines):
                for c,ch in enumerate(line):
                    if r < rows and c < cols:
                        node = grid[r][c]
                        if ch != ".":
                            node.make_obstacle()
                    
            return grid, rows, cols, node_width,node_height

    except FileNotFoundError:
        print(f"Errore: file {map_path} non trovato")
        return None, 0, 0, 0, 0
    except Exception as e:
        print(f"Errore nel caricamento della mappa: {e}")
        return None, 0, 0, 0, 0


def make_grid(rows, cols):
    """Crea una griglia di nodi QUADRATI ottimizzata per riempire lo schermo"""
    import math
    
    # Calcola quale dimensione sarebbe necessaria per riempire completamente ogni asse
    size_for_width = VIEWPORT_WIDTH / cols
    size_for_height = VIEWPORT_HEIGHT / rows
    
    # Usa la dimensione più piccola per mantenere i nodi quadrati
    exact_size = min(size_for_width, size_for_height)
    
    # Calcola quanto spazio verrebbe sprecato con la dimensione standard
    total_width_standard = cols * exact_size
    total_height_standard = rows * exact_size
    wasted_width = VIEWPORT_WIDTH - total_width_standard
    wasted_height = VIEWPORT_HEIGHT - total_height_standard
    wasted_percent_w = (wasted_width / VIEWPORT_WIDTH) * 100
    wasted_percent_h = (wasted_height / VIEWPORT_HEIGHT) * 100
    
    # Applica ottimizzazione SOLO se c'è uno squilibrio significativo
    # (una dimensione spreca molto più dell'altra)
    max_wasted = max(wasted_percent_w, wasted_percent_h)
    min_wasted = min(wasted_percent_w, wasted_percent_h)
    
    # Se la differenza di spreco è > 10% E lo spreco massimo è > 10%, ottimizza
    if (max_wasted - min_wasted) > 10 and max_wasted > 10:
        if wasted_height > wasted_width:
            # La larghezza è il limite (mappa alta e stretta)
            # Aumenta la dimensione per riempire il 95% dell'altezza
            target_size = (VIEWPORT_HEIGHT * 0.95) / rows
            # Ma non superare troppo la larghezza disponibile (max 130%)
            if (cols * target_size) <= VIEWPORT_WIDTH * 1.3:
                exact_size = target_size
                print(f"Debug: Mappa alta/stretta, spazio sprecato H={wasted_percent_h:.1f}% W={wasted_percent_w:.1f}%, aumento a {exact_size:.2f}px")
            else:
                print(f"Debug: Mappa alta/stretta, ma aumento creerebbe troppo overflow in larghezza")
        else:
            # L'altezza è il limite (mappa larga e bassa)
            # Aumenta la dimensione per riempire il 95% della larghezza
            target_size = (VIEWPORT_WIDTH * 0.95) / cols
            # Ma non superare troppo l'altezza disponibile (max 130%)
            if (rows * target_size) <= VIEWPORT_HEIGHT * 1.3:
                exact_size = target_size
                print(f"Debug: Mappa larga/bassa, spazio sprecato W={wasted_percent_w:.1f}% H={wasted_percent_h:.1f}%, aumento a {exact_size:.2f}px")
            else:
                print(f"Debug: Mappa larga/bassa, ma aumento creerebbe troppo overflow in altezza")
    else:
        print(f"Debug: Mappa bilanciata (spreco W={wasted_percent_w:.1f}% H={wasted_percent_h:.1f}%), uso dimensione standard")
    
    # Verifica dimensione minima
    if exact_size >= MIN_NODE_SIZE:
        # Arrotondamento intelligente
        # Per mappe bilanciate, arrotonda normalmente
        # Per mappe ottimizzate, arrotonda per eccesso
        if max_wasted > min_wasted + 10:
            node_size = math.ceil(exact_size)  # Arrotonda per eccesso
        else:
            node_size = round(exact_size)  # Arrotonda normale
        
        total_width = cols * node_size
        total_height = rows * node_size
        
        # Se supera del 20%, riduci di 1 (per mappe bilanciate vogliamo stare dentro)
        max_overflow = 1.2 if max_wasted <= min_wasted + 10 else 1.3
        if total_width > VIEWPORT_WIDTH * max_overflow or total_height > VIEWPORT_HEIGHT * max_overflow:
            node_size -= 1
            total_width = cols * node_size
            total_height = rows * node_size
        
        node_width = node_height = node_size
        
        aspect_ratio = max(cols/rows, rows/cols)
        print(f"Debug: Griglia {rows}x{cols} (aspect ratio: {aspect_ratio:.2f})")
        print(f"Debug: Dimensione calcolata: {exact_size:.2f}px")
        print(f"Debug: Dimensione finale (quadrata): {node_size}x{node_size}")
        print(f"Debug: Totale griglia: {total_width}x{total_height}")
        print(f"Debug: Viewport: {VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
        print(f"Debug: Utilizzo: {(total_width/VIEWPORT_WIDTH)*100:.1f}% width, {(total_height/VIEWPORT_HEIGHT)*100:.1f}% height")
    else:
        # Per mappe molto grandi, usa dimensione minima
        node_width = node_height = MIN_NODE_SIZE
        print(f"Debug: Griglia molto grande {rows}x{cols}, usando dimensione minima {MIN_NODE_SIZE}")
    
    grid = []
    for i in range(rows):  # fai i numeri da 0 a rows-1
        grid.append([])  # aggiungo per ogni riga i una lista vuota che conterrà i nodi di quella riga
        for j in range(cols): # per ogni colonna j nella riga i 
            node=Node(i,j,node_width,node_height,rows,cols) # creo un nodo
            grid[i].append(node) # aggiungo il nodo alla riga i
    return grid,node_width,node_height


def draw_grid(win,rows,cols,node_width,node_height,offset_x, offset_y):  # finestra su cui disegnare, num righe e colonne totali, larghezza totale di win
    for i in range(rows+1):
        y =  i * node_height - offset_y
        if -1 <= y <= VIEWPORT_HEIGHT + 1:
             pygame.draw.line(win, GREY,(0,y),(VIEWPORT_WIDTH,y))
    for j in range(cols+1):
        x = j* node_width - offset_x
        if -1 <= x <= VIEWPORT_WIDTH + 1:
            pygame.draw.line(win, GREY, (x,0),(x,VIEWPORT_HEIGHT))
       

def draw (win,grid,rows,cols,node_width,node_height,offset_x,offset_y):
    win.fill(BACKGROUND)

    #disegno solo nodi visibili
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




def get_clicked_position(pos,rows,cols,node_width,node_height,offset_x,offset_y):  #pos è la posizione restituita da pygame in pixel 
    
    x,y = pos # pos sono coordinate in pixel dove x indica la colonna (le ascisse) y la riga (le ordinate)-> pygame restituisce (x,y) io li ho invertiti per convenzioni perche in (x,y) 
    
    real_x = x + offset_x
    real_y = y + offset_y

    row= real_y // node_height
    col = real_x // node_width
    return  row,col

def run_algorithm_thread(draw_func,grid,start,end):
    global algorithm_running
    try:
        algorithm(draw_func,grid,start,end)
    finally:
        algorithm_running = False


def main():
    pygame.init()
    ROWS = 50 #valore di default cambiabile
    COLS = 50
    grid, node_width, node_height = make_grid(ROWS,COLS) # crea la griglia come lista di liste
    
    # Offset iniziali 
    total_width = COLS * node_width
    total_height = ROWS * node_height
    
    # Calcolo offset per centratura
    if total_width < VIEWPORT_WIDTH:
        offset_x = -(VIEWPORT_WIDTH - total_width) // 2
    else:
        offset_x = 0
        
    if total_height < VIEWPORT_HEIGHT:
        offset_y = -(VIEWPORT_HEIGHT - total_height) // 2
    else:
        offset_y = 0
    

    global stop_requested, algorithm_running
    algorithm_running = False
    start=None
    end=None
    run = True 
    map_loaded = False
    draw(WIN,grid,ROWS,COLS,node_width,node_height, offset_x, offset_y)
    
    clock = pygame.time.Clock()
    needs_redraw = False  # Flag per gestire il ridisegno
    
    while run:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_requested = True
                run = False
                break

            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and start and end and not algorithm_running:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        algorithm_running=True
                        stop_requested = False
                        draw_func = lambda: draw(WIN, grid, ROWS, COLS, node_width, node_height, offset_x, offset_y)
                        thread = threading.Thread(target = run_algorithm_thread, args =(draw_func,grid, start, end))
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
                        start = None
                        end = None 
                        grid, node_width, node_height = make_grid(ROWS,COLS)
                        map_loaded = False
                        
                        total_width = COLS * node_width
                        total_height = ROWS * node_height

                        if total_width < VIEWPORT_WIDTH:
                                offset_x = ((VIEWPORT_WIDTH - total_width) // 2) // node_width * node_width
                        else:
                            offset_x = 0

                        if total_height < VIEWPORT_HEIGHT:
                            offset_y = ((VIEWPORT_HEIGHT - total_height) // 2) // node_height * node_height
                        else:
                            offset_y = 0

                        
                        needs_redraw = True

        if not algorithm_running:
            if pygame.mouse.get_pressed()[0]:     # get_pressed è una funzione che restituisce una tupla(True,false, true) o qualsiasi combainzione che ci dice che il puls. sinistro /centrale /destro sono stati cliccati  e mettendo [0] significa che mi sto interessando a quello sinistro
                pos= pygame.mouse.get_pos()  
                row,col = get_clicked_position(pos,ROWS,COLS,node_width,node_height,offset_x, offset_y) # chiamo funzione ausiliaria creata prima
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
                        elif node!= end and node!=start and not map_loaded and not node.is_obstacle():
                            node.make_obstacle()
                            needs_redraw = True
                        
            elif pygame.mouse.get_pressed()[2]: # tasto destro cancella le cose
                pos= pygame.mouse.get_pos()  
                row,col = get_clicked_position(pos,ROWS,COLS,node_width, node_height, offset_x,offset_y) # chiamo funzione ausiliaria creata prima
                if 0 <= row < ROWS and 0 <= col < COLS:
                        node = grid[row][col]
                        changed = False

                        if node == start:
                            start=None
                            node.reset()
                            changed = True
                        elif node ==end:
                            end=None
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
    
