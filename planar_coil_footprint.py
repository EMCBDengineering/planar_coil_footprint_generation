import KicadModTree
from typing import NamedTuple


class Via(NamedTuple):
    """
    Class to define the Via as a datatype
    """
    diameter: float
    drill: float

class Pad(NamedTuple):
    """
    Class to define the Pad as a datatype
    """
    diameter: float

class Coil_Geometrics(NamedTuple):
    """
    Class to define the width and length of a single rectangular coil
    """
    width: float
    length: float
    trackwidth: float

class Coordinate(NamedTuple):
    """
    Class to define a coordinate by x- and y-coordinate
    """
    x: float
    y: float


class coil():
    """
    generic coil-class for easy coil-buildung
    """
    def __init__(self, footprint_name) -> None:
        """
        initializes a footprint-handle by the name
        """
        self.mod = KicadModTree.Footprint(footprint_name)
        return

    def draw_line(self, begin: Coordinate, end: Coordinate, layer: str, trackwidth: float) -> None:
        """
        creates a straight line
        """
        self.mod.append(
            KicadModTree.Line(
                start=[begin.x, begin.y],
                end=[end.x, end.y],
                layer=layer,
                width=trackwidth
            )
        )
        return

    def draw_via(self, position: Coordinate, via: Via, number: int) -> None:
        """
        creates a via;
        difference between via- and pad-generation is mostly LAYERS_THT and LAYERS_SMT
        """
        self.mod.append(
            KicadModTree.Pad(
            number = number,
            type=KicadModTree.Pad.TYPE_THT,
            shape=KicadModTree.Pad.SHAPE_CIRCLE,
            at=[position.x, position.y],
            size=[via.diameter, via.diameter],
            drill=via.drill,
            layers=KicadModTree.Pad.LAYERS_THT
            )
        )
        return

    def draw_pad(self, position: Coordinate, pad: Pad, number: int) -> None:
        """
        creates a pad;
        difference between via- and pad-generation is mostly LAYERS_THT and LAYERS_SMT
        """
        self.mod.append(KicadModTree.Pad(
            number = number,
            type=KicadModTree.Pad.TYPE_SMT,
            shape=KicadModTree.Pad.SHAPE_CIRCLE,
            at=[position.x, position.y],
            size=[pad.diameter, pad.diameter],
            layers=KicadModTree.Pad.LAYERS_SMT
            )
        )
        return


def rectangular_coil_footprint(coil_geometrics: Coil_Geometrics, turns: int, via: Via, pad: Pad, footprint_name: str) -> KicadModTree.Footprint:
    """
    creates a footprint-handle of a rectangular-shaped coil 
    """
    # create a coil-object
    rectangular_coil = coil(footprint_name)

    # set the starting-position and draw the first pad
    pos0 = Coordinate(x=0.0, y=coil_geometrics.length/2)
    rectangular_coil.draw_pad(position=pos0, pad=pad, number=0)

    pos1 = Coordinate(x=0.0, y=0.0)
    rectangular_coil.draw_line(begin=pos0, end=pos1, layer="F.Cu", trackwidth=coil_geometrics.trackwidth)

    for i in range(turns):
        # structure for every turn
        pos2 = Coordinate(x=pos1.x + coil_geometrics.width, y=pos1.y)
        rectangular_coil.draw_line(begin=pos1, end=pos2, layer="F.Cu", trackwidth=coil_geometrics.trackwidth)

        rectangular_coil.draw_via(position=pos2, via=via, number=i*2 + 1)

        pos3 = pos1
        rectangular_coil.draw_line(begin=pos2, end=pos3, layer="B.Cu", trackwidth=coil_geometrics.trackwidth)

        pos4 = Coordinate(x=pos3.x, y=pos3.y - coil_geometrics.length/2)
        rectangular_coil.draw_line(begin=pos3, end=pos4, layer="B.Cu", trackwidth=coil_geometrics.trackwidth)

        rectangular_coil.draw_via(position=pos4, via=via, number=i*2 + 2)

        pos5 = Coordinate(x=pos4.x, y=pos4.y - coil_geometrics.length/2)
        rectangular_coil.draw_line(begin=pos4, end=pos5, layer="F.Cu", trackwidth=coil_geometrics.trackwidth)

        pos1 = pos5

    # draw the last pad
    rectangular_coil.draw_pad(
            position=pos5, pad=pad, number=turns*2 - 1
        )

    # give back the footprint-handle
    return KicadModTree.KicadFileHandler(rectangular_coil.mod)

def calc_clearance(coil_geometrics: Coil_Geometrics, via: Via) -> float:
    """
    calculates the clearance of a rectangular coil
    """
    return (coil_geometrics.length - via.diameter - coil_geometrics.trackwidth) / 2


if __name__ == "__main__":
    coil_params = Coil_Geometrics(width=6, length=8, trackwidth=0.3)
    turns = 3
    via = Via(diameter=0.8, drill=0.6)
    pad = Pad(diameter=1)
    name = "Pad_testing"

    footprint_file = rectangular_coil_footprint(coil_params, turns, via, pad, name)
    footprint_file.writeFile(name + ".kicad_mod")

    print("Clearance = " + str(calc_clearance(coil_geometrics=coil_params, via=via)))