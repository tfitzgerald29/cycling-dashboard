# Cycling Dashboard

A dashboard for tracking and visualizing cycling metrics and performance over time.

dashboard is packaged up and runs via run_dashboard.sh or mac application. The backend scrubs new files and appends to previous .json file and creates new .json with latest data. The data is then read into mem and the web browser (hosted locally) is lauched with various views. Using Dash for frontend.

## Features

- **Recent Rides**: View current month summary, latest ride details, and weekly breakdowns
- **Distance and Time**: Visualize annual, monthly, and weekly distance and time metrics
- **Chronic Training Load**: Track CTL metrics over time

## Setup

1. Clone the repository:
```
git clone https://github.com/tfitzgerald29/cycling-dashboard.git
```
