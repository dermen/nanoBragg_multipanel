from __future__ import print_function

import numpy as np
from scipy.spatial.transform.rotation import Rotation

try:
  from cfelpyutils.crystfel_utils import load_crystfel_geometry
except ImportError:
  print("You must first install cfelpyutils using `libtbx.python -m pip install cfelpyutils --user`")
  exit()

from dxtbx.model import Panel, Detector, Beam, Crystal
from dxtbx.model import ExperimentList, Experiment
from nanoBragg_multipanel.utils import sim_spots, sim_background, H5AttributeGeomWriter


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


if __name__ == '__main__':

# <><><><><><><><>
  USE_CUDA = False
  input_file = 'Jungfrau16M_swissFEL.geom'  # this file is the crystfel geometry
  output_file = 'Jungfrau16M_swissFEL.expt'  # this file will store dxtbx detector
  imgfile_out = "some_jungfrau16M_sims.h5"  # this file will store the multi panel image simulations
# <><><><><><><><>

  convert_crystfel_to_dxtbx(input_file, output_file, detdist_override=250)  # override the detector distance (mm)

  detector = load_detector_from_expt(output_file)
  # get the detector
  # get the beam
  wavelength =1.3
  sample_to_source_direction = (0, 0, 1)  # in dials, +z points from sample to source, and detector panels origins are all at -z
  beam = Beam(sample_to_source_direction, wavelength=wavelength)

  # get the crystal
  # lysozyme
  lookup_symbol = "P43212"
  real_a = 79, 0, 0
  real_b = 0, 79, 0
  real_c = 0, 0, 38
  # NOTE if your lattice is C-centered you will need to convert to the primitive setting (I think)

  # get some structure factors
  from simtbx.nanoBragg.tst_nanoBragg_basic import fcalc_from_pdb
  res = min([d.get_max_resolution_at_corners(beam.get_s0()) for d in detector])
  Famp = fcalc_from_pdb(resolution=res)  # just grab the dummie structure factors

  # make an arbitrary incident energy spectrum here
  wavelengths = [wavelength]
  weights = [1]

  fast_dim, slow_dim = detector[0].get_image_size()
  img_sh = (len(detector), slow_dim, fast_dim)  # note for hdf5 we must abide by numpy convention for array shape
  Nimg = 2

  # Note: for efficiency, if simulating many crystal shots, we only compute background once
  # consider generating background once and subsequently loading from disk, replacing this section fo code with a section that loads background from disk
  background_on_panels = []
  for pidx in range(len(detector)):
    print("\rDoing background panel %d" % (pidx), end="")
    water = sim_background(DETECTOR=detector, BEAM=beam, pidx=pidx, sample_thick_mm=0.200,
                           wavelengths=wavelengths, wavelength_weights=weights, total_flux=1e12)
    background_on_panels.append(water)

  rotations = Rotation.random(Nimg, random_state=8675309)
  with H5AttributeGeomWriter(imgfile_out, image_shape=img_sh, num_images=Nimg, detector=detector, beam=beam,
                             dtype=np.float64, compression_args=None) as writer:

    for i_img in range(Nimg):
      output_panels = []
      for pidx in range(len(detector)):
        # only show params for first panel, otherwise too much output
        if pidx == 0:
          show_params = True
        else:
          show_params = False

        # rotate the crystal randomly
        R = rotations[i_img].as_dcm()
        A = np.dot(R,real_a)
        B = np.dot(R,real_b)
        C = np.dot(R,real_c)
        crystal = Crystal(A,B,C, lookup_symbol)  # instantiate dxtbx crystal model (these are usually stored in expt files output by DIALS after indexing)

        # simulate the spots, consider changing this function and/or its arguments to meet your needs
        panel_pixels = sim_spots(crystal, detector, beam, Famp, wavelengths, weights, pidx=pidx, crystal_size_mm=0.050,
                           beam_size_mm=0.001, total_flux=1e12, time_panels=True, show_params=show_params, cuda=USE_CUDA,
                           mosaic_vol_A3=2000**3, profile="gauss", background_raw_pixels=background_on_panels[pidx])
        output_panels.append(panel_pixels)

      # save the image to hdf5
      output_panels = np.array(output_panels)
      writer.add_image(output_panels)
