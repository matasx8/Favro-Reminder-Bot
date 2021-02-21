from apscheduler.schedulers.background import BackgroundScheduler
from favroAPI import favroAPI
from dataHandler import dataHandler
from mail_script import mailer
from flask import Flask
from datetime import datetime
from datetime import timedelta
import atexit
import json


app = Flask(__name__)


@app.route("/")
def starter():
    return "Stuck Task reminder v1"


@app.route("/json", methods=["GET"])
def get_req():
    """
    Handle get request
    """
    settings = read_settings()

    # variables
    org_id = {"organizationId": settings["favroInfo"]["organizationId"]}
    widget_common_id = (
        'widgetCommonId', settings["favroInfo"]["widgetCommonId"])
    email = settings["favroInfo"]["email"]
    token = settings["favroInfo"]["token"]
    desired_column = settings["favroInfo"]["desiredColumn"]

    # all columns
    all_columns = favroAPI.get_all_columns(
        org_id, email, token, (widget_common_id,))
    if isinstance(all_columns, str):
        print(all_columns)
        return 500

    # find desired column id
    column_id = dataHandler.extract_desired_column_id(
        all_columns, desired_column)

    # get all tasks
    json_list = favroAPI.get_json(org_id, email, token,
                                  ((widget_common_id), ("columnId", column_id)))
    if isinstance(json_list, str):
        print(json_list)
        return 500

    # return filtered stuck tasks
    return json.dumps(dataHandler.extract_cards_from_json(json_list, 72), indent=4)


def setup_schedule():
    """schedules check and mail script for every work day"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_mail, trigger="cron", day_of_week='mon-fri', hour=8,
                      minute=0)
    # scheduler.add_job(func=check_and_mail, trigger="interval",
    #                 seconds=20)  # for testing
    scheduler.start()
    # scheduler.
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


def setup_try_again_schedule():
    """schedules check and mail script in 1 hr"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_and_mail, trigger="date",
                      run_date=datetime.now() + timedelta(hours=1))
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())


def read_settings():
    """reads setting file"""
    with open("settings.json") as f:
        return json.load(f)


def check_and_mail():
    """script for checking favro api and sending mail"""
    # variables
    try:
        settings = read_settings()
    except FileNotFoundError as e:
        print(e)
        setup_try_again_schedule()
        return
    else:
        org_id = {"organizationId": settings["favroInfo"]["organizationId"]}
        widget_common_id = (
            'widgetCommonId', settings["favroInfo"]["widgetCommonId"])
        desired_column = settings["favroInfo"]["desiredColumn"]
        email = settings["favroInfo"]["email"]
        token = settings["favroInfo"]["token"]
        mailer_email = settings["mailer"]["email"]
        mailer_psw = settings["mailer"]["psw"]

        # get all columns in widget and retrieve Reviewing column id
        all_columns = favroAPI.get_all_columns(
            org_id, email, token, (widget_common_id,))
        if isinstance(all_columns, str):
            print(all_columns)
            setup_try_again_schedule()
            return
        column_id = dataHandler.extract_desired_column_id(
            all_columns, desired_column)

        # gets cards from favro
        response_json = favroAPI.get_json(org_id, email, token, (widget_common_id,
                                                                 ("columnId", column_id)))
        if isinstance(response_json, str):
            print(response_json)
            setup_try_again_schedule()
            return

        # Gets cards that are older than 3 days, boils down json
        filtered_response_json = dataHandler.extract_cards_from_json(
            response_json, hour_limit=72)

        # Finds unique assigned users and gets their data
        unique_assigned_users = dataHandler.extract_unique_assigned_users_from_json(
            filtered_response_json)

        user_data = get_assigned_user_data(
            unique_assigned_users, org_id, email, token)
        if isinstance(user_data, str):
            print(user_data)
            setup_try_again_schedule()
            return

        # merge data for email sender
        users_and_tasks = dataHandler.merge_user_data_and_cards(
            user_data, filtered_response_json)

        # send emails
        try:
            mailer(mailer_email, mailer_psw).send_reminders(
                users_and_tasks, desired_column)
        except Exception:
            print("Exception caught in mailer script, will try again in 1h")


# protect from errors
def get_assigned_user_data(unique_assigned_users, org_id, email, token):
    """
    Gets names and emails that match the user ids

    Args:
        unique_assigned_users (dict): unique users who have cards assigned to them

    Returns: 

    dict: users with their info
    """
    all_users_from_page = favroAPI.get_users_json(org_id, email, token)
    if isinstance(all_users_from_page, str):
        return all_users_from_page
    user_data = dataHandler.extract_users_from_json(
        all_users_from_page, unique_assigned_users)
    i = 0
    while len(user_data) < len(unique_assigned_users):
        if i > 200:
            return "Something went wrong, while loop trying to go forever"
        all_users_from_page = favroAPI.get_users_json(
            org_id, email, token, (("requestId", all_users_from_page["requestId"]), ("page", all_users_from_page["page"] + 1)))
        if isinstance(all_users_from_page, str):
            return all_users_from_page
        user_data.update(dataHandler.extract_users_from_json(
            all_users_from_page, unique_assigned_users))
    return user_data


if __name__ == "__main__":
    setup_schedule()
    app.run(debug=False)
