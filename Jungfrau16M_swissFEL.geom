; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; Optimized panel offsets can be found at the end of the file
; adu_per_eV = 0.0001104
adu_per_eV = 0.1104
res = 13333.3
clen = 0.0986
photon_energy = 9060
max_adu = 250000

dim0 = %
dim1 = ss
dim2 = fs
data = /data/data

rigid_group_quad0 = m0,m4,m8,m12,m1,m5,m9,m13
rigid_group_quad1 = m2,m6,m10,m14,m3,m7,m11,m15
rigid_group_quad2 = m16,m20,m24,m28,m17,m21,m25,m29
rigid_group_quad3 = m18,m22,m26,m30,m19,m23,m27,m31
rigid_group_collection_quads = quad0,quad1,quad2,quad3


mask_file = /das/work/p17/p17592/res/20181201/biglyso/lyso039/lyso039_0143.JF07T32V01.mask.h5
mask = /mask
mask_good = 0x1
mask_bad = 0x0

;square in the center
;badregionB/min_x = -110
;badregionB/max_x = 120
;badregionB/min_y = -110
;badregionB/max_y = 120

m0/min_fs = 0
m0/min_ss = 0
m0/max_fs = 1029
m0/max_ss = 513
m0/fs = -0.999998x -0.001781y
m0/ss = -0.001781x +0.999998y
m0/corner_x = 2022.32
m0/corner_y = -2198.11

m1/min_fs = 0
m1/min_ss = 514
m1/max_fs = 1029
m1/max_ss = 1027
m1/fs = -0.999997x -0.002121y
m1/ss = -0.002121x +0.999997y
m1/corner_x = 992.161
m1/corner_y = -2200.14

m2/min_fs = 0
m2/min_ss = 1028
m2/max_fs = 1029
m2/max_ss = 1541
m2/fs = -0.999998x +0.000986y
m2/ss = +0.000986x +0.999998y
m2/corner_x = -43.7436
m2/corner_y = -2134.68

m3/min_fs = 0
m3/min_ss = 1542
m3/max_fs = 1029
m3/max_ss = 2055
m3/fs = -0.999999x -0.000023y
m3/ss = -0.000023x +0.999999y
m3/corner_x = -1072.89
m3/corner_y = -2126.52

m4/min_fs = 0
m4/min_ss = 2056
m4/max_fs = 1029
m4/max_ss = 2569
m4/fs = -0.999997x -0.001616y
m4/ss = -0.001616x +0.999997y
m4/corner_x = 2027.5
m4/corner_y = -1656.53

m5/min_fs = 0
m5/min_ss = 2570
m5/max_fs = 1029
m5/max_ss = 3083
m5/fs = -0.999999x +0.000000y
m5/ss = +0.000000x +0.999999y
m5/corner_x = 991.301
m5/corner_y = -1657.26

m6/min_fs = 0
m6/min_ss = 3084
m6/max_fs = 1029
m6/max_ss = 3597
m6/fs = -0.999997x +0.001963y
m6/ss = +0.001963x +0.999997y
m6/corner_x = -44.1869
m6/corner_y = -1593.78

m7/min_fs = 0
m7/min_ss = 3598
m7/max_fs = 1029
m7/max_ss = 4111
m7/fs = -0.999999x +0.000563y
m7/ss = +0.000563x +0.999999y
m7/corner_x = -1075.85
m7/corner_y = -1586.96

m8/min_fs = 0
m8/min_ss = 4112
m8/max_fs = 1029
m8/max_ss = 4625
m8/fs = -0.999994x +0.003516y
m8/ss = +0.003516x +0.999994y
m8/corner_x = 2030.76
m8/corner_y = -1114.75

m9/min_fs = 0
m9/min_ss = 4626
m9/max_fs = 1029
m9/max_ss = 5139
m9/fs = -0.999999x +0.000026y
m9/ss = +0.000026x +0.999999y
m9/corner_x = 995.061
m9/corner_y = -1114.39

m10/min_fs = 0
m10/min_ss = 5140
m10/max_fs = 1029
m10/max_ss = 5653
m10/fs = -0.999999x +0.000697y
m10/ss = +0.000697x +0.999999y
m10/corner_x = -44.8018
m10/corner_y = -1047.08

m11/min_fs = 0
m11/min_ss = 5654
m11/max_fs = 1029
m11/max_ss = 6167
m11/fs = -0.999999x +0.000646y
m11/ss = +0.000646x +0.999999y
m11/corner_x = -1079.09
m11/corner_y = -1041.56

m12/min_fs = 0
m12/min_ss = 6168
m12/max_fs = 1029
m12/max_ss = 6681
m12/fs = -0.999994x +0.002795y
m12/ss = +0.002795x +0.999994y
m12/corner_x = 2032.79
m12/corner_y = -566.903

m13/min_fs = 0
m13/min_ss = 6682
m13/max_fs = 1029
m13/max_ss = 7195
m13/fs = -0.999999x +0.000247y
m13/ss = +0.000247x +0.999999y
m13/corner_x = 996.264
m13/corner_y = -565.896

m14/min_fs = 0
m14/min_ss = 7196
m14/max_fs = 1029
m14/max_ss = 7709
m14/fs = -0.999998x +0.000704y
m14/ss = +0.000704x +0.999998y
m14/corner_x = -43.1554
m14/corner_y = -497.074

m15/min_fs = 0
m15/min_ss = 7710
m15/max_fs = 1029
m15/max_ss = 8223
m15/fs = -0.999997x +0.001816y
m15/ss = +0.001816x +0.999997y
m15/corner_x = -1081.96
m15/corner_y = -496.396

m16/min_fs = 0
m16/min_ss = 8224
m16/max_fs = 1029
m16/max_ss = 8737
m16/fs = -0.999999x +0.000610y
m16/ss = +0.000610x +0.999999y
m16/corner_x = 2100.54
m16/corner_y = -15.9363

m17/min_fs = 0
m17/min_ss = 8738
m17/max_fs = 1029
m17/max_ss = 9251
m17/fs = -0.999999x -0.000592y
m17/ss = -0.000592x +0.999999y
m17/corner_x = 1065.72
m17/corner_y = -14.2014

m18/min_fs = 0
m18/min_ss = 9252
m18/max_fs = 1029
m18/max_ss = 9765
m18/fs = -0.999999x -0.000388y
m18/ss = -0.000388x +0.999999y
m18/corner_x = 24.8796
m18/corner_y = 52.8116

m19/min_fs = 0
m19/min_ss = 9766
m19/max_fs = 1029
m19/max_ss = 10279
m19/fs = -0.999997x +0.002101y
m19/ss = +0.002101x +0.999997y
m19/corner_x = -1012.48
m19/corner_y = 51.1795

m20/min_fs = 0
m20/min_ss = 10280
m20/max_fs = 1029
m20/max_ss = 10793
m20/fs = -0.999999x +0.000008y
m20/ss = +0.000008x +0.999999y
m20/corner_x = 2099.44
m20/corner_y = 533.32

m21/min_fs = 0
m21/min_ss = 10794
m21/max_fs = 1029
m21/max_ss = 11307
m21/fs = -0.999999x -0.001464y
m21/ss = -0.001464x +0.999999y
m21/corner_x = 1064.87
m21/corner_y = 536.031

m22/min_fs = 0
m22/min_ss = 11308
m22/max_fs = 1029
m22/max_ss = 11821
m22/fs = -0.999992x -0.003689y
m22/ss = -0.003689x +0.999992y
m22/corner_x = 25.1571
m22/corner_y = 604.111

m23/min_fs = 0
m23/min_ss = 11822
m23/max_fs = 1029
m23/max_ss = 12335
m23/fs = -0.999999x -0.000659y
m23/ss = -0.000659x +0.999999y
m23/corner_x = -1010.83
m23/corner_y = 599.081

m24/min_fs = 0
m24/min_ss = 12336
m24/max_fs = 1029
m24/max_ss = 12849
m24/fs = -0.999990x -0.004207y
m24/ss = -0.004207x +0.999990y
m24/corner_x = 2097.03
m24/corner_y = 1083.26

m25/min_fs = 0
m25/min_ss = 12850
m25/max_fs = 1029
m25/max_ss = 13363
m25/fs = -0.999994x -0.002979y
m25/ss = -0.002979x +0.999994y
m25/corner_x = 1062.42
m25/corner_y = 1084.48

m26/min_fs = 0
m26/min_ss = 13364
m26/max_fs = 1029
m26/max_ss = 13877
m26/fs = -0.999976x -0.006709y
m26/ss = -0.006709x +0.999976y
m26/corner_x = 25.2952
m26/corner_y = 1151.75

m27/min_fs = 0
m27/min_ss = 13878
m27/max_fs = 1029
m27/max_ss = 14391
m27/fs = -0.999996x -0.002079y
m27/ss = -0.002079x +0.999996y
m27/corner_x = -1009.47
m27/corner_y = 1144.77

m28/min_fs = 0
m28/min_ss = 14392
m28/max_fs = 1029
m28/max_ss = 14905
m28/fs = -0.999999x -0.000823y
m28/ss = -0.000823x +0.999999y
m28/corner_x = 2090.9
m28/corner_y = 1622.26

m29/min_fs = 0
m29/min_ss = 14906
m29/max_fs = 1029
m29/max_ss = 15419
m29/fs = -0.999982x -0.005881y
m29/ss = -0.005881x +0.999982y
m29/corner_x = 1059.89
m29/corner_y = 1629.16

m30/min_fs = 0
m30/min_ss = 15420
m30/max_fs = 1029
m30/max_ss = 15933
m30/fs = -0.999975x -0.007006y
m30/ss = -0.007006x +0.999975y
m30/corner_x = 24.3374
m30/corner_y = 1693.61

m31/min_fs = 0
m31/min_ss = 15934
m31/max_fs = 1029
m31/max_ss = 16447
m31/fs = -0.999987x -0.004798y
m31/ss = -0.004798x +0.999987y
m31/corner_x = -1005.55
m31/corner_y = 1685.53




m0/coffset = -0.000294
m1/coffset = -0.000294
m2/coffset = -0.000294
m3/coffset = -0.000294
m4/coffset = -0.000294
m5/coffset = -0.000294
m6/coffset = -0.000294
m7/coffset = -0.000294
m8/coffset = -0.000294
m9/coffset = -0.000294
m10/coffset = -0.000294
m11/coffset = -0.000294
m12/coffset = -0.000294
m13/coffset = -0.000294
m14/coffset = -0.000294
m15/coffset = -0.000294
m16/coffset = -0.000294
m17/coffset = -0.000294
m18/coffset = -0.000294
m19/coffset = -0.000294
m20/coffset = -0.000294
m21/coffset = -0.000294
m22/coffset = -0.000294
m23/coffset = -0.000294
m24/coffset = -0.000294
m25/coffset = -0.000294
m26/coffset = -0.000294
m27/coffset = -0.000294
m28/coffset = -0.000294
m29/coffset = -0.000294
m30/coffset = -0.000294
m31/coffset = -0.000294

