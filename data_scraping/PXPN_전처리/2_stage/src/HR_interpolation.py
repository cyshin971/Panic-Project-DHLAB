import pandas as pd
import numpy as np
from tqdm import tqdm

def main():
    HR = pd.read_csv('/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/HR.csv')
    if 'heart_rate' in HR.columns:
        HR.rename(columns={'heart_rate': 'HR'}, inplace=True)
    HR['HR'] = pd.to_numeric(HR['HR'], errors='coerce')
    HR['datetime'] = pd.to_datetime(HR['date'] + ' ' + HR['time'], errors='coerce')
    
    out = []
    for pid, grp in tqdm(HR.groupby('ID'), desc='Processing IDs'):
        grp = grp.dropna(subset=['datetime']).set_index('datetime').sort_index()
        for day, day_grp in grp.groupby(grp.index.date):
            orig_count = day_grp['HR'].dropna().shape[0]
            base = pd.to_datetime(f"{day}") + pd.to_timedelta(np.arange(1440), unit='m')
            df_full = pd.DataFrame(index=base)
            if orig_count > 720:
                tmp = day_grp[['HR']].resample('1min').mean()
                tmp = tmp.reindex(df_full.index)
                tmp['HR'] = tmp['HR'].interpolate(method='time', limit=30, limit_direction='both')
                df_full['HR'] = tmp['HR']
            else:
                df_full['HR'] = np.nan
            df_full['ID'] = pid
            df_full['date'] = pd.to_datetime(day).date()
            df_full['time'] = df_full.index.time.astype(str)
            out.append(df_full[['HR', 'ID', 'date', 'time']])
    
    HR_interp = pd.concat(out, ignore_index=True)
    HR_interp.to_csv('/Users/lee-junyeol/Downloads/github/Panic-Project-DHLAB/junyeol_lee/panic 총정리/PXPN_전처리/2_stage/processed/HR_interpolated_720.csv', index=False)

if __name__ == '__main__':
    main()
