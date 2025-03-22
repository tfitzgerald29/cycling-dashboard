import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime, timedelta
from backend.cyclingdataprocessor import CyclingDataProcessor
from frontend.dataviz import CyclingDataVisualizer
import webbrowser
from threading import Timer
import pandas as pd

def open_browser():
    webbrowser.open('http://127.0.0.1:8050/')

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Initialize data processor and visualizer
data_processor = CyclingDataProcessor()
visualizer = CyclingDataVisualizer()

# Process any new files before starting the app
print("Processing new files...")
new_data = data_processor.process_new_files()
existing_data = data_processor.read_existing_files()

if new_data:
    updated_data = data_processor.create_new_file(new_data, existing_data)
    data_processor.write_out_file(updated_data)
    print(f"Processed {len(new_data)} new files")
else:
    print("No new files to process, using latest data file")

# Create the base dataframe with all data
all_data_df = data_processor.create_dataframe(existing_data)

# Get date ranges from the data
if not all_data_df.empty:
    timestamps = pd.to_datetime(all_data_df['timestamp'])
    min_date = timestamps.min().strftime('%Y-%m-%d')
    max_date = timestamps.max().strftime('%Y-%m-%d')
else:
    min_date = str(datetime.now().date() - timedelta(days=365*5))  # 5 years back as fallback
    max_date = str(datetime.now().date())

print(f"Data range: {min_date} to {max_date}")

# Create date ranges
current_month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
current_month_end = str(datetime.now().date())
recent_date_range = data_processor.create_future_dates_df(
    current_month_start,
    current_month_end
)
full_date_range = data_processor.create_future_dates_df(min_date, max_date)

# Create merged dataframes for different views
recent_merged_df = data_processor.merge_dataframes(recent_date_range, all_data_df)
full_merged_df = data_processor.merge_dataframes(full_date_range, all_data_df)

# Create the specific dataframes for visualizations
recent_rides = data_processor.get_recent_rides_data(recent_merged_df, current_month=True)
latest_ride_metrics = data_processor.get_latest_ride_metrics(full_merged_df)
weekly_totals = data_processor.get_weekly_totals(full_merged_df)

# Get current month weekly summaries
current_month_weekly_summary = data_processor.get_current_month_weekly_summary(recent_merged_df)

print(f"Found {len(weekly_totals)} weeks of data")
print(f"Found {len(all_data_df)} total activities")
print(f"Found {len(recent_rides)} activities in current month")

# Define the layout
app.layout = html.Div([
    html.H1('Cycling Dashboard', style={'textAlign': 'center', 'marginBottom': 30}),
    
    dcc.Tabs(id='tabs', value='recent-rides', children=[
        # Recent Rides Tab
        dcc.Tab(label='Recent Rides', value='recent-rides', children=[
            html.Div([
                html.H2('Current Month Summary', style={'textAlign': 'center'}),
                html.P(
                    "Shows data for the current month, including weeks that overlap with previous or next month.", 
                    style={'textAlign': 'center', 'fontStyle': 'italic', 'color': '#666'}
                ),
                html.Div(id='recent-rides-stats', style={'textAlign': 'center', 'marginBottom': 20}),
                html.H3('Latest Ride Details', style={'textAlign': 'center', 'marginTop': 30}),
                html.Div(id='latest-ride-metrics'),
                html.H3('Current Month Overview', style={'textAlign': 'center', 'marginTop': 30}),
                html.Div(id='recent-rides-graph'),
                html.H3('Current Month Rides', style={'textAlign': 'center', 'marginTop': 30}),
                html.Div(id='recent-rides-table')
            ])
        ]),
        
        # Distance and Time Tab
        dcc.Tab(label='Distance and Time', value='distance-time', children=[
            html.Div([
                html.H2('Annual Distance and Time', style={'textAlign': 'center'}),
                html.Div(id='annual-distance-plot'),
                html.H2('Monthly Distance and Time', style={'textAlign': 'center', 'marginTop': 30}),
                html.Div(id='monthly-distance-plot'),
                html.H2('Weekly Distance and Time', style={'textAlign': 'center', 'marginTop': 30}),
                html.Div(id='weekly-totals-plot'),
                html.Div([
                    html.Label('Date Range:'),
                    dcc.DatePickerRange(
                        id='distance-date-range',
                        start_date=(datetime.now() - timedelta(days=365)).date(),
                        end_date=datetime.now().date(),
                        display_format='YYYY-MM-DD'
                    )
                ], style={'margin': '20px 0'})
            ])
        ]),
        
        # Chronic Training Load Tab
        dcc.Tab(label='Chronic Training Load', value='ctl', children=[
            html.Div([
                html.H2('CTL Graph', style={'textAlign': 'center'}),
                html.Div([
                    html.Label('Date Range:'),
                    dcc.DatePickerRange(
                        id='ctl-date-range',
                        start_date=(datetime.now() - timedelta(days=365)).date(),
                        end_date=datetime.now().date(),
                        display_format='YYYY-MM-DD'
                    )
                ], style={'margin': '20px 0'}),
                html.Div(id='ctl-graph')
            ])
        ])
    ])
])

# Callback for Recent Rides tab
@app.callback(
    [Output('recent-rides-table', 'children'),
     Output('recent-rides-graph', 'children'),
     Output('recent-rides-stats', 'children'),
     Output('latest-ride-metrics', 'children')],
    Input('tabs', 'value')
)
def update_recent_rides(tab):
    print(f"Recent rides data shape: {recent_rides.shape if hasattr(recent_rides, 'shape') else 'No shape'}")
    
    # Create visualizations using pre-processed data
    fig_table, fig_graph, total_hours, total_distance = visualizer.create_recent_rides_visualizations(recent_rides)
    
    # Get the month name
    current_month_name = datetime.now().strftime('%B %Y')
    
    # Create weekly summary stats
    if not current_month_weekly_summary.empty:
        # Create a formatted HTML table for the weekly summaries
        table_header = [
            html.Thead(html.Tr([
                html.Th("Week"), 
                html.Th("Distance (mi)"), 
                html.Th("Hours"), 
                html.Th("Work (Kj)"), 
                html.Th("TSS"), 
                html.Th("Ascent (ft)"), 
                html.Th("Descent (ft)")
            ]))
        ]
        
        rows = []
        for _, week in current_month_weekly_summary.iterrows():
            row = html.Tr([
                html.Td(week['week_range']),
                html.Td(f"{week['Distance']:.1f}"),
                html.Td(f"{week['Hours']:.1f}"),
                html.Td(f"{week['Kjs']:,.0f}"),
                html.Td(f"{week['TSS']:.0f}"),
                html.Td(f"{week['Ascent']:,.0f}"),
                html.Td(f"{week['Descent']:,.0f}")
            ])
            rows.append(row)
        
        # Add totals row
        total_distance = current_month_weekly_summary['Distance'].sum()
        total_hours = current_month_weekly_summary['Hours'].sum()
        total_kjs = current_month_weekly_summary['Kjs'].sum()
        total_tss = current_month_weekly_summary['TSS'].sum()
        total_ascent = current_month_weekly_summary['Ascent'].sum()
        total_descent = current_month_weekly_summary['Descent'].sum()
        
        total_row = html.Tr([
            html.Td("TOTAL", style={'fontWeight': 'bold'}),
            html.Td(f"{total_distance:.1f}", style={'fontWeight': 'bold'}),
            html.Td(f"{total_hours:.1f}", style={'fontWeight': 'bold'}),
            html.Td(f"{total_kjs:,.0f}", style={'fontWeight': 'bold'}),
            html.Td(f"{total_tss:.0f}", style={'fontWeight': 'bold'}),
            html.Td(f"{total_ascent:,.0f}", style={'fontWeight': 'bold'}),
            html.Td(f"{total_descent:,.0f}", style={'fontWeight': 'bold'})
        ], style={'backgroundColor': '#f2f2f2'})
        
        rows.append(total_row)
        
        table_body = [html.Tbody(rows)]
        
        weekly_table = html.Table(
            table_header + table_body,
            style={
                'width': '100%',
                'textAlign': 'center',
                'borderCollapse': 'collapse'
            }
        )
        
        monthly_totals = html.Div([
            html.H4(f"Monthly Totals for {current_month_name}"),
            html.P([
                f"Total Distance: {current_month_weekly_summary['Distance'].sum():.1f} miles | ",
                f"Total Hours: {current_month_weekly_summary['Hours'].sum():.1f} | ",
                f"Total Work: {current_month_weekly_summary['Kjs'].sum():,.0f} Kj | ",
                f"Total TSS: {current_month_weekly_summary['TSS'].sum():.0f}"
            ]),
            html.H4("Weekly Breakdown (includes overlapping weeks)"),
            weekly_table
        ])
    else:
        monthly_totals = html.Div([
            html.H4(f"No rides found for {current_month_name}")
        ])
    
    # Create latest ride metrics table
    latest_metrics_fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Metric', 'Value'],
            font=dict(size=12, color='black', family='Arial Black')
        ),
        cells=dict(values=[latest_ride_metrics['Metric'], latest_ride_metrics['Value']])
    )])
    
    return dcc.Graph(figure=fig_table), dcc.Graph(figure=fig_graph), monthly_totals, dcc.Graph(figure=latest_metrics_fig)

# Callback for Distance and Time tab
@app.callback(
    [Output('annual-distance-plot', 'children'),
     Output('monthly-distance-plot', 'children'),
     Output('weekly-totals-plot', 'children')],
    [Input('distance-date-range', 'start_date'),
     Input('distance-date-range', 'end_date')]
)
def update_distance_time_plots(start_date, end_date):
    try:
        # Create new date range dataframe for the selected period
        date_range = data_processor.create_future_dates_df(start_date, end_date)
        merged_df = data_processor.merge_dataframes(date_range, all_data_df)
        
        print(f"Distance Time Tab: Processing data for {start_date} to {end_date}")
        print(f"Data shape: {merged_df.shape}")
        
        # Check if we have any data
        if merged_df.empty:
            print("No data available for the selected date range")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available for the selected date range",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return dcc.Graph(figure=empty_fig), dcc.Graph(figure=empty_fig), dcc.Graph(figure=empty_fig)
        
        # Create visualizations
        print("Creating annual data...")
        annual_data = data_processor.get_annual_data(merged_df)
        print(f"Annual data shape: {annual_data.shape}")
        
        print("Creating monthly data...")
        monthly_data = data_processor.get_monthly_data(merged_df)
        print(f"Monthly data shape: {monthly_data.shape}")
        
        print("Creating weekly data...")
        weekly_data = data_processor.get_weekly_totals(merged_df)
        print(f"Weekly data shape: {weekly_data.shape}")
        
        annual_plot = visualizer.create_annual_distance_plot(annual_data)
        monthly_plot = visualizer.create_monthly_distance_plot(monthly_data)
        weekly_plot = visualizer.create_weekly_totals_plot(weekly_data)
        
        return dcc.Graph(figure=annual_plot), dcc.Graph(figure=monthly_plot), dcc.Graph(figure=weekly_plot)
    except Exception as e:
        import traceback
        print(f"Error in update_distance_time_plots: {str(e)}")
        print(traceback.format_exc())
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return dcc.Graph(figure=empty_fig), dcc.Graph(figure=empty_fig), dcc.Graph(figure=empty_fig)

# Callback for Chronic Training Load tab
@app.callback(
    Output('ctl-graph', 'children'),
    [Input('ctl-date-range', 'start_date'),
     Input('ctl-date-range', 'end_date')]
)
def update_ctl_graph(start_date, end_date):
    try:
        # Create new date range dataframe for the selected period
        date_range = data_processor.create_future_dates_df(start_date, end_date)
        merged_df = data_processor.merge_dataframes(date_range, all_data_df)
        
        # Check if we have any data
        if merged_df.empty:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No data available for the selected date range",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return dcc.Graph(figure=empty_fig)
        
        # Create visualizations
        ctl_plot = visualizer.create_ctl_graph(merged_df, start_date, end_date)
        
        return dcc.Graph(figure=ctl_plot)
    except Exception as e:
        print(f"Error in update_ctl_graph: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Error loading data: {str(e)}",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return dcc.Graph(figure=empty_fig)

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(debug=True, port=8050) 