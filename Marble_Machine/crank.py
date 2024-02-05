# PY5 IMPORTED MODE CODE

# Class responsible for all the logic and display functions for the 'crank handle'
class Crank:
    stroke_color = 0
    fill_color = 0

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

        self.angle = -HALF_PI
        self.angle_velocity = 0
        self.angle_acceleration = 0
        self.damping = 0.992

    def update(self):
        self.angle += self.angle_velocity
        self.angle_velocity += self.angle_acceleration
        self.angle_velocity *= self.damping
        self.angle_velocity = constrain(self.angle_velocity, 0, 0.2)
        self.angle_acceleration = 0

    def display(self):
        with push():
            translate(self.x, self.y)
            no_stroke()

            # Draw the outside circle
            fill(self.fill_color)
            circle(0, 0, self.size)

            # Draw the inside smaller circle
            fill(self.stroke_color)
            rotate(self.angle)
            circle(self.size * 0.4, 0, 20)


    def turn(self, m_x, m_y, pm_x, pm_y):
        vect = Py5Vector(m_x - self.x, m_y - self.y)
        prev_vect = Py5Vector(pm_x - self.x, pm_y - self.y)

        # If the mouse is inside the circle
        if (vect.mag <= (self.size / 2)):
            diff_vect = vect.heading - prev_vect.heading
            # And we turn clockwise
            if (0 < diff_vect < 1):
                self.angle_acceleration = diff_vect / 50
