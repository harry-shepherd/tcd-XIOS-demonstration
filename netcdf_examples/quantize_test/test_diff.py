import subprocess
import numpy
import netCDF4
import copy
import glob
import os
import sys

def check_files_match():
    '''
    Check that each netcdf file has a matching cdl file, and vice versa
    '''
    sys.stdout.write('Check the NetCDF and CDL files match: ')
    cdl_filenames = [''.join(f.split('.')[:-1]) for f in os.listdir('.')
                     if f[-3:] == 'cdl']
    netcdf_filenames = [''.join(f.split('.')[:-1]) for f in os.listdir('.')
                        if f[-2:] == 'nc']
    netcdf_fnames = copy.deepcopy(netcdf_filenames)
    cdl_fnames = copy.deepcopy(cdl_filenames)
    for cdl_fn in cdl_filenames:
        if cdl_fn in netcdf_filenames:
            netcdf_fnames.remove(cdl_fn)
    for netcdf_fn in netcdf_filenames:
        if netcdf_fn in cdl_filenames:
            cdl_fnames.remove(netcdf_fn)
    try:
        assert len(cdl_fnames) == 0
        assert len(netcdf_fnames) == 0
        sys.stdout.write('OK\n\n')
    except AssertionError:
        sys.stdout.write('FAIL\n')
        if len(cdl_fnames):
            cdl_fnames = ['{}.cdl'.format(f) for f in cdl_fnames]
            sys.stderr.write('The following cdl files do not have a '
                             'corresponding netcdf file\n{}\n'.
                             format('\n'.join(cdl_fnames)))
        if len(netcdf_fnames):
            netcdf_fnames = ['{}.nc'.format(f) for f in netcdf_fnames]
            sys.stderr.write('The following NetCDF files do not have a '
                             'corresponding cdl file\n{}\n'.
                             format('\n'.join(netcdf_fnames)))
        sys.exit(1)

def check_data():
    '''
    Check the netcdf output matches our cdl files
    '''
    nfailures = 0
    tolerance = 5e-03
    netcdf_fileroot = [''.join(f.split('.')[:-1]) for f in os.listdir('.')
                       if f[-2:] == 'nc']
    for netcdf_file in netcdf_fileroot:
        sys.stdout.write('Checking file {}.nc '.format(netcdf_file))
        # create our netcdf file to compare against
        reference_ncfile = '{}_ref.nc'.format(netcdf_file)
        subprocess.run(['ncgen', '-k', 'nc4', '-o', reference_ncfile,
                        '{}.cdl'.format(netcdf_file)])
        test_results = netCDF4.Dataset(
            '{}.nc'.format(netcdf_file))['field'][:]
        expected = netCDF4.Dataset(reference_ncfile)['field'][:]
        diff = test_results - expected
        msg = 'The produced data array in file {0}.nc differes from \nthat in' \
              ' the reference cdl file {0}.cdl\n'.format(netcdf_file)
        if not numpy.allclose(test_results, expected, rtol=tolerance):
            sys.stdout.write('FAIL\n')
            sys.stderr.write(msg)
            nfailures += 1
        else:
            sys.stdout.write('OK\n')
        os.remove(reference_ncfile)
    if nfailures:
        sys.exit(1)


if __name__ == '__main__':
    check_files_match()
    check_data()
