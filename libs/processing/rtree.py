from rtree import index


class RectangleTree:
    def __init__(self, content):
        self.index = index.Index()
        for i, roi in enumerate(content):
            self.index.insert(i, roi['coords'], obj=roi['content'])
    
    def find_intersection(self, rectangle):
        return list(self.index.intersection(rectangle))
