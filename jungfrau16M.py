from __future__ import print_function
from cfelpyutils.crystfel_utils import load_crystfel_geometry
from dxtbx.model import Panel, Detector, Beam, Crystal
from dxtbx.model import ExperimentList, Experiment
import numpy as np
from scitbx.matrix import sqr, col
from simtbx.nanoBragg.quick_flex_beams import sim_spots, sim_background, H5AttributeGeomWriter


def convert_crystfel_to_dxtbx(geom_filename, output_filename, detdist_override=None):
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
      'gain': 1.0,
      'identifier': '',
      'image_size': (num_fast_pix, num_slow_pix),
      'mask': [],
      'material': 'Si',
      'mu': 0,
      'name': panel_name,
      'origin': origin,
      'pedestal': 0.0,
      'pixel_size': (pixsize_mm, pixsize_mm),
      'px_mm_strategy': {'type': 'SimplePxMmStrategy'},
      'raw_image_offset': (0, 0),
      'slow_axis': SLOW,
      'thickness': 0,
      'trusted_range': (-1.0, 1e6),  # Not sure what the trusted range is here
      'type': 'SENSOR_PAD'}
    dxtbx_node = Panel.from_dict(panel_description)
    dxtbx_det.add_panel(dxtbx_node)

  E =Experiment()
  E.detector = dxtbx_det
  El = ExperimentList()
  El.append(E)
  El.as_file(output_filename)  # this can be loaded into nanoBragg


def get_xray_beams(spectrum, beam_originator):
  from dxtbx_model_ext import flex_Beam
  from dxtbx.model import BeamFactory

  xray_beams = flex_Beam()
  for wavelen, flux in spectrum:
    beam = BeamFactory.simple(wavelen * 1e-10)
    beam.set_flux(flux)
    beam.set_unit_s0(beam_originator.unit_s0)
    beam.set_polarization_fraction(beam_originator.polarization_fraction)
    beam.set_divergence(beam_originator.divergence)
    xray_beams.append(beam)

  return xray_beams


if __name__ == '__main__':
  input_file = 'Jungfrau16M_swissFEL.geom'
  output_file = 'Jungfrau16M_swissFEL.expt'
  convert_crystfel_to_dxtbx(input_file, output_file, detdist_override=250)  # override the detector distance to 170mm

  # get the detector
  detector = ExperimentList.from_file(output_file).detectors()[0]

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

  # get some structure factors
  from simtbx.nanoBragg.tst_nanoBragg_basic import fcalc_from_pdb
  res = min([d.get_max_resolution_at_corners(beam.get_s0()) for d in detector])
  Famp = fcalc_from_pdb(resolution=res)  # just grab the dummie structure factors

  # make an arbitrary incident energy spectrum here
  wavelengths = [wavelength]
  weights = [1]

  master_out = "some_jungfrau16M_sims.h5"

  fast_dim, slow_dim = detector[0].get_image_size()
  img_sh = (len(detector), slow_dim, fast_dim)  # note for hdf5 we must abide by numpy convention for array shape
  Nimg = 2
  USE_CUDA = False
  from scipy.spatial.transform.rotation import Rotation

  # Note: for efficiency, if simulating many crystal shots,
  # consider generating background once and subsequently loading from  disk
  background_on_panels = []
  for pidx in range(len(detector)):
    print("\rDoing background panel %d" % (pidx), end="")
    water = sim_background(DETECTOR=detector, BEAM=beam, pidx=pidx, sample_thick_mm=0.200,
                           wavelengths=wavelengths, wavelength_weights=weights, total_flux=1e12)
    background_on_panels.append(water)

  rotations = Rotation.random(Nimg, random_state=8675309)
  with H5AttributeGeomWriter(master_out, image_shape=img_sh, num_images=Nimg, detector=detector, beam=beam,
                             dtype=np.float64, compression_args=None) as writer:

    for i_img in range(Nimg):
      output_panels = []
      for pidx in range(len(detector)):
        if pidx == 0:
          show_params = True
        else:
          show_params = False
        R = rotations[i_img].as_dcm()
        A = np.dot(R,real_a)
        B = np.dot(R,real_b)
        C = np.dot(R,real_c)
        crystal = Crystal(A,B,C, lookup_symbol)
        panel_pixels = sim_spots(crystal, detector, beam, Famp, wavelengths, weights, pidx=pidx, crystal_size_mm=0.050,
                           beam_size_mm=0.001, total_flux=1e12, time_panels=True, show_params=show_params, cuda=USE_CUDA,
                           mosaic_vol_A3=2000**3, profile="gauss", background_raw_pixels=background_on_panels[pidx])
        output_panels.append(panel_pixels)
      output_panels = np.array(output_panels)

      writer.add_image(output_panels)
