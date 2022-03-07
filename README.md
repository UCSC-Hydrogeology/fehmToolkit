# FEHM Toolkit
This toolkit consists of utilities and convenience functions to enable fast and efficient use of [FEHM](https://github.com/lanl/FEHM) and [LaGriT](https://github.com/lanl/LaGriT), which are software packages created by Los Alamos National Labs for simulations of coupled fluid-heat-solute transport and related processes. The specific focus of the FEHM Toolkit is on simulations of seafloor hydrothermal circulation.   

## Work in progress
This toolkit is in the early stages of development and is not yet in working order. This page will be updated when an initial release is ready. Work to date is focused on collating and testing previous Matlab versions of the code.

## Installation and use
We currently only support "development" installations (see section below for instructions).

TODO(dustin): update with documentation for using the toolkit in non-dev mode.

### Heat input
To run the utility for generating heat input (`.hflx`) files, first activate a virtual environment with `fehm_toolkit` installed, then run:
```bash
python -m python -m fehm_toolkit.heat_in --help
```
This will show you the additional parameters you need to specify, for example:
```bash
python -m fehm_toolkit.heat_in --config_file p12.hfi --fehm_file p12.fehm --area_file p12.area --outside_zone_file p12_outside.zone --output_file test.hflx
```

## Development
The toolkit and its dependencies can be installed for development purposes. Simply clone the repository, then run the following commands:

**Important** we strongly recommend installing this into a virtual environment (TODO: provide a link or tutorial explaining how to do this).

```bash
pip install -e ".[all]"
```
After this, run the tests to check everything is running correctly:
```bash
pytest
```
