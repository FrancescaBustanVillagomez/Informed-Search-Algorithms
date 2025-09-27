


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
        if not node.is_start() and not node.is_end():
            node.make_path()
        draw()

def algorithm(draw,grid,start,end):
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

    while frontier:
        if stop_requested:
            return
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
        
def run_algorithm_thread(draw,grid,start,end):
    #global runnin_algorithm
    algorithm(draw,grid,start,end)
    #runnin_algorithm = False