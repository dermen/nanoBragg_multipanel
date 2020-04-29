from __future__ import print_function

try:
  from cfelpyutils.crystfel_utils import load_crystfel_geometry
except ImportError:
  print("You must first install cfelpyutils using `libtbx.python -m pip install cfelpyutils --user`")
  exit()

from dxtbx.model import Panel, Detector
from dxtbx.model import ExperimentList, Experiment


def convert_crystfel_to_dxtbx(geom_filename, output_filename, detdist_override=None):
  """
  :param geom_filename: a crystfel geometry file https://www.desy.de/~twhite/crystfel/manual-crystfel_geometry.html
  :param output_filename: filename for a dxtbx experiment containing a single detector model (this is a json file)
  :param detdist_override: alter the detector distance stored in the crystfel geometry to this value (in millimeters)
  """
  geom = load_crystfel_geometry(geom_filename)

  dxtbx_det = Detector()

  for panel_name in geom['panels'].keys():
    P = geom['panels'][panel_name]
    FAST = P['fsx'], P['fsy'], P['fsz']
    SLOW = P['ssx'], P['ssy'], P['ssz']

    # dxtbx uses millimeters
    pixsize = 1/P['res']  # meters
    pixsize_mm = pixsize * 1000
    detdist = P['coffset'] + P['clen']  # meters
    detdist_mm = detdist*1000
    if detdist_override is not None:
      detdist_mm = detdist_override
    # dxtbx and crystfel both identify the outer corner of the first pixel in memory as the origin of the panel
    origin = P['cnx']*pixsize_mm, P['cny']*pixsize_mm, -detdist_mm  # dxtbx assumes crystal as at point 0,0,0

    num_fast_pix = P["max_fs"] - P['min_fs'] + 1
    num_slow_pix = P["max_ss"] - P['min_ss'] + 1

    panel_description = {'fast_axis': FAST,
      'gain': 1.0, # I dont think nanoBragg cares about this parameter
      'identifier': '',
      'image_size': (num_fast_pix, num_slow_pix),
      'mask': [],
      'material': 'Si',
      'mu': 0,  # NOTE for a thick detector set this to appropriate value
      'name': panel_name,
      'origin': origin,
      'pedestal': 0.0,  # I dont think nanoBragg cares about this parameter
      'pixel_size': (pixsize_mm, pixsize_mm),
      'px_mm_strategy': {'type': 'SimplePxMmStrategy'},
      'raw_image_offset': (0, 0),  # not sure what this is
      'slow_axis': SLOW,
      'thickness': 0,  # note for a thick detector set this to appropriate value
      'trusted_range': (-1.0, 1e6),  # set as you wish
      'type': 'SENSOR_PAD'}
    dxtbx_node = Panel.from_dict(panel_description)
    dxtbx_det.add_panel(dxtbx_node)

  E =Experiment()
  E.detector = dxtbx_det
  El = ExperimentList()
  El.append(E)
  El.as_file(output_filename)  # this can be loaded into nanoBragg


def load_detector_from_expt(expt_file, exp_id=0):
  detector = ExperimentList.from_file(expt_file).detectors()[exp_id]
  return detector




