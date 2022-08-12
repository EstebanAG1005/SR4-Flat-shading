# SR3 Models
# Graficas por computadora 
# Esteban Aldana Guerra 20591

from obj import Obj
from gl import Render, color


r = Render()

width = 1024
height = 1024

# Se crea tamaño de pantalla
r.glCreateWindow(width, height)

# Se carga el obj
r.load('coffe.obj', translate=(0.85, 0.5), scale=(600, 600))
r.glFinish('coffe.bmp')

