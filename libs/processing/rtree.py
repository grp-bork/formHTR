from rtree import index
from libs.region import Rectangle


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
        results.append([Rectangle(*candidate.bbox, candidate.object) for candidate in candidates])
        self.google_rtree.mark_rectangles(candidates)

        candidates = self.amazon_rtree.find_intersection(rectangle)
        results.append([Rectangle(*candidate.bbox, candidate.object) for candidate in candidates])
        self.amazon_rtree.mark_rectangles(candidates)

        candidates = self.azure_rtree.find_intersection(rectangle)
        results.append([Rectangle(*candidate.bbox, candidate.object) for candidate in candidates])
        self.azure_rtree.mark_rectangles(candidates)

        return results
    
    def filter_artefacts(self):
        google_remaining = self.google_rtree.filter_unused()
        amazon_remaining = self.amazon_rtree.filter_unused()
        azure_remaining = self.azure_rtree.filter_unused()
        return {'google': google_remaining, 'amazon': amazon_remaining, 'azure': azure_remaining}


class RectangleTree:
    def __init__(self, content):
        self.index = index.Index()
        for i, roi in enumerate(content):
            self.index.insert(i, roi.get_coords(), obj=roi.content)
        self.used_rois = set()
    
    def find_intersection(self, rectangle):
        return list(self.index.intersection(rectangle, objects=True))

    def mark_rectangles(self, rectangles):
        for rectangle in rectangles:
            self.used_rois.add(rectangle.id)

    def prune_residuals(self, residuals):
        for residual in residuals:
            candidates = self.find_intersection(residual.get_coords())
            for candidate in candidates:
                x, y = (candidate.bbox[0] + candidate.bbox[2])/2, (candidate.bbox[1] + candidate.bbox[3])/2
                if residual.point_is_inside(x, y):
                    self.index.delete(candidate.id, candidate.bbox)

    def filter_unused(self):
        all_rectangles = list(self.index.intersection(self.index.get_bounds(), objects=True))
        unused_rectangles = []
        for item in all_rectangles:
            if item.id not in self.used_rois:
                unused_rectangles.append(Rectangle(*item.bbox, item.object))
        return unused_rectangles
