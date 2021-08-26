import math
import pygame
import time


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

    def addDensity(self, x, y, amount, N):
        index = IX(x, y, N)
        self.density[index] += amount

    def addVelocity(self, x, y, amountX, amountY, N):
        index = IX(x, y, N)
        self.Vx[index] += amountX
        self.Vy[index] += amountY

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

        tic = time.perf_counter()
        diffuse(1, Vx0, Vx, visc, dt, 4, N)
        diffuse(2, Vy0, Vy, visc, dt, 4, N)
        toc = time.perf_counter()
        print(f"ran two diffuse in {toc - tic:0.4f} seconds")

        tic = time.perf_counter()
        project(Vx0, Vy0, Vx, Vy, 4, N)
        toc = time.perf_counter()
        print(f"ran project in {toc - tic:0.4f} seconds")

        tic = time.perf_counter()
        advect(1, Vx, Vx0, Vx0, Vy0, dt, N)
        advect(2, Vy, Vy0, Vx0, Vy0, dt, N)
        toc = time.perf_counter()
        print(f"ran two advect in {toc - tic:0.4f} seconds")

        tic = time.perf_counter()
        project(Vx, Vy, Vx0, Vy0, 4, N)
        toc = time.perf_counter()
        print(f"ran 2nd project in {toc - tic:0.4f} seconds")

        tic = time.perf_counter()
        diffuse(0, s, density, diff, dt, 4, N)
        advect(0, density, s, Vx, Vy, dt, N)
        toc = time.perf_counter()
        print(f"ran diffuse & advect in {toc - tic:0.4f} seconds")

        print('#### FINISH ####')

    def render(self):
        for j in range(self.size - 1):
            for i in range(self.size - 1):
                d = self.density[IX(i, j, self.size)]
                if d > 0:
                    print(d)
                COLOR = (0, 0, d)
                pygame.draw.rect(self.screen, COLOR, (i, j, 1, 1))



'''
the IX function is used to go from a 2D coordinate to the position of that coordinate in a one dimensional array, this
is from Dan Shiffman's original video, i will likely come back and change it to improve its speed as I want to use as few
arrays as possible.
'''


def IX(x, y, N):
    # N here is screenSize from the main loop
    return int(x + y * N)


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
    lin_solve(b, x, x0, a, 1 + 6 * a, iter, N)


'''
Function for solving linear equations of fluid dynamics
a - calculated in the diffuse function above
iter - number of iterations is how many times we apply the 'rules' of this function to our grid in general: iter > means
       more detail but slower speeds
'''


def lin_solve(b, x, x0, a, a_eq, iter, N):
    c_recip = 1.0 / a_eq
    for iteration in range(iter):
        for j in range(1, N - 1, 1):
            for i in range(1, N - 1, 1):
                x[IX(i, j, N)] = (x0[IX(i, j, N)] + a * (
                        x[IX(i + 1, j, N)] + x[IX(i - 1, j, N)] + x[IX(i, j + 1, N)] + x[
                    IX(i, j - 1, N)])) * c_recip

        set_bnd(b, x, N)


'''
Set_bnd
to keep the fluid in the box when a velocity goes into the wall the wall responds by perfectly countering it
'''


def set_bnd(b, x, N):

    # I wasn't sure which way round the if statement should go here so if it doesnt work change them

    for i in range(1, N - 1, 1):
        x[IX(i, 0, N)] = -x[IX(i, 1, N)] if b == 2 else x[IX(i, 1, N)]
        x[IX(i, N - 1, N)] = -x[IX(i, N - 2, N)] if b == 2 else x[IX(i, N - 2, N)]

    for j in range(1, N - 1, 1):
        x[IX(0, j, N)] = -x[IX(1, j, N)]if b == 1 else x[IX(1, j, N)]
        x[IX(N - 1, j, N)] = -x[IX(N - 2, j, N)] if b == 1 else x[IX(N - 2, j, N)]

    x[IX(0, 0, N)] = 0.5 * (x[IX(1, 0, N)] + x[IX(0, 1, 0)])
    x[IX(0, N - 1, N)] = 0.5 * (x[IX(1, N - 1, N)] + x[IX(0, N - 2, N)])
    x[IX(N - 1, 0, N)] = 0.5 * (x[IX(N - 2, 0, N)] + x[IX(N - 1, 1, N)])
    x[IX(N - 1, N - 1, N)] = 0.5 * (x[IX(N - 2, N - 1, N)] + x[IX(N - 1, N - 2, N)])


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
            div[IX(i, j, N)] = -0.5 * (
                    velocX[IX(i + 1, j, N)] - velocX[IX(i - 1, j, N)] + velocY[IX(i, j + 1, N)] - velocY[
                IX(i, j - 1, N)]) / N
            p[IX(i, j, N)] = 0

    set_bnd(0, div, N)
    set_bnd(0, p, N)
    lin_solve(0, p, div, 1, 6, iter, N)

    for j in range(1, N - 1, 1):
        for i in range(1, N - 1, 1):
            velocX[IX(i, j, N)] -= 0.5 * (p[IX(i + 1, j, N)] - p[IX(i - 1, j, N)]) * N
            velocY[IX(i, j, N)] -= 0.5 * (p[IX(i, j + 1, N)] - p[IX(i, j - 1, N)]) * N

    set_bnd(1, velocX, N)
    set_bnd(2, velocY, N)


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
    dtx = dt * (N - 2)
    dty = dt * (N - 2)

    for j in range(1, N - 1, 1):
        for i in range(1, N - 1, 1):
            tmp1 = dtx * velocX[IX(i, j, N)]
            tmp2 = dty * velocY[IX(i, j, N)]

            x = i - tmp1
            y = j - tmp2

            if x < 0.5: x = 0.5
            if x > N + 0.5: x = N + 0.5

            i0 = math.floor(x)
            i1 = i0 + 1.0

            if y < 0.5: y = 0.5
            if y > N + 0.5: y = N + 0.5

            j0 = math.floor(y)
            j1 = j0 + 1.0

            s1 = x - i0
            s0 = 1.0 - s1
            t1 = y - j0
            t0 = 1.0 - t1

            i0i = int(i0)
            i1i = int(i1)
            j0i = int(j0)
            j1i = int(j1)

            d[IX(i, j, N)] = s0 * ((t0 *(d0[IX(i0i, j0i, N)])) + (t1 * (d0[IX(i0i, j1i, N)]))) + s1 * ((t0 *(d0[IX(i1i, j0i, N)])) + (t1 * (d0[IX(i1i, j1i, N)])))

    set_bnd(b, d, N)




