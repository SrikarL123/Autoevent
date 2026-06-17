import cv2
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

spreadsheet = client.open("Event Registration Form Responses")
print("Spreadsheet URL:")
print(spreadsheet.url)

attendance_sheet = spreadsheet.worksheet("Attendance")
print("Connected to:", attendance_sheet.title)

attendance_sheet.append_row(
    ["TEST", "TEST", "TEST", "TEST", "TEST"]
)

print("Test row added")

detector = cv2.QRCodeDetector()

cap = cv2.VideoCapture(0)

scanned_ids = set()

while True:

    success, frame = cap.read()

    data, bbox, _ = detector.detectAndDecode(frame)

    if data:

        reg_id, name, email = data.split("|")

        if reg_id not in scanned_ids:

            scanned_ids.add(reg_id)

            timestamp = datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )

            attendance_sheet.update("A2:E2", [[
                reg_id,
                name,
                email,
                timestamp,
                "Present"
            ]])

            print(
                f"{name} marked present"
            )

    cv2.imshow("QR Scanner", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()