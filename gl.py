# SR4 Flat Shading
# Graficas por computadora 
# Esteban Aldana Guerra 20591

import struct
import random
from obj import Obj
from collections import namedtuple

V2 = namedtuple('Vertex2', ['x', 'y'])
V3 = namedtuple('Vertex3', ['x', 'y', 'z'])

def sub(v0, v1):
    return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)


def dot(v0, v1):
    return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v0, v1):
    return V3(
    v0.y * v1.z - v0.z * v1.y,
    v0.z * v1.x - v0.x * v1.z,
    v0.x * v1.y - v0.y * v1.x,
)

def length(v0):
    return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
    v0length = length(v0)

    if not v0length:
        return V3(0, 0, 0)

    return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def bbox(*vertices): 
    xs = [ vertex.x for vertex in vertices ]
    ys = [ vertex.y for vertex in vertices ]
    xs.sort()
    ys.sort()

    return V2(xs[0], ys[0]), V2(xs[-1], ys[-1])

def barycentric(A, B, C, P):
    bary = cross(
        V3(C.x - A.x, B.x - A.x, A.x - P.x), 
        V3(C.y - A.y, B.y - A.y, A.y - P.y)
    )

    if abs(bary[2]) < 1:
        return -1, -1, -1  

    return (
        1 - (bary[0] + bary[1]) / bary[2], 
        bary[1] / bary[2], 
        bary[0] / bary[2]
    )

# 1 byte
def char(c):
    return struct.pack('=c', c.encode('ascii'))

# 2 bytes
def word(c):
    return struct.pack('=h', c)

# 4 bytes 
def dword(c):
    return struct.pack('=l', c)

# funcion de color
def color(r, g, b):
    return bytes([b, g, r])

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)

class Render(object):
 
  def __init__(self,width,height):
    self.width = width
    self.height = height
    self.current_color = WHITE
    self.clear()

  def glInit(self):
        pass

  def clear(self):
    self.framebuffer = [
      [BLACK for x in range(self.width)] 
      for y in range(self.height)
    ]
    self.zbuffer = [
      [-float('inf') for x in range(self.width)]
      for y in range(self.height)
    ]

  def set_color(self, color):
    self.current_color = color

  def point(self, x, y, color = None):
    try:
      self.framebuffer[y][x] = color or self.current_color
    except:
      pass
    

  def triangle(self, A, B, C, color=None):
    bbox_min, bbox_max = bbox(A, B, C)

    for x in range(bbox_min.x, bbox_max.x + 1):
      for y in range(bbox_min.y, bbox_max.y + 1):
        w, v, u = barycentric(A, B, C, V2(x, y))
        if w < 0 or v < 0 or u < 0:  
          continue
        
        z = A.z * w + B.z * v + C.z * u

        if z > self.zbuffer[x][y]:
          self.point(x, y, color)
          self.zbuffer[x][y] = z

  def transform(self, vertex, translate=(0, 0, 0), scale=(1, 1, 1)):
    return V3(
      round((vertex[0] + translate[0]) * scale[0]),
      round((vertex[1] + translate[1]) * scale[1]),
      round((vertex[2] + translate[2]) * scale[2])
    )
    
  def load(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
    model = Obj(filename)

    light = V3(0,0,1)

    for face in model.vfaces:
        vcount = len(face)

        if vcount == 3:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1

          a = self.transform(model.vertices[f1], translate, scale)
          b = self.transform(model.vertices[f2], translate, scale)
          c = self.transform(model.vertices[f3], translate, scale)

          normal = norm(cross(sub(b, a), sub(c, a)))
          intensity = dot(normal, light)
          grey = round(255 * intensity)
          if grey < 0:
            continue  
          
          self.triangle(a, b, c, color(grey, grey, grey))
        else:
          f1 = face[0][0] - 1
          f2 = face[1][0] - 1
          f3 = face[2][0] - 1
          f4 = face[3][0] - 1   

          vertices = [
            self.transform(model.vertices[f1], translate, scale),
            self.transform(model.vertices[f2], translate, scale),
            self.transform(model.vertices[f3], translate, scale),
            self.transform(model.vertices[f4], translate, scale)
          ]

          normal = norm(cross(sub(vertices[0], vertices[1]), sub(vertices[1], vertices[2])))  
          intensity = dot(normal, light)
          grey = round(255 * intensity)
          if grey < 0:
            continue 

  
          A, B, C, D = vertices 
        
          self.triangle(A, B, C, color(grey, grey, grey))
          self.triangle(A, C, D, color(grey, grey, grey))

  def glFinish(self, filename):
            f = open(filename, 'bw')

            #file header
            f.write(char('B'))
            f.write(char('M'))
            f.write(dword(14 + 40 + self.width * self.height * 3))
            f.write(dword(0))
            f.write(dword(14 + 40))

            #image header
            f.write(dword(40))
            f.write(dword(self.width))
            f.write(dword(self.height))
            f.write(word(1))
            f.write(word(24))   
            f.write(dword(0))
            f.write(dword(24))
            f.write(dword(self.width * self.height * 3))
            f.write(dword(0))
            f.write(dword(0))
            f.write(dword(0)) 
            f.write(dword(0))

            # pixel data

            for x in range(self.width):
                for y in range(self.height):
                    f.write(self.framebuffer[x][y])
            
            f.close()