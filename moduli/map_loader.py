from grid import make_grid
from node import Node


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
        cols = len(map_lines[0])
        grid, node_width, node_heigth = make_grid(rows,cols,win_width)

        for r, line in enumerate(map_lines):
            for c,ch in enumerate(line):
                node = grid[r][c]
                if ch != ".":
                    node.make_obstacle()
                    
    return grid, rows, cols, node_width,node_heigth