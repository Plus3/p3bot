from flask import Flask, request, redirect, session

app = Flask(__name__)

@app.route("/api_call/",)
def smsEcho():
    print request.data
    return ""

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')