import cv2


class SelectROIsWidget:
    """
    Widget to draw ROIs on the given template.
    """
    def __init__(self, image, config, display_residuals):
        self.original_image = image
        self.image = self.original_image.copy()
        self.config = config
        self.display_residuals = display_residuals

        self.drawing_in_progress = False
        self.start_x, self.start_y = -1, -1

        cv2.namedWindow('Select ROIs')
        cv2.setMouseCallback('Select ROIs', self.process_events)

        self.draw_existing_rectangles()
        cv2.imshow('Select ROIs', self.image)

    def process_events(self, event, x, y, *kwargs):
        """
        React to mouse events.
        """
        # Store rectangle initial coordinates on left mouse button click
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing_in_progress = True
            self.start_x, self.start_y = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing_in_progress:
                # Draw a temporary rectangle
                dynamic_image = self.image.copy()
                cv2.rectangle(dynamic_image, (self.start_x, self.start_y), (x, y), (0,0,255), 2)
                cv2.imshow('Select ROIs', dynamic_image)

        # Record final rectangle coordinates on left mouse button release
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing_in_progress = False
            # accept only non-empty rectangles
            if self.start_x != x and self.start_y != y:
                print(f'Added rectangle: top left {(self.start_x, self.start_y)}, bottom right: {(x, y)}')
                self.config.add_roi(self.start_x, self.start_y, x, y)

                # Draw rectangle 
                cv2.rectangle(self.image, (self.start_x, self.start_y), (x, y), (240,20,20), 5)
                cv2.imshow("Select ROIs", self.image)

    def draw_existing_rectangles(self):
        """
        Include existing regions into the image.
        """
        for region in self.config.regions:
            cv2.rectangle(self.image, region.get_start(), region.get_end(), (240,20,20), 5)
        if self.display_residuals:
            for residual in self.config.residuals:
                cv2.rectangle(self.image, residual.get_start(), residual.get_end(), (60,166,71), 5)

    def reset_image(self):
        """
        Start again with empty image.
        """
        self.image = self.original_image.copy()

    def undo_add_rectangle(self):
        """
        Remove last region (undo).
        """
        self.config.delete_last_region()
        self.reset_image()
        self.draw_existing_rectangles()
        cv2.imshow('Select ROIs', self.image)
