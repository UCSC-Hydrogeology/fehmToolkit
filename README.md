# FEHM Toolkit
This toolkit consists of utilities and convenience functions to enable fast and efficient use of [FEHM](https://github.com/lanl/FEHM) and [LaGriT](https://github.com/lanl/LaGriT), which are software packages created by Los Alamos National Labs for simulations of coupled fluid-heat-solute transport and related processes. The specific focus of the FEHM Toolkit is on simulations of seafloor hydrothermal circulation.   

## Work in progress
This toolkit is in the early stages of development and is not yet in working order. This page will be updated when an initial release is ready. Work to date is focused on collating and testing previous Matlab versions of the code.

## Installation and use
TODO: complete this section when we have basic working functionality on some of the tools.

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
