# Commute Challenge Application

This Flask application integrates with the Strava API to track and validate commute activities for a challenge. It calculates the sum of kilometers commuted to a workplace within a specified challenge period.

## Features

- Strava OAuth2 authorization flow
- Fetching Strava activities within a challenge timeframe
- Filtering valid commute activities based on proximity to workplace coordinates
- Summing up the distance of valid commute activities

## Requirements

- Python 3.x
- Flask
- python-dotenv
- A Strava account with an application to obtain `CLIENT_ID` and `CLIENT_SECRET`

## Installation

1. Clone the repository:
git clone https://github.com/Edios/strava-commute-challange
cd commute-challenge-app

2. Install the required Python packages:
pip install -r requirements.txt

3. Create a `.env` file in the root directory with the following environment variables:
`
CLIENT_ID=your_strava_client_id
CLIENT_SECRET=your_strava_client_secret
WORKPLACE_COORDINATES=latitude,longitude
TOLERANCE_RADIUS=radius_in_meters
PROXIES={‘http’: ‘http://your_proxy’, ‘https’: ‘https://your_proxy’} # Optional- can be removed from app.py
`
## Usage

1. Start the Flask application:
python app.py
2. Navigate to `http://IP_HERE:5000/` in your web browser.
3. Follow the authorization link to authorize the application with your Strava account.
4. After authorization, the application will display the sum of kilometers commuted to the workplace during the challenge period.

## Development

- Set `debug=True` in `app.run()` for enabling Flask's debug mode.
- TODO: Move variables and settings to another module for better configuration management.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.