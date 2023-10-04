import cv2


class AnnotateROIsWidget:
    """
    Widget to annotate ROIs on the given template.
    """
    def __init__(self, image, config):
        self.original_image = image
        self.image = self.original_image.copy()
        self.config = config
        self.num_of_regions = len(self.config.regions)

        self.selected_index = 0

        cv2.namedWindow('Annotate ROIs')
        # cv2.setMouseCallback('Annotate ROIs', self.process_events)

        self.draw_regions()
        cv2.imshow('Annotate ROIs', self.image)
        self.config.announce_status(self.selected_index)

    def process_events(self, event, x, y, *kwargs):
        """
        TODO when click inside a rectangle, select it
        will require a smarter data structure
        """
        pass

    def draw_regions(self):
        """
        Draw regions. Highligh the selected one.
        """
        for i, region in enumerate(self.config.regions):
            colour = (240,20,20)
            if i == self.selected_index:
                colour = (0,0,255)
            cv2.rectangle(self.image, region.get_start(), region.get_end(), colour, 2)

    def reset_image(self):
        """
        Start again with empty image.
        """
        self.image = self.original_image.copy()
        self.draw_regions()
        cv2.imshow('Annotate ROIs', self.image)

    def update_content_type(self, content_type):
        self.config.update_content_type(self.selected_index, content_type)
        self.config.announce_status(self.selected_index)

    def next_region(self):
        if self.selected_index + 1 < self.num_of_regions:
            self.selected_index += 1
            self.reset_image()
            self.config.announce_status(self.selected_index)

    def previous_region(self):
        if self.selected_index - 1 >= 0:
            self.selected_index -= 1
            self.reset_image()
            self.config.announce_status(self.selected_index)

    def read_varname(self):
        varname = input("\nEnter name: ")
        self.config.update_varname(self.selected_index, varname)
        self.config.announce_status(self.selected_index)
