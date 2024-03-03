import os

from flask import Flask, session, render_template, request, redirect, url_for

from commute_challenge import CommuteChallenge
from strava_auth import get_authorization_link, StravaClientData

app = Flask(__name__)
app.secret_key = os.urandom(12)


def authorization_data_provided() -> bool:
    return "client_id" in session and "client_secret" in session


@app.route("/", methods=["POST", "GET"])
def authorization_init():
    if request.method == "POST":
        client_id = request.form["client_id"]
        session["client_id"] = client_id
        client_secret = request.form["client_secret"]
        session["client_secret"] = client_secret
        session["url"] = get_authorization_link(client_id, f"{request.host_url}application")
        return redirect(url_for("authorization_link"))
    else:
        return render_template('index.html')


@app.route("/authorization_link")
def authorization_link():
    if authorization_data_provided():
        return render_template("authorization_link.html", url=session["url"])
    else:
        redirect(url_for("index"))


# TODO: Add checking for &code= in get
@app.route("/application")
def application():
    code = request.args.get("code")
    print(code)
    session["code"] = code
    strava_client_data = StravaClientData(session["client_id"], session["client_secret"])
    strava_client_data.generate_refresh_token(code)
    strava_client_data.generate_access_token()

    commute_challenge = CommuteChallenge()
    all_activities = commute_challenge.fetch_strava_activities(strava_client_data.access_token)
    valid_commute_activities = commute_challenge.get_valid_workplace_commute_activities(all_activities)
    sum_of_kilometers = commute_challenge.sum_up_activities_distance(valid_commute_activities)
    return render_template("application.html", sum_of_kilometers=sum_of_kilometers)


if __name__ == "__main__":
    app.run(debug=True)
