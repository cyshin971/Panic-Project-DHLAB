import pandas as pd
import numpy as np

# 1. 불러오고 컬럼 정리
HR = pd.read_csv('/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/2_stage/processed/HR.csv')
HR.rename(columns={'heart_rate': 'HR'}, inplace=True)
HR['HR'] = pd.to_numeric(HR['HR'], errors='coerce')
HR['datetime'] = pd.to_datetime(HR['date'] + ' ' + HR['time'])

# 2. ID별로, 날짜별로 1분 단위 리인덱스 + 보간
time_range = pd.date_range('00:00', '23:59', freq='1min').time
full_times = [t.strftime('%H:%M:%S') for t in time_range]

out = []
for pid, grp in HR.groupby('ID'):
    grp = grp.set_index('datetime').sort_index()
    for day, day_grp in grp.groupby(grp.index.date):
        # Prepare original data and aggregate to minute resolution to dedupe timestamps
        df = day_grp.copy()

        # Resample to 1-minute bins, averaging duplicates
        df = df.resample('1min').mean()

        # Create full-day minute-level DatetimeIndex
        base = pd.to_datetime(f"{day}") + pd.to_timedelta(np.arange(1440), unit='m')
        # Ensure index is unique to avoid reindex errors
        df = df[~df.index.duplicated(keep='first')]
        df = df.reindex(base)

        # Interpolate HR values over time, but limit to 30-minute gaps
        df['HR'] = df['HR'].interpolate(method='time', limit=30, limit_direction='both')

        # Fill metadata columns
        df['ID'] = pid
        df['date'] = day
        df['time'] = df.index.time.astype(str)

        # Collect final columns
        out.append(df[['HR', 'ID', 'date', 'time']])

HR_interp = pd.concat(out, ignore_index=True)
HR_interp.to_csv('/Users/lee-junyeol/Downloads/panic 총정리/PXPN_전처리/2_stage/processed/HR_interpolated.csv', index=False)