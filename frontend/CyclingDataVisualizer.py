import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
from typing import Tuple, Dict, Any

class CyclingDataVisualizer:
    def __init__(self):
        pass

    def create_monthly_distance_plot(self, monthly_data: pd.DataFrame) -> go.Figure:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Bar(
                x=monthly_data['yrmo'].astype(str),
                y=monthly_data.Distance_miles,
                name="Distance In Miles",
                text=round(monthly_data.Distance_miles, 1),
                textposition='auto'
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=monthly_data['yrmo'].astype(str),
                y=monthly_data.total_timer_time,
                name="Riding Time",
                mode='lines+markers'
            ),
            secondary_y=True
        )

        # Update layout
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="auto",
                y=.99,
                xanchor="auto",
                x=.01
            )
        )

        # Set axes titles
        fig.update_xaxes(title_text="Year and Month")
        fig.update_yaxes(title_text="Distance (miles)", secondary_y=False)
        fig.update_yaxes(title_text="Hours", secondary_y=True)

        return fig

    def create_ctl_graph(self, merged_df: pd.DataFrame, start_dt: str, end_dt: str) -> go.Figure:
        filtered_df = merged_df[
            (pd.to_datetime(merged_df['timestamp']) >= start_dt) & 
            (pd.to_datetime(merged_df['timestamp']) <= end_dt)
        ]
        
        fig = px.line(
            filtered_df,
            x='timestamp',
            y='CTL',
            width=1400,
            height=800,
            markers=True
        )
        
        return fig

    def create_annual_distance_plot(self, annual_data: pd.DataFrame) -> go.Figure:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Bar(
                x=annual_data['yr'].astype(str),
                y=annual_data.Distance_miles,
                name="Distance In Miles",
                text=round(annual_data.Distance_miles)
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=annual_data['yr'].astype(str),
                y=annual_data.total_timer_time,
                name="Riding Time",
                mode='lines+markers'
            ),
            secondary_y=True
        )

        # Update layout
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="auto",
                y=.99,
                xanchor="auto",
                x=.01
            )
        )

        # Set axes titles
        fig.update_xaxes(title_text="Year")
        fig.update_yaxes(title_text="Distance Ridden", secondary_y=False)
        fig.update_yaxes(title_text="Hours Ridden", secondary_y=True, range=[0, 400])

        return fig

    def create_recent_rides_visualizations(self, recent_rides: pd.DataFrame) -> Tuple[go.Figure, go.Figure, float, float]:
        # Create table visualization
        vals = recent_rides.columns.to_list()
        vals.remove('hours')

        fig_tbl = go.Figure(data=go.Table(
            columnwidth=[400, 400],
            header=dict(values=vals),
            cells=dict(values=[recent_rides[col] for col in vals])
        ))

        # Create graph visualization
        fig_grph = make_subplots(specs=[[{"secondary_y": True}]])

        fig_grph.add_trace(
            go.Bar(
                x=recent_rides['date'].astype(str),
                y=recent_rides.Distance,
                name="Distance In Miles",
                text=recent_rides.Distance
            ),
            secondary_y=False,
        )

        fig_grph.add_trace(
            go.Scatter(
                x=recent_rides['date'].astype(str),
                y=recent_rides.hours,
                name="Riding Time",
                mode='lines+markers'
            ),
            secondary_y=True
        )

        # Update layout
        fig_grph.update_layout(
            legend=dict(
                orientation="h",
                yanchor="auto",
                y=.99,
                xanchor="auto",
                x=.01
            )
        )

        # Set axes titles
        fig_grph.update_xaxes(title_text="Day")
        fig_grph.update_yaxes(title_text="Distance Ridden", secondary_y=False)
        fig_grph.update_yaxes(title_text="Hours Ridden", secondary_y=True, range=[0, 5])

        # Calculate summary statistics
        total_hours = round(recent_rides.hours.sum(), 1)
        total_distance = recent_rides.Distance.sum()

        return fig_tbl, fig_grph, total_hours, total_distance

    def create_daily_distance_plot(self, daily_data: pd.DataFrame) -> go.Figure:
        # Limit the number of days to avoid performance issues
        max_days = 365
        if len(daily_data) > max_days:
            print(f"Daily data has {len(daily_data)} days, limiting to last {max_days}")
            daily_data = daily_data.tail(max_days)
            
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Bar(
                x=daily_data['date'].astype(str),
                y=daily_data.Distance_miles,
                name="Distance In Miles",
                text=round(daily_data.Distance_miles, 1)
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=daily_data['date'].astype(str),
                y=daily_data.total_timer_time,
                name="Riding Time",
                mode='lines+markers'
            ),
            secondary_y=True
        )

        # Update layout
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="auto",
                y=.99,
                xanchor="auto",
                x=.01
            ),
            xaxis=dict(
                type='category',
                tickangle=-45,
                tickfont=dict(size=10),
                # Limit number of ticks for readability
                nticks=min(len(daily_data), 30)
            ),
            height=600  # Increase height for better visibility
        )

        # Set axes titles
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Distance (miles)", secondary_y=False)
        fig.update_yaxes(title_text="Hours", secondary_y=True)

        return fig

    def create_weekly_totals_plot(self, weekly_data: pd.DataFrame) -> go.Figure:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Bar(
                x=weekly_data['week_start'],
                y=weekly_data.Distance_miles,
                name="Distance In Miles",
                text=weekly_data.Distance_miles
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=weekly_data['week_start'],
                y=weekly_data.hours,
                name="Riding Time (Hours)",
                mode='lines+markers'
            ),
            secondary_y=True
        )

        # Update layout
        fig.update_layout(
            title="Weekly Distance and Time Totals (All Data)",
            title_x=0.5,
            legend=dict(
                orientation="h",
                yanchor="auto",
                y=.99,
                xanchor="auto",
                x=.01
            ),
            xaxis=dict(
                type='category',
                tickangle=-45,
                tickfont=dict(size=10),
                # Show more ticks for larger datasets
                nticks=max(20, min(len(weekly_data), 52))  # Show up to 52 ticks, but at least 20
            ),
            height=800  # Make plot taller to accommodate more data
        )

        # Set axes titles
        fig.update_xaxes(title_text="Week Starting")
        fig.update_yaxes(title_text="Distance (miles)", secondary_y=False)
        fig.update_yaxes(title_text="Hours", secondary_y=True)

        return fig

    def create_monthly_tss_plot(self, monthly_data: pd.DataFrame) -> go.Figure:
        """Create a bar chart showing Training Stress Score (TSS) by month"""
        
        # Check for different possible column names for TSS
        tss_columns = ['training_stress_score', 'TSS', 'tss_total']
        tss_column = None
        
        for col in tss_columns:
            if col in monthly_data.columns:
                tss_column = col
                break
                
        if not tss_column:
            print("Warning: No TSS column found in monthly data")
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="No Training Stress Score data available",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False
            )
            return empty_fig
            
        fig = go.Figure()
        
        # Add bar chart for monthly TSS
        fig.add_trace(
            go.Bar(
                x=monthly_data['yrmo'].astype(str),
                y=monthly_data[tss_column],
                name="Monthly TSS",
                text=[f"{int(val):,}" for val in monthly_data[tss_column]],
                textposition='auto'
            )
        )
        
        # Update layout
        fig.update_layout(
            title="Monthly Training Stress Score",
            title_x=0.5,
            xaxis_title="Year and Month",
            yaxis_title="Training Stress Score",
            height=600,
            legend=dict(
                orientation="h",
                yanchor="auto",
                y=.99,
                xanchor="auto",
                x=.01
            )
        )
        
        # Add commas to y-axis tick labels
        fig.update_yaxes(tickformat=",")
        
        return fig 