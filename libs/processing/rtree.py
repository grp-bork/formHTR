from rtree import index
from libs.logsheet_config import Rectangle


class Ensemble:
    def __init__(self, indetified_content, config):
        self.google_rtree = RectangleTree(indetified_content['google'])
        self.google_rtree.prune_residuals(config.residuals)
        self.amazon_rtree = RectangleTree(indetified_content['amazon'])
        self.amazon_rtree.prune_residuals(config.residuals)
        self.azure_rtree = RectangleTree(indetified_content['azure'])
        self.azure_rtree.prune_residuals(config.residuals)

    def find_intersection(self, rectangle):
        results = []

        candidates = self.google_rtree.find_intersection(rectangle)
        results.append([Rectangle(*candidate.bbox, candidate.obj) for candidate in candidates])
        self.google_rtree.delete_rectangles(candidates)

        candidates = self.amazon_rtree.find_intersection(rectangle)
        results.append([Rectangle(*candidate.bbox, candidate.obj) for candidate in candidates])
        self.amazon_rtree.delete_rectangles(candidates)

        candidates = self.azure_rtree.find_intersection(rectangle)
        results.append([Rectangle(*candidate.bbox, candidate.obj) for candidate in candidates])
        self.azure_rtree.delete_rectangles(candidates)

        return results


class RectangleTree:
    def __init__(self, content):
        self.index = index.Index()
        for i, roi in enumerate(content):
            self.index.insert(i, roi.get_coords(), obj=roi.content)
    
    def find_intersection(self, rectangle):
        return list(self.index.intersection(rectangle))
    
    def delete_rectangle(self, id, coords):
        self.index.delete(id, coords)

    def delete_rectangles(self, rectangles):
        for rectangle in rectangles:
            self.delete_rectangle(rectangle.id, rectangle.bbox)

    def prune_residuals(self, residuals):
        for residual in residuals:
            candidates = self.find_intersection(residual)
            self.delete_rectangles(candidates)
