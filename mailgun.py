import customexception
import requests
from datetime import timedelta, datetime

class Email:
    API_KEY = "key-681208735ecee9dcc1364b20a78ee769"
    API_BASE_URL = "https://api.mailgun.net/v3/kloudbit.com"
    DEV_EMAIL = "clh10242016@mailinator.com"

    def __init__(self, env):
        self.env = env
        pass

    def send_invite_message(self, to):
        to = to
        html = "<html><head></head><body>"
        html += "Hello! "
        html += "<br><br>Thanks a lot for signing up for the Kloudbit Beta, the easiest way to build backend applications for web or mobile apps.  Today, we're happy to announce that Kloudbit is ready for you to explore!"
        html += "<br><br><a href='https://dashboard.kloudbit.com/createaccount'>Click Here</a> to Sign Up!"
        html += "<br><br>Remember, Kloudbit is still in 'beta' and hiccups might happen.  If you have any comments or suggestions, we'd love to hear them."
        html += "<br><br>Thank you so much for your interest!"
        html += "<br><br>--<br>Chris Hickey<br>Founder, <a href='http://www.kloudbit.com'>Kloudbit</a>"
        html += "</body></html>"

        params = {"to":to, "from":"Kloudbit Team <chris@kloudbit.com>", "subject": "Private Beta Invite", "html":html}

        if self.env == "prod":
            params["bcc"]="chris@kloudbit.com"

        return self.send_message(params)

    def send_welcome_message(self, to, name):
        to = self.DEV_EMAIL if self.env == "dev" else to
        html = "Hi "+name.split()[0]+","
        html += "<br><br>I'm really excited that you signed up for Kloudbit!"

        '''
        html += "<br><br>One quick question if you don't mind me asking...why did you sign up?"
        html += "<br><br>Please reply here and let me know.  I would love to hear more about what you're working on!"
        html += "<br><br>Also, please read our <a href='http://www.kloudbit.com/documentation'>documentation</a> or <a href='http://dashboard.kloudbit.com/'>create an application</a> to get started!"
        html += "<br><br>--<br>Chris Hickey<br>Founder, <a href='http://www.kloudbit.com'>Kloudbit</a>"
        '''

        html += "<br><br>Do you need any help getting started?"
        html += "<br><br>Please reply here and let me know.  I would love to hear more about what you're working on!"
        html += "<br><br>--<br>Chris Hickey<br>Founder, <a href='http://www.kloudbit.com'>Kloudbit</a>"

        x = datetime.now() + timedelta(minutes=15)
        deliverytime = x.strftime('%a, %w %b %Y %X') + " GMT"

        params = {"to":to, "from":"Kloudbit Team <chris@kloudbit.com>", "subject": "Welcome to Kloudbit!", "html":html, "o:deliverytime":deliverytime}

        if self.env == "prod":
            params["bcc"]="chris@kloudbit.com"

        return self.send_message(params)

    def send_message(self, params):
        url = self.API_BASE_URL + "/messages"
        auth = ("api", self.API_KEY)

        response = requests.post(url,params=params,auth=auth)
        print response
        return response


