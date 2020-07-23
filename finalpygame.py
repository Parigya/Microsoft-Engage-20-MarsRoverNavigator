import visibilitygraph
from visibilitygraph import VisGraph
import graph
from graph import Point
import visiblevertices
import dijkstra
import astar
import tqdm
import pygame

pygame.init()

display_width = 1280
display_height = 720

black = (0, 0, 0)
white = (255, 255, 255)
red = (237, 41, 57)
gray = (169, 169, 169)
orange=(243, 113, 33)
blue=(17, 29, 94)
green = (0, 128, 0)

LEFT = 1
RIGHT = 3

gameDisplay = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('MARS ROVER ')
icon=pygame.image.load('mars-rover.png')
background=pygame.image.load('marss.jpg')
background1=pygame.image.load('mars-surface1.jpg')
startpt=pygame.image.load('flag.png')
endpt=pygame.image.load('red-flag.png')
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

def draw_polygon(polygon, color, size, complete=True):
    if complete:
        polygon.append(polygon[0])
    p1 = polygon[0]
    for p2 in polygon[1:]:
        pygame.draw.line(gameDisplay, color, (p1.x, p1.y), (p2.x, p2.y), size)
        p1 = p2

def draw_visible_vertices(edges, color, size):
    for edge in edges:
        pygame.draw.line(gameDisplay, color, (edge.p1.x, edge.p1.y), (edge.p2.x, edge.p2.y), size)

def draw_visible_mouse_vertices(pos, points, color, size):
    for point in points:
        pygame.draw.line(gameDisplay, color, (pos.x, pos.y), (point.x, point.y), size)

def draw_text(mode_txt, color, size, x, y):
    font = pygame.font.SysFont(None, size)
    text = font.render(mode_txt, True, color)
    gameDisplay.blit(text, (x, y))

def help_screen():
    rectw = 500
    recth = 500
    rectwi = rectw-10
    recthi = recth-10
    startx = (display_width*0.5-rectw/2)+370
    starty = 70
    startxi = startx+5
    startyi = 75

    helping = True
    while helping:
        for event in pygame.event.get():
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_h:
                    helping = False
                    
        #font = pygame.font.Font('freesansbold.ttf', 32)
        #text = font.render('GeeksForGeeks', True, black, white)  
  
        pygame.draw.rect(gameDisplay, black, (startx, starty, rectw, recth))
        pygame.draw.rect(gameDisplay, white, (startxi, startyi, rectwi, recthi))
        
        draw_text("Mars Rover Navigator",orange,50,460,20)
        draw_text("Congratulations on your successful landing to Mars! ",blue,38,10,230)
        draw_text("We have built you a special program to navigate over the surface of Mars",blue,30,10,300)
        draw_text("  (which mind you is full of craters, mountains) in the  shortest possible",blue,30,10,330)
        draw_text("distance from one point to another. Mind you, you can go inside the craters",blue,30,10,360)
        draw_text("                     and mountains to explore but not cross them!",blue,30,10,390)
        draw_text("   Have fun exploring! Do read the instructions to have a safe experience",blue,30,10,420)
        
        draw_text("-- MARS ROVER SIMULATOR --", black, 25, startxi+110, startyi+10)
        draw_text("Q - QUIT", black, 22, startxi+10, startyi+45)
        draw_text("H - TOGGLE HELP SCREEN (THIS SCREEN)", black, 22, startxi+10, startyi+77)
        draw_text("D - TOGGLE DRAW MODE", black, 22, startxi+10, startyi+109)
        draw_text("    Draw polygons by left clicking to set a point of the", black, 22, startxi+10, startyi+138)
        draw_text("    polygon. Right click to close and finish the polygon.", black, 22, startxi+10, startyi+167)
        draw_text("    U - UNDO LAST POLYGON POINT PLACEMENT", black, 22, startxi+10, startyi+199)
        draw_text("    C - CLEAR THE SCREEN", black, 22, startxi+10, startyi+231)
        draw_text("S - TOGGLE SHORTEST PATH MODE (DIJKSTRA)", black, 22, startxi+10, startyi+263)
        draw_text("    Left click to set start point, right click to set end point.", black, 22, startxi+10, startyi+292)
        #draw_text("    Hold left/right mouse button down to drag start/end point.", black, 22, startxi+10, startyi+321)
        draw_text("A - TOGGLE SHORTEST PATH MODE (A*)", black, 22, startxi+10, startyi+324)
        draw_text("    Left click to set start point, right click to set end point.", black, 22, startxi+10, startyi+356)
        #draw_text("    Hold left/right mouse button down to drag start/end point.", black, 22, startxi+10, startyi+411)
        draw_text("E - ADD ANOTHER DESTINATION ",black,22,startxi+10,startyi+388)
        draw_text("M - TOGGLE VISIBILE VERTICES FROM MOUSE CURSOR", black, 22, startxi+10, startyi+420)
        draw_text("G - TOGGLE POLYGON VISIBILITY GRAPH", black, 22, startxi+10, startyi+452)

        pygame.display.update()
        clock.tick(10)

class Simulator():

    def __init__(self):
        self.polygons = []
        self.work_polygon = []
        self.mouse_point = None
        self.mouse_vertices = []
        self.start_point = None
        self.end_point = None
        self.path=[]
        self.shortest_path = []

        self.g = VisGraph()
        self.built = False
        self.show_static_visgraph = True
        self.show_mouse_visgraph = False
        self.mode_draw = True
        self.mode_path = False
        self.mode_path1 = False

    def toggle_draw_mode(self):
        self.mode_draw = not self.mode_draw
        self._clear_shortest_path()
        self.mode_path = False

    def close_polygon(self):
        if len(self.work_polygon) > 1:
            self.polygons.append(self.work_polygon)
            self.work_polygon = []
            self.g.build(self.polygons, status=False)
            self.built = True

    def draw_point_undo(self):
        if len(self.work_polygon) > 0:
            self.work_polygon.pop()

    def toggle_shortest_path_mode(self):
        if self.mode_path:
            self._clear_shortest_path()
        self.mode_path = True
        self.mode_draw = False
        
    def toggle_shortest_path_mode1(self):
        if self.mode_path1:
            self._clear_shortest_path()
        self.mode_path1 = True
        self.mode_draw = False

    def clear_all(self):
        self.__init__()

    def _clear_shortest_path(self):
        self.shortest_path = []
        self.start_point = []
        self.end_point = [] 
        
def game_loop():
    sim = Simulator()
    gameExit = False
    sx=0
    sy=0
    ex=0
    ey=0
    i=0
    flag=False
    a=False
    d=False
    while not gameExit:

        # Event loop
        for event in pygame.event.get():
            pos = pygame.mouse.get_pos()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()
                elif event.key == pygame.K_h:
                    help_screen()
                elif event.key == pygame.K_g:
                    sim.show_static_visgraph = not sim.show_static_visgraph
                elif event.key == pygame.K_m:
                    sim.show_mouse_visgraph = not sim.show_mouse_visgraph
                elif event.key == pygame.K_d:
                    sim.toggle_draw_mode()
                elif event.key == pygame.K_s:
                    sim.toggle_shortest_path_mode()
                    d=True
                    a=False
                elif event.key == pygame.K_a:
                    sim.toggle_shortest_path_mode1()
                    a=True
                    d=False
                elif event.key == pygame.K_e:
                    flag=True
                    sx=ex
                    sy=ey
                    ex=0
                    ey=0
                    if d:
                        sim.toggle_shortest_path_mode()
                    if a:
                        sim.toggle_shortest_path_mode1()

            if sim.mode_draw:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_u:
                        sim.draw_point_undo()
                    elif event.key == pygame.K_c:
                        sim.clear_all()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == LEFT:
                        sim.work_polygon.append(Point(pos[0], pos[1]))
                    elif event.button == RIGHT:
                        sim.close_polygon()

            if sim.mode_path and sim.built:
                if event.type == pygame.MOUSEBUTTONUP or any(pygame.mouse.get_pressed()):
                    if pygame.mouse.get_pressed()[LEFT-1] or event.button == LEFT:
                        sim.start_point = Point(pos[0], pos[1])
                        sx=pos[0]
                        sy=pos[1]
                    elif pygame.mouse.get_pressed()[RIGHT-1] or event.button == RIGHT:
                        if flag:
                            sim.start_point = Point(sx,sy)
                        sim.end_point = Point(pos[0], pos[1])
                        ex=pos[0]
                        ey=pos[1]
                    if sim.start_point and sim.end_point:
                        sim.path.append(sim.g.shortest_path(sim.start_point, sim.end_point))
            
            if sim.mode_path1 and sim.built:
                if event.type == pygame.MOUSEBUTTONUP or any(pygame.mouse.get_pressed()):
                    if pygame.mouse.get_pressed()[LEFT-1] or event.button == LEFT:
                        sim.start_point = Point(pos[0], pos[1])
                        sx=pos[0]
                        sy=pos[1]
                    elif pygame.mouse.get_pressed()[RIGHT-1] or event.button == RIGHT:
                        if flag:
                            sim.start_point = Point(sx,sy)
                        sim.end_point = Point(pos[0], pos[1])
                        ex=pos[0]
                        ey=pos[1]
                    if sim.start_point and sim.end_point:
                        sim.path.append(sim.g.shortest_path1(sim.start_point, sim.end_point))

            if sim.show_mouse_visgraph and sim.built:
                if event.type == pygame.MOUSEMOTION:
                    sim.mouse_point = Point(pos[0], pos[1])
                    sim.mouse_vertices = sim.g.find_visible(sim.mouse_point)

        # Display loop
        gameDisplay.fill(white)
        gameDisplay.blit(background1,(0,0))
        gameDisplay.blit(startpt,(sx,sy))
        gameDisplay.blit(endpt,(ex,ey))
        if len(sim.work_polygon) > 1:
            draw_polygon(sim.work_polygon, black, 3, complete=False)

        if len(sim.polygons) > 0:
            for polygon in sim.polygons:
                draw_polygon(polygon, black, 3)

        if sim.built and sim.show_static_visgraph:
            draw_visible_vertices(sim.g.visgraph.get_edges(), gray, 1)

        if sim.built and sim.show_mouse_visgraph and len(sim.mouse_vertices) > 0:
            draw_visible_mouse_vertices(sim.mouse_point, sim.mouse_vertices, gray, 1)

        if len(sim.path) > 1:
            for p in sim.path:
                draw_polygon(p, red, 3, complete=False)

        if sim.mode_draw:
            draw_text("-- DRAW MODE --", black, 25, 5, 5)
        elif sim.mode_path:
            draw_text("-- Dijkstra Algorithm --", black, 25, 5, 5)
        elif sim.mode_path1:
            draw_text("-- A* Algorithm --", black, 25, 5, 5)
        else:
            draw_text("-- VIEW MODE --", black, 25, 5, 5)

        pygame.display.update()
        clock.tick(20)

if __name__ == "__main__":
    gameDisplay.blit(background,(0,0))
    help_screen()
    game_loop()
    pygame.quit()
    quit()
