import pygame
import math
from queue import PriorityQueue

from pygame.constants import MOUSEBUTTONDOWN, QUIT

# Colours (in RGB format)
BLANKCOLOUR   = (255,255,255) # Colour of a blank node
PATHCOLOUR    = (255,000,000) # Colour of the path
CLOSEDCOLOUR  = (100,100,100) # Colour of a closed node
OPENCOLOUR    = (215,215,215) # Colour of an open node
WALLCOLOUR    = (000,000,000) # Colour of the walls
STARTCOLOUR   = (000,255,000) # Colour of the start node
ENDCOLOUR     = (000,000,255) # Colour of the end node
DIVIDERCOLOUR = (000,000,000) # Colour of the divider between nodes

# Sets up the Pygame display
WIDTH  = 800 # Width and height will be the same to make the gui square.
WINDOW   = pygame.display.set_mode((WIDTH,WIDTH)) # Set's GUI size
pygame.display.set_caption("A* Visualiser")    # Set's GUI name


class Point:
    def __init__(self, row, column, width, total_rows):
        self.row        = row
        self.column     = column
        self.width      = width
        self.total_rows = total_rows
        self.x          = row * width
        self.y          = column * width
        self.colour     = BLANKCOLOUR
        
    def get_position(self):
        return self.row, self.column
    
    def is_path(self):
        return self.colour == PATHCOLOUR
    
    def make_path(self):
        self.colour = PATHCOLOUR
    
    def is_closed(self):
        return self.colour == CLOSEDCOLOUR
    
    def make_closed(self):
        self.colour = CLOSEDCOLOUR
    
    def is_open(self):
        return self.colour == OPENCOLOUR
    
    def make_open(self):
        self.colour = OPENCOLOUR
    
    def is_barrier(self):
        return self.colour == WALLCOLOUR
    
    def make_barrier(self):
        self.colour = WALLCOLOUR
    
    def is_start(self):
        return self.colour == STARTCOLOUR
    
    def make_start(self):
        self.colour = STARTCOLOUR
    
    def is_end(self):
        return self.colour == ENDCOLOUR
    
    def make_end(self):
        self.colour = ENDCOLOUR
    
    def reset(self):
        self.colour = BLANKCOLOUR
    
    def draw(self,WINDOW):
        pygame.draw.rect(WINDOW, self.colour, (self.x, self.y, self.width, self.width))
        
    def update_neighbours(self, grid):
        self.neighbours = []
        
        # Checks if node below is a barrier or not
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.column].is_barrier():
            self.neighbours.append(grid[self.row +1][self.column])
            
        # Checks if node above is a barrier or not
        if self.row > 0 and not grid[self.row - 1][self.column].is_barrier():
            self.neighbours.append(grid[self.row - 1][self.column])
            
        # Checks if node to the right is a barrier or not
        if self.column < self.total_rows - 1 and not grid[self.row][self.column + 1].is_barrier():
            self.neighbours.append(grid[self.row][self.column + 1])
            
        # Checks if node to the left is a barrier or not
        if self.column > 0 and not grid[self.row][self.column - 1].is_barrier():
            self.neighbours.append(grid[self.row][self.column - 1])
    
    def __lt__(self, other):
        return False

def heuristic(pointOne, pointTwo):
    # Uses L distance from point one to point two
    
    x1, y1 = pointOne
    x2, y2 = pointTwo
    returnval = math.sqrt(((x1-x2)**2)+(y1-y2)**2)
    return returnval

def construct_grid(rows,width):
    grid = []            # Creates an empty grid
    gap  = width // rows # Defines the width of the blank node
    
    # Creates a 2D array and populates each point with a blank node
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            point = Point(i , j, gap, rows)
            grid[i].append(point)
            
    return grid

def draw_grid(WINDOW,rows,width):
    gap = width // rows
    for i in range (rows):
        pygame.draw.line(WINDOW, DIVIDERCOLOUR, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(WINDOW, DIVIDERCOLOUR, (j * gap, 0), (j * gap, width))

def draw(WINDOW, grid, rows, width):
    WINDOW.fill(BLANKCOLOUR)
    
    for row in grid:
        for point in row:
            point.draw(WINDOW)
            
    draw_grid(WINDOW, rows, width)
    pygame.display.update()
    
def get_selected_position(position, rows, width):
    gap    = width // rows
    y, x   = position
    row    = y // gap
    column = x // gap
    
    return row, column

def showPath(previous_node, current, draw):
    while current in previous_node:
        current = previous_node[current]
        current.make_path()
        draw()

def shortestPath(draw, grid, startPosition, endPosition):
    counter    = 0 # Used to break ties in the queue
    open_set = PriorityQueue()
    open_set.put((0, counter, startPosition)) # Puts the start node and it's F value into the open set
    previous_node = {}
    
    g_value = {point: float("inf") for row in grid for point in row}
    g_value[startPosition] = 0
    
    f_value = {point: float("inf") for row in grid for point in row}
    f_value[startPosition] = heuristic(startPosition.get_position(), endPosition.get_position())
    
    open_set_hash = {startPosition} # Tracks all the items in or outside of the PriorityQueue
    
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                
        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == endPosition:
            showPath(previous_node, endPosition, draw)
            endPosition.make_end()
            startPosition.make_start()
            return True
        
        for neighbour in current.neighbours:
            temporary_g_value = g_value[current] + 1
            
            if temporary_g_value < g_value[neighbour]:
                previous_node[neighbour] = current
                g_value[neighbour] = temporary_g_value
                f_value[neighbour] = temporary_g_value + heuristic(startPosition.get_position(), endPosition.get_position())
                if neighbour not in open_set_hash:
                    counter += 1
                    open_set.put((f_value[neighbour], counter, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()
        draw()
    
        if current != startPosition:
            current.make_closed()
        
                


def main(WINDOW, width):
    ROWS = 25
    grid = construct_grid(ROWS,width)
    
    startPosition = None
    endPosition   = None
    
    runProgram = True
    
    while runProgram:
        draw(WINDOW, grid, ROWS, width)
        # Check every event that has occured
        for event in pygame.event.get():
            if event.type == QUIT:
                runProgram = False # Exits the loop
            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    # print("LEFT MOUSE")
                    position    = pygame.mouse.get_pos()
                    row, column = get_selected_position(position, ROWS, width)
                    point       = grid[row][column]
                    if not startPosition and point != endPosition:
                        startPosition= point
                        startPosition.make_start()
                        
                    elif not endPosition and point != startPosition:
                        endPosition = point
                        endPosition.make_end()
                    
                    elif point != startPosition and point != endPosition:
                        point.make_barrier()
                
                elif event.button == 3: # Right mouse button
                    # print("RIGHT MOUSE")
                    position = pygame.mouse.get_pos()
                    row, column = get_selected_position(position, ROWS, width)
                    point = grid[row][column]
                    point.reset()
                    if point == startPosition:
                        startPosition = None
                    elif point == endPosition:
                        endPosition = None
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and startPosition and endPosition:
                    # print("RUN!")
                    for row in grid:
                        for point in row:
                            point.update_neighbours(grid)
                    shortestPath(lambda: draw(WINDOW, grid, ROWS, width), grid, startPosition, endPosition)
                    
                if event.key == pygame.K_BACKSPACE:
                    startPosition = None
                    endPosition   = None
                    grid = construct_grid(ROWS,width)
                
                
    pygame.quit() # Closes the pygame window
                
main(WINDOW, WIDTH)
