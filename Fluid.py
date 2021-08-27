import math
import pygame
import Coord
import time
import random

Screen_Size = 512
pixel_size = 16
scale = int(Screen_Size/pixel_size)

class Fluid:
    def __init__(self, size, dt, diff, visc, s, density, Vx, Vy, Vx0, Vy0, screen):
        self.size = size
        self.dt = dt
        self.diff = diff
        self.visc = visc
        self.s = s
        self.density = density
        self.Vx = Vx
        self.Vy = Vy
        self.Vx0 = Vx0
        self.Vy0 = Vy0
        self.screen = screen

    def addDensity(self, x, y, amount):
        self.density[Coord.Coord(int(x), int(y))] += amount

    def addVelocity(self, x, y, amountX, amountY):
        self.Vx[Coord.Coord(int(x), int(y))] += amountX
        self.Vy[Coord.Coord(int(x), int(y))] += amountY

    def step(self):
        N = self.size
        visc = self.visc
        diff = self.diff
        dt = self.dt
        Vx = self.Vx
        Vy = self.Vy
        Vx0 = self.Vx0
        Vy0 = self.Vy0
        s = self.s
        density = self.density

        #tic = time.perf_counter()
        self.Vx = diffuse(1, Vx0, Vx, visc, dt, 4, N)
        self.Vy = diffuse(2, Vy0, Vy, visc, dt, 4, N)
        #toc = time.perf_counter()
        #print(f"ran two diffuse in {toc - tic:0.4f} seconds")

        self.Vx0 = self.Vx
        self.Vy0 = self.Vy

        #tic = time.perf_counter()
        self.Vx, self.Vy = project(Vx0, Vy0, Vx, Vy, 4, N)
        #toc = time.perf_counter()
        #print(f"ran project in {toc - tic:0.4f} seconds")

        self.Vx0 = self.Vx
        self.Vy0 = self.Vy

        #tic = time.perf_counter()
        self.Vx = advect(1, Vx, Vx0, Vx0, Vy0, dt, N)
        self.Vy = advect(2, Vy, Vy0, Vx0, Vy0, dt, N)

        self.Vx = constraining_looper(self.Vx, -1, 1)
        self.Vy = constraining_looper(self.Vy, -1, 1)

        #toc = time.perf_counter()
        #print(f"ran two advect in {toc - tic:0.4f} seconds")

        self.Vx0 = self.Vx
        self.Vy0 = self.Vy

        #tic = time.perf_counter()
        self.Vx, self.Vy = project(Vx, Vy, Vx0, Vy0, 4, N)
        #toc = time.perf_counter()
        #print(f"ran 2nd project in {toc - tic:0.4f} seconds")

        self.Vx0 = self.Vx
        self.Vy0 = self.Vy

        #tic = time.perf_counter()
        self.s = diffuse(0, s, density, diff, dt, 4, N)
        self.density = advect(0, density, s, Vx, Vy, dt, N)
        #toc = time.perf_counter()
        #print(f"ran diffuse & advect in {toc - tic:0.4f} seconds")


    def render(self):
        for j in range(self.size - 1):
            for i in range(self.size - 1):
                d = self.density[Coord.Coord(int(i), int(j))]
                if d != 0:
                    COLOR = (d,d,d)
                    pygame.draw.rect(self.screen, COLOR, (i*pixel_size, j*pixel_size, pixel_size, pixel_size))

    def fade(self):
        for j in range(self.size - 1):
            for i in range(self.size - 1):
                d = self.density[Coord.Coord(int(i), int(j))]
                self.density.update({Coord.Coord(int(i), int(j)): constrain(d, 0, 255)})


'''
Function for diffusion of Dye
b - ?
x - current array
x0 - previous values
diff - diffusion amount
dt - time step
iter - number of iterations (used in lin_solve, explained there)
N - Screen Size from main loop
'''


def diffuse(b, x, x0, diff, dt, iter, N):
    a = dt * diff * (N - 2) * (N - 2)
    x = lin_solve(b, x, x0, a, 1 + 6 * a, iter, N)
    return x


'''
Function for solving linear equations of fluid dynamics
a - calculated in the diffuse function above
iter - number of iterations is how many times we apply the 'rules' of this function to our grid in general: iter > means
       more detail but slower speeds
'''


def lin_solve(b, x, x0, a, a_eq, iter, N):
    c_recip = 1.0 / a_eq
    #tic = time.perf_counter()
    #for iteration in range(iter):
    for i in range(1, N - 1, 1):
        for j in range(1, N - 1, 1):
                    x.update({Coord.Coord(int(i), int(j)):
                     (x0[Coord.Coord(int(i), int(j))]
                      + a * (x[Coord.Coord(int(i + 1), int(j))]
                      + x[Coord.Coord(int(i - 1), int(j))]
                      + x[Coord.Coord(int(i), int(j + 1))]
                      + x[Coord.Coord(int(i), int(j - 1))])) * c_recip})


    x = set_bnd(b, x, N)
    #toc = time.perf_counter()
    #print(f"@@@@ ran inside lin_solve in {toc - tic:0.4f} seconds")

    return x


'''
Set_bnd
to keep the fluid in the box when a velocity goes into the wall the wall responds by perfectly countering it
'''


def set_bnd(b, x, N):
    # I wasn't sure which way round the if statement should go here so if it doesnt work change them

    #tic = time.perf_counter()
    for i in range(1, N - 1, 1):
        x[Coord.Coord(0, int(i))] = -x[Coord.Coord(int(1), int(i))] if b == 1 else x[Coord.Coord(int(1), int(i))]
        x[Coord.Coord(int(N), int(i))] = -x[Coord.Coord(int(N - 1), int(i))] if b == 1 else x[
            Coord.Coord(int(N - 1), int(i))]
        x[Coord.Coord(int(i), 0)] = -x[Coord.Coord(int(i), int(1))] if b == 2 else x[Coord.Coord(int(i), int(1))]
        x[Coord.Coord(int(i), int(N))] = -x[Coord.Coord(int(i), int(N - 1))] if b == 2 else x[
            Coord.Coord(int(i), int(N - 1))]

    x[Coord.Coord(0, 0)] = 0.5 * (x[Coord.Coord(1, 0)] + x[Coord.Coord(0, 1)])
    x[Coord.Coord(0, N)] = 0.5 * (x[Coord.Coord(1, N)] + x[Coord.Coord(0, N - 1)])
    x[Coord.Coord(N, 0)] = 0.5 * (x[Coord.Coord(N - 1, 0)] + x[Coord.Coord(N, 1)])
    x[Coord.Coord(N, N)] = 0.5 * (x[Coord.Coord(N - 1, N)] + x[Coord.Coord(N, N - 1)])

    #toc = time.perf_counter()
    #print(f"  @@@@ ran inside lin_solve's set_bnd in {toc - tic:0.4f} seconds")

    return x


'''
velocX - array of x components
velocY - array of y components
p - array of pressure
div - array of divergence
iter - iterations
N - screen size
'''


def project(velocX, velocY, p, div, iter, N):

    for j in range(1, N - 1, 1):
        for i in range(1, N - 1, 1):
            # if IX(i ,j, N) == 32896:
            # print(f'INSIDE for loop in project div 1ST IS - {div[32896]}')
            div[Coord.Coord(int(i), int(j))] = -0.5 * (
                        velocX[Coord.Coord(int(i + 1), int(j))] - velocX[Coord.Coord(int(i - 1), int(j))] + velocY[
                    Coord.Coord(int(i), int(j + 1))] - velocY[Coord.Coord(int(i), int(j - 1))]) / N
            # if IX(i ,j, N) == 32896:
            # print(f'INSIDE for loop in project div 2nd IS - {div[32896]}')
            p[Coord.Coord(int(i), int(j))] = 0

    div = set_bnd(0, div, N)
    p = set_bnd(0, p, N)
    p = lin_solve(0, p, div, 1, 6, iter, N)

    for j in range(1, N - 1, 1):
        for i in range(1, N - 1, 1):
            plusP_i = p[Coord.Coord(int(i + 1), int(j))]
            minusP_i = p[Coord.Coord(int(i - 1), int(j))]
            plusP_j = p[Coord.Coord(int(i), int(j + 1))]
            minusP_j = p[Coord.Coord(int(i), int(j - 1))]
            velocX[Coord.Coord(int(i), int(j))] -= constrain((0.5 * (plusP_i - minusP_i) * N), -1, 1)
            velocY[Coord.Coord(int(i), int(j))] -= constrain((0.5 * (plusP_j - minusP_j) * N), -1, 1)

    velocX = set_bnd(1, velocX, N)
    velocY = set_bnd(2, velocY, N)

    return velocX, velocY


'''
advect - this is the function that actually moves things around
b - ?
d - ?
d0 = ??
dt - time step
N - screen size

the original code has i, j, i float, j float in the for loops. i am not going to implement this i am just going to use
i and j.
'''


def advect(b, d, d0, velocX, velocY, dt, N):

    dt0 = dt*N
    for i in range(1, N, 1):
        for j in range(1, N, 1):
                x = constrain((i - dt0 * velocX[Coord.Coord(int(i), int(j))]), 0, N)
                y = constrain((j - dt0 * velocY[Coord.Coord(int(i), int(j))]), 0, N)

                if x < 0.5: x = 0.5
                if x > N + 0.5: x = N + 0.5

                i0 = int(x)
                i1 = constrain((int(i0 + 1)), 0, N)

                if y < 0.5: y = 0.5
                if y > N + 0.5: y = N + 0.5

                j0 = int(y)
                j1 = constrain((int(j0 + 1)), 0, N)

                s1 = x - i0
                s0 = 1.0 - s1
                t1 = y - j0
                t0 = 1.0 - t1

                d[Coord.Coord(int(i), int(j))] = s0 * (t0 * d0[Coord.Coord(int(i0), int(j0))]
                                               + t1 * d0[Coord.Coord(int(i0), int(j1))]) \
                                               + s1 * (t0 * d0[Coord.Coord(int(i1), int(j0))]
                                               + t1 * d0[Coord.Coord(int(i1), int(j1))])

    d = set_bnd(b, d, N)

    return d


def constraining_looper(dict, min, max):
    for key in dict:
        dict[key] = constrain(dict[key], min, max)

    return dict

def constrain(value, min, max):
    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value
