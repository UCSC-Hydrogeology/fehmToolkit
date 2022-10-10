# FEHM Toolkit
This toolkit consists of utilities and convenience functions to enable fast and efficient use of [FEHM](https://github.com/lanl/FEHM) and [LaGriT](https://github.com/lanl/LaGriT), which are software packages created by Los Alamos National Labs for simulations of coupled fluid-heat-solute transport and related processes.

This toolkit abstracts away most manual file copying and editing associated with setting up FEHM runs, supports assigning properties, initial conditions, and boundary conditions for runs, and streamlines post-run model analysis. All of this is managed in a single [configuration file](#configuration) within each run directory, and accessed as a [command-line tool](#usage).

The specific focus of the FEHM Toolkit is on simulations of seafloor hydrothermal circulation, though it can be used in other contexts and even modified to better support other use-cases as the need arises.

## Work in progress
* This toolkit is in the early stages of development and is not yet in working order.
* Work to date is focused on collating and testing previous Matlab versions of the code.
* This page will be updated when an initial release is ready.

## Usage
After [installing the package](#installation), you can invoke commands directly using `fehmtk`:

```zsh
fehmtk --help
fehmtk run_from_run --help
```

An sample workflow looks like this:
1. Create a new FEHM run directory from the grid found in `my_mesh` (previously created by LaGriT):

    ```zsh
    fehmtk run_from_mesh my_mesh my_run ../nist120-1800.out --run_root run_1
    ```

1. Update `my_run/config.yaml` (see [Configuration](#configuration))
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
All of the configuration used by the `fehmtk` for a model run is kept as a single [YAML file](https://yaml.org/spec/1.2.2/#chapter-2-language-overview) (usually `config.yaml`), within the run directory. This provides `fehmtk` with file paths and settings for its various commands, particularly those responsible for property assignment and the specification of initial and boundary conditions.

### Overlap with FEHM configuration
FEHM has its own configuration files, notably the files index (usually `fehmn.files`) and the FEHM input file (often ending in `.dat` or `.txt`). There is some redundancy between the `fehmtk` config and that used by FEHM, and utilities will attempt to keep any shared references aligned when handling these files, such as when making a new model directory. Still, users should take care to ensure that the FEHM config files stay in sync with the `fehmtk` config.

### Specification
The configuration has a number of top-level keys. The `files_config` is shared across utilities, and ensures `fehmtk` has a unified view of files in a given run directory. Other top-level keys pertain to specific utilities; some are optional and some are mandatory. 

A common construction throughout the configuration is a `model`, which consists of both a `kind` and `params`. This allows the relevant utility to take a different set of parameters depending the type of model you want to use.

Example configs can be found in the repository test fixtures, e.g. [here](test/end_to_end/fixtures/outcrop_2d/cond/config.yaml).

#### Files config
Mapping of file kinds to relative paths for each file. Paths are resolved relative to the config file.
```yaml
files_config:
  area: cond.area
  check: cond.chk
  # ...
  water_properties: ../../nist120-1800.out
```
This only shows a few keys, see [files_config.py](fehmtk/config/files_config.py) for full list of keys.

#### Heat flux config
Mapping with a single top level key `heat_flux_model` with a model as a value.
```yaml
heat_flux_config:
  heat_flux_model:
    kind: constant_MW_per_m2
    params:
      constant: 3.67e-07
```

See [heat_flux_models.py](fehmtk/preprocessors/heat_flux_models.py) for a full list of supported models and their required params.

#### Boundaries config
Mapping with a single top level key `flow_configs`, with a list of FlowConfigs as a value:
```yaml
boundaries_config:
  flow_configs:
  - boundary_model:
      kind: 'open_flow'
      params:
        input_fluid_temp_degC: 2
        aiped_to_volume_ratio: 1.0e-08
    outside_zones: ['top']
    material_zones: []  # these can also be omitted if empty (done with outside_zones below)
  - boundary_model:
      kind: 'open_flow'
      params:
        input_fluid_temp_degC: 10
        aiped_to_volume_ratio: 1.0e-08
    material_zones: [1, 2]
```

#### Rock properties config
Mapping with keys for each property config (`compressibility_config`, `conductivity_config`, `permeability_config`, `porosity_config`, `specific_heat_config`), as well as the `zone_assignment_order`. The assignment order can be important in cases where some nodes are members of more than one zone, and for these nodes later zone assignments will overwrite earlier ones.

Property configs contain a list of mappings, each containing a `property_model` and `zones`. This allows flexible specification of property models to one or more zones at a time, for each property.

```yaml
rock_properties_config:
  compressibility_configs:
  - property_model:
      kind: overburden
      params:
        a: 0.09
        grav: 9.81
        min_overburden: 25.0
        rhow: 1000.0
    zones: [1]
  - property_model:
      kind: constant
      params:
        constant: 6.0e-10
    zones: [2]
  # ...
  specific_heat_configs:
  - property_model:
      kind: constant
      params:
        constant: 800.0
    zones:
    - 1
    - 2
  zone_assignment_order: [1, 2]
```

See [property_models](fehmtk/property_models) for a full list of supported models and their required params.

#### Pressure config (optional)
**Note:** The `hydrostatic pressure` utility is considered deprecated. It is recommended to use FEHM itself to compute hydrostatic pressures. (TODO: link to a sample workflow for this)

Mapping with required key for `pressure_model`, and optional keys for `interpolation_model` and `sampling_model`. This config is optional, and can be safely omitted if you do not plan to perform hydrostatic pressure calculations.

```yaml
pressure_config:
  pressure_model:  # required
    kind: depth
    params:
      z_interval_m: 5
      reference_z: 4450
      reference_pressure_MPa: 25
      reference_temperature_degC: 2
  interpolation_model:  # optional
    kind: regular_grid
    params:
      x_samples: 50
      y_samples: 50
      z_samples: 20
  sampling_model:  # optional
    kind: explicit_lists
    params:
      explicit_outside_zones: [top]
      explicit_material_zones: []
      explicit_nodes: []
```

The pressure model controls how the hydrostatic pressure calculation is performed, and is the only required model. By default, this calculation will be done explicitly for all nodes in the model, although note that this can be prohibitively expensive for large grids.

* Defining an `interpolation_model` has the explicit calculation performed on a smaller list of targets (e.g. a regular grid), then interpolate these results for node values.
* Defining a `sampling_model` has this explicit calculation performed only on the nodes or zones specified.
  * If enabled without interpolation, only sampled nodes are included in the calculation.
  * If enabled with interpolation, all remaining nodes are interpolated via the given method.
