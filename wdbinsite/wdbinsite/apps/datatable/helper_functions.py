import copy
from astropy.time import Time
from astropy import constants as const
import astropy.io.fits as astroread
import numpy as np



#   **  Helper Functions  **



# Input: parameter captured from filter form GET
# Output: boolean, True if paramter is not blank and not None; False otherwise
# Note: Needed to decide whether to filter on the parameter; most bad values should've been caught by the filter forms' type restriction and min/max values
def is_valid_query(param):
    
    return(param != '' and param is not None)



# Input: jd (float): datatime value in julian format
# Output: string in 'day mon year hour:min' format
# Notes: Uses astropy.Time package
def jd_to_readable_date(jd):
    
    return Time(jd, format='jd').strftime("%d %b %y %H:%M")
    
    
    
# These two functions come from Jo Bovy's apogee python package (https://github.com/jobovy/apogee/tree/main).
# Absolutely all credit goes to him and his collaborators for these two functions; I just didn't want to worry about installing this package on the server's virtual environment.

# Begin copied code: 
def fitApvisit(spec, specerr, wave, deg=4, niter=10, usigma=3., lsigma=0.1, cont_pixels=None):
    """
    Continuum fitting routine for apVisit spectra (one spectrum at a time; aspcap method only)
    INPUT:
       spec - single spectrum to fit
       specerr - error on the spectrum; assume no covariances
       wave - wavelength grid corresponding to spec and specerr; must have length 12288
       ASPCAP keywords:
          deg = (4) degree of the polynomial
          niter = (10) number of sigma-clipping iterations to perform
          usigma, lsigma = (3., 0.1) upper and lower sigmas for sigma clipping
    OUTPUT:
       continuum
    Added by Meredith Rawls, 2016-11
       TODO: -Generalize to work for wavelength grid of any length
             -Allow multiple apVisits to be continuum-normalized at once, like the regular 'fit'
    """
    # Parse the input
    tspec = copy.copy(spec)
    tspecerr = specerr
    if len(wave) != 12288:
        raise ValueError('Length of apVisit wavelength array is not 12288; cannot proceed.')
    if wave[1] < wave[0]: # not sorted by increasing wavelength; fix it
        wave = np.flipud(wave)
        tspec = np.flipud(tspec)
        tspecerr = np.flipud(tspecerr)
    cont = np.empty_like(tspec)
    bluewav = wave[0:4096]
    greenwav = wave[4096:8192]
    redwav = wave[8192::]
    # Blue
    cont[0:4096] = _fit_aspcap(bluewav, tspec[0:4096], tspecerr[0:4096], deg, niter, usigma, lsigma)
    # Green
    cont[4096:8192] = _fit_aspcap(greenwav, tspec[4096:8192], tspecerr[4096:8192], deg, niter, usigma, lsigma)
    # Red
    cont[8192::] = _fit_aspcap(redwav, tspec[8192::], tspecerr[8192::], deg, niter, usigma, lsigma)
    return cont


def _fit_aspcap(wav,spec,specerr,deg,niter,usigma,lsigma):
    """Fit the continuum with an iterative upper/lower rejection"""
    # Initial fit
    chpoly= np.polynomial.Chebyshev.fit(wav,spec,deg,w=1./specerr)
    tcont= chpoly(wav)
    tres= spec-tcont
    sig= np.std(tres)
    mask= (tres < usigma*sig)*(tres > -lsigma*sig)
    spec[True^mask]= chpoly(wav[True^mask])
    for ii in range(niter):
        chpoly= np.polynomial.Chebyshev.fit(wav,
                                               spec,
                                               deg,
                                               w=1./specerr)
        tcont= chpoly(wav)
        tres= spec-tcont
        sig= np.std(tres)
        mask= (tres < usigma*sig)*(tres > -lsigma*sig)
        spec[True^mask]= chpoly(wav[True^mask])
    return chpoly(wav)

# End copied code
# Everything after the previous line is Christine's own code, not copied from anyone else.



# Input: filename that contains combined spectrum
# Output: wavelength in Aangstroms; combined and model spectra normalized to 1
def read_comb_files(filename):
    
    # Get normalized combined spectrum
    specComb = astroread.getdata(filename, 1).flatten()
    # Get best fitting model spectrum
    specModel = astroread.getdata(filename, 3).flatten()
    
    # Get wavelengths
    hdrComb = astroread.getheader(filename, 1)
    speclogWav = ((np.arange(hdrComb['NAXIS1']) + 1.0) - hdrComb['CRPIX1']) * hdrComb['CDELT1'] + hdrComb['CRVAL1']
    specWav = 10.0**speclogWav
    
    
    return(specWav, specComb, specModel)
    



# Input: filename that contains visit spectrum, raw Doppler shift RV [km/s], real RV [km/s]
# Output: original observed wavelengths in Aangstroms; wavelengths with 1) raw Doppler shift removed, and 2) raw Doppler shift removed and RV added back; visit spectra normalized to 1
def read_vis_files(filename, Vraw, RV):
    
    # Get visit spectrum
    specVisit = astroread.getdata(filename, 1).flatten()
    # Get error in visit spectrum
    specerrVisit = astroread.getdata(filename, 2).flatten()
    # Get observed wavelengths
    waveVisit = astroread.getdata(filename, 4).flatten()
    
    # Normalize using Jo Bovy's functions to get the continuum and remove it
    contVisit = fitApvisit(specVisit, specerrVisit, waveVisit)
    specNormVisit = specVisit/contVisit
    
    # Calculate Doppler shifts for both the raw 
    doppler_factor_raw = (const.c.cgs.value/(const.c.cgs.value - Vraw*1e5))
    doppler_factor_hel = ((const.c.cgs.value - RV*1e5)/const.c.cgs.value)  
    
    # Remove the raw Doppler shift from the observed wavelengths
    rmvVraw_Wav = (waveVisit / doppler_factor_raw)
    # Remove the raw Doppler shift AND add back Doppler shift from real RV from the observed wavelengths
    addVhel_Wav = (waveVisit / doppler_factor_raw) / doppler_factor_hel
    
    
    return(waveVisit, rmvVraw_Wav, addVhel_Wav, specNormVisit)
        

