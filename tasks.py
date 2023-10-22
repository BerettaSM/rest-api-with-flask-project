import os
import requests
from dotenv import load_dotenv


# Worker is a separate process, it must load the environment again.
load_dotenv()


DOMAIN = os.getenv('MAILGUN_DOMAIN')
API_KEY = os.getenv('MAILGUN_API_KEY')


def send_simple_message(to, subject, body):
    return requests.post(
		url=f"https://api.mailgun.net/v3/{DOMAIN}/messages",
		auth=("api", API_KEY),
		data={
            "from": f"Excited User <mailgun@{DOMAIN}>",
			"to": [to],
			"subject": subject,
			"text": body
        }
    )


def send_user_registration_email(email, username):
    return send_simple_message(
        to=email,
        subject="Successfully signed up!",
        body=f"Hi {username}! You have successfully signed up to the Stores REST API."
    )
