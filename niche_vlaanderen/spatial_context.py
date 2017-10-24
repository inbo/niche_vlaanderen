import rasterio
from affine import Affine

class SpatialContext(object):
    """Stores the spatial context of the grids in niche

    This class is based on the rasterio model of a grid.

    Attributes
    ----------
    affine: Affine
        Matrix that contains the affine transformation of the plane to convert
        grid coordinates to real world coordinates.
        https://github.com/sgillies/affine
    width, height: int
        Integer numbers containing the width and height of the raster
    crs: rasterio.CRS
        Container class for coordinate reference system info

    """

    def __init__(self, dst):
        self.affine = dst.affine
        self.width = dst.width
        self.height = dst.height
        self.crs = dst.crs

    def __repr__(self):
        s = "Extent: %s\n\n" \
            "%s\n\n" \
        "width: %d, height: %d\n\n" \
        "Projection: %s" % (self.extent, self.affine.__repr__(),
                            self.width, self.height, self.crs.to_string())
        return s

    def __eq__(self, other):
        """Compare two SpatialContexts

        Equal to: Small differences (<1cm are allowed)
        """

        if self.width != other.width:
            return False

        if self.height != other.height:
            return False

        if self.crs.to_string() != other.crs.to_string():
            return False

        if self.affine.almost_equals(other.affine, precision=0.01)\
                and self.width == other.width and self.height == other.height:
            return True
        else:
            return False

    def __ne__(self, other):
        """ Compare two SpatialContexts

        Not equal to: Small differences are allowed
        """
        if self.width != other.width:
            return True

        if self.height != other.height:
            return True

        if self.crs.to_string() != other.crs.to_string():
            return True

        if self.affine.almost_equals(other.affine, precision=0.01)\
                and self.width == other.width and self.height == other.height:
            return False
        else:
            return True

    def check_overlap(self, new_sc):
        """Checks whether two SpatialContexts overlap

        Overlapping spatial contexts are SpatialContexts with the same grid
        dimensions (no resampling is needed to convert them).

        Overlapping SpatialContexts can be used to intersect (set_overlap) or
        can be used to define a read window.
        """
        if not ((self.affine[0] == new_sc.affine[0])
                and (self.affine[1] == new_sc.affine[1])
                and (self.affine[3] == new_sc.affine[3])
                and (self.affine[4] == new_sc.affine[4])):
            print("error: different grid size or orientation")
            return False

            # check cells overlap
        dgx = (~self.affine)[2] - (~new_sc.affine)[2]
        dgy = (~self.affine)[5] - (~new_sc.affine)[5]

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
        extent_self = (self.affine) * (0,0), \
                      (self.affine) * (self.width, self.height)
        return extent_self

    def set_overlap(self, new_sc):
        """ Sets the spatial context to the overlap of both SpatialContexts

        Parameters
        ==========
        new_sc: SpatialContext

        """
        # Check orientation and cell size are equal
        if not self.check_overlap(new_sc):
            return None

        # determine the extent in the old and new system
        extent_self = self.extent

        extent_new = new_sc.extent

        # The startpoint of the combined raster is the left coordinate
        # (if the 0th coefficient of affine is positive). and the bottom
        # coordinate (if the 4th coefficient is negative)


        if self.affine[0] > 0:
            extent_x = (max(extent_self[0][0], extent_new[0][0]),
                        min(extent_self[1][0], extent_new[1][0]))
        else:
            extent_x = (min(extent_self[0][0], extent_new[0][0]),
                        max(extent_self[1][0], extent_new[1][0]))

        if self.affine[4] > 0:
            extent_y = max(extent_self[0][1], extent_new[0][1]),\
                       min(extent_self[1][1], extent_new[1][1])
        else:
            extent_y = min(extent_self[0][1], extent_new[0][1]),\
                       max(extent_self[1][1], extent_new[1][1])

        self.width = round((extent_x[1] - extent_x[0]) / self.affine[0])
        self.height = round((extent_y[1] - extent_y[0]) / self.affine[4])

        self.affine = Affine(self.affine[0], self.affine[1], extent_x[0],
                             self.affine[3], self.affine[4], extent_y[0])

        return True

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
            return None

        # Get minimum and maximum position in the new grid system
        gminxy = (~new_sc.affine) *((0,0) * self.affine)
        gmaxxy = (~new_sc.affine) *(
            (self.width, self.height) * self.affine)

        if (gminxy[0] <0 or gminxy[1] < 0
            or gmaxxy[0] > new_sc.width or gmaxxy[1] > new_sc.height):
            print("Error: new SpatialContexts is larger than current context\n"
                  "Can not determine a read window")
            return None

        # we can safely round hdere because we checked overlap before
        # (differences are smaller than the tolerance)
        return (round(gminxy[1]), round(gmaxxy[1])),\
               (round(gminxy[0]), round(gmaxxy[0]))