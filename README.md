# FEHM Toolkit
This toolkit consists of utilities and convenience functions to enable fast and efficient use of [FEHM](https://github.com/lanl/FEHM) and [LaGriT](https://github.com/lanl/LaGriT), which are software packages created by Los Alamos National Labs for simulations of coupled fluid-heat-solute transport and related processes.

This toolkit abstracts away most manual file copying and editing associated with setting up FEHM runs, supports assigning properties, initial conditions, and boundary conditions for runs, and streamlines post-run model analysis. All of this is managed in a single configuration file within each run directory (#configuration), and accessed as a command-line tool (#usage).

The specific focus of the FEHM Toolkit is on simulations of seafloor hydrothermal circulation, though it can be used in other contexts and even modified to better support other use-cases as the need arises.

## Work in progress
* This toolkit is in the early stages of development and is not yet in working order.
* Work to date is focused on collating and testing previous Matlab versions of the code.
* This page will be updated when an initial release is ready.

## Usage
After installing the package (#installation), you can invoke commands directly using `fehmtk`:
```zsh
fehmtk --help
```

An sample workflow looks like this:
1. Create a new FEHM run directory from the grid found in `my_mesh` (previously created by LaGriT):
```zsh
fehmtk run_from_mesh my_mesh my_run ../nist120-1800.out --run_root run_1
```
1. Update `my_run/config.yaml` (see #configuration)
1. Run utilities to generate properties and boundary conditions:
```zsh
fehmtk rock_properties my_run/config.yaml
fehmtk heat_in my_run/config.yaml --plot
```
1. Update `my_run/run_1.dat` to configure your FEHM run
1. Run FEHM

## Installation
We recommend installing as an editable package for both development and use of the toolkit.

1. Install a system for managing virual environments. [Anaconda](https://www.anaconda.com/products/distribution#Downloads) or the lighter-weight [Miniconda](https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links) are recommended, but you can use whatever you prefer.
1. Create a new virtual environment (unless you want to install into an existing one):

    ```zsh
    conda create -n fehmtk python=3.9
    ```

1. Clone the repository to your local code directory (`~/code` in this case):

    ```zsh
    cd ~/code
    git clone git@github.com:UCSC-Hydrogeology/fehmToolkit.git
    ```

1. Install the toolkit into your environment:

    ```zsh
    conda activate fehmtk
    cd fehmToolkit
    pip install -e ".[all]"
    ```

1. Run the tests to check everything is set up correctly:

    ```zsh
    pytest
    ```

1. Start using the toolkit:

    ```zsh
    fehmtk --help
    ```

## Configuration
--- TODO clean this up
Yaml format, all in one place, some overlap with FEHM configuration, sync utility to handle that, manual editing of .dat required
