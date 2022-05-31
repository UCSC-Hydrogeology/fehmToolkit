from pathlib import Path


def read_nist_lookup_table(nist_file: Path) -> dict[tuple[float, float], dict[str, float]]:
    """Reads a NIST whitespace-delimited lookup table of fluid properties.

    This returns a dictionary of (P, T) to properties, where the key is in units of MPa and degrees C, respectively.
    """
    # TODO(dustin): add support for reading additional fluid properties as required

    properties_lookup_MPa_degC = {}
    with open(nist_file) as f:
        for line in f:
            pressure, temperature, density = (float(v) for v in line.strip().split()[:3])
            properties_lookup_MPa_degC[(pressure, temperature)] = {
                'density_kg_m3': density,
            }
    return properties_lookup_MPa_degC
