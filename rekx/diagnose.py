"""Docstring for the diagnose.py module.

Functions to inspect the metadata, the structure
and specifically diagnose and validate
the chunking shapes of NetCDF files.
"""

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Tuple

import xarray as xr

from .log import logger
from .models import (
    XarrayVariableSet,
    select_xarray_variable_set_from_dataset,
)


def detect_chunking_shapes(
    file_path: Path,
    variable_set: XarrayVariableSet = XarrayVariableSet.all,
    # ) -> Tuple[Dict[str, Set[int]], str]:
) -> Tuple[Dict, str]:
    """
    Detect the chunking shapes of variables within single NetCDF file.

    Parameters
    ----------
    file_path: Path
        Path to input file
    variable_set: XarrayVariableSet
        Name of the set of variables to query. See also docstring of
        XarrayVariableSet

    Returns
    -------
    Tuple[Dict, str]
    # Tuple[Dict[str, Set[int]], str]
        A tuple containing a dictionary `chunking_shape` and the name of the
        input file. The nested dictionary's first level keys are variable names,
        and the second level keys are the chunking shapes encountered, with the
        associated values being sets of file names where those chunking shapes
        are found.

    Raises
    ------
    FileNotFoundError
        If the specified NetCDF file does not exist.

    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    chunking_shapes = {}
    with xr.open_dataset(file_path, engine="netcdf4") as dataset:
        selected_variables = select_xarray_variable_set_from_dataset(
            netcdf4_variable_set=XarrayVariableSet,
            variable_set=variable_set,
            dataset=dataset,
        )
        for variable in selected_variables:
            chunking_shape = dataset[variable].encoding.get("chunksizes")
            if chunking_shape and chunking_shape != "contiguous":
                # Review Me ! ----------------------
                # if variable not in chunking_shapes:
                #     chunking_shapes[variable] = set()
                # Review Me ! ----------------------

                chunking_shapes[variable] = chunking_shape

                # Review Me ! ----------------------
                # chunking_shapes[variable].add(tuple(chunking_shape))
                # Review Me ! ----------------------

    return chunking_shapes, file_path.name


def detect_chunking_shapes_parallel(
    file_paths: List[Path],
    variable_set: XarrayVariableSet = XarrayVariableSet.all,
) -> dict:
    """Detect the chunking shapes of variables in NetCDF files.

    Detect and aggregate the chunking shapes of variables within a set of
    multiple NetCDF files in parallel.

    Parameters
    ----------
    file_paths: List[Path]
        A list of file paths pointing to the NetCDF files to be scanned.

    Returns
    -------
    dict
        A nested dictionary where the first level keys are variable names, and the
        second level keys are the chunking shapes encountered, with the associated
        values being sets of file names where those chunking shapes are found.

    """
    aggregated_chunking_shapes = {}
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(detect_chunking_shapes, file_path, variable_set.value)
            for file_path in file_paths
        ]

        for future in as_completed(futures):
            try:
                chunking_shapes, file_name = future.result()
                logger.info(f"Scanned file: {file_name}")

                for variable, chunking_shape in chunking_shapes.items():
                    if variable not in aggregated_chunking_shapes:
                        aggregated_chunking_shapes[variable] = {}
                        logger.info(
                            f"Initial chunk sizes set for {variable} in {file_name}"
                        )
                    if chunking_shape not in aggregated_chunking_shapes[variable]:
                        aggregated_chunking_shapes[variable][chunking_shape] = set()
                        logger.info(
                            f"New chunking shape {chunking_shape} found for variable {variable} in {file_name}"
                        )
                    aggregated_chunking_shapes[variable][chunking_shape].add(file_name)

            except Exception as e:
                logger.error(f"Error processing file: {e}")

    return aggregated_chunking_shapes
