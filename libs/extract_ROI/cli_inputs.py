import cv2


def process_cli(widget):
    exit = False
    while not exit:
        key = cv2.waitKey(0)
        # Close program with 'q' or 'Esc' button
        if key == ord('q') or key == 27:
            exit = True
        # Delete last rectangle with 'd'
        if key == ord('d'):
            widget.undo_add_rectangle()
