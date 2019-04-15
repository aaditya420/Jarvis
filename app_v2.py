import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

app_v2 = Flask(__name__)

@app_v2.route("/webhook", methods=["POST"])
def webhook():

    print("Request...")
    req = request.get_json()
    print(req)
    print(json.dumps(req, indent=4))

    resp = make_response({"ABC":"1"})
    resp.headers["Content-Type"] = "application/json"

    return resp

if __name__ == "__main__":
    app_v2.run(debug=True)