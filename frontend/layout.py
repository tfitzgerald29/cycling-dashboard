from datetime import datetime, timedelta

import dash
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output


class create_app_layout:
    def __init__(self):
        pass

    def create_layout(self):
        layout = html.Div(
            [
                html.H1(
                    "Cycling Dashboard",
                    style={"textAlign": "center", "marginBottom": 10},
                ),
                dcc.Tabs(
                    id="tabs",
                    value="recent-rides",
                    children=[
                        # Recent Rides Tab
                        dcc.Tab(
                            label="Recent Rides",
                            value="recent-rides",
                            children=[
                                html.Div(
                                    [
                                        # Monthly totals section
                                        html.H2(
                                            "Monthly Totals",
                                            style={
                                                "textAlign": "center",
                                                "marginTop": 5,
                                                "marginBottom": 5,
                                            },
                                        ),
                                        html.Div(id="monthly-totals"),
                                        # Latest ride section
                                        html.H3(
                                            "Most Recent Ride",
                                            style={
                                                "textAlign": "center",
                                                "marginTop": 5,
                                                "marginBottom": 5,
                                            },
                                        ),
                                        html.Div(id="lastride"),
                                        # Ride metrics section
                                        html.H4(
                                            "Weekly Summary",
                                            style={
                                                "textAlign": "center",
                                                "marginTop": 5,
                                                "marginBottom": 5,
                                            },
                                        ),
                                        html.Div(id="weekly-summary"),
                                        # Last 14 days section
                                        html.H4(
                                            "Last 14 Days",
                                            style={
                                                "textAlign": "center",
                                                "marginTop": 5,
                                                "marginBottom": 5,
                                            },
                                        ),
                                        html.Div(id="last-14-rides"),
                                    ]
                                )
                            ],
                        ),
                        # Distance and Time Tab
                        dcc.Tab(
                            label="Distance and Time",
                            value="distance-time",
                            children=[
                                html.Div(
                                    [
                                        html.H2(
                                            "Annual Distance and Time",
                                            style={"textAlign": "center"},
                                        ),
                                        html.Div(id="annual-distance-plot"),
                                        html.H2(
                                            "Monthly Distance and Time",
                                            style={
                                                "textAlign": "center",
                                                "marginTop": 20,
                                            },
                                        ),
                                        html.Div(id="monthly-distance-plot"),
                                        html.H2(
                                            "Weekly Distance and Time",
                                            style={
                                                "textAlign": "center",
                                                "marginTop": 20,
                                            },
                                        ),
                                        html.Div(id="weekly-totals-plot"),
                                        html.Div(
                                            [
                                                html.Label("Date Range:"),
                                                dcc.DatePickerRange(
                                                    id="distance-date-range",
                                                    start_date=(
                                                        datetime.now()
                                                        - timedelta(days=365)
                                                    ).date(),
                                                    end_date=datetime.now().date(),
                                                    display_format="YYYY-MM-DD",
                                                ),
                                            ],
                                            style={"margin": "20px 0"},
                                        ),
                                    ]
                                )
                            ],
                        ),
                        # Chronic Training Load Tab
                        dcc.Tab(
                            label="Chronic Training Load",
                            value="ctl",
                            children=[
                                html.Div(
                                    [
                                        html.H2(
                                            "CTL Graph", style={"textAlign": "center"}
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Date Range:"),
                                                dcc.DatePickerRange(
                                                    id="ctl-date-range",
                                                    start_date=(
                                                        datetime.now()
                                                        - timedelta(days=365)
                                                    ).date(),
                                                    end_date=(
                                                        datetime.now()
                                                        + timedelta(days=45)
                                                    ).date(),
                                                    display_format="YYYY-MM-DD",
                                                ),
                                            ],
                                            style={"margin": "20px 0"},
                                        ),
                                        html.Div(id="ctl-graph"),
                                        html.H2(
                                            "Monthly Training Stress Score",
                                            style={
                                                "textAlign": "center",
                                                "marginTop": 30,
                                            },
                                        ),
                                        html.Div(id="monthly-tss-graph"),
                                    ]
                                )
                            ],
                        ),
                    ],
                ),
            ]
        )
        return layout
