from ctypes import *
from ctypes import WINFUNCTYPE


class Coordinate(Structure):
    _fields_=[('dNum1',     c_double),
              ('dNum2',     c_double),
              ('dNum3',     c_double), 
              ('dLatacc',   c_double), 
              ('dLongacc',  c_double),
              ('iNum4',     c_long),
              ('IO_Status', c_long)]
    def __repr__(self):
        return ','.join([i+":"+str(getattr(self, i)) for i, j in self._fields_])
dll = WinDLL("gcalc\\GCalc.dll")
dll.restype = None
dll.argtypes = [POINTER(Coordinate)]
func = dll.GCALC_GridtoGeo


def gda94Towgs84(zone, east, north):
    coord = Coordinate()
    coord.dNum1 = c_double(east)
    coord.dNum2 = c_double(north)
    coord.dNum3 = c_double(zone)
    coord.iNum4 = c_long(1)
    func(byref(coord))
    return coord

if __name__ == "__main__":
    x = 280711.375
    y = 6133025.2736
    z = 54
    print ("Converting x={},y={},z={} to lat/lng".format(x, y, z))
    print (gda94Towgs84(z, x, y))