import pygame
import Fluid
import Coord
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

11:39 27/08 - down to 4.23 seconds with the introduction of dictionaries

13:27 27/08 -
this is the index density is added at - 32896
this is the density in add density - 100.0
at correct index, this is the value of d - 100.0
density not zero at - (128, 128)
Vx before density declared - 1.0
1st step density is - 100.0
(111) just to check this is N - 256
(111) veloc X starting project 1.0
(111) veloc Y starting project 1.0
(111) p starting project 1.0
(111) div starting project 1.0
################################################
div before set_bnd-0.0
div after set_bnd-0.0
p before set_bnd 0.0
p after set_bnd 0.0
p before lin solve 0.0
p after lin solve -2.848958482176866e-06
################################################
VelocX and VelocY at end (0.9078298253886603, 0.9078298253886603)
value when back in step function - 0.9078298253886603
value when back in step funciton - 0.9078298253886603
@@@@@@@@@@@@@@@@@@ outside project in step @@@@@@@@@@@@@@@@@@
1st - 0.9078298253886603
1st - 0.9078298253886603
INSIDE ADVECT 1ST IS -2.848958482176866e-06
INSIDE ADVECT 2nd IS 0.0
INSIDE ADVECT 1ST IS -0.0
INSIDE ADVECT 2nd IS 0.0
2nd - 0.0
2nd - 0.0
3rd - 0.0
3rd - 0.0
@@@@@@@@@@@@@@@@@@ outside project in step fin @@@@@@@@@@@@@@@@@@
(111) just to check this is N - 256
(111) veloc X starting project 0.0
(111) veloc Y starting project 0.0
(111) p starting project 0.9078298253886603
(111) div starting project 0.9078298253886603
################################################
div before set_bnd0.000306736971055684
div after set_bnd0.000306736971055684
p before set_bnd 0.0
p after set_bnd 0.0
p before lin solve 0.0
p after lin solve -7.404934578019768e-05
################################################
VelocX and VelocY at end (0.036076802889768424, 0.03607680288976842)
value when back in step function after 2nd project - 0.036076802889768424
value when back in step funciton after 2nd project - 0.03607680288976842
INSIDE ADVECT 1ST IS 100.0
INSIDE ADVECT 2nd IS 0.6997189764790552
#### FINISHED STEP ####

'''

Screen_Size = 512
pixel_size = 32
scale = int(Screen_Size/pixel_size)
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)


screen = pygame.display.set_mode((Screen_Size, Screen_Size))
pygame.display.set_caption("Smoke and Wind chime simulator")

clock = pygame.time.Clock()

pygame.init()

'''
declaring fluid variables and then creating a fluid class object with them
'''

'''
empty = {}
empty1 = {}

for i in range(Screen_Size*Screen_Size):
    empty[i] = 0

for i in range(Screen_Size*Screen_Size):
    empty1[i] = 0
'''


size = pixel_size
DT = 0.1
diff = 0
visc = 0
#s = np.empty(Screen_Size*Screen_Size, dtype=float)
#density = np.empty(Screen_Size*Screen_Size, dtype=float)

s = Coord.generate_empty(pixel_size)
density = Coord.generate_empty(pixel_size)

#Vx = np.empty(Screen_Size*Screen_Size, dtype=float)
#Vy = np.empty(Screen_Size*Screen_Size, dtype=float)

#Vx0 = np.empty(Screen_Size*Screen_Size, dtype=float)
#Vy0 = np.empty(Screen_Size*Screen_Size, dtype=float)

Vx = Coord.generate_empty(pixel_size)
Vy = Coord.generate_empty(pixel_size)

Vx0 = Coord.generate_empty(pixel_size)
Vy0 = Coord.generate_empty(pixel_size)

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
    fluid.addDensity(int(scale/2), int(scale/2), 100)
    fluid.addVelocity(int(scale/2), int(scale/2), 0.2, -0.2)
    fluid.addVelocity(int(scale/2), int(scale/2), 0, -0.2)
    fluid.render()

    fluid.step()

    pygame.display.update()

    clock.tick(30)
