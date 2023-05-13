from flask import *
from numpy import *
from cvzone import *
from pickle import *
import numpy as np
import re, cv2, ibm_db as ibm

app = Flask(__name__)
app.secret_key = "this is very confidential"

conn = ibm.connect(
    "DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=hyg80243;PWD=qds76Yi7MJgvZhSG;",
    "", "")

print("CONNECTED!")


@app.route("/")
def project():
    return render_template("index.html")


@app.route("/hero")
def home():
    return render_template("index.html")


@app.route("/model")
def model():
    return render_template("model.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/reg", methods=["POST", "GET"])
def signup():
    msg = ""
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE NAME = ?"
        stmt = ibm.prepare(conn, sql)
        ibm.bind_param(stmt, 1, name)
        ibm.execute(stmt)
        account = ibm.fetch_assoc(stmt)
        if account:
            return render_template("login.html", error=True)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid email address"
        else:
            insert_sql = "INSERT INTO REGISTER VALUES (?, ?, ?)"
            prep_stmt = ibm.prepare(conn, insert_sql)
            ibm.bind_param(prep_stmt, 1, name)
            ibm.bind_param(prep_stmt, 2, email)
            ibm.bind_param(prep_stmt, 3, password)
            ibm.execute(prep_stmt)
            msg = "Account created successfully"
    return render_template("login.html", msg=msg)


@app.route("/log", methods=["POST", "GET"])
def login1():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE EMAIL = ? AND PASSWORD = ?"
        stmt = ibm.prepare(conn, sql)
        ibm.bind_param(stmt, 1, email)
        ibm.bind_param(stmt, 2, password)
        ibm.execute(stmt)
        account = ibm.fetch_assoc(stmt)
        print(account)
        if account:
            session["Loggedin"] = True
            session["id"] = account["EMAIL"]
            session["email"] = account["EMAIL"]
            return render_template("model.html")
        else:
            msg = "Incorrect Email / Password"
            return render_template("login.html", msg=msg)
    else:
        return render_template("login.html")


@app.route("/predict")
def predict():
    cap = cv2.VideoCapture("carParkingInput.mp4")
    with open("parkingSlotPosition", "rb") as f:
        posList = load(f)

    width, height = 167, 58

    def checkParkingSpace(imgPro):
        spaceCounter = 0

        for pos in posList:
            x, y = pos
            imgCrop = imgPro[y: y + height, x: x + width]

            count = cv2.countNonZero(imgCrop)
            if count < 900:
                color = (0, 255, 0)
                thickness = 5
                spaceCounter += 1

            else:
                color = (0, 0, 255)
                thickness = 2

            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        putTextRect(img, f"Free : {spaceCounter}/{len(posList)}", (100, 50), scale=3, thickness=5, offset=20,
                    colorR=(0, 200, 0))

    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        success, img = cap.read()

        imgG = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgB = cv2.GaussianBlur(imgG, (3, 3), 1)
        imgT = cv2.adaptiveThreshold(imgB, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
        imgM = cv2.medianBlur(imgT, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgD = cv2.dilate(imgM, kernel, iterations=1)
        checkParkingSpace(imgD)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break


if __name__ == "__main__":
    app.run(debug=True)
