# PY5 IMPORTED MODE CODE

# Class responsible for all the logic and display functions for the toggle buttons
class Toggle:
    diameter = 0
    stroke_color = 0
    fill_color = 0

    def __init__(self, x, y, w, h, value = False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.value = value

    def __repr__(self):
        return f'Toggle({self.x}, {self.y}, {self.w}, {self.h}, {self.value})'

    def display(self):
        with push():
            rect_mode(CORNER)
            translate(self.x, self.y)

            # Draw the line
            stroke(self.stroke_color)
            stroke_weight(4)
            line(self.diameter/2, 0 + self.h/2, self.w - self.diameter/2, self.h/2)

            # # Draw the toggle
            no_stroke()
            if not self.value:
                # ON
                fill(self.stroke_color + 30)
                circle(self.diameter/2, self.h/2, self.diameter)
            else:
                # OFF
                fill(self.fill_color - 10)
                circle(self.w - self.diameter/2, self.h/2, self.diameter)

    def clicked(self, m_x, m_y):
        # Are we inside the bounding box
        if (self.x <= m_x <= self.x + self.w) and (self.y <= m_y <= self.y + self.h):
            self.value = not self.value
