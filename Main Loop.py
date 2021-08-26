import pygame
import Fluid
import numpy as np

'''
currently each update to the fluid takes 5.544 seconds to complete this is much too slow to do anything with and has
halted progress towards actually getting the density of dye in the fluid to be drawn as dye could only be added to the
simulation once every 5.544 seconds the following is the print out:

ran two diffuse in 1.4435 seconds
ran project in 1.1292 seconds
ran two advect in 0.7518 seconds
ran 2nd project in 1.1283 seconds
ran diffuse & advect in 1.0912 seconds
#### FINISH ####

even taking 1 second would lead to lots of lag so all functions must be reduced, i believe the biggest time sink is using
the 1 dimensional array for everything

'''

Screen_Size = 256
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)


screen = pygame.display.set_mode((Screen_Size, Screen_Size))
pygame.display.set_caption("Smoke and Wind chime simulator")

clock = pygame.time.Clock()

pygame.init()

'''
declaring fluid variables and then creating a fluid class object with them
'''

size = Screen_Size
DT = 0.1
diff = 0
visc = 0
s = np.empty(Screen_Size*Screen_Size, dtype=float)
density = np.empty(Screen_Size*Screen_Size, dtype=float)

Vx = np.empty(Screen_Size*Screen_Size, dtype=float)
Vy = np.empty(Screen_Size*Screen_Size, dtype=float)

Vx0 = np.empty(Screen_Size*Screen_Size, dtype=float)
Vy0 = np.empty(Screen_Size*Screen_Size, dtype=float)

fluid = Fluid.Fluid(size, DT, diff, visc, s, density, Vx, Vy, Vx0, Vy0, screen)

running = True
dragged = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        if event.type == pygame.MOUSEBUTTONDOWN:
            dragged = True
        elif event.type == pygame.MOUSEBUTTONUP:
            dragged = False

    screen.fill((0, 0, 0))

    Mouse_x, Mouse_y = pygame.mouse.get_pos()

    # in update
    if dragged:
        fluid.addDensity(Mouse_x, Mouse_y, 100, Screen_Size)

    fluid.step()
    fluid.render()

    pygame.display.update()

    clock.tick(30)
