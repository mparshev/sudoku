import pygame
import random
import os
import sys
import threading
import time
import win32api

class Cell:

    def __init__(self, index):
        self.index = index
        self.value = '123456789'
        self.guess = False
        
    def __str__(self):
        if self.guess: return '['+self.value.center(7) + ']'
        return self.value.center(9)

    def text(self):
        if len(self.value)==0: return 'X'
        if len(self.value)>1: return '?'
        return self.value
    
    def color(self):
        if len(self.value)==0: return (255,0,0)
        if self.guess: return (0,0,0)
        return (128,255,128)
        
    def row(self):
        return self.index // 9
        
    def col(self):
        return self.index % 9
    
    def same_group(self, other):
        if self.index == other.index : return False
        if self.row() == other.row() : return True
        if self.col() == other.col() : return True
        if self.row() // 3 != other.row() // 3 : return False
        if self.col() // 3 != other.col() // 3 : return False
        return True
        
class Sudoku:

    def __init__(self):
        self.cells = [ Cell(i) for i in range(81) ]
        self.backups = []
        self.done = False
        random.seed()
        
    def pickup_cell(self):
        unsolved = [ c.index for c in self.cells if len(c.value)>1 ]
        if unsolved:
            return self.cells[random.choice(unsolved)]

    def backup(self):
        return [ (c.value, c.guess) for c in self.cells ]
        
    def restore(self, backup):
        for i in range(81):
            self.cells[i].value, self.cells[i].guess = backup[i]
        
    def solve(self, start_cell):
        #start_cell.guess = True
        clist = [ start_cell ]
        while clist:
            #self.draw()
            cell = clist.pop()
            for c in self.cells:
                if c.same_group(cell) and cell.value in c.value:
                    if c.value == cell.value: return False
                    c.value = c.value.replace(cell.value,'')
                    if len(c.value)==1: 
                        c.guess = False
                        clist.append(c)
        return True
   
    def play(self):
        while(True):
            #self.draw()
            cell = self.pickup_cell()
            if not cell: return self.validate()
            values = cell.value
            value = random.choice(values)
            self.backups.append([self.backup(), cell.index, value])
            cell.value = value 
            while self.backups:
                cell.guess = True
                if self.solve(cell): break
                # restore from backup
                backup, index, value = self.backups.pop()
                self.restore(backup)
                cell = self.cells[index]
                cell.value = cell.value.replace(value,'')
            time.sleep(0.01)
                
    def validate(self):
        for c1 in self.cells:
            if len(c1.value)!=1: return False
            for c2 in self.cells:
                if c1.same_group(c2):
                    if c1.value == c2.value: return False
        self.done = True
        return True

    def draw(self, screen, blind=False):
        font_big = pygame.font.SysFont('couriernew', 30)
        font_small = pygame.font.SysFont('couriernew', 8)
        screen.fill((255,255,255))
        for i in range(10):
            pygame.draw.line(screen,(25,25,25),(25,25+i*50),(475,25+i*50), width= 3 if i%3==0 else 1)
            pygame.draw.line(screen,(25,25,25),(25+i*50,25),(25+i*50,475), width= 3 if i%3==0 else 1)
        for i in range(9):
            for j in range(9):
                cell = self.cells[i*9+j]
                if cell.guess:
                    cell_color = (0,0,0)
                elif blind:
                    cell_color = (255,255,255)
                else:
                    cell_color = (128,255,128)
                text = font_big.render(cell.text(), True, cell_color)
                rect = text.get_rect()
                screen.blit(text, (25+50*i+25-rect.width/2, 25+50*j+25-rect.height/2))
                if len(cell.value)>1:
                    text = font_small.render(cell.value,True,(0,0,0))
                    rect = text.get_rect()
                    screen.blit(text, (25+50*i+25-rect.width/2, 25+50*j+50-rect.height))

    def print(self, screen):
        file_name = 'sudoku.jpg'
        self.draw(screen, blind=True) 
        pygame.image.save(screen, file_name)
        win32api.ShellExecute(0, 'print', file_name, None, '.', 0)

def play():
    s = Sudoku()
    t = threading.Thread(target=s.play)
    t.start()
    return s
    
pygame.init()
screen = pygame.display.set_mode((500,500))
pygame.display.set_caption('Sudoku')
s = play()
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            #print('key=', event.key)
            if event.key == 112:    # p
                s.print(screen)
            else:
                s = play()
        if event.type == pygame.QUIT:
            sys.exit()
    s.draw(screen)
    if s.done:
        font = pygame.font.SysFont('couriernew', 12)
        text = font.render('Game over. Press "p" to print or any key to play again.', True,(0,0,0))
        rect = text.get_rect()
        screen.blit(text, ((500 - rect.width)/2, 475 + (25 - rect.height)/2))
    pygame.display.update()
