import numpy
import xarray


def write_to_netcdf(
    location_time_series,
    path,
    longitude,
    latitude,
):
    """Save to NetCDF with lon and lat dimensions of length 1."""
    # A new 'coords' for longitude and latitude, each of length 1
    new_coords = {
        'lon': numpy.array([longitude]),
        'lat': numpy.array([latitude]),
        'time': location_time_series.time
    }
    
    # Expand the data to include lat and lon dimensions
    new_data = location_time_series.values[:, numpy.newaxis, numpy.newaxis]
    
    # Create the new DataArray
    data_array = xarray.DataArray(
            new_data,
            coords=new_coords,
            dims=['time', 'lat', 'lon'],
            name=location_time_series.name,
            attrs=location_time_series.attrs,
    )
    
    # Add attributes to longitude and latitude for CF compliance
    data_array.lon.attrs['long_name'] = 'longitude'
    data_array.lon.attrs['units'] = 'degrees_east'
    data_array.lat.attrs['long_name'] = 'latitude'
    data_array.lat.attrs['units'] = 'degrees_north'
    
    # Save to NetCDF
    data_array.to_netcdf(path)
