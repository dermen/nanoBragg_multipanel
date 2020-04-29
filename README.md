## Installation
----
This package depends on CCTBX, DXTBX, and DIALS

To install CCTBX, DXTBX and DIALS one needs to create an install folder, and go there

```
export XTAL=$HOME/Crystal # install 
mkdir $XTAL
cd $XTAL
```

and then download the cctbx bootrap script which auto installs a lot of packages, including CCTBX, DXTBX, and DIALS

```
wget https://raw.githubusercontent.com/cctbx/cctbx_project/master/libtbx/auto_build/bootstrap.py
```

### check for cuda

We will try to build using nvcc so that we can run nanoBragg on the GPU. To do that, after setting up CUDA on your machine you need to specify where cuda libraries and tools (e.g. nvcc, nvidia-smi) are located. This usually amounts to 

```
export PATH=/usr/local/cuda-10.1/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/cuda-10.1/lib64
```

Before building for GPU-use you should be able to do

```
nvidia-smi -a
```

and see the GPU device(s) listed on your current node. Usually its a good idea to also try running some of the cuda sample scripts, e.g.

```
cd /usr/local/cuda-10.1/samples/1_Utilities/deviceQuery
make
./deviceQuery
```

If you are working on a cluster, you might simply just have to ```module load cuda``` and let all your cuda woes vanish. 


### Run Bootstrap
Next we can run bootstrap. First use bootstrap to pull in CCTBX+DIALS+DXTBX specific modules

```
python bootstrap.py hot update --builder=dials
```

You will see a modules folder now in ```$XTAL/modules```. This above command can routinely be run to bring in updates, though you can also go to specific module folders and run ```git pull``` for any updates.  Next we need to build a python environment and for that we use conda (usually bootstrap can also do this, but it tries to be sneaky and find hidden condas you might not want it to use, so the most fool proof installation method is as follows):

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
```

Follow the onscreen instructions, elect to install conda somewhere convenient. I let conda build in ```$XTAL/newconda3``` for example. Then with the new conda, create the cctbx environment we will be using by providing the path to an environment file located in the dials repository

```
source ~/newconda3/etc/profile.d/conda.sh
conda create --name cctbx --file modules/dials/.conda-envs/dials_py36_linux-64.txt
cd $XTAL
python bootstrap.py  build --use_conda=./newconda3/envs/cctbx/ --builder=dials --nproc=12 --config-flags='--enable_cuda'
```

And thats it for the build. It might take a while.  

### Using the build

Whenever you want to use cctbx,dials, or dxtbx you just need to set your environment with the magic script

```
source $XTAL/build/setpaths.sh
```

This will add a lot of programs to your path. Notably it will add ```libtbx.python``` which is a wrapper script pointing to your cctbx python installation. You can now write python scripts using cctbx/dials/dxtbx libraries and run them with libtbx.python.

## Run the multi panel code 
---
The next step is to clone this repo into the modules folder

```
cd $XTAL/modules
git clone https://github.com/dermen/nanoBragg_multipanel.git

# install the multi panel format class for using dials image viewer to read multi panel hdf5
cd nanoBragg_multipanel
dxtbx.install_format -u format/FormatHDF5AttributeGeometry.py 

# install dependencies for reading crystfel geometry files
libtbx.python -m pip install cfelpyutils --user
```

Now we can simulate Jungfrau images

```
cd $XTAL/modules/nanoBragg_multipanel/
libtbx.python examples.py

dials.image_viewer jungfrau_images.h5

libtbx.python examples.py --model eiger
dials.image_viewer eiger_images.h5
```

I hope the script provides a good example of how to simulate multi panel setups! You can use cuda by adding the argument ```--cuda```, though speed ups may not be noticable until you switch on mosacitiy divergence etc.  Eiger sim takes longer I think because the eiger model includes a thickness.


### Optional: ipython

You can install it along with jupyter

```
libtbx.python -m pip install jupyter
libtbx.refresh 

# launch an interactive session
libtbx.ipython --pylab
```

### Optional: pycharm

Download the community edition pycharm and when you install it create a new project with the ```$XTAL/modules``` folder as root.
Choose as your python interpreter ```$XTAL/build/bin/python```. It won't be perfect, but it will index a lot of the code so you can then work with libtbx in an IDE.  