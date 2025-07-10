import os
import zipfile
import pandas as pd
import numpy as np

import os
import zipfile
import pandas as pd

def read_all_data(title, outer_zip_path, exclude_keywords=None):
    """
    title: string to match in CSV filenames (e.g., 'HeartRate')
    outer_zip_path: path to the outer ZIP file that contains subfolders and inner ZIPs
    exclude_keywords: list of substrings; if any are present in a CSV filename, that file will be skipped.
    """
    # List of IDs to process
    id_list = [
        "PXPN_10006", "PXPN_10007", "PXPN_10008", "PXPN_10009", "PXPN_10010",
        "PXPN_10011", "PXPN_10012", "PXPN_10013", "PXPN_10014", "PXPN_10015",
        "PXPN_10018", "PXPN_10019", "PXPN_10020", "PXPN_10021", "PXPN_10022",
        "PXPN_10023", "PXPN_10024", "PXPN_10025", "PXPN_10028", "PXPN_10029",
        "PXPN_10030", "PXPN_10032", "PXPN_10034", "PXPN_10035", "PXPN_10036",
        "PXPN_10037", "PXPN_10038", "PXPN_10039", "PXPN_10040"
    ]

    all_data_list = []
    try:
        with zipfile.ZipFile(outer_zip_path, 'r') as outer_zf:
            # Iterate over each ID in the predefined list
            for id_dir in id_list:
                # Define folder prefix for this ID inside the outer ZIP
                folder_prefix = f"PassiveData/{id_dir}_PassiveData"
                # Iterate through all members and find inner ZIPs for this ID
                for member in outer_zf.namelist():
                    if member.startswith(folder_prefix) and member.lower().endswith('.zip'):
                        # Read inner ZIP bytes
                        with outer_zf.open(member) as inner_stream:
                            from io import BytesIO
                            inner_buf = BytesIO(inner_stream.read())
                            try:
                                with zipfile.ZipFile(inner_buf, 'r') as inner_zf:
                                    for inner_member in inner_zf.namelist():
                                        if title in inner_member and inner_member.lower().endswith('.csv') and (
                                            exclude_keywords is None or not any(
                                                kw.lower() in inner_member.lower() for kw in exclude_keywords
                                            )
                                        ):
                                            with inner_zf.open(inner_member) as csvfile:
                                                try:
                                                    df_temp = pd.read_csv(csvfile, index_col=False)
                                                    df_temp['ID'] = id_dir
                                                    all_data_list.append(df_temp)
                                                except Exception:
                                                    continue
                            except zipfile.BadZipFile:
                                continue
    except FileNotFoundError:
        print(f"Outer ZIP not found: {outer_zip_path}")
        return pd.DataFrame()

    return pd.concat(all_data_list, axis=0, ignore_index=True) if all_data_list else pd.DataFrame()


from pandas import DataFrame
from scipy.signal import welch
from scipy.integrate import simps
from mne.time_frequency import psd_array_multitaper
from CosinorPy import cosinor, cosinor1
import pandas as pd 
import numpy as np 


def bandpower(data, sf, band, method='welch', window_sec=None, relative=False):
    band = np.asarray(band)
    low, high = band

    # Compute the modified periodogram (Welch)
    if method == 'welch':
        if window_sec is not None:
            nperseg = window_sec * sf
        else:
            nperseg = (2 / low) * sf

        freqs, psd = welch(data, sf, nperseg=nperseg)

    elif method == 'multitaper':
        psd, freqs = psd_array_multitaper(data, sf, adaptive=True,
                                          normalization='full', verbose=0)

    # Frequency resolution
    freq_res = freqs[1] - freqs[0]

    # Find index of band in frequency vector
    idx_band = np.logical_and(freqs >= low, freqs <= high)

    # Integral approximation of the spectrum using parabola (Simpson's rule)
    bp = simps(psd[idx_band], dx=freq_res)

    if relative:
        bp /= simps(psd, dx=freq_res)
    return bp

def check_bandpower_value_a(col_index, col_HR):
    sampling_frequency =  1/60
    temp = pd.DataFrame()
    temp['index'] = col_index
    temp['HR'] = col_HR
    temp = temp.fillna(method='ffill')
    temp = temp.fillna(method='backfill')
    data = temp.HR
    power_rel = bandpower(data, sampling_frequency, [0.0005, 0.001], 'multitaper', relative=True)
    return power_rel

def check_bandpower_value_b(col_index, col_HR):
    sampling_frequency =  1/60
    temp = pd.DataFrame()
    temp['index'] = col_index
    temp['HR'] = col_HR
    temp = temp.fillna(method='ffill')
    temp = temp.fillna(method='backfill')
    data = temp.HR
    power_rel = bandpower(data, sampling_frequency, [0.0001, 0.0005], 'multitaper', relative=True)
    return power_rel

def check_bandpower_value_c(col_index, col_HR):
    sampling_frequency =  1/60
    temp = pd.DataFrame()
    temp['index'] = col_index
    temp['HR'] = col_HR
    temp = temp.fillna(method='ffill')
    temp = temp.fillna(method='backfill')
    data = temp.HR
    power_rel = bandpower(data, sampling_frequency, [0.00005, 0.0001], 'multitaper', relative=True)
    return power_rel

def check_bandpower_value_d(col_index, col_HR):
    sampling_frequency =  1/60
    temp = pd.DataFrame()
    temp['index'] = col_index
    temp['HR'] = col_HR
    temp = temp.fillna(method='ffill')
    temp = temp.fillna(method='backfill')
    data = temp.HR
    power_rel = bandpower(data, sampling_frequency, [0.00001, 0.00005], 'multitaper', relative=True)
    return power_rel

def mesor(col_index, col_HR):
    MESOR = cosinor1.fit_cosinor(col_index, col_HR, period= 1440, plot_on=False)[3]['values'][0]
    return MESOR

def amplitude(col_index, col_HR):
    amp = cosinor1.fit_cosinor(col_index , col_HR, period= 1440, plot_on=False)[3]['values'][1]
    return amp

def acrophase(col_index, col_HR):
    acr = cosinor1.fit_cosinor(col_index, col_HR, period= 1440, plot_on=False)[3]['values'][2]
    acrophase_min = cosinor.acrophase_to_hours(acr)
    acrophase = (acrophase_min +1440)/60
    return acrophase_min