# SR4 Flat-Shading
# Graficas por computadora 
# Esteban Aldana Guerra 20591

from obj import Obj
from gl import Render, color, V2, V3

width = 1200
height = 1200

r = Render(width,height)

# Se carga el obj
r.load('coffe.obj', V3(1, 0.5, 0), V3(600, 600, 600))
r.glFinish('coffe.bmp')

