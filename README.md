3D Tetris Game
A fully playable 3D Tetris game built with Python, Pygame, and OpenGL.
Installation
Install the required dependencies:
pip3 install -r requirements.txt
How to Play
Run the game:
python3 tetris_3d.py
Controls
Piece Movement
Arrow Keys: Move piece horizontally and in depth
LEFT/RIGHT: Move piece left/right (X axis)
UP/DOWN: Move piece forward/backward (Z axis)
SPACE: Drop piece instantly to the bottom
Piece Rotation
Q: Rotate around X axis
W: Rotate around Y axis
E: Rotate around Z axis
Camera Controls
A/D: Rotate camera left/right
S/W: Rotate camera up/down (note: W is used for both piece rotation and camera)
Game Controls
R: Restart game (when game is over)
Close window or Ctrl+C: Quit game
Game Rules
Pieces fall from the top of a 10x20x10 3D grid
Move and rotate pieces to fit them into the grid
Complete horizontal layers (all 100 blocks filled) to clear them and score points
Game ends when a new piece cannot be placed at the spawn position
Each cleared layer gives you 100 points
Features
Full 3D rendering with OpenGL lighting and shading
7 different classic tetromino shapes
Colorful pieces with edge outlines
Real-time score display
Smooth camera rotation to view from different angles
Automatic piece falling with collision detection
Layer clearing mechanics
Enjoy the game!
