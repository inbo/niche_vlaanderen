from osgeo import gdal

from .input_types import InputLayerTypes as it

import logging
import os.path

class Niche(object):
    '''
    '''
    def __init__(self):
        self._inputfiles = dict()
        self.log = logging.getLogger()


    def set_input(self,type, file):
        # check type is valid value from enum
        if not isinstance(type, it):
            self.log.error("Invalid input type")
            return False

        # check file exists
        if not os.path.exists(file):
            self.log.error("File %s does not exist" % file)
            return False

        self._inputfiles[type] = file
        return True

    def _check_input_files(self):
        # check all necessary files are set
        if not [it.MHW, it.MLW] in self._inputfiles.keys():
            self.log.error("MHW and MLW must be defined")

        # check files exist
        for f in self._inputfiles:
            if not os.path.exists(file):
                self.log.error("File %s does not exist" % file)
                return False

        # check boundaries overlap with study area + same grid
        for f in self._inputfiles:
            ds = gdal.Open(f)
            gt = ds.GetGeoTransform()


        pass

