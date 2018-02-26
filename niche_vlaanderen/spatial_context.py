from affine import Affine
from textwrap import dedent
import warnings


class SpatialContextError(Exception):
    """

    """


class SpatialContext(object):
    """Stores the spatial context of the grids in niche

    This class is based on the rasterio model of a grid.

    Attributes
    ----------
    transform: Affine
        Matrix that contains the transform transformation of the plane to
        convert grid coordinates to real world coordinates.
        https://github.com/sgillies/transform
    width, height: int
        Integer numbers containing the width and height of the raster
    crs: rasterio.CRS
        Container class for coordinate reference system info

    """

    def __init__(self, dst):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            if isinstance(dst.transform, Affine):
                self.transform = dst.transform
            else:
                # for compatibility with rasterio 0.x
                self.transform = dst.affine

        self.width = int(dst.width)
        self.height = int(dst.height)
        # only occurs on Python 2
        if dst.crs is None:  # pragma: no cover
            self.crs = ""
        elif isinstance(dst.crs, str):
            self.crs = dst.crs
        else:
            self.crs = dst.crs.to_string()

        if self.transform[0] < 0:
            raise SpatialContextError(  # pragma: no cover
                "Grid is indexed right to left. This is very uncommon."
                "Try resampling your grid in GIS prior to using in Niche."
            )

        if self.transform[4] > 0:
            raise SpatialContextError(
                "Grid is indexed top to bottom. This is very uncommon."
                "Try resampling your grid in GIS prior to using in Niche."
            )

    def __repr__(self):

        s = """\
        Extent: %s

        %s

        width: %d, height: %d

        Projection: %s"""

        s = dedent(s) % (self.extent, self.transform.__repr__(),
                         self.width, self.height, self.crs)
        return s

    def compare(self, other):
        """Compare two SpatialContexts

        Equal to: Small differences (<1cm are allowed)
        """

        if self.width != other.width:
            return False

        if self.height != other.height:
            return False

        if self.crs != other.crs:
            if self.crs == '' or self.crs == '':
                print("Ignoring missing CRS in comparison")
            else:
                print("Warning: CRS definitions are not equal!")
                # TODO: we should probably look at the strict validation here.
                # currently disabled until we have a better way to detect
                # l72 variants
                # return False

        if self.transform.almost_equals(other.transform, precision=0.01):
            return True
        else:
            return False

    def __eq__(self, other):
        """Compare two SpatialContexts

        Equal to: Small differences (<1cm are allowed)
        """
        return self.compare(other)

    def __ne__(self, other):
        """ Compare two SpatialContexts

        Not equal to: Small differences are allowed
        """
        return not self.compare(other)

    def check_overlap(self, new_sc):
        """Checks whether two SpatialContexts overlap

        Overlapping spatial contexts are SpatialContexts with the same grid
        dimensions (no resampling is needed to convert them).

        Overlapping SpatialContexts can be used to intersect (set_overlap) or
        can be used to define a read window.
        """
        if not ((self.transform[0] == new_sc.transform[0])
                and (self.transform[1] == new_sc.transform[1])
                and (self.transform[3] == new_sc.transform[3])
                and (self.transform[4] == new_sc.transform[4])):
            print("error: different grid size or orientation")
            return False

            # check cells overlap
        dgx = (~self.transform)[2] - (~new_sc.transform)[2]
        dgy = (~self.transform)[5] - (~new_sc.transform)[5]

        # if this differences are not integer numbers, cells do not overlap
        # we 0.01 m
        if abs(dgx - round(dgx)) > 0.01 or abs(dgy - round(dgy)) > 0.01:
            print("cells do not overlap")
            print(dgx, dgy)
            return False
        else:
            return True

    @property
    def extent(self):
        extent_self = (self.transform) * (0, 0), \
                      (self.transform) * (self.width, self.height)
        return extent_self

    def set_overlap(self, new_sc):
        """ Sets the spatial context to the overlap of both SpatialContexts

        Parameters
        ==========
        new_sc: SpatialContext

        """
        # Check orientation and cell size are equal
        if not self.check_overlap(new_sc):
            raise SpatialContextError("no overlap in extent")

        # determine the extent in the old and new system
        extent_self = self.extent

        extent_new = new_sc.extent

        # The starting point of the combined raster is the left coordinate
        # (if the 0th coefficient of transform is positive). and the bottom
        # coordinate (if the 4th coefficient is negative)
        # Note that usually the 0th coefficient is positive and the 4th
        # negative.

        extent_x = (max(extent_self[0][0], extent_new[0][0]),
                    min(extent_self[1][0], extent_new[1][0]))

        extent_y = (min(extent_self[0][1], extent_new[0][1]),
                    max(extent_self[1][1], extent_new[1][1]))

        self.width = round((extent_x[1] - extent_x[0]) / self.transform[0])
        self.height = round((extent_y[1] - extent_y[0]) / self.transform[4])

        self.transform = \
            Affine(self.transform[0], self.transform[1], extent_x[0],
                   self.transform[3], self.transform[4], extent_y[0])

    def get_read_window(self, new_sc):
        """Gets the read window that overlap with a different SpatialContext

        Gets the window to be read from a new SpatialContext to
        overlap with the current (equally large or larger) SpatialContext

        Parameters
        ==========

        new_sc: SpatialContext
            Spatial context for which a read window is to be determined,
            based on the extent of the overall (equally large or larger
            base SpatialContext)
        """
        if not self.check_overlap(new_sc):
            raise SpatialContextError(
                "Error: No overlap between both Spatial contexts."
            )

        # Get minimum and maximum position in the new grid system
        gminxy = (~new_sc.transform) * ((0, 0) * self.transform)
        gmaxxy = (~new_sc.transform) * (
            (self.width, self.height) * self.transform)

        # we can safely round here because we checked overlap before
        # (differences are smaller than the tolerance
        window = (round(gminxy[1], 2), round(gmaxxy[1], 2)),\
                 (round(gminxy[0], 2), round(gmaxxy[0], 2))

        if window[0][0] < 0 or window[1][0] < 0 or window[1][1] > new_sc.width\
           or window[1][0] > new_sc.height:

            raise SpatialContextError(
                "Error: new SpatialContexts is larger than current context.\n"
                "Can not determine a read window")

        return window

    @property
    def cell_area(self):
        return abs(self.transform[0] * self.transform[4])
