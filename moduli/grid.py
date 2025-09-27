import heapq
import math
from node import Node




def make_grid(rows,cols,width):  # num righe e colonne totali e larghezza totale della finestra in pixel
    grid=[] # griglia sarà una lista di liste  dove ogni grid[i] è un riga della griglia e grid[i][j] è un nodo/cella
    #dim = width // max(rows,cols) # dimensione in pixel di ogni nodo in base al lato piu grande   es. se finestra di 400 px e rows=20 ogni cella sarà 400//20 = 20px
    node_width = width // cols
    node_heigth = width // rows
    for i in range(rows):  # fai i numeri da 0 a rows-1
        grid.append([])  # aggiungo per ogni riga i una lista vuota che conterrà i nodi di quella riga
        for j in range(cols): # per ogni colonna j nella riga i 
            node=Node(i,j,node_width,node_heigth,rows,cols) # creo un nodo
            grid[i].append(node) # aggiungo il nodo alla riga i
    return grid,node_width,node_width

def draw_grid(win,rows,cols,node_width,node_height):  # finestra su cui disegnare, num righe e colonne totali, larghezza totale di win
    for i in range(rows+1):
        pygame.draw.line(win,GREY,(0,i*node_height),(cols * node_width,i*node_height)) # disegna una linea orizzontale per ogni riga sulla superficie win di colore GREY dal punto iniziale (0,i*dim) al punto finale (width,i*dim)
    for j in range(cols+1):
        pygame.draw.line(win,GREY,(j*node_width,0),(j*node_width,rows*node_height))

def draw (win,grid,rows,cols,node_width,node_heigth): 
    win.fill(BACKGROUND)
    
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win,rows,cols,node_width,node_heigth)
    pygame.display.update()      

def get_clicked_position(pos,rows,cols,node_width,node_heigth):  #pos è la posizione restituita da pygame in pixel 
    
    x,y = pos # pos sono coordinate in pixel dove x indica la colonna (le ascisse) y la riga (le ordinate)-> pygame restituisce (x,y) io li ho invertiti per convenzioni perche in (x,y) 
    row= y // node_heigth
    col = x // node_width
    return  row,col