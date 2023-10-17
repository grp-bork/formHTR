class Region:
    """
    Class to represent single ROI
    """
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

    def __str__(self):
        return f'({self.start_x}, {self.start_y}) ({self.end_x}, {self.end_y})'

    def get_start(self):
        return (self.start_x, self.start_y)
    
    def get_end(self):
        return (self.end_x, self.end_y)

    def get_coords(self):
        return [self.start_x, self.start_y, self.end_x, self.end_y]


class Residual(Region):
    def __init__(self, start_x, start_y, end_x, end_y, expected_content):
        super().__init__(start_x, start_y, end_x, end_y)
        self.expected_content = expected_content

    def __str__(self):
        return f'Residual {self.expected_content}: {super().__str__()}'

    def update_expected_content(self, expected_content):
        self.expected_content = expected_content


class ROI(Region):
    def __init__(self, start_x, start_y, end_x, end_y, varname=None, content_type=None):
        super().__init__(start_x, start_y, end_x, end_y)
        self.varname = varname
        self.content_type = content_type

    def __str__(self):
        return f'Region {self.varname}: {super().__str__()} - {self.content_type}'

    def update_content_type(self, content_type):
        self.content_type = content_type

    def update_varname(self, varname):
        self.varname = varname


class Rectangle(Region):
    def __init__(self, start_x, start_y, end_x, end_y, content):
        super().__init__(start_x, start_y, end_x, end_y)
        self.content = content
        self.center_x, self.center_y = self.compute_center()

    def __str__(self):
        return f'"{self.content}": {super().__str__()}'
    
    def __repr__(self):
        return str(self)

    def compute_center(self):
        return (self.start_x + self.end_x)/2, (self.start_y + self.end_y)/2

    def is_left(self, other):
        return self.end_x <= other.center_x and self.start_y <= other.center_y <= self.end_y
