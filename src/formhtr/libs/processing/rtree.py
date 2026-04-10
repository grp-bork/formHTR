from rtree import index
from ..region import Rectangle


class Ensemble:
    def __init__(self, indetified_content, config):
        """Build spatial indexes for each OCR engine and drop residual-matched words.

        Args:
            indetified_content: Dict with keys ``google``, ``amazon``, ``azure``;
                values are lists of ``Rectangle`` or ``None``.
            config: ``LogsheetConfig`` with ``residuals`` to prune from each tree.
        """
        self.google_rtree = RectangleTree(indetified_content['google'] if indetified_content['google'] is not None else [])
        self.google_rtree.prune_residuals(config.residuals)
        self.amazon_rtree = RectangleTree(indetified_content['amazon'] if indetified_content['amazon'] is not None else [])
        self.amazon_rtree.prune_residuals(config.residuals)
        self.azure_rtree = RectangleTree(indetified_content['azure'] if indetified_content['azure'] is not None else [])
        self.azure_rtree.prune_residuals(config.residuals)

    def find_intersection(self, rectangle):
        """Intersect one ROI with each provider tree and mark hits as used.

        Args:
            rectangle: ``[x0, y0, x1, y1]`` ROI bounds.

        Returns:
            Dict mapping provider name to lists of ``Rectangle`` copies for that ROI.
        """
        results = dict()

        candidates = self.google_rtree.find_intersection(rectangle)
        results['google'] = [Rectangle(*candidate.bbox, candidate.object) for candidate in candidates]
        self.google_rtree.mark_rectangles(candidates)

        candidates = self.amazon_rtree.find_intersection(rectangle)
        results['amazon'] = [Rectangle(*candidate.bbox, candidate.object) for candidate in candidates]
        self.amazon_rtree.mark_rectangles(candidates)

        candidates = self.azure_rtree.find_intersection(rectangle)
        results['azure'] = [Rectangle(*candidate.bbox, candidate.object) for candidate in candidates]
        self.azure_rtree.mark_rectangles(candidates)

        return results
    
    def filter_artefacts(self):
        """Collect OCR rectangles that were not assigned to any ROI.

        Returns:
            Dict ``google`` / ``amazon`` / ``azure`` -> list of unused ``Rectangle``.
        """
        google_remaining = self.google_rtree.filter_unused()
        amazon_remaining = self.amazon_rtree.filter_unused()
        azure_remaining = self.azure_rtree.filter_unused()
        return {'google': google_remaining, 'amazon': amazon_remaining, 'azure': azure_remaining}


class RectangleTree:
    def __init__(self, content):
        """Index word rectangles for fast intersection queries.

        Args:
            content: Iterable of ``Rectangle`` instances with ``get_coords()`` and ``content``.
        """
        self.index = index.Index()
        for i, roi in enumerate(content):
            self.index.insert(i, roi.get_coords(), obj=roi.content)
        self.used_rois = set()
    
    def find_intersection(self, rectangle):
        """Return indexed items whose bounds intersect ``rectangle``.

        Args:
            rectangle: ``[x0, y0, x1, y1]`` query bounds.

        Returns:
            List of rtree result objects (``bbox``, ``object``, ``id``).
        """
        return list(self.index.intersection(rectangle, objects=True))

    def mark_rectangles(self, rectangles):
        """Record result objects as consumed by ROI assignment.

        Args:
            rectangles: Iterable of intersection results from ``find_intersection``.
        """
        for rectangle in rectangles:
            self.used_rois.add(rectangle.id)

    def prune_residuals(self, residuals):
        """Remove OCR items that match configured residual (printed) text regions.

        Args:
            residuals: Iterable of ``Residual`` with ``expected_content`` and bounds.
        """
        for residual in residuals:
            candidates = self.find_intersection(residual.get_coords())
            for candidate in candidates:
                x, y = (candidate.bbox[0] + candidate.bbox[2])/2, (candidate.bbox[1] + candidate.bbox[3])/2
                if residual.point_is_inside(x, y):
                    if candidate.object in residual.expected_content:
                        self.index.delete(candidate.id, candidate.bbox)
    
    def filter_unused(self):
        """Return rectangles never marked via ``mark_rectangles``.

        Returns:
            List of ``Rectangle`` rebuilt from remaining index entries.
        """
        if self.index.get_size() != 0:
            all_rectangles = list(self.index.intersection(self.index.get_bounds(), objects=True))
            unused_rectangles = []
            for item in all_rectangles:
                if item.id not in self.used_rois:
                    unused_rectangles.append(Rectangle(*item.bbox, item.object))
            return unused_rectangles
        return []
