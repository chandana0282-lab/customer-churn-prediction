from flask import Flask, render_template, request
from flask_mail import Mail, Message
import pickle
import csv
import os
import numpy as np

app = Flask(__name__)

# Email configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "chandana0282@gmail.com"
app.config["MAIL_PASSWORD"] = "fqtottnsksiartpd"

mail = Mail(app)

# Load model
model = pickle.load(open("model/churn_model.pkl", "rb"))

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Prediction route
@app.route("/predict", methods=["POST"])
def predict():

    gender = int(request.form["gender"])
    tenure = int(request.form["tenure"])
    monthly_charges = float(request.form["monthly_charges"])
    email = request.form["email"]

    data = np.array([[
        gender, 0, 0, 0,
        tenure, 0, 0, 0,
        0, 0, 0, 0,
        0, 0, 0, 0,
        0,
        monthly_charges,
        monthly_charges
    ]])

    prediction = model.predict(data)

    # Customer may leave
    if prediction[0] == 1:

        msg = Message(
            "Customer Churn Alert",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email]
        )

        msg.body = """
Dear Customer,

We noticed that you may not be fully satisfied with our service.

Please share your valuable suggestions using the link below:

http://127.0.0.1:5000/suggestion

Your feedback helps us improve our services.

Thank you,
Customer Support Team
"""

        mail.send(msg)
        result = "Customer may leave"

    # Customer will stay
    else:

        msg = Message(
            "Thank You",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email]
        )

        msg.body = """
Dear Customer,

Thank you for staying with us.

We appreciate your trust and support.

Thank you.
"""

        mail.send(msg)
        result = "Customer will stay"

    return render_template(
        "result.html",
        result=result,
        gender=gender,
        tenure=tenure,
        monthly_charges=monthly_charges,
    )


# Suggestion page
@app.route("/suggestion")
def suggestion():
    return render_template("suggestion.html")


# Save suggestion
@app.route("/submit_suggestion", methods=["POST"])
def submit_suggestion():

    reason = request.form["reason"]
    message = request.form["message"]

    file_exists = os.path.isfile("feedback.csv")

    with open(
        "feedback.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Reason", "Message"])

        writer.writerow([reason, message])

    return """
    <h1>Thank You For Your Suggestion!</h1>
    <h2>Feedback Saved Successfully</h2>
    <a href='/'>Go Home</a>
    """


if __name__ == "__main__":
    app.run(debug=True)