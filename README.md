# Advanced Informed Search Algorithms: Analysis & Implementation

This repository contains the source code and experimental framework developed for my Bachelor's Thesis in Computer Science at Sapienza Università di Roma.

The project focuses on the comparative analysis and implementation of advanced informed search algorithms for pathfinding problems. It includes a graphical visualization tool built with Pygame and a benchmarking suite to evaluate the algorithms across different domains (Empty, Maze, and Game maps from the Moving AI Lab).

## Thesis Objectives

The primary goals of this project were to:

* Compare optimal informed search algorithms against sub-optimal/anytime variants.
* Analyze fundamental algorithmic trade-offs (Solution Optimality, Execution Time, Peak Memory Consumption, and Number of Nodes Expanded/Generated).

##Implemented Algorithms

The project features four distinct search algorithms to highlight different approaches to the pathfinding problem:

* **A\* (A-Star)**: The standard optimal and complete algorithm. It uses the evaluation function $f(n)=g(n)+h(n)$ to find the shortest path, heavily relying on memory to store the frontier and explored nodes.
* **IDA\* (Iterative Deepening A\*)**: An optimal algorithm designed to drastically reduce memory usage. It combines Depth-First Search with A*'s heuristic, running iterations constrained by an increasing threshold. It trades time for space, maintaining an $O(d)$ memory complexity.
* **WA\* (Weighted A\*)**: A Bounded Sub-optimal Search. By multiplying the heuristic by a weight $W>1$ ($f(n)=g(n)+W \cdot h(n)$), it becomes greedier, finding solutions much faster at the cost of strict optimality. The solution is guaranteed to be $\epsilon$-admissible.
* **ARA\* (Anytime Repairing A\*)**: An Anytime Search algorithm. It quickly finds an initial sub-optimal path using a high weight, and continuously improves it as long as time permits by decreasing the weight towards 1.0. It efficiently reuses previous search trees (Repairing) using an INCONS list to avoid redundant work.

## Installation & Setup

Clone the repository:

```bash
git clone [https://github.com/FrancescaBustanVillagomez/progetto.git](https://github.com/FrancescaBustanVillagomez/progetto.git)
cd progetto
cd progetto


Install the required dependencies:
Ensure you have Python installed, then install pygame:

pip install pygame


Run the visualizer:

python pathfinding.py

```
## Choosing the Algorithm
To select which algorithm to run and visualize, you need to manually edit a single line in the pathfinding.py file.
Locate the run_algorithm_thread function and uncomment the line corresponding to the algorithm you want to test, while commenting out the others.

```bash
# Example: Running A*
risultato = a_star(draw_func, grid, start, end, benchmark)
# risultato = wighted_a_star(draw_func, grid, start, end, benchmark, 1.5)
# risultato = ida_star(start, end, draw_func, grid, benchmark)
# risultato = ara_star(draw_func, grid, start, end, benchmark, 3.0, 0.5)
```


## Controls & Usage

The tool features an interactive GUI that allows you to draw custom obstacles or load pre-existing maps to test the algorithms visually or analytically.

Keyboard Controls:


SPACE : Start the Visualization Mode. Watch the algorithm explore the grid in real-time.

B : Start the Benchmark Mode. Disables GUI animations to run the algorithm at maximum speed and prints performance metrics (Time, Nodes, Cost, Memory) directly to the terminal.

M : Cycle through loaded maps (Small, Medium, Large domains).

C : Clear the grid and reset the environment.

Mouse Controls:

Left Click :

1st click: Place the Start node (Orange).

2nd click: Place the End/Target node (Red).

Subsequent clicks/drag: Draw Obstacles (Black).

Right Click : Erase nodes/obstacles.

## Experimental Setup & Domains

The algorithms were rigorously tested using standardized benchmarks from the Moving AI Lab.
Three distinct map typologies were used to stress-test the algorithms under different geometric constraints:

Empty Maps (Baseline testing)

Maze Maps (Stress test for local minima and memory bounds)

Game Maps (Real-world scenarios, e.g., Dragon Age: Origins)

## Customizing the Maps

By default, the `MAPS` list in the code includes pre-configured **small, medium, and large** maps. However, the system is fully customizable: you can easily modify this list inside `pathfinding.py` to add and test any map you prefer.

## Author

Francesca Bustan Villagomez
Bachelor's Degree in Computer Science
Sapienza Università di Roma
