import math
from typing import Annotated, List

import numpy as np
import typer
from pydantic import BaseModel, conlist, field_validator

from rekx.typer_parameters import OrderCommands

from .rich_help_panel_names import rich_help_panel_rechunking
from .typer_parameters import typer_argument_variable_shape


class VariableShapeModel(BaseModel):
    variable_shape: conlist(int, min_length=2, max_length=4)

    @field_validator("variable_shape")
    @classmethod
    def validate_shape(cls, value):
        if isinstance(value, str):
            try:
                return list(map(int, value.split(",")))
            except ValueError:
                raise ValueError("Invalid integer in the list")
        return value


# app = typer.Typer(
#     cls=OrderCommands,
#     add_completion=True,
#     add_help_option=True,
#     rich_markup_mode="rich",
#     help=f'Determine a good chunk layout',
# )


def binlist(n, width=0):
    """Return list of bits that represent a non-negative integer.
    n      -- non-negative integer
    width  -- number of bits in returned zero-filled list (default 0)
    """
    return [int(bit) for bit in bin(n)[2:].zfill(width)]


def perturb_shape(shape, on_bits):
    """Return shape perturbed by adding 1 to elements corresponding to 1 bits in on_bits
    shape  -- list of variable dimension sizes
    on_bits -- non-negative integer less than 2**len(shape)
    """
    return [dim + bit for dim, bit in zip(shape, binlist(on_bits, len(shape)))]


def calculate_ideal_number_of_chunks(
    variable_shape: List[int], float_size: int, chunk_size: int
) -> float:
    """Calculate the ideal number of chunks based on the variable shape and chunk size"""
    # ideal_number_of_values = chunk_size / float_size if chunk_size > float_size else 1
    ideal_number_of_values = max(chunk_size // float_size, 1)
    ideal_number_of_chunks = np.prod(variable_shape) / ideal_number_of_values
    return ideal_number_of_chunks


def adjust_first_dimension(
    variable_shape: List[int], number_of_chunks_per_axis: float
) -> float:
    """Adjust the size of the first dimension of the chunk shape"""
    if variable_shape[0] / (number_of_chunks_per_axis**2) < 1:
        return 1.0, number_of_chunks_per_axis / math.sqrt(
            variable_shape[0] / (number_of_chunks_per_axis**2)
        )
    return (
        variable_shape[0] // (number_of_chunks_per_axis**2),
        number_of_chunks_per_axis,
    )


def determine_chunking_shape(
    variable_shape: VariableShapeModel,
    float_size: int = 4,
    chunk_size: int = 4096,
    # dimensions: int = 3,
) -> List[int]:
    """Determine optimal chunk shape for a 3D array.

    Based on Python code and algorithm developed by Russ Rew, posted at
    "Chunking Data: Choosing Shapes",
    https://www.unidata.ucar.edu/blog_content/data/2013/chunk_shape_3D.py
    accessed on 31 October 2023

    Parameters
    ----------
    variable_shape:
        The shape of the 3D array

    float_size:
        Size of a float value in bytes
    chunk_size:
        Maximum allowable chunk size in bytes which cannot be greater
    than the size of the physical block
    dimensions:
        Number of dimensions (should be 3 for a 3D array)

    Returns
    -------
    Optimal chunk shape as a list of integers
    """
    # if verbose:
    #     print(f"Variable Shape: {variable_shape.variable_shape}")

    # Calculate ideal number of chunks
    ideal_number_of_chunks = calculate_ideal_number_of_chunks(
        variable_shape, float_size, chunk_size
    )
    number_of_chunks_per_axis = ideal_number_of_chunks**0.25

    # Initialize the first candidate chunking shape
    first_dimension, number_of_chunks_per_axis = adjust_first_dimension(
        variable_shape, number_of_chunks_per_axis
    )
    first_candidate_chunking_shape = [first_dimension]

    # Factor to increase other dimensions to at least 1 if required
    sizing_factor = 1.0
    for dimension_size in variable_shape[1:]:
        if dimension_size / number_of_chunks_per_axis < 1:
            sizing_factor *= number_of_chunks_per_axis / dimension_size

    # Adjust other dimensions
    for dimension_size in variable_shape[1:]:
        chunking_shape = (
            1.0
            if dimension_size / number_of_chunks_per_axis < 1
            else (sizing_factor * dimension_size) // number_of_chunks_per_axis
        )
        first_candidate_chunking_shape.append(chunking_shape)

    # Fine-tuning to find the best chunk shape
    best_chunk_size = 0
    best_chunking_shape = first_candidate_chunking_shape
    for index in range(8):  # Total number of dimensions is 3, so 2^3 = 8
        # a candidate chunk shape during the fine-tuning process
        candidate_chunking_shape = perturb_shape(first_candidate_chunking_shape, index)
        number_of_values_in_chunk = np.prod(candidate_chunking_shape)
        this_chunk_size = float_size * number_of_values_in_chunk
        if best_chunk_size < this_chunk_size <= chunk_size:
            best_chunk_size = this_chunk_size  # Update best chunk size
            best_chunking_shape = list(candidate_chunking_shape)  # Update best shape

    return list(map(int, best_chunking_shape))


def is_power_of_two(n):
    """Check if a number is a power of two."""
    return (n != 0) and (n & (n - 1) == 0)


def find_nearest_divisor(n, divisors):
    """Find the nearest acceptable divisor for a number."""
    nearest_divisor = min(
        divisors, key=lambda x: abs(x - n) if n % x == 0 else float("inf")
    )
    return nearest_divisor if n % nearest_divisor == 0 else n


def determine_chunking_shape_alternative(
    variable_shape,
    float_size=4,
    chunk_size=4096,
    max_chunks: int = None,
    min_chunk_size: int = None,
    force_power_of_two: bool = False,
    spatial_divisors: List[int] = None,
):
    """
    Determine optimal chunk shape for a variable with additional constraints.

    Parameters
    ----------
    variable_shape : list of int
        The shape of the variable (time, latitude, longitude).
    float_size : int
        Size of a float value in bytes.
    chunk_size : int
        Maximum allowable chunk size in bytes.
    max_chunks : int, optional
        Maximum number of chunks allowed.
    min_chunk_size : int, optional
        Minimum allowable chunk size in bytes.
    force_power_of_two : bool, optional
        Whether to force chunk dimensions to be powers of two.
    spatial_divisors : list of int, optional
        Acceptable divisors for the spatial dimensions.

    Returns
    -------
    list of int
        Optimal chunk shape.

    Examples
    --------
    variable_shape_example = [100, 400, 400]  # Example 3D variable shape
    force_power_of_two_example = True  # Enforce that chunk dimensions are powers of two
    spatial_divisors_example = [2**i for i in range(1, 9)]  # Acceptable spatial divisors
    determine_chunking_shape(
        variable_shape_example,
        force_power_of_two=force_power_of_two_example,
        spatial_divisors=spatial_divisors_example
    )
    """
    # ideal number of chunks
    variable_size = np.prod(variable_shape) * float_size
    ideal_chunk_volume = min(
        chunk_size, variable_size // max_chunks if max_chunks else variable_size
    )
    if min_chunk_size:
        ideal_chunk_volume = max(ideal_chunk_volume, min_chunk_size)

    # initial chunk dimensions without considering power of two or specific divisors
    chunk_dimensions = [
        int(
            np.round(
                (ideal_chunk_volume / (float_size * np.prod(variable_shape[: i + 1])))
                ** (1 / (len(variable_shape) - i))
            )
        )
        for i in range(len(variable_shape))
    ]
    chunk_dimensions = [
        max(1, min(dim, variable_shape[i])) for i, dim in enumerate(chunk_dimensions)
    ]

    # Adjust dimensions to meet power of two constraint
    if force_power_of_two:
        chunk_dimensions = [2 ** int(np.log2(dim)) for dim in chunk_dimensions]

    # Adjust spatial dimensions to meet specific divisors constraint
    if spatial_divisors:
        for i in range(1, len(variable_shape)):
            chunk_dimensions[i] = find_nearest_divisor(
                variable_shape[i], spatial_divisors
            )

    # Ensure that the chunk size is within the limits
    chunk_volume = np.prod(chunk_dimensions) * float_size
    while chunk_volume > chunk_size and any(dim > 1 for dim in chunk_dimensions):
        for i in range(len(chunk_dimensions)):
            if chunk_dimensions[i] > 1:
                chunk_dimensions[i] //= 2
                break
        chunk_volume = np.prod(chunk_dimensions) * float_size

    # Ensure chunk dimensions do not exceed the variable dimensions
    chunk_dimensions = [
        min(dim, variable_shape[i]) for i, dim in enumerate(chunk_dimensions)
    ]

    # Ensure the total number of chunks does not exceed max_chunks if set
    if max_chunks:
        while (
            np.prod(np.ceil(np.array(variable_shape) / np.array(chunk_dimensions)))
            > max_chunks
        ):
            for i in range(len(chunk_dimensions)):
                if chunk_dimensions[i] < variable_shape[i]:
                    chunk_dimensions[i] *= 2
                break

    return chunk_dimensions


def determine_chunking_shape_alternative_symmetrical(
    variable_shape,
    float_size=4,
    chunk_size=4096,
    max_chunks: int = None,
    min_chunk_size: int = None,
    force_power_of_two: bool = False,
    spatial_divisors: List[int] = None,
):
    """
    Determine optimal symmetrical chunk shape for a variable with additional constraints.

    Parameters
    ----------
    variable_shape : list of int
        The shape of the variable (time, latitude, longitude).
    float_size : int
        Size of a float value in bytes.
    chunk_size : int
        Maximum allowable chunk size in bytes.
    max_chunks : int, optional
        Maximum number of chunks allowed.
    min_chunk_size : int, optional
        Minimum allowable chunk size in bytes.
    force_power_of_two : bool, optional
        Whether to force chunk dimensions to be powers of two.
    spatial_divisor : int, optional
        Acceptable divisor for the spatial dimensions.

    Returns
    -------
    list of int
        Optimal symmetrical chunk shape.

    Examples
    --------
    variable_shape_example = [100, 2600, 2600]
    force_power_of_two_example = True
    spatial_divisor_example = 32
    determine_chunking_shape_symmetrical(
        variable_shape_example,
        force_power_of_two=force_power_of_two_example,
        spatial_divisor=spatial_divisor_example
    )
    """

    def find_largest_divisor_in_list(n, divisors):
        """
        Find the largest divisor of 'n' within the provided list of 'divisors'.

        Parameters:
        n (int): The number for which to find the divisor.
        divisors (list of int): A list of potential divisors.

        Returns:
        int: The largest divisor in the list that divides 'n', or 1 if none are found.
        """
        largest_divisor = 1
        for divisor in sorted(divisors, reverse=True):
            if n % divisor == 0:
                largest_divisor = divisor
                break
        return largest_divisor

    # Determine the largest spatial dimension that is less than or equal to the spatial_divisor
    # and is a divisor of the spatial dimensions of the variable
    if spatial_divisors:
        max_spatial_divisor = find_largest_divisor_in_list(
            min(variable_shape[1:]), spatial_divisors
        )
    else:
        max_spatial_divisor = min(variable_shape[1:])

    # If enforcing power of two, find the nearest power of two that is less than or equal to the max_spatial_divisor
    if force_power_of_two:
        max_spatial_divisor = 2 ** int(np.floor(np.log2(max_spatial_divisor)))

    # Calculate the maximum chunk volume given the constraints
    max_chunk_volume = chunk_size / float_size
    if min_chunk_size:
        max_chunk_volume = max(max_chunk_volume, min_chunk_size / float_size)

    # Initialize the spatial dimensions as large as possible given the constraints
    spatial_dimension = max_spatial_divisor
    while spatial_dimension > 1 and (spatial_dimension**2 > max_chunk_volume):
        spatial_dimension //= 2

    # Ensure the spatial dimensions do not exceed the variable dimensions
    spatial_dimension = min(spatial_dimension, variable_shape[1], variable_shape[2])

    # Calculate the time dimension given the maximum chunk volume and spatial dimensions
    time_dimension = int(np.floor(max_chunk_volume / (spatial_dimension**2)))
    time_dimension = max(1, min(time_dimension, variable_shape[0]))

    # Create the chunk shape
    chunk_shape = [time_dimension, spatial_dimension, spatial_dimension]

    # Ensure the chunk size does not exceed the chunk_size limit
    while np.prod(chunk_shape) * float_size > chunk_size:
        # Reduce the spatial dimensions if possible
        if spatial_dimension > 1:
            spatial_dimension //= 2
            chunk_shape = [time_dimension, spatial_dimension, spatial_dimension]
        # Otherwise, reduce the time dimension
        elif time_dimension > 1:
            time_dimension //= 2
            chunk_shape[0] = time_dimension

    # Adjust if the number of chunks exceeds max_chunks
    if (
        max_chunks
        and np.prod(np.ceil(np.array(variable_shape) / np.array(chunk_shape)))
        > max_chunks
    ):
        # Increase the chunk size by increasing the time dimension
        while (
            time_dimension < variable_shape[0]
            and np.prod(np.ceil(np.array(variable_shape) / np.array(chunk_shape)))
            > max_chunks
        ):
            time_dimension *= 2
            chunk_shape[0] = time_dimension

    return chunk_shape


# @app.command(
#     'suggest',
#     no_args_is_help=True,
#     help='Suggest a good chunking shape [yellow]Needs a review![/yellow]',
#     rich_help_panel=rich_help_panel_rechunking,
# )
def suggest_chunking_shape(
    variable_shape: Annotated[VariableShapeModel, typer_argument_variable_shape],
    float_size: int = 4,
    chunk_size: int = 4096,
) -> None:
    """ """
    good_chunking_shape = determine_chunking_shape(
        variable_shape=variable_shape,
        float_size=float_size,
        chunk_size=chunk_size,
    )
    print(good_chunking_shape)


# @app.command(
#     'suggest-alternative',
#     no_args_is_help=True,
#     help='Suggest a good chunking shape [red]Merge to [code]suggest[/code][/red]',
#     rich_help_panel=rich_help_panel_rechunking,
# )
def suggest_chunking_shape_alternative(
    variable_shape: Annotated[VariableShapeModel, typer_argument_variable_shape],
    float_size: int = 4,
    chunk_size: int = 4096,
    max_chunks: int = None,
    min_chunk_size: int = None,
    force_power_of_two: bool = False,
    spatial_divisors: List[int] = [2**i for i in range(6, 12)],
) -> None:
    """ """
    good_chunking_shape = determine_chunking_shape_alternative(
        variable_shape=variable_shape,
        float_size=float_size,
        chunk_size=chunk_size,
        max_chunks=max_chunks,
        min_chunk_size=min_chunk_size,
        force_power_of_two=force_power_of_two,
        spatial_divisors=spatial_divisors,
    )
    print(good_chunking_shape)


# @app.command(
#     'suggest-alternative-symmetrical',
#     no_args_is_help=True,
#     help='Suggest a good chunking shape [red]Merge to [code]suggest[/code][/red]',
#     rich_help_panel=rich_help_panel_rechunking,
# )
def suggest_chunking_shape_alternative_symmetrical(
    variable_shape: Annotated[VariableShapeModel, typer_argument_variable_shape],
    float_size: int = 4,
    chunk_size: int = 4096,
    max_chunks: int = None,
    min_chunk_size: int = None,
    force_power_of_two: bool = False,
    spatial_divisors: List[int] = [2**i for i in range(6, 12)],
) -> None:
    """ """
    good_chunking_shape = determine_chunking_shape_alternative_symmetrical(
        variable_shape=variable_shape,
        float_size=float_size,
        chunk_size=chunk_size,
        max_chunks=max_chunks,
        min_chunk_size=min_chunk_size,
        force_power_of_two=force_power_of_two,
        spatial_divisors=spatial_divisors,
    )
    print(good_chunking_shape)
