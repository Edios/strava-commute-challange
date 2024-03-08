import os,ast
from datetime import datetime

from flask import Flask, session, render_template, request, redirect, url_for

from dotenv import load_dotenv

from commute_challenge import CommuteChallenge,CommuteStatistics
from strava_auth import get_authorization_link, StravaClientData

def parse_envirorment_variable_coordinates_to_tuple(envirorment_variable:str) -> tuple:
    """
    Parse sting input like '55.000000,15.00000' to (55.000000,15.00000)
    """
    return tuple([float(coordinate) for coordinate in envirorment_variable.split(",")])

# TODO: Move variables and settings to another module
load_dotenv()
CLIENT_ID=os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
WORKPLACE_COORDINATES=parse_envirorment_variable_coordinates_to_tuple(os.getenv("WORKPLACE_COORDINATES"))
TOLERANCE_RADIUS=int(os.getenv("TOLERANCE_RADIUS"))
CHALLENGE_START_DATE = datetime(2024, 3, 1).timestamp()
CHALLENGE_FINISH_DATE = datetime(2024, 6, 1).timestamp()
PROXIES=ast.literal_eval(os.getenv("PROXIES"))

app = Flask(__name__)
app.secret_key = os.urandom(128)

@app.route("/", methods=["GET"])
def application():
    code = request.args.get("code")
    print(f"Recived code:{code}")
    if code is None:
        return redirect("/authorize")

    session["code"] = code
    strava_client_data = StravaClientData(CLIENT_ID, CLIENT_SECRET,PROXIES)
    try:
        strava_client_data.generate_refresh_token(code)
    except KeyError:
        return redirect("/authorize")

    #print(f"Generated refresh token {strava_client_data.refresh_token}")
    strava_client_data.generate_access_token()
    #print(f"Generated refresh token {strava_client_data.access_token}")
    commute_challenge = CommuteChallenge(WORKPLACE_COORDINATES,TOLERANCE_RADIUS,proxies=PROXIES)
    all_activities = commute_challenge.fetch_strava_activities(strava_client_data.access_token, before=CHALLENGE_FINISH_DATE, after=CHALLENGE_START_DATE)
    #print(f"All fetched activities {all_activities}")
    valid_commute_activities = commute_challenge.get_valid_workplace_commute_activities(all_activities)
    #print(f"Filtred out activities {valid_commute_activities}")
    commute_statistics = CommuteStatistics(activities=valid_commute_activities,target_distance = 250)
    #sum_of_kilometers = commute_challenge.sum_up_activities_distance(valid_commute_activities)
    #print(f"Sum of kilometers {sum_of_kilometers}")
    if commute_statistics.activities:
        return render_template("application.html", commute_statistics=commute_statistics)
    else:
        return render_template("no_activity_registred.html")

@app.route("/logout", methods=["GET"])
def logout():
    session["code"] = None
    return redirect("/authorize")

@app.route("/authorize", methods=["GET"])
def authorization_init():
    return render_template("authorization_link.html", url=get_authorization_link(CLIENT_ID, request.host_url))

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5000)
