# HWO General Target Visibility Tool (hwo_gtvt)

HWO requires shielding from the Sun for operation, which limits the available position angles observable at a given time. This script calculates the allowed position angles for a given Right Ascension and Declination for each instrument on the telescope. Currently the only allowed instrument is V3PA.

This is a fork of the JWST General Target Visibility Tool (https://github.com/spacetelescope/jwst_gtvt). This tool parameterizes spacecraft-dependent constants like sun angle and roll.

# Dependencies

This tool requires a few packages:

* astropy

* astroquery (for moving target support)

* docopt

* maplotlib

* numpy

* pysiaf

* pandas

* tabulate

# Installation

You can clone the respository from GitHub and install the tool inside a virtual environment:

	$ python3 -m venv .venv # create virtual environment if you don't have one already
	$ source .venv/bin/activate # or activate.csh, or activate.fish
	$ cd /path/to/jwst_gtvt_hwo # path to repository
	$ pip install .

(The period in the last command is required and is not punctuation.)

# Usage

There are two scripts available: `hwo_gtvt` for fixed targets and `hwo_mtvt` for moving targets. The arguments and options are the same as the JWST General Target Visibility Tool, except the only allowed instrument is V3PA.

# Example

By default you need only specify R.A. and Dec. in either sexigesimal or degrees.
The observability windows will be printed to the terminal and a plot showing the windows for each instrument will pop up.

`$ hwo_gtvt --ra=16:52:58.9 --dec=02:24:03`

`$ hwo_gtvt --ra=253.2458 --dec=2.4008`

# Parameterization

In `/hwo_gtvt/data/`, the `parameters.json` file parameterizes various spacecraft constants. All angles in this file are in degrees. The file currently parameterizes the HWO, based on info from the following paper: https://arxiv.org/pdf/2602.11046.


