from datetime import date
import json
import os


def make_serializable(data):
    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.strftime("%Y-%m-%d")
    return data


def save_booking_to_json(booking_data, filename="../appointments.json"):
    booking_data = make_serializable(booking_data)


    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                data = json.load(file)
        else:
            data = []
    except json.JSONDecodeError:

        data = []


    data.append(booking_data)

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)