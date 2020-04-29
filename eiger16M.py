from dxtbx.model import Detector, Panel
import h5py
import numpy as np
from scipy.ndimage import label


def panelize_eiger(eiger_dxtbx_model, is_a_gap):
  """
  :param eiger_dxtbx_model: dxtbx geometry for the eiger (single node model)
  :param is_a_gap: a 2D numpy array the same shape as the eiger image (4371, 4150)
    True means the pixel is a gap, False means the pixel is a mask
    Make this by loading an eiger image and selecting all pixels that are equal to -1
    is_a_gap = np.array(eiger_image)==-1
  :return: dxtbx multi panel model for eiger 16M
  """
  multiEiger = Detector()
  # we will make a new detector where wach panel has its own origin, but all share the same fast,slow scan directions
  detector_origin = np.array(eiger_dxtbx_model[0].get_origin())
  F = np.array(eiger_dxtbx_model[0].get_fast_axis())
  S = np.array(eiger_dxtbx_model[0].get_slow_axis())
  pixsize = eiger_dxtbx_model[0].get_pixel_size()[0]
  panel_dict = eiger_dxtbx_model[0].to_dict()

  is_a_panel = np.logical_not(is_a_gap)
  labs, nlabs = label(is_a_panel)

  for i in range(nlabs+1):
    region = labs == i
    npixels = np.sum(region)
    # there might be some other connected regions that are not panels (bad regions for example)
    if 200000 < npixels < 530000:  # panel size is 529420 pixels, I think
      ypos, xpos = np.where(region)
      jmin, imin = min(ypos), min(xpos)  # location of first pixel in the region
      jmax, imax = max(ypos), max(xpos)
      panel_shape = (int(imax-imin), int(jmax-jmin))
      panel_origin = detector_origin + F*imin*pixsize + S*jmin*pixsize
      panel_dict["origin"] = tuple(panel_origin)
      panel_dict["image_size"] = panel_shape
      panel = Panel.from_dict(panel_dict)
      multiEiger.add_panel(panel)

  return multiEiger


def get_multi_panel_eiger(detdist_mm=200, pixsize_mm=0.075, as_single_panel=False):
    """

    :param detdist_mm: sample to detector in mm
    :param pixsize_mm: pix in mm
    :param as_single_panel: whether to return as just a large single panel camera
    :return: dxtbx detector
    """
    # load a file specifying the gap positions
    # this is a 2D array
    # usually -1 is a gap, so you can create this array by doing
    # is_a_gap = np.array(eiger_image)==-1  (pseudo)
    is_a_gap = h5py.File("eiger_gaps.h5", "r")["is_a_gap"][()]

    # to view:
    #import pylab as plt
    #plt.imshow( is_a_gap)
    #plt.show()
    # its not perfect, some small regions are also flagged, we shall filter them though

    ydim,xdim = is_a_gap.shape

    center_x = xdim/2. * pixsize_mm
    center_y = ydim/2. * pixsize_mm
    master_panel_dict = {'type': 'SENSOR_PAD',
        'fast_axis': (1.0, 0.0, 0.0),
        'slow_axis': (0.0, -1.0, 0.0),
        'origin': (-center_x, center_y, -detdist_mm),
        'raw_image_offset': (0, 0),
        'image_size': (xdim, ydim),
        'pixel_size': (pixsize_mm, pixsize_mm),  # NOTE this will depend on your model
        'trusted_range': (-1.0, 65535.0),
        'thickness': 0.45,
        'material': 'Si',
        'mu': 3.969545947994824,
        'identifier': '',
        'mask': [],
        'gain': 1.0,
        'pedestal': 0.0,
        'px_mm_strategy': {'type': 'SimplePxMmStrategy'}}

    master_panel = Panel.from_dict(master_panel_dict)
    master_det = Detector()
    master_det.add_panel(master_panel)

    if as_single_panel:
        return master_det
    else:
        return panelize_eiger(master_det, is_a_gap)

