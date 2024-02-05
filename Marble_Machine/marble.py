# PY5 IMPORTED MODE CODE

# Class responsible for all the logic and display functions for the marbles
class Marble():
    ball_diameter = 0
    top_offset = 0
    bottom_offset = 0
    gravity = 0
    stroke_color = 0
    fill_color = 0

    def __init__(self, x):
        self.orig_x = x
        self.position = Py5Vector2D(x, self.top_offset)
        self.velocity = Py5Vector2D(0, 0)

        self.falling = False
        self.bouncing = False
        self.out_of_screen = False

        self.glowing = 255
        self.opacity = 0

    def __repr__(self):
        return f'Marble({self.orig_x:.2f}, ({self.position.x:.2f}, {self.position.y:.2f}))'

    def update(self):
        if self.falling and not self.out_of_screen:
            self.velocity.y += self.gravity
            self.position += self.velocity

            # Do we reach the bars for bouncing ?
            if not self.bouncing:
                if ((self.position.y + self.ball_diameter/2) >= (height - self.bottom_offset)):
                    # Bounce
                    self.bouncing = True
                    # In a random direction
                    self.velocity.heading = random(-3 * QUARTER_PI, -QUARTER_PI)
                    self.velocity.mag *= 0.5

            # Do we fall out of the screen ?
            if self.bouncing:
                self.glowing -= 4
                if (self.position.y - self.ball_diameter/2 >= height):
                    # Set the marble to be removed
                    self.out_of_screen = True
                    self.glowing = 0

        # We are not falling, and not out of the screen,
        # so we were just created at the top of the screen
        elif not self.out_of_screen:
            self.opacity += 3

    def display(self):
        no_stroke()

        # Draw circle
        if not self.falling:
            # fade in
            fill(self.fill_color, self.opacity)
        elif self.bouncing:
            # glowing on bounce
            fill(255, self.glowing)
        else:
            # juste falling
            fill(self.fill_color)

        circle(*self.position, self.ball_diameter)

        # Draw the bars
        if self.bouncing:
            # Only one marble should be responsible for drawing the bar, the one bouncing
            fill(255, self.glowing)
            rect(self.orig_x, height - self.bottom_offset + 5, 50, 8)
