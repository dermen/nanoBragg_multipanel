
import time
import numpy as np
from scipy import constants
import json
import h5py
import numpy as np

#import simtbx
#shapetype = simtbx.nanoBragg.shapetype
from simtbx.nanoBragg import shapetype
from simtbx.nanoBragg import nanoBragg
from scitbx.array_family import flex
from dxtbx_model_ext import flex_Beam
from dxtbx.model import BeamFactory


ENERGY_CONV = 1e10*constants.c*constants.h / constants.electron_volt


def sim_background(DETECTOR, BEAM,wavelengths, wavelength_weights,
                   total_flux, pidx=0, beam_size_mm=0.001,
                   Fbg_vs_stol=None, sample_thick_mm=100, density_gcm3=1,
                   molecular_weight=18):
    wavelength_weights = np.array(wavelength_weights)
    weights = (wavelength_weights / wavelength_weights.sum()) * total_flux
    spectrum = list(zip(wavelengths, weights))
    xray_beams = get_xray_beams(spectrum, BEAM)


    SIM = nanoBragg(DETECTOR, BEAM, panel_id=int(pidx))
    SIM.beamsize_mm = beam_size_mm
    SIM.xray_beams = xray_beams
    if Fbg_vs_stol is None:
        Fbg_vs_stol = flex.vec2_double(
        [(0, 2.57), (0.0365, 2.58), (0.07, 2.8), (0.12, 5), (0.162, 8), (0.2, 6.75), (0.18, 7.32),
         (0.216, 6.75), (0.236, 6.5), (0.28, 4.5), (0.3, 4.3), (0.345, 4.36), (0.436, 3.77), (0.5, 3.17)])
    SIM.flux = total_flux
    SIM.Fbg_vs_stol = Fbg_vs_stol
    SIM.amorphous_sample_thick_mm = sample_thick_mm
    SIM.amorphous_density_gcm3 = density_gcm3
    SIM.amorphous_molecular_weight_Da = molecular_weight
    SIM.progress_meter = False
    SIM.add_background() #1, 0)
    background_raw_pixels = SIM.raw_pixels.deep_copy()
    SIM.free_all()
    del SIM
    return background_raw_pixels


def sim_spots(
        CRYSTAL, DETECTOR, BEAM, Famp, wavelengths,
        wavelength_weights, total_flux, pidx=0, cuda=False, oversample=0,
        mosaic_vol_A3=3000**3, mos_dom=1, mos_spread=0, profile=None,
        crystal_size_mm=0.01, beam_size_mm=0.001, device_Id=0,
        show_params=False,  printout_pix=None, time_panels=True,
        verbose=0, default_F=0, interpolate=0,
        noise_seed=None, calib_seed=None, mosaic_seed=None,
        recenter=True, spot_scale_override=None, add_noise=True,
        adc_offset=10, readout_noise_adu=3,gain=1,
        background_raw_pixels=None, background_scale=1):

    assert len(wavelengths) == len(wavelength_weights)

    wavelength_weights = np.array(wavelength_weights)
    weights = (wavelength_weights / wavelength_weights.sum()) * total_flux
    spectrum = list(zip(wavelengths, weights))
    xray_beams = get_xray_beams(spectrum, BEAM)

    tinit = time.time()
    SIM = nanoBragg(DETECTOR, BEAM,
                verbose=verbose, panel_id=int(pidx))

    if profile is not None:
        if profile == "gauss":
            SIM.xtal_shape = shapetype.Gauss
        elif profile == "tophat":
            SIM.xtal_shape = shapetype.Tophat
        elif profile == "round":
            SIM.xtal_shape = shapetype.Round
        elif profile == "square":
            SIM.xtal_shape = shapetype.Square

    if recenter:
        SIM.beam_center_mm = DETECTOR[int(pidx)].get_beam_centre(BEAM.get_s0())

    if printout_pix is not None:
        SIM.printout_pixel_fastslow = printout_pix

    if noise_seed is not None:
        SIM.seed = noise_seed
    if calib_seed is not None:
        SIM.calib_seed = calib_seed
    if mosaic_seed is not None:
        SIM.mosaic_seed = mosaic_seed

    SIM.exposure_s = 1

    SIM.interpolate = interpolate

    # Crystal properties
    Nunit_cell = mosaic_vol_A3 / CRYSTAL.get_unit_cell().volume()
    N = np.power(Nunit_cell, 1/3.)
    SIM.Ncells_abc = int(N), int(N), int(N)
    SIM.mosaic_spread_deg = mos_spread
    SIM.mosaic_domains = mos_dom
    SIM.Fhkl = Famp  # setting Fhkl property overrides unit cell, so we should do this before setting Amatrix
    SIM.Amatrix = Amatrix_dials2nanoBragg(CRYSTAL)  # Amatrix takes priority for unit cell
    SIM.spot_scale = determine_spot_scale(beam_size_mm, crystal_size_mm, mosaic_vol_A3)
    if spot_scale_override is not None:
        SIM.spot_scale = spot_scale_override

    # Beam properties
    SIM.xray_beams = xray_beams
    SIM.beamsize_mm = beam_size_mm
    SIM.flux = total_flux

    SIM.default_F = default_F

    if cuda:
        SIM.device_Id = int(device_Id)

    if oversample > 0:
        SIM.oversample = oversample

    if cuda:
        SIM.add_nanoBragg_spots_cuda()
    else:
        SIM.add_nanoBragg_spots()

    if show_params:
        SIM.show_params()
        print("Mosaic domain volume: %2.7g (mm^3)" % mosaic_vol_A3)
        print("spot scale: %2.7g" % SIM.spot_scale)

    if cuda:
        SIM.raw_pixels /= len(wavelengths) #panel_image /= len(energies)

    if background_raw_pixels is not None:
        SIM.raw_pixels += background_raw_pixels*background_scale

    if add_noise:
        SIM.adc_offset_adu = adc_offset
        SIM.detector_psf_fwhm_mm = 0
        SIM.quantum_gain = gain
        SIM.readout_noise_adu = readout_noise_adu
        SIM.add_noise()

    raw_pixels = SIM.raw_pixels.as_numpy_array()
    SIM.free_all()
    if time_panels:
        tdone = time.time()-tinit
        print("Panel %d took %.4f seconds" % (pidx, tdone))
    del SIM
    return raw_pixels


def determine_spot_scale(beam_size_mm, crystal_thick_mm, mosaic_vol_A3):
    if beam_size_mm <= crystal_thick_mm:
        illum_xtal_vol = crystal_thick_mm * beam_size_mm**2
    else:
        illum_xtal_vol = crystal_thick_mm**3
    return illum_xtal_vol / mosaic_vol_A3 * (1e21)


def get_xray_beams(spectrum, beam_originator):
    xray_beams = flex_Beam()
    for wavelen, flux in spectrum:
        beam = BeamFactory.simple(wavelen*1e-10)
        beam.set_flux(flux)
        beam.set_unit_s0(beam_originator.get_unit_s0())
        beam.set_polarization_fraction(beam_originator.get_polarization_fraction())
        beam.set_divergence(beam_originator.get_divergence())
        xray_beams.append(beam)

    return xray_beams


def Amatrix_dials2nanoBragg(crystal):
    """
    returns the A matrix from a cctbx crystal object
    in nanoBragg frormat
    :param crystal: cctbx crystal
    :return: Amatrix as a tuple
    """
    Amatrix = tuple(np.array(crystal.get_A()).reshape((3, 3)).T.ravel())
    return Amatrix


class H5AttributeGeomWriter:

    def __init__(self, filename, image_shape, num_images, detector, beam, dtype=None,
                 compression_args=None, detector_and_beam_are_dicts=False):
        """
        Simple class for writing dxtbx compatible HDF5 files

        :param filename:  input file path
        :param image_shape: shape of a single image (Npanel x Nfast x Nslow)
        :param num_images: how many images will you be writing to the file
        :param detector: dxtbx detector model
        :param beam: dxtbx beam model
        :param dtype: datatype for storage
        :param compression_args: compression arguments for h5py, lzf is performant and simple
            if you only plan to read file in python
            Examples:
              compression_args={"compression": "lzf"}  # Python only
              comression_args = {"compression": "gzip", "compression_opts":9}
        :param detector_and_beam_are_dicts:
        """
        if compression_args is None:
            compression_args = {}

        self.file_handle = h5py.File(filename, 'w')
        self.beam = beam
        self.detector = detector
        self.detector_and_beam_are_dicts = detector_and_beam_are_dicts
        if dtype is None:
            dtype = np.float64
        dset_shape = (num_images,) + tuple(image_shape)
        self.image_dset = self.file_handle.create_dataset(
            "images", shape=dset_shape,
            dtype=dtype, **compression_args)

        self._write_geom()
        self._counter = 0

    def add_image(self, image):
        if self._counter >= self.image_dset.shape[0]:  # TODO update dset size feature, which is possible
            raise IndexError("Maximum number of images is %d" % (self.image_dset.shape[0]))
        self.image_dset[self._counter] = image
        self._counter += 1

    def _write_geom(self):
        beam = self.beam
        det = self.detector
        if not self.detector_and_beam_are_dicts:
            beam = beam.to_dict()
            det = det.to_dict()

        self.image_dset.attrs["dxtbx_beam_string"] = json.dumps(beam)
        self.image_dset.attrs["dxtbx_detector_string"] = json.dumps(det)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file_handle.close()

    def __enter__(self):
        return self

    def close_file(self):
        self.file_handle.close()
