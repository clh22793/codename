import customexception
import unirest

class Email:
    API_KEY = "key-681208735ecee9dcc1364b20a78ee769"
    API_BASE_URL = "https://api.mailgun.net/v3/magicstack.io"
    DEV_EMAIL = "clh10242016@mailinator.com"

    def __init__(self, env):
        self.env = env
        pass

    def send_welcome_message(self, to):
        to = self.DEV_EMAIL if self.env == "dev" else to
        html = "I'm excited that you signed up for MagicKloud."
        html += "<br><br>One quick question if you don't mind me asking...why did you sign up?"
        html += "<br><br>Reply here and let me know.  I would love to hear more about what you're working on."
        html += "<br><br>Chris"
        html += "<br><br>PS: CTA"
        html += "<br><br>--<br>Chris Hickey<br>Founder, <a href='http://www.magicstack.io'>MagicKloud.io</a>"

        params = {"to":to, "from":"MagicKloud Team <team@magicstack.io>", "subject": "Welcome to MagicKloud!", "html":html}

        self.send_message(params)

    def send_message(self, params):
        url = self.API_BASE_URL + "/messages"
        auth = ("api", self.API_KEY)

        response = unirest.post(url,params=params,auth=auth)
        print response.code
        print response.body