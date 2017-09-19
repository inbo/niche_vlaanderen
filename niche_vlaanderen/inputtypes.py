from enum import Enum

class InputLayerTypes(Enum):
    GRENS = 1 # Grens studiegebied
    REGIO = 2 # Ongebruikt - om studiegebied op te splitsen
    BODEM = 3 
    GLG = 4
    GVG = 5
    GHG = 6
    KWEL = 7
    OVERSTROMING_TROFIE = 8
    OVERSTROMING_ZUURGRAAD = 9
    ATMOSF_DEPOSITIE = 10
    MEST_DIERLIJK = 11
    MEST_KUNST = 12
    BEHEER = 13
    MINERAALRIJKDOM = 14
    REGENLENS = 15
    OVERSTROMING_VEGETATIE = 16
    NULGRID = 17
