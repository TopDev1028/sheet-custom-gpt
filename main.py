import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

apikey = os.environ["API_KEY"]
openai.api_key = apikey

emailjs_endpoint = "https://api.emailjs.com/api/v1.0/email/send"
service_id = "service_fetv5k8"
template_id = "template_5h1bvic"
user_id = "7aQkQH0NpKEF62QXs"
private_key = "PJ1TRAlupgVQDXpGK2XCz"
from_email = "app.seed5406@gmail.com"


def main():
    sheet_url = "https://docs.google.com/spreadsheets/d/1ts_I-TzZKccuexTNJjrwPtLFkjIGz258I8tGS-6v_eA/edit?usp=sharing"
    base_prompt = "Hello {}, here's your weekly update for {}, {}:"

    data_rows = fetch_data_from_sheet(sheet_url)
    for row in data_rows:
        custom_prompt = create_custom_prompt(row, base_prompt)
        gpt_response = get_gpt_response(custom_prompt)

        user_email = row["Email"]
        user_email = "adamelmer0078@gmail.com"
        user_name = row["First Name"] + " " + row["Last Name"]
        send_email("Your Weekly GPT Update", gpt_response, user_email, user_name)


if __name__ == "__main__":
    main()
