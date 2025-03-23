import json
import datetime
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
import os
from garmin_fit_sdk import Decoder, Stream
from dateutil import tz
from pytz import timezone
from typing import Dict, List, Union, Optional, Tuple
import logging

class CyclingDataProcessor:
    def __init__(self):
        self.download_path = "/Users/tylerfitzgerald/Downloads/"
        self.data_files_path = "/Users/tylerfitzgerald/Documents/activities/output/Data_files/"
        self.logs_path = "/Users/tylerfitzgerald/Documents/activities/output/logs/"
        self.processed_files_path = os.path.join(self.data_files_path, "processed_files.json")


    def process_new_files(self) -> list:
        mega_list = []
        with os.scandir(self.download_path) as path:
            for entry in path:
                if entry.name.endswith(".fit") and entry.is_file():
                    stream = Stream.from_file(entry.path)
                    decoder = Decoder(stream)
                    messages, errors = decoder.read()

                    for dic in messages['session_mesgs']:
                        new_dict = {}
                        for k, v in dic.items():
                            if not str(k).isdigit():
                                if k == 'timestamp':
                                    tz_denver = timezone('America/Denver')
                                    v_denver = v.astimezone(tz_denver)
                                    new_dict[str(k)] = str(v_denver.date())
                                    new_dict['yr'] = v_denver.year
                                    new_dict['week_num'] = v_denver.isocalendar().week
                                    new_dict['mnth'] = v_denver.month
                                    new_dict['week_num_yr'] = f"{v_denver.year}_{v_denver.isocalendar().week}"
                                    new_dict['yrmo'] = int(v_denver.year * 100 + v_denver.month)
                                elif k == 'start_time':
                                    new_dict[str(k)] = str(v.astimezone(timezone('America/Denver')))
                                elif k == 'total_distance':
                                    new_dict['Distance_miles'] = (v / 1000) * 0.621371
                                elif k == 'total_elapsed_time':
                                    new_dict['RidingTime'] = str(timedelta(seconds=round(v)))
                                elif k == 'total_timer_time':
                                    new_dict[k] = v
                                    new_dict['PedalTime'] = str(timedelta(seconds=round(v)))
                                elif k == 'total_ascent':
                                    new_dict['total_ascent_feet'] = v * 3.28084
                                elif k == 'total_descent':
                                    new_dict['total_descent_feet'] = v * 3.28084
                                elif k == 'avg_temperature':
                                    new_dict['avg_temp_f'] = round((v * 9/5) + 32)
                                elif k == 'avg_speed':
                                    new_dict['avg_MPH'] = v * 2.23694
                                elif k == 'total_work':
                                    new_dict['Kjs'] = v / 1000
                                elif k == 'left_right_balance':
                                    right_pct = v / (32768 + v)
                                    left_pct = 1 - right_pct
                                    new_dict['PowerBalance'] = f"{right_pct:.0%} R | {left_pct:.0%} L"
                                else:
                                    new_dict[str(k)] = v
                        try:
                            new_dict.pop("total_grit")
                            new_dict.pop("avg_flow")
                        except:
                            pass
                        mega_list.append(new_dict)
        return mega_list

    def read_existing_files(self) -> list:
        # Get only JSON files
        files = [f for f in os.listdir(self.data_files_path) if f.endswith('.json')]
        if not files:
            raise ValueError(f"No JSON files found in {self.data_files_path}")
            
        paths = [os.path.join(self.data_files_path, basename) for basename in files]
        
        currentfile = max(paths, key=os.path.getctime)
        currentdatafile = os.path.basename(currentfile).replace("'","")
        all_activities=json.load(open(f'''{self.data_files_path}/{currentdatafile}'''))
        return all_activities

    def create_new_file(self, new_file: list, existing_file: list) -> list:
        seen = []
        for i in new_file:
            existing_file.append(i)
        
        for x in existing_file:
            if x not in seen:
                seen.append(x)
        return seen

    def write_out_file(self, outfile: list) -> None:
        max_dates = [datetime.strptime(k['timestamp'], '%Y-%m-%d').date() for k in outfile]
        max_date = str(max(max_dates)).replace("-", "")
        output_path = os.path.join(self.data_files_path, f"HL_Summary_{max_date}.json")
        with open(output_path, "w") as of:
            json.dump(outfile, of)

    def create_future_dates_df(self, start_dt: str, end_dt: str) -> pd.DataFrame:
        df = pd.DataFrame({"timestamp": pd.date_range(start_dt, end_dt)})
        df["Year"] = df.timestamp.dt.year
        df['timestamp'] = df.timestamp.dt.strftime('%Y-%m-%d')
        return df

    def create_dataframe(self, input_file: list) -> pd.DataFrame:
        return pd.DataFrame(input_file)

    def merge_dataframes(self, date_frame: pd.DataFrame, actual_frame: pd.DataFrame) -> pd.DataFrame:
        df_merged = pd.merge(date_frame, actual_frame, how='left', on='timestamp')
        df_merged = df_merged.sort_values(by=['timestamp'])
        df_merged['training_stress_score'] = df_merged['training_stress_score'].fillna(0)
        df_merged['CTL'] = df_merged['training_stress_score'].rolling(window=42).mean()
        df_merged['timestamp'] = pd.to_datetime(df_merged['timestamp'])
        return df_merged

    def get_monthly_data(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        aggregate_df = merged_df.groupby(['yrmo'])[['Distance_miles', 'total_timer_time']].sum().reset_index()
        aggregate_df = aggregate_df.sort_values(by=['yrmo'])
        aggregate_df['total_timer_time'] = round(aggregate_df['total_timer_time'] / 3600, 2)
        aggregate_df['yrmo'] = aggregate_df['yrmo'].astype(int)
        return aggregate_df

    def get_annual_data(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        aggregate_df = merged_df.groupby(['yr'])[['Distance_miles', 'total_timer_time']].sum().reset_index()
        aggregate_df = aggregate_df.sort_values(by=['yr'])
        aggregate_df['total_timer_time'] = round(aggregate_df['total_timer_time'] / 3600, 2)
        aggregate_df['yr'] = aggregate_df['yr'].astype(int)
        return aggregate_df

    def get_daily_data(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate data by day.
        
        Args:
            merged_df: DataFrame with merged activity data
            
        Returns:
            DataFrame with daily totals
        """
        # Convert timestamp to datetime for date operations if it's not already
        if not pd.api.types.is_datetime64_any_dtype(merged_df['timestamp']):
            merged_df = merged_df.copy()
            merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'])
        
        # Create date column
        merged_df['date'] = merged_df['timestamp'].dt.date
        
        # Group by date and calculate totals
        daily_df = merged_df.groupby('date').agg({
            'Distance_miles': 'sum',
            'total_timer_time': 'sum'
        }).reset_index()
        
        # Convert time to hours
        daily_df['total_timer_time'] = round(daily_df['total_timer_time'] / 3600, 2)
        
        # Sort by date
        daily_df = daily_df.sort_values('date')
        
        # Format date for display
        daily_df['date'] = pd.to_datetime(daily_df['date']).dt.strftime('%Y-%m-%d')
        
        return daily_df

    def get_recent_rides_data(self, merged_df: pd.DataFrame, current_month: bool = False) -> pd.DataFrame:
        if current_month:
            # Use the date range already provided (should be current month)
            recent_rides = merged_df[merged_df['RidingTime'].notnull()].copy()
        else:
            # Use the traditional last 14 days
            incl = str(date.today() + timedelta(days=-14))
            recent_rides = merged_df[(merged_df['timestamp'] >= incl) & (merged_df['RidingTime'].notnull())].copy()
        
        recent_rides['date'] = recent_rides['timestamp'].dt.date
        recent_rides['Distance_miles'] = round(recent_rides['Distance_miles'], 2)
        recent_rides['total_ascent_feet'] = round(recent_rides['total_ascent_feet'], 2)
        recent_rides['total_descent_feet'] = round(recent_rides['total_descent_feet'], 2)
        recent_rides['hours'] = recent_rides['total_timer_time'] / 3600
        recent_rides['Kjs'] = round(recent_rides['Kjs'], 0)

        columns = ['yr', 'sub_sport', 'hours', 'date', 'RidingTime', 'PedalTime', 'Distance_miles', 
                  'Kjs', 'avg_power', 'max_power', 'normalized_power', 'training_stress_score', 
                  'intensity_factor', 'PowerBalance', 'avg_cadence', 'total_ascent_feet', 'total_descent_feet']
        
        recent_rides = recent_rides[columns].sort_values(by='date', ascending=False)
        
        recent_rides = recent_rides.rename(columns={
            'Distance_miles': 'Distance',
            'training_stress_score': 'TSS',
            'total_ascent_feet': 'ascent',
            'total_descent_feet': 'descent',
            'sub_sport': 'sport',
            'normalized_power': 'NP',
            'intensity_factor': 'IF'
        })
        
        return recent_rides

    def get_current_month_weekly_summary(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create weekly summaries for the current month, including weeks that overlap with the month.
        
        Args:
            merged_df: DataFrame with merged activity data for the current month
            
        Returns:
            DataFrame with weekly summaries for the current month and overlapping weeks
        """
        # Filter for rides with data
        rides_df = merged_df[merged_df['RidingTime'].notnull()].copy()
        
        if rides_df.empty:
            return pd.DataFrame()
        
        # Convert timestamp to datetime for date operations if it's not already
        if not pd.api.types.is_datetime64_any_dtype(rides_df['timestamp']):
            rides_df['timestamp'] = pd.to_datetime(rides_df['timestamp'])
        
        # Get current month and year
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Get first and last day of current month
        first_day = datetime(current_year, current_month, 1)
        if current_month == 12:
            last_day = datetime(current_year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(current_year, current_month + 1, 1) - timedelta(days=1)
        
        # Find weeks that overlap with current month
        # Calculate first day of the week (Monday) for first day of month
        first_week_start = first_day - timedelta(days=first_day.weekday())
        
        # Calculate first day of the week (Monday) for last day of month
        last_week_start = last_day - timedelta(days=last_day.weekday())
        
        # Get data for a wider range to include overlapping weeks
        extended_start = first_week_start - timedelta(days=1)  # Include previous week if needed
        extended_end = last_week_start + timedelta(days=8)    # Include next week if needed
        
        # Get all activities from relevant weeks
        all_df = self.create_dataframe(self.read_existing_files())
        all_df['timestamp'] = pd.to_datetime(all_df['timestamp'])
        
        # Filter to relevant date range
        extended_df = all_df[(all_df['timestamp'] >= extended_start) & 
                              (all_df['timestamp'] <= extended_end) &
                              all_df['RidingTime'].notnull()].copy()
        
        if extended_df.empty:
            return pd.DataFrame()
        
        # Add ISO week number and year
        extended_df['week_num'] = extended_df['timestamp'].dt.isocalendar().week
        extended_df['iso_year'] = extended_df['timestamp'].dt.isocalendar().year
        extended_df['year_week'] = extended_df['iso_year'].astype(str) + '-' + extended_df['week_num'].astype(str).str.zfill(2)
        
        # Get Monday of each activity's week
        extended_df['week_start_day'] = extended_df['timestamp'] - pd.to_timedelta(extended_df['timestamp'].dt.weekday, unit='D')
        
        # Get unique weeks in the data
        unique_weeks = extended_df[['year_week', 'week_start_day']].drop_duplicates()
        
        # Make sure we include all dates in those weeks, even if no activities
        all_weeks = []
        for _, week in unique_weeks.iterrows():
            week_start = week['week_start_day']
            week_end = week_start + timedelta(days=6)
            
            # Check if this week overlaps with current month
            if (week_start <= last_day) and (week_end >= first_day):
                all_weeks.append({
                    'year_week': week['year_week'],
                    'week_start': week_start,
                    'week_end': week_end
                })
        
        if not all_weeks:
            return pd.DataFrame()
            
        # Convert to DataFrame and sort
        weeks_df = pd.DataFrame(all_weeks)
        weeks_df = weeks_df.sort_values('week_start')
        
        # Initialize results with zero values
        results = []
        for _, week_row in weeks_df.iterrows():
            week_data = extended_df[extended_df['year_week'] == week_row['year_week']]
            
            if week_data.empty:
                week_summary = {
                    'year_week': week_row['year_week'],
                    'week_start': week_row['week_start'],
                    'week_end': week_row['week_end'],
                    'Distance': 0,
                    'Hours': 0,
                    'Kjs': 0,
                    'TSS': 0,
                    'Ascent': 0,
                    'Descent': 0
                }
            else:
                week_summary = {
                    'year_week': week_row['year_week'],
                    'week_start': week_row['week_start'],
                    'week_end': week_row['week_end'],
                    'Distance': week_data['Distance_miles'].sum(),
                    'Hours': week_data['total_timer_time'].sum() / 3600,
                    'Kjs': week_data['Kjs'].sum(),
                    'TSS': week_data['training_stress_score'].sum(),
                    'Ascent': week_data['total_ascent_feet'].sum(),
                    'Descent': week_data['total_descent_feet'].sum()
                }
            
            results.append(week_summary)
        
        # Convert to DataFrame
        weekly_summary = pd.DataFrame(results)
        
        # Format values
        weekly_summary['Hours'] = round(weekly_summary['Hours'], 1)
        weekly_summary['Distance'] = round(weekly_summary['Distance'], 1)
        weekly_summary['Kjs'] = round(weekly_summary['Kjs'], 0)
        weekly_summary['TSS'] = round(weekly_summary['TSS'], 0)
        weekly_summary['Ascent'] = round(weekly_summary['Ascent'], 0)
        weekly_summary['Descent'] = round(weekly_summary['Descent'], 0)
        
        # Extract week number for sorting
        weekly_summary['week_num'] = weekly_summary['year_week'].str.split('-').str[1].astype(int)
        
        # Format date range for each week
        weekly_summary['week_start_str'] = weekly_summary['week_start'].dt.strftime('%b %d')
        weekly_summary['week_end_str'] = weekly_summary['week_end'].dt.strftime('%b %d')
        weekly_summary['week_range'] = weekly_summary['week_start_str'] + ' - ' + weekly_summary['week_end_str']
        
        # Add month indicator for spans
        weekly_summary['current_month_marker'] = ''
        for i, row in weekly_summary.iterrows():
            start_month = row['week_start'].month
            end_month = row['week_end'].month
                
        # Sort by week start date
        weekly_summary = weekly_summary.sort_values('week_start')
        
        return weekly_summary

    def get_latest_ride_metrics(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        # Get the latest ride data
        latest_ride = merged_df[merged_df['RidingTime'].notnull()].sort_values(by='timestamp', ascending=False).iloc[0]
        
        # Create a dictionary of metrics with their display names
        metrics = {
            'Date': latest_ride['timestamp'].strftime('%Y-%m-%d'),  # Format the date properly
            'Sport': latest_ride['sub_sport'],
            'Distance (miles)': round(latest_ride['Distance_miles'], 2),
            'Riding Time': latest_ride['RidingTime'],
            'Pedal Time': latest_ride['PedalTime'],
            'Work (Kj)': f"{round(latest_ride['Kjs'], 0):,}",
            'Average Power': latest_ride['avg_power'],
            'Max Power': latest_ride['max_power'],
            'Normalized Power': latest_ride['normalized_power'],
            'Training Stress Score': latest_ride['training_stress_score'],
            'Intensity Factor': latest_ride['intensity_factor'],
            'Power Balance': latest_ride['PowerBalance'],
            'Average Cadence': latest_ride['avg_cadence'],
            'Ascent (ft)': f"{round(latest_ride['total_ascent_feet'], 0):,}",
            'Descent (ft)': f"{round(latest_ride['total_descent_feet'], 0):,}"
        }
        
        # Create DataFrame in long format
        df = pd.DataFrame({
            'Metric': list(metrics.keys()),
            'Value': list(metrics.values())
        })
        
        return df
        
    def get_weekly_totals(self, merged_df: pd.DataFrame, num_weeks: int = None) -> pd.DataFrame:
        """
        Calculate weekly distance and time totals with weeks starting on Monday.
        
        Args:
            merged_df: The merged DataFrame with all ride data
            num_weeks: Number of weeks to include (default: None = all weeks)
            
        Returns:
            DataFrame with weekly totals
        """
        # Filter for rides with data
        rides_df = merged_df[merged_df['RidingTime'].notnull()].copy()
        
        # Convert timestamp to datetime for date operations
        rides_df['timestamp'] = pd.to_datetime(rides_df['timestamp'])
        
        # Calculate week number (with Monday as start of week)
        rides_df['year'] = rides_df['timestamp'].dt.isocalendar().year
        rides_df['week'] = rides_df['timestamp'].dt.isocalendar().week
        rides_df['year_week'] = rides_df['year'].astype(str) + '-' + rides_df['week'].astype(str).str.zfill(2)
        
        # Calculate week start date (Monday)
        rides_df['week_start'] = rides_df['timestamp'].dt.to_period('W-MON').dt.start_time
        
        # Group by week and calculate totals
        weekly_totals = rides_df.groupby(['year_week', 'week_start']).agg({
            'Distance_miles': 'sum',
            'total_timer_time': 'sum'
        }).reset_index()
        
        # Sort by date
        weekly_totals = weekly_totals.sort_values('week_start', ascending=False)
        
        # Limit to requested number of weeks if specified
        if num_weeks is not None:
            weekly_totals = weekly_totals.head(num_weeks)
        
        # Convert time to hours
        weekly_totals['hours'] = weekly_totals['total_timer_time'] / 3600
        
        # Format values
        weekly_totals['Distance_miles'] = weekly_totals['Distance_miles'].round(1)
        weekly_totals['hours'] = weekly_totals['hours'].round(1)
        
        # Format week_start as 'Mon, Jan 1'
        weekly_totals['week_start'] = weekly_totals['week_start'].dt.strftime('%a, %b %d, %Y')
        
        return weekly_totals