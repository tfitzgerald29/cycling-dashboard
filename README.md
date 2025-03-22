# Cycling Dashboard

A dashboard for tracking and visualizing cycling metrics and performance over time.

## Features

- **Recent Rides**: View current month summary, latest ride details, and weekly breakdowns
- **Distance and Time**: Visualize annual, monthly, and weekly distance and time metrics
- **Chronic Training Load**: Track CTL metrics over time

## Setup

1. Clone the repository:
```
git clone https://github.com/tfitzgerald29/cycling-dashboard.git
cd cycling-dashboard
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Run the dashboard:
```
./run_dashboard.sh
```
Or manually:
```
python main.py
```

## Project Structure

- `main.py`: Main application file
- `frontend/`: Front-end related code
  - `dataviz.py`: Visualization components
- `backend/`: Back-end related code
  - `cyclingdataprocessor.py`: Data processing logic 