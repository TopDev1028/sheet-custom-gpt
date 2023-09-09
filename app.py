from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

apikey = os.environ["API_KEY"]
openai.api_key = apikey

emailjs_endpoint = "https://api.emailjs.com/api/v1.0/email/send"
service_id = "service_5peyvtk"
template_id = "template_qwhfcng"
user_id = "_lo-TOzXvazKwRmAB"

app = Flask(__name__)
CORS(app)


def get_gpt_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=1500
    )
    return response.choices[0].text.strip()


def fetch_data_from_sheet(sheet_url):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet using its URL
    sheet = client.open_by_url(sheet_url).sheet1
    data = sheet.get_all_records()

    return data


def create_custom_prompt(data_row, base_prompt):
    first_name = data_row["First Name"]
    last_name = data_row["Last Name"]
    email = data_row["Email"]
    city = data_row["City"]
    state = data_row["State"]

    formatted_prompt = (
        base_prompt.replace("[First Name]", first_name)
        .replace("[Last Name]", last_name)
        .replace("[Email]", email)
        .replace("[City]", city)
        .replace("[State]", state)
    )

    return formatted_prompt


def send_email(subject, message, to_email, to_name):
    data = {
        "service_id": service_id,
        "template_id": template_id,
        "user_id": user_id,
        "template_params": {
            "subject": subject,
            "message": message,
            "to_email": to_email,
            "to_name": to_name,
        },
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            emailjs_endpoint, data=json.dumps(data), headers=headers
        )
        if response.status_code == 200:
            print("Email sent successfully.")
        else:
            print("Error sending email:", response.text)
    except Exception as e:
        print("Error sending email:", str(e))


@app.route("/", methods=["GET", "POST"])
def process():
    if request.method == "POST":
        sheet_url = "https://docs.google.com/spreadsheets/d/1ts_I-TzZKccuexTNJjrwPtLFkjIGz258I8tGS-6v_eA/edit?usp=sharing"
        base_prompt = request.json.get("prompt")
        print(base_prompt)
        # base_prompt = "Hello [First Name] [Last Name], your email is [Email]. You live in [City], [State].:"

        data_rows = fetch_data_from_sheet(sheet_url)
        for row in data_rows:
            custom_prompt = create_custom_prompt(row, base_prompt)
            gpt_response = get_gpt_response(custom_prompt)

            user_email = row["Email"]
            user_name = row["First Name"]
            send_email("Email for Your Clients", gpt_response, user_email, user_name)
        return jsonify({"response": gpt_response})

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
