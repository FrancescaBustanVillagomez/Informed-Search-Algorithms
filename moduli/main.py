import pygame
import math # mi serve per abs da usare nella euristica
import heapq   #frontiera
import os    # serve per il file
import threading   # per separere l'esecuzione e la gestione della pagina
import sys #serve per interrompere il programma
from grid import make_grid,draw,get_clicked_position
from algorithm import algorithm,run_algorithm_thread
from map_loader import load_map
from node import Node,GREY,BACKGROUND
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP = os.path.join(BASE_DIR, "mappe", "ost004d.map")
#MAP = "mappe/brc997d.map"
#MAP = "mappe/orz302d.map"

WIDTH =800 #larghzza finestra
WIN = pygame.display.set_mode((WIDTH,WIDTH))  #funzione che mi permette di creare la finestra princiaple di tipo surface con cui posso interagire
pygame.display.set_caption("A* Algotithm")  #imposto titolo della finestra

stop_requested = False   # variabile che controlla seè stata inviata la richiesta di chiusura

#definzione dei colori usati per l'interfaccia (colori in RGB)



def listener(win,width):
    ROWS = 50 #valore di default cambiabile
    COLS = 50
    grid, node_width, node_heigth = make_grid(ROWS,COLS,width) # creato la griglia come lista di liste
    global stop_requested
    start=None
    end=None
    run = True
    global runnin_algorithm
    runnin_algorithm = False
    map_loaded = False
    draw(win,grid,ROWS,COLS,node_width,node_heigth)
    while run:
        #draw(win,grid,ROWS,COLS,node_width,node_heigth)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_requested = True
                run = False
                pygame.quit()
                sys.exit()

                break
            if not runnin_algorithm:
                if pygame.mouse.get_pressed()[0]:     # get_pressed è una funzione che restituisce una tupla(True,false, true) o qualsiasi combainzione che ci dice che il puls. sinistro /centrale /destro sono stati cliccati  e mettendo [0] significa che mi sto interessando a quello sinistro
                    pos= pygame.mouse.get_pos()  
                    row,col = get_clicked_position(pos,ROWS,COLS,node_width,node_heigth) # chiamo funzione ausiliaria creata prima
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        node = grid[row][col]
                        if not start and node != end and not node.is_obstacle():
                            start = node
                            start.make_start()
                        elif not end and node != start and not node.is_obstacle():
                            end = node
                            end.make_end()
                        elif node!= end and node!=start and not map_loaded:
                            node.make_obstacle()
                        draw(win, grid, ROWS, COLS, node_width, node_heigth)
                elif pygame.mouse.get_pressed()[2]: # tasto destro cancella le cose
                    pos= pygame.mouse.get_pos()  
                    row,col = get_clicked_position(pos,ROWS,COLS,node_width, node_heigth) # chiamo funzione ausiliaria creata prima
                    if 0 <= row < ROWS and 0 <= col < COLS:
                        node = grid[row][col]
                        if node == start:
                            start=None
                            node.reset()
                        elif node ==end:
                            end=None
                            node.reset()
                        elif not map_loaded and node.is_obstacle():
                            node.reset()
                        draw(win, grid, ROWS, COLS, node_width, node_heigth)    
            if event.type == pygame.KEYDOWN:
                if not runnin_algorithm:
                    if event.key == pygame.K_SPACE and start and end and not runnin_algorithm:
                        for row in grid:
                            for node in row:
                                node.update_neighbors(grid)
                        runnin_algorithm=True
                        thread = threading.Thread(target = run_algorithm_thread, args =(lambda: draw(win, grid, ROWS, COLS, node_width, node_heigth),grid, start, end))
                        thread.start()                        
                    elif event.key == pygame.K_m:
                        grid, ROWS,COLS, node_width, node_heigth = load_map(MAP,width)
                        WIDTH = node_width * COLS
                        WIN = pygame.display.set_mode((WIDTH,WIDTH))
                        start = None
                        end = None
                        map_loaded = True
                        draw(win, grid, ROWS, COLS, node_width, node_heigth)
                    
                if event.key == pygame.K_c:
                    start = None
                    end = None 
                    grid, node_width, node_heigth = make_grid(ROWS,COLS,width)
                    runnin_algorithm=False
                    map_loaded = False
                    draw(win, grid, ROWS, COLS, node_width, node_heigth)
                
                    
    pygame.quit()  #chiude la finestra una volta usciti dal while (solo quando run = false)

listener(WIN,WIDTH)