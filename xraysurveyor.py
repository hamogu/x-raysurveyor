import os
import numpy as np
import transforms3d
import marxs
from marxs.optics import MarxMirror, CATGrating, EfficiencyFile
from marxs.simulator import Sequence
from marxs.design.rowland import (design_tilted_torus,
                                  RowlandTorus, GratingArrayStructure)

path = os.path.dirname(__file__)

blazeang = 1.5
phi = [0, 2. * np.pi]
phi = [-0.3 - np.pi / 2, .3 - np.pi / 2]
R, r, pos4d = design_tilted_torus(9e3, np.deg2rad(blazeang),
                                  2 * np.deg2rad(blazeang))
rowland = RowlandTorus(R, r, pos4d=pos4d)
blazemat = transforms3d.axangles.axangle2mat(np.array([0, 0, 1.]),
                                             np.deg2rad(-blazeang))


# Load Ralf's efficiency table
catfile = os.path.join(path, 'sim_input', 'Si-ox_p200_th15_dc02_d6110.dat')
gratingeff = EfficiencyFile(catfile, orders=np.arange(2, -13, -1))
gas = GratingArrayStructure(rowland=rowland, d_element=70.,
                            x_range=[5e3, 1e4], radius=[283., 290., 382., 390., 432., 442., 538., 550.],
                            phi=phi, elem_class=CATGrating,
                            elem_args={'zoom': [1, 30, 30], 'orientation': blazemat,
                                       'd': 0.0002,
                                       'order_selector': gratingeff})


hrmafile = os.path.join(os.path.dirname(marxs.optics.__file__), 'hrma.par')
marxm = MarxMirror(hrmafile, position=np.array([0., 0, 0]))


def prune(photons):
    return photons[(photons['probability'] > 0) & (photons['mirror_shell'] == 0)]

satellite = Sequence(elements=[marxm, prune])

# Place an additional detector in the focal plane for comparison
# Detectors are transparent to allow this stuff
detfp = marxs.optics.FlatDetector(zoom=[.2, 1000, 1000])
detfp.loc_coos_name = ['detfp_x', 'detfp_y']
detfp.detpix_name = ['detfppix_x', 'detfppix_y']
detfp.display['opacity'] = 0.2

# Place an additional detector on the Rowland circle.
detcirc = marxs.optics.CircularDetector.from_rowland(rowland, width=20)
detcirc.loc_coos_name = ['detcirc_phi', 'detcirc_y']
detcirc.detpix_name = ['detcircpix_x', 'detcircpix_y']
detcirc.display['opacity'] = 0.2
