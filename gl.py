# SR3 Models
# Graficas por computadora 
# Esteban Aldana Guerra 20591

import struct
from obj import Obj

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


class Render(object):
    def __init__(self):
        self.background = color(0,0,0)
        self.figura = color(255,255,255)
        
    def glInit(self):
        pass
    
    def glClear(self):
        self.framebuffer = [
            [self.background for x in range(self.width)]
            for y in range(self.height)
        ]

    def glCreateWindow(self, width, height): 
        self.width = width
        self.height = height
        self.glClear()
    
    def point(self, x,y):
        try:
            self.framebuffer[y][x] = self.figura
        except:
            pass

    def glViewPort(self, x, y, width, height):
        self.posXV = x
        self.posYV = y
        self.viewpWidth = width
        self.viewpHeight = height

    def glClearColor(self, r, g, b):
        self.background = color(int(round(r*255)),int(round(g*255)),int(round(b*255)))

    def glColor(self, r,g,b):
        self.figura = color(int(round(r*255)),int(round(g*255)),int(round(b*255)))

    def glVertex(self, x, y):
        CordX = round((x+1)*(self.viewpWidth/2)+self.posXV)
        CordY = round((y+1)*(self.viewpHeight/2)+self.posYV)
        self.point(CordX, CordY)
    
    def glLine(self,x0, y0, x1, y1):
        x0 = int(round((x0+1) * self.width / 2))
        y0 = int(round((y0+1) * self.height / 2))
        x1 = int(round((x1+1) * self.width / 2))
        y1 = int(round((y1+1) * self.height / 2))
        steep=abs(y1 - y0)>abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0>x1:
            x0,x1 = x1,x0
            y0,y1 = y1,y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)
        y = y0
        offset = 0
        threshold = dx

        for x in range(x0, x1):
            if offset>=threshold:
                y += 1 if y0 < y1 else -1
                threshold += 2*dx
            if steep:
                self.point(x, y)
            else:
                self.point(y, x)
            offset += 2*dy

    def load(self, filename, translate, scale):
        model = Obj(filename)
        
        for face in model.faces:
            vcount = len(face)

            for j in range(vcount):
                f1 = face[j][0]
                f2 = face[(j + 1) % vcount][0]

                v1 = model.vertices[f1 - 1]
                v2 = model.vertices[f2 - 1]
                
                x0 = round((v1[0] + translate[0]) * scale[0])
                y0 = round((v1[1] + translate[1]) * scale[1])
                x1 = round((v2[0] + translate[0]) * scale[0])
                y1 = round((v2[1] + translate[1]) * scale[1])

                x0 = ((2*x0)/self.width)-1
                y0 = ((2*y0)/self.height)-1
                x1 = ((2*x1)/self.width)-1
                y1 = ((2*y1)/self.height)-1

                self.glLine(x0, y0, x1, y1)

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
                f.write(self.framebuffer[y][x])
        
        f.close()
