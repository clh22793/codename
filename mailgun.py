import customexception
#import unirest
import requests

class Email:
    #API_KEY = "key-681208735ecee9dcc1364b20a78ee769"
    API_KEY = "key-681208735ecee9dcc1364b20a78ee769"
    #API_BASE_URL = "https://api.mailgun.net/v3/magicstack.io"
    API_BASE_URL = "https://api.mailgun.net/v3/kloudbit.com"
    DEV_EMAIL = "clh10242016@mailinator.com"

    def __init__(self, env):
        self.env = env
        pass

    def send_welcome_message(self, to, name):
        to = self.DEV_EMAIL if self.env == "dev" else to
        html = "Hi "+name.split()[0]+","
        html += "<br><br>I'm really excited that you signed up for Kloudbit!"
        html += "<br><br>One quick question if you don't mind me asking...why did you sign up?"
        html += "<br><br>Please reply here and let me know.  I would love to hear more about what you're working on."
        html += "<br><br>Chris"
        html += "<br><br>PS: Read our <a href='http://www.kloudbit.com/documentation'>documentation</a> or <a href='http://dashboard.kloudbit.com/'>create an API</a> to get started!"
        html += "<br><br>--<br>Chris Hickey<br>Founder, <a href='http://www.kloudbit.com'>Kloudbit</a>"

        params = {"to":to, "cc":"chris@kloudbit.com", "from":"Kloudbit Team <chris@kloudbit.com>", "subject": "Welcome to Kloudbit!", "html":html}

        self.send_message(params)

    def send_message(self, params):
        url = self.API_BASE_URL + "/messages"
        auth = ("api", self.API_KEY)

        response = requests.post(url,params=params,auth=auth)
        print response


