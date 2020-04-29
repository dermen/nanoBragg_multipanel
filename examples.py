from __future__ import print_function

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("--cuda", action="store_true", help="try to simulate with cuda")
parser.add_argument("--model", choices=["jungfrau", "eiger", "eigermono"], type=str, default="jungfrau", help="eiger mono is a single panel eiger")
args = parser.parse_args()

import numpy as np
from scipy.spatial.transform.rotation import Rotation
try:
  from cfelpyutils.crystfel_utils import load_crystfel_geometry
except ImportError:
  print("You must first install cfelpyutils using `libtbx.python -m pip install cfelpyutils --user`")
  exit()
from dxtbx.model import Beam, Crystal
from nanoBragg_multipanel.jungfrau16M import convert_crystfel_to_dxtbx, load_detector_from_expt
from nanoBragg_multipanel.utils import sim_spots, sim_background, H5AttributeGeomWriter

imgfile_out = "%s_images.h5" % args.model

if args.model.startswith('eiger'):
  from nanoBragg_multipanel.eiger16M import get_multi_panel_eiger
  if args.model.endswith("mono"):
    detector = get_multi_panel_eiger(as_single_panel=True)
  else:
    detector= get_multi_panel_eiger()
else:  # elif args.model == "jungfrau":
  input_file = "Jungfrau16M_swissFEL.geom"
  output_file = input_file.replace(".geom", ".expt")  # this file will store dxtbx detector
  convert_crystfel_to_dxtbx(input_file, output_file, detdist_override=250)  # override the detector distance (mm)
  # get the detector
  detector = load_detector_from_expt(output_file)

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

if args.model=='eigermono':
  # NOTE if doing a monolithic eiger you might want to put the gaps as untrusted values
  import h5py
  is_a_gap = h5py.File("eiger_gaps.h5", "r")["is_a_gap"][()]  # use this mask

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
      if args.model.startswith("eiger"):
        readout_adu = 0
      else:
        readout_adu = 3

      panel_pixels = sim_spots(crystal, detector, beam, Famp, wavelengths, weights, pidx=pidx, crystal_size_mm=0.050,
                         beam_size_mm=0.001, total_flux=1e12, time_panels=True, show_params=show_params, cuda=args.cuda,
                         mosaic_vol_A3=2000**3, profile="gauss", background_raw_pixels=background_on_panels[pidx],
                        readout_noise_adu=readout_adu)
      if args.model == "eigermono":
        panel_pixels[is_a_gap] = -1

      output_panels.append(panel_pixels)

    # save the image to hdf5
    output_panels = np.array(output_panels)
    writer.add_image(output_panels)
