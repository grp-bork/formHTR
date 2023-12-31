import cv2


def process_cli(widget):
    exit = False
    while not exit:
        key = cv2.waitKey(0)
        # Close program with 'q' or 'Esc' button
        if key == ord('q') or key == 27:
            exit = True
        if key == ord('j'): # left ROI
            widget.previous_region()
        if key == ord('k'): # right ROI
            widget.next_region()
        if key in [ord('h'), ord('c'), ord('b'), ord('n')]:
            widget.update_content_type(chr(key))
        if key == ord('r') or key == ord('d'):
            widget.update_content_type(None)
        if key == ord('v'):
            widget.read_varname()
