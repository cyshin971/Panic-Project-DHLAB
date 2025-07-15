import os
import zipfile
import pandas as pd
import numpy as np



import zipfile
import pandas as pd
from io import BytesIO

def read_all_data(title, outer_zip_path, exclude_keywords=None):
    """
    title 키워드를 포함한 CSV 파일을 모두 읽어 DataFrame 으로 결합하여 반환합니다.
    outer_zip_path: 'raw_data/PXPN/pixelpanic_raw_data.zip' 같은 상대 또는 절대 경로를 지정하세요.
    exclude_keywords: 해당 키워드가 포함된 파일명은 건너뜁니다.
    """
    all_data_list = []
    try:
        with zipfile.ZipFile(outer_zip_path, 'r') as outer_zf:
            entries = []
            for f in outer_zf.namelist():
                raw = os.path.basename(f)
                if ('PassiveData/' in f and raw.endswith('.zip') and '_PassiveData' in raw
                        and not any(x in f for x in ['__MACOSX', '/._', '.DS_Store'])):
                    pid = raw.split('_PassiveData')[0]
                    if pid.startswith('SRTN'):
                        continue
                    entries.append((pid, f))
            # 각 ZIP 파일 순회
            for pid, zip_path in entries:
                with outer_zf.open(zip_path) as inner_stream:
                    buf = BytesIO(inner_stream.read())
                    buf.seek(0)
                    if not zipfile.is_zipfile(buf):
                        continue
                    buf.seek(0)
                    with zipfile.ZipFile(buf, 'r') as inner_zf:
                        for member in inner_zf.namelist():
                            name_lower = member.lower()
                            if (title in member and name_lower.endswith('.csv')
                                    and (exclude_keywords is None or not any(kw.lower() in name_lower for kw in exclude_keywords))):
                                with inner_zf.open(member) as csvfile:
                                    try:
                                        df_temp = pd.read_csv(csvfile, index_col=False)
                                        df_temp['ID'] = pid
                                        all_data_list.append(df_temp)
                                    except Exception:
                                        continue
    except FileNotFoundError:
        print(f"Outer ZIP not found: {outer_zip_path}")
        return pd.DataFrame()

    if all_data_list:
        return pd.concat(all_data_list, axis=0, ignore_index=True)
    else:
        return pd.DataFrame()



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