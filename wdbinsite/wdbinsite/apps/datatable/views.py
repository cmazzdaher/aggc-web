from django.shortcuts import render
from django.views.generic import View, TemplateView

import numpy as np
import pandas as pd
import json
import os

import plotly.graph_objs as go
import plotly.offline as opy

from . import helper_functions as hf


#   **  Data Imports  **


# Read general summary file
datafile = 'wdbinsite/static/files/wdbin_main_summary.csv'
datatable = pd.read_csv(datafile)


# Read allStar summary file
allStar = 'wdbinsite/static/files/wdbin_apogee_allStar_summary.csv'
allStardf = pd.read_csv(allStar)


# Read allVisit summary file
allVisit = 'wdbinsite/static/files/wdbin_apogee_allVisit_summary.csv'
allVisitdf = pd.read_csv(allVisit)


    
    
#   **  Primary Page Functions  **



# Purpose: page with filterable, searchable data table that has links via APOGEE IDs to individual source pages
# HTML template: table.html
# Data files: wdbin_main_summary.csv
# Notes: Also implements the sorting from the filter form
def fetch_table(request):
    
    # GET filter form entries; if no value entered by user, then returns None
    
    # RAs
    ra_min = request.GET.get('min_RA')
    ra_max = request.GET.get('max_RA')
    
    # Decs
    dec_min = request.GET.get('min_Dec')
    dec_max = request.GET.get('max_Dec')
    
    # Gaia G
    g_max = request.GET.get('max_G')
    
    # APOGEE Teff
    teff_min = request.GET.get('min_Teff')
    teff_max = request.GET.get('max_Teff')
    
    # APOGEE log(g)
    logg_min = request.GET.get('min_logg')
    logg_max = request.GET.get('max_logg')
    
    # APOGEE vsini
    vsini_max = request.GET.get('max_vsini')
    
    # Observing Program dropdown box
    obs_prog = request.GET.get('obs_prog')
    
    # Number of RVs
    Nrvs_min = request.GET.get('min_Nrvs')
    Nrvs_max = request.GET.get('max_Nrvs')
    
    # APOGEE DRVM for visits with S/N>= 40
    drvmsnr40_max = request.GET.get('min_DRVMsnr40')
    
    
    # Set original data table source
    datain = datatable
    
    
    # Basic outline: 
    # Check if is_valid_query(param) returns True. If so, then the parameter is valid for filtering.
    # Filter datain based on that parameter.
    
    # Each of these if statements is executed independently. As many or as few filter options can be provided as desired.
    
    # RA min/max
    if hf.is_valid_query(ra_min):
        datain = datain[datain['RA'] >= float(ra_min)]
    
    if hf.is_valid_query(ra_max):
        datain = datain[datain['RA'] <= float(ra_max)]
    
    
    # Dec min/max
    if hf.is_valid_query(dec_min):
        datain = datain[datain['Dec'] >= float(dec_min)]

    if hf.is_valid_query(dec_max):
        datain = datain[datain['Dec'] <= float(dec_max)]

 
    # Gaia G max
    if hf.is_valid_query(g_max):
        datain = datain[datain['G'] <= float(g_max)]
    
    
    # Teff min/max
    if hf.is_valid_query(teff_min):
        datain = datain[datain['Teff'] >= float(teff_min)]
    
    if hf.is_valid_query(teff_max):
        datain = datain[datain['Teff'] <= float(teff_max)]
    
    
    # log(g) min/max
    if hf.is_valid_query(logg_min):
        datain = datain[datain['logg'] >= float(logg_min)]

    if hf.is_valid_query(logg_max):
        datain = datain[datain['logg'] <= float(logg_max)]
        
    
    # vsini max
    if hf.is_valid_query(vsini_max):
        datain = datain[datain['vsini'] <= float(vsini_max)]
        
    
    # Observing Program
    # Beacuse of the dropdown box, the value should always be valid. But just in case...
    if hf.is_valid_query(obs_prog):
        # If the default value of 'All Stars' then no filtering should be done. If any other value, then filter the results.
        if obs_prog != 'All Stars':
            datain = datain[datain['Obs_Program'] == obs_prog]

    
    # Number of RVs min/max
    if hf.is_valid_query(Nrvs_min):
        datain = datain[datain['Nrvs'] >= int(Nrvs_min)]

    if hf.is_valid_query(Nrvs_max):
        datain = datain[datain['Nrvs'] <= int(Nrvs_max)]
    
    
    # DRVM for S/N > 40 max
    if hf.is_valid_query(drvmsnr40_max):
        datain = datain[datain['DRVM_SNR40'] >= float(drvmsnr40_max)]

    
    
    # Convert the pandas dataframe to a list of JSON entries that can be passed to the HTML response
    json_records = datain.to_json(orient ='records')
    data = json.loads(json_records)

    context = {'d': data}

    return render(request, 'datatable/table.html', context)



# Purpose: page with summary information from all spectro-photometric, primarily APOGEE
# HTML template: summary.html
# Data files: wdbin_apogee_allStar_summary.csv and wdbin_apogee_allVisit_summary.csv
# Notes: TODO add plots of the spectra
def indv_summary(request, **kwargs):
    
    # Limit summary table to entries matching the APOGEE ID, then pass the dataframe as a list of JSON entries that can be passed to the HTML response
    borja_entries = datatable[datatable['APOGEE_ID'] == kwargs['pk']]
    borja_json_records = borja_entries.to_json(orient = 'records')
    borja_data = json.loads(borja_json_records)
    
    
    # Limit allStar table to entries matching the APOGEE ID, then pass the dataframe as a list of JSON entries that can be passed to the HTML response
    allStar_entries = allStardf[allStardf['APOGEE_ID'] == kwargs['pk']]
    allStar_json_records = allStar_entries.to_json(orient = 'records')
    allStar_data = json.loads(allStar_json_records)
    
    
    # Limit allVisit table to entries matching the APOGEE ID
    allVisit_entries = allVisitdf[allVisitdf['APOGEE_ID'] == kwargs['pk']]
    # Convert JDs to human-readable dates
    allVisit_entries.insert(loc=5, column='date', value=hf.jd_to_readable_date(allVisit_entries['jd']))
    # Pass the dataframe as a list of JSON entries that can be passed to the HTML response
    allVisit_json_records = allVisit_entries.to_json(orient = 'records')
    allVisit_data = json.loads(allVisit_json_records)
    
    
    # Path to the individual star's folder
    spectra_path = 'wdbinsite/static/files/indv_stars/' + kwargs['pk'] + '/'
    
    # Iterate for as many allStar entries as available
    for row in allStar_data:
        
        # If there are multiple allStar entries, then the combined spectrum files have the LocID in the name to distinguish them
        if len(allStar_data) > 1:
            combfilename = spectra_path + 'aspcapStar-dr17-' + kwargs['pk'] + '_' + str(row['LocID']) + '.fits'
        
        # Otherwise, the combined spectrum filename is very simple
        else:
            combfilename = spectra_path + 'aspcapStar-dr17-' + kwargs['pk'] + '.fits'
        
        
        # Check to see if the file exists
        if os.path.isfile(combfilename) == True:
            
            # Access the wavelengths, combined spectrum, and model spectrum
            wavs, comb, model = hf.read_comb_files(combfilename)
            
            # Plot the spectra; these will go in the top panel
            combfig = go.Scatter(x=wavs/10000., y=comb, mode='lines', line={ 'color': 'blue', 'width': 2}, name='Combined Spectrum', xaxis='x2', yaxis='y2', legendgroup=2)
            modelfig = go.Scatter(x=wavs/10000., y=model, mode='lines', line={ 'color': 'gray', 'width': 2}, name='Best-fit Model', xaxis='x2', yaxis='y2', legendgroup=2)
            
            # Add the combined/model spectra to the list of plots
            scat_list = [modelfig,combfig]
    
        
        else:
            
            textfig = go.Scatter(x=[1.6], y=[1.0], text=['The combined spectrum file was unable to be downloaded'], textfont={'size': 20}, 
                                 mode='markers+text', marker={'color': '#FFFFFF', 'size': 8}, xaxis='x2', yaxis='y2', legendgroup=2, name='')
            
            # If the file didn't exist, just initialize a blank array
            scat_list = [textfig]
    
        # Access the allVisit info from the non-rounded array
        visit_entries = allVisitdf[(allVisitdf['APOGEE_ID'] == kwargs['pk']) & (allVisitdf['LocID'] == row['LocID'])]
        
        
        missing_rv_counter = 0
        
        # Iterate over each visit by going over each row in the dataframe
        for r in range(len(visit_entries)):
            
            # Go over row by row
            star = visit_entries.iloc[[r]]
            
            # Access the visit spectrum file's name
            visfilename = spectra_path + star['filename'].values[0]
            
            # Check to see if the file exists
            if os.path.isfile(visfilename) == True:
                
                # Access the wavelengths and normalized visit spectrum
                _, _, wavs, spec = hf.read_vis_files(visfilename, star['rv'].values, star['vraw'].values)
                
                # Create the string that will be the label in the legend
                leg_label = 'RV=' + str(np.around(star['rv'].values[0], decimals=2)) + ' km/s, Date: '+ hf.jd_to_readable_date(star['jd'].values[0])
                
                # Plot the visit spectrum; this will go in the bottom panel
                visfig = go.Scatter(x=wavs/10000., y=spec, mode='lines', line={'width': 2}, name=leg_label, xaxis='x', yaxis='y', legendgroup=1)
                
                # Append to the list of plots made earlier
                scat_list.append(visfig)
            
            else:
                
                visfig = go.Scatter(x=[1.66], y=[1.89 - missing_rv_counter*0.12], text=['Visit spectrum: '+ star['filename'].values[0] + ' unable to be downloaded'], textfont={'size': 10}, 
                                    mode='markers+text', marker={'color': '#FFFFFF', 'size': 8}, xaxis='x', yaxis='y', legendgroup=2, name='')
                # Append to the list of plots made earlier
                scat_list.append(visfig)
                
                missing_rv_counter += 1
    
        # Set the formatting for the dual-panel plot
        layout = go.Layout(xaxis={'title':'Wavelength [&mu;m]', 'titlefont': {'size':20}, 'domain': [0.0, 1.0],
                                  'range': [1.51, 1.71], 'tickvals': [1.52, 1.54, 1.56, 1.58, 1.6, 1.62, 1.64, 1.66, 1.68, 1.7],
                                  'minor': {'ticks': 'inside', 'tickvals': np.arange(1.515,1.7,0.005), 'ticklen': 4, 'tickwidth': 1},
                                  'ticks': 'inside', 'ticklen': 7, 'tickwidth': 1.5, 'tickfont': {'size':15}, 'nticks': 5},
                           
                           xaxis2={'anchor': 'y2', 'domain': [0.0, 1.0], 
                                   'range': [1.51, 1.71], 'tickvals': [1.52, 1.54, 1.56, 1.58, 1.6, 1.62, 1.64, 1.66, 1.68, 1.7],
                                   'minor': {'ticks': 'inside', 'tickvals': np.arange(1.515,1.7,0.005), 'ticklen': 4, 'tickwidth': 1},
                                   'ticks': 'inside', 'ticklen': 7, 'tickwidth': 1.5, 'tickfont': {'size':15}, 'nticks': 5},
                   
                           yaxis={'title':'Normalized Flux', 'titlefont': {'size':20}, 'domain': [0.0, 0.48],
                                  'range': [0.2,2.0], 'tickvals': [0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9],
                                  'minor': {'ticks': 'inside', 'tickvals': [0.6, 0.8, 1.0, 1.2], 'ticklen': 4, 'tickwidth': 1},
                                  'ticks': 'inside', 'ticklen': 7, 'tickwidth': 1.5, 'tickfont': {'size':15}, 'nticks': 5}, 
                           
                           yaxis2={'title':'Normalized Flux', 'titlefont': {'size':20}, 'domain': [0.52, 1.0],
                                  'range': [0.4,1.4], 'tickvals': [0.5, 0.7, 0.9, 1.1, 1.3],
                                  'minor': {'ticks': 'inside', 'tickvals': [0.6, 0.8, 1.0, 1.2], 'ticklen': 4, 'tickwidth': 1},
                                  'ticks': 'inside', 'ticklen': 7, 'tickwidth': 1.5, 'tickfont': {'size':15}, 'nticks': 5},
                   
                           font={'family': 'Didact Gothic'}, 
                   
                           template='simple_white',
                           legend= {'tracegroupgap': 250},
                           margin={'t':20, 'b': 0, 'l': 0, 'r': 0}
                           )
    
        # Create a figure based on the list of scatter plots and formatting settings
        figcomb = go.Figure(data=scat_list,layout=layout)

        # If someone saves the plot using the Save button, here's the name that it will automatically assign to the new file
        savename = kwargs['pk'] + '_combspectra'
        
        # Add the figure object to the dictionary that represents each allStar entry; we can easily access it when iterating over the allStar_data list in the summary.html file
        row['graph'] = figcomb.to_html(full_html=False, default_height=600, default_width=1100, 
                                       config={#'displayModeBar':False, # make interactive bar always visible
                                               'displaylogo': False, # remove plotly logo
                                               'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'pan', 'zoom'], # remove certain buttons from the interactive bar
                                               'toImageButtonOptions': {'format': 'jpeg', 'filename': savename, 'height': 600, 'width': 1100, 'scale': 1} # settings for the plot if downloaded
                                               }
                                       )
                                                
    
    # Define the context that will be passed to the HTTP response
    context = {'allStar': allStar_data, 'allVisit': allVisit_data, 'borja': borja_data, 'object_id': kwargs['pk']}
    
    
    return render(request, 'datatable/summary.html', context=context)



# Purpose: page with RV curves and the current best orbital solutions
# HTML template: rvcurve.html
# Data files: indiv_stars/<apid>_visits.csv, plus text files with orbital parameters from the Joker and direct integrator
# Notes: TODO work with Evan to get text files setup for the orbital solutions
def indv_rvcurve(request, **kwargs):
    
    # Identify the path to the <apid> directory
    rvpath = 'wdbinsite/static/files/indv_stars/' + kwargs['pk'] + '/'
    
    # Read the visits CSV file
    rvs = pd.read_csv(rvpath + kwargs['pk'] + '_visits.csv')
    
    # Add a column for the date
    rvs.insert(loc=4, column='date', value=hf.jd_to_readable_date(rvs['jd']))
    
    # Convert the pandas dataframe to a list of JSON entries that can be passed to the HTML response
    rvs_json_records = rvs.to_json(orient = 'records')
    rvs_data = json.loads(rvs_json_records)
    
    #   *  Plotting  *
    
    # Calculate upper edge of the time data
    baseline = rvs['jd'].max() - rvs['jd'].min()
    # Calculate a buffer zone for the min/max values on the X-axis
    timediff = baseline/15.
    
    # Calculate lower/upper edges of the RV data
    positive_rv_edge = max(rvs['rv'].values+rvs['rverr'].values)
    negative_rv_edge = min(rvs['rv'].values-rvs['rverr'].values)
    # Calculate a buffer zone for the min/max values on the Y-axis
    fracdiff = (positive_rv_edge - negative_rv_edge)/7.
    
    # Define the ticks that will be displayed along with selecting the ones that actually get labels
    ticks = [10,20,30,40,50,60,70,80,90,100,200]
    ticktxt = [10, '', '', '', 50, '', '', '', '', 100, 200]
    
    # Actual scatter plot with colorbar
    scatfig = go.Scatter(x=rvs['jd'].values.flatten().tolist()-rvs['jd'].min(), y=rvs['rv'].values.flatten().tolist(), 
                         error_y={'type': 'data', 'array': rvs['rverr'].values.flatten().tolist(), 'visible': True},
                         mode='markers', 
                         marker_symbol='square',
                         marker={ 'color': np.log10(rvs['snr'].values.flatten().tolist()), 'colorscale':'Viridis', 'showscale':True, 
                                  'cmin': np.log10(10), 'cmax': np.log10(250), 'size': 12,
                                  'line': {'width': 1, 'color': 'black'},
                                  'colorbar': {'title': "Visit S/N", 'tickvals': np.log10(ticks), 'ticktext': ticktxt, 
                                               'ticks': 'inside', 'ticklen': 7, 'tickwidth': 1.5}})
    
    # Set the layout and formatting options
    layout = go.Layout(xaxis={'title':'Days Since First Observation', 
                              'titlefont': {'size':20},
                              'ticks': 'inside', 
                              'ticklen': 7, 
                              'tickwidth': 1.5, 
                              'tickfont': {'size':15},
                              'range': [-timediff, baseline+timediff],
                              'nticks': 5},
                       
                       yaxis={'title':'RV   [km/s]', 
                              'titlefont': {'size':20},
                              'ticks': 'inside', 
                              'ticklen': 7, 
                              'tickwidth': 1.5, 
                              'tickfont': {'size':15},
                              'range': [negative_rv_edge-fracdiff, positive_rv_edge+fracdiff]}, 
                       
                       font={'family': 'Didact Gothic'}, 
                       
                       template='simple_white',
                       )
    
    # Create a figure based on this scatter plot and formatting settings
    figrv = go.Figure(data=[scatfig],layout=layout)
    
    # If someone saves the plot using the Save button, here's the name that it will automatically assign to the new file
    savename = kwargs['pk'] + '_rvcurve'
    
    # Define the context that will be passed to the HTTP response, with extensive config settings
    context={'object_id': kwargs['pk'], 'rvdata': rvs_data,
             'graph': figrv.to_html(full_html=False, default_height=500, default_width=700, 
                                    config={'displayModeBar':True, # make interactive bar always visible
                                            'displaylogo': False, # remove plotly logo
                                            'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'pan', 'zoom'], # remove certain buttons from the interactive bar
                                            'toImageButtonOptions': {'format': 'jpeg', 'filename': savename, 'height': 500, 'width': 700, 'scale': 1} # settings for the plot if downloaded
                                            }
                                    )
              }
    
    return render(request, 'datatable/rvcurve.html', context=context)



# Purpose: page with SED with as many filters as possible
# HTML template: sed.html
# Data files: None yet, but probably will be text files in indiv_stars/<apid>/ as provided by Borja
# Notes: TODO get data file(s) from Borja so I can read them in here and plot using plotly
def indv_sed(request, **kwargs):
    
    return render(request, 'datatable/sed.html', context={'object_id': kwargs['pk']})



# Purpose: page with light curve(s) from as many sources as we have
# HTML template: lightcurve.html
# Data files: None yet, but probably will be text files in indiv_stars/<apid>/ as provided by Don
# Notes: TODO get data files from Don so I can read them in here and plot using plotly
def indv_lightcurve(request, **kwargs):
    
    return render(request, 'datatable/lightcurve.html', context={'object_id': kwargs['pk']})



# Purpose: page with status updates and running notes on the source, including plans to observe or outside checks that should be done
# HTML template: status.html
# Data files: None
# Notes: TODO make an interactable, editable table for users to leave notes wiki-style
def indv_status(request, **kwargs):
    
    return render(request, 'datatable/status.html', context={'object_id': kwargs['pk']})


    
    