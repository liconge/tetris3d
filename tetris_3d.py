import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import numpy as np

# Game constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_DEPTH = 10
BLOCK_SIZE = 1

# Colors for different pieces
COLORS = [
    (1, 0, 0),      # Red
    (0, 1, 0),      # Green
    (0, 0, 1),      # Blue
    (1, 1, 0),      # Yellow
    (1, 0, 1),      # Magenta
    (0, 1, 1),      # Cyan
    (1, 0.5, 0),    # Orange
]

# 3D Tetromino shapes (relative coordinates)
SHAPES = [
    # I piece (straight line)
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)],
    # O piece (cube)
    [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)],
    # T piece
    [(0, 0, 0), (1, 0, 0), (2, 0, 0), (1, 1, 0)],
    # L piece
    [(0, 0, 0), (0, 1, 0), (0, 2, 0), (1, 0, 0)],
    # J piece
    [(1, 0, 0), (1, 1, 0), (1, 2, 0), (0, 0, 0)],
    # S piece
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (2, 1, 0)],
    # Z piece
    [(1, 0, 0), (2, 0, 0), (0, 1, 0), (1, 1, 0)],
]

class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = GRID_WIDTH // 2
        self.y = GRID_HEIGHT - 2
        self.z = GRID_DEPTH // 2
        
    def get_blocks(self):
        """Get absolute positions of all blocks in the piece"""
        return [(self.x + dx, self.y + dy, self.z + dz) for dx, dy, dz in self.shape]
    
    def rotate_x(self):
        """Rotate around X axis"""
        self.shape = [(x, -z, y) for x, y, z in self.shape]
    
    def rotate_y(self):
        """Rotate around Y axis"""
        self.shape = [(z, y, -x) for x, y, z in self.shape]
    
    def rotate_z(self):
        """Rotate around Z axis"""
        self.shape = [(-y, x, z) for x, y, z in self.shape]

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.display = (800, 600)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Tetris")
        
        # Set up OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        glLight(GL_LIGHT0, GL_POSITION, (5, 5, 5, 1))
        glLight(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1))
        glLight(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
        
        # Set up perspective
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glTranslatef(-GRID_WIDTH/2, -GRID_HEIGHT/2, -40)
        
        # Game state
        self.grid = [[[None for _ in range(GRID_DEPTH)] 
                      for _ in range(GRID_HEIGHT)] 
                     for _ in range(GRID_WIDTH)]
        self.current_piece = Piece()
        self.score = 0
        self.game_over = False
        self.fall_speed = 500  # milliseconds
        self.last_fall = pygame.time.get_ticks()
        
        # Camera rotation
        self.rotation_x = 30
        self.rotation_y = 45
        
    def draw_cube(self, x, y, z, color):
        """Draw a single cube at the given position"""
        glPushMatrix()
        glTranslatef(x * BLOCK_SIZE, y * BLOCK_SIZE, z * BLOCK_SIZE)
        glColor3f(*color)
        
        # Draw cube faces
        vertices = [
            [0, 0, 0], [BLOCK_SIZE, 0, 0], [BLOCK_SIZE, BLOCK_SIZE, 0], [0, BLOCK_SIZE, 0],  # Front
            [0, 0, BLOCK_SIZE], [BLOCK_SIZE, 0, BLOCK_SIZE], [BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], [0, BLOCK_SIZE, BLOCK_SIZE]  # Back
        ]
        
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),  # Front, Back
            (0, 1, 5, 4), (2, 3, 7, 6),  # Bottom, Top
            (0, 3, 7, 4), (1, 2, 6, 5)   # Left, Right
        ]
        
        # Draw faces
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
        
        # Draw edges in black
        glDisable(GL_LIGHTING)
        glColor3f(0, 0, 0)
        glLineWidth(2)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()
        glLineWidth(1)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
    
    def draw_grid_outline(self):
        """Draw the game board outline"""
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glLineWidth(1)
        glBegin(GL_LINES)
        
        # Draw grid edges
        corners = [
            (0, 0, 0), (GRID_WIDTH, 0, 0), (GRID_WIDTH, GRID_HEIGHT, 0), (0, GRID_HEIGHT, 0),
            (0, 0, GRID_DEPTH), (GRID_WIDTH, 0, GRID_DEPTH), (GRID_WIDTH, GRID_HEIGHT, GRID_DEPTH), (0, GRID_HEIGHT, GRID_DEPTH)
        ]
        
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        
        for edge in edges:
            glVertex3f(*corners[edge[0]])
            glVertex3f(*corners[edge[1]])
        
        glEnd()
        glEnable(GL_LIGHTING)
    
    def check_collision(self, blocks):
        """Check if any block collides with grid or boundaries"""
        for x, y, z in blocks:
            if x < 0 or x >= GRID_WIDTH or z < 0 or z >= GRID_DEPTH or y < 0:
                return True
            if y < GRID_HEIGHT and self.grid[x][y][z] is not None:
                return True
        return False
    
    def lock_piece(self):
        """Lock the current piece into the grid"""
        for x, y, z in self.current_piece.get_blocks():
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and 0 <= z < GRID_DEPTH:
                self.grid[x][y][z] = self.current_piece.color
        
        self.clear_layers()
        self.current_piece = Piece()
        
        # Check if new piece immediately collides (game over)
        if self.check_collision(self.current_piece.get_blocks()):
            self.game_over = True
    
    def clear_layers(self):
        """Clear completed horizontal layers"""
        layers_cleared = 0
        y = 0
        while y < GRID_HEIGHT:
            # Check if layer is full
            full = True
            for x in range(GRID_WIDTH):
                for z in range(GRID_DEPTH):
                    if self.grid[x][y][z] is None:
                        full = False
                        break
                if not full:
                    break
            
            if full:
                layers_cleared += 1
                # Remove this layer and shift everything down
                for y2 in range(y, GRID_HEIGHT - 1):
                    for x in range(GRID_WIDTH):
                        for z in range(GRID_DEPTH):
                            self.grid[x][y2][z] = self.grid[x][y2 + 1][z]
                
                # Clear top layer
                for x in range(GRID_WIDTH):
                    for z in range(GRID_DEPTH):
                        self.grid[x][GRID_HEIGHT - 1][z] = None
            else:
                y += 1
        
        if layers_cleared > 0:
            self.score += layers_cleared * 100
    
    def move_piece(self, dx, dy, dz):
        """Try to move the piece"""
        self.current_piece.x += dx
        self.current_piece.y += dy
        self.current_piece.z += dz
        
        if self.check_collision(self.current_piece.get_blocks()):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            self.current_piece.z -= dz
            return False
        return True
    
    def rotate_piece(self, axis):
        """Try to rotate the piece"""
        old_shape = self.current_piece.shape[:]
        
        if axis == 'x':
            self.current_piece.rotate_x()
        elif axis == 'y':
            self.current_piece.rotate_y()
        elif axis == 'z':
            self.current_piece.rotate_z()
        
        if self.check_collision(self.current_piece.get_blocks()):
            self.current_piece.shape = old_shape
            return False
        return True
    
    def drop_piece(self):
        """Drop piece to the bottom"""
        while self.move_piece(0, -1, 0):
            pass
        self.lock_piece()
    
    def render(self):
        """Render the game"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glPushMatrix()
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        
        # Draw grid outline
        self.draw_grid_outline()
        
        # Draw locked blocks
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                for z in range(GRID_DEPTH):
                    if self.grid[x][y][z] is not None:
                        self.draw_cube(x, y, z, self.grid[x][y][z])
        
        # Draw current piece
        for x, y, z in self.current_piece.get_blocks():
            if 0 <= y < GRID_HEIGHT:
                self.draw_cube(x, y, z, self.current_piece.color)
        
        glPopMatrix()
        
        # Draw score (2D overlay)
        self.draw_text(f"Score: {self.score}", 10, 10)
        if self.game_over:
            self.draw_text("GAME OVER - Press R to restart", 10, 40)
        
        pygame.display.flip()
    
    def draw_text(self, text, x, y):
        """Draw 2D text overlay"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glColor3f(1, 1, 1)
        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, (255, 255, 255))
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        glRasterPos2f(x, y)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def reset(self):
        """Reset the game"""
        self.grid = [[[None for _ in range(GRID_DEPTH)] 
                      for _ in range(GRID_HEIGHT)] 
                     for _ in range(GRID_WIDTH)]
        self.current_piece = Piece()
        self.score = 0
        self.game_over = False
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.reset()
                    else:
                        if event.key == pygame.K_LEFT:
                            self.move_piece(-1, 0, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_piece(1, 0, 0)
                        elif event.key == pygame.K_UP:
                            self.move_piece(0, 0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.move_piece(0, 0, 1)
                        elif event.key == pygame.K_SPACE:
                            self.drop_piece()
                        elif event.key == pygame.K_q:
                            self.rotate_piece('x')
                        elif event.key == pygame.K_w:
                            self.rotate_piece('y')
                        elif event.key == pygame.K_e:
                            self.rotate_piece('z')
                        elif event.key == pygame.K_a:
                            self.rotation_y -= 5
                        elif event.key == pygame.K_d:
                            self.rotation_y += 5
                        elif event.key == pygame.K_s:
                            self.rotation_x += 5
                        elif event.key == pygame.K_w:
                            self.rotation_x -= 5
            
            if not self.game_over:
                # Auto-fall
                current_time = pygame.time.get_ticks()
                if current_time - self.last_fall > self.fall_speed:
                    if not self.move_piece(0, -1, 0):
                        self.lock_piece()
                    self.last_fall = current_time
            
            self.render()
            clock.tick(60)

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
