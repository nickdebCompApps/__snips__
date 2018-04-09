from twilio.rest import Client
from keys import key

class Messenger():
    def __init__(self):
        self.account_sid = key.api_keys['TWILIO_SID']
        self.auth_token = key.api_keys['TWILIO_TOKEN']
        self.client = Client(self.account_sid, self.auth_token)
        self.body = None

    def send_sms(self):
        message = self.client.api.messages.create(
            to="+18609667758",
            body=self.body,
            from_="+18603563068"
        )


