import gspread
from google.oauth2.service_account import Credentials
import uuid
import qrcode
from email.message import EmailMessage
import smtplib

EMAIL = "doestovesky1@gmail.com"
APP_PASSWORD = "vquu ieky dyui wdze"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def generate_qr(name, email, reg_id):

    qr_data = f"{reg_id}|{name}|{email}"

    img = qrcode.make(qr_data)

    img.save(f"qr_codes/{reg_id}.png")


def send_email(name, email, reg_id):

    msg = EmailMessage()

    msg["Subject"] = "Event Registration Confirmed"
    msg["From"] = EMAIL
    msg["To"] = email

    msg.set_content("Please view this email in HTML format.")

    msg.add_alternative(f"""
<html>
<body style="font-family: Arial;">

<h2 style="color:#2563eb;">
Registration Confirmed
</h2>

<p>Hello <b>{name}</b>,</p>

<p>
Thank you for registering for our event.
</p>

<div style="
border:1px solid #ddd;
padding:15px;
border-radius:10px;
width:300px;
">

<h3>Your Registration Details</h3>

<p>
<b>Registration ID:</b><br>
{reg_id}
</p>

</div>

<p>
Your QR code is attached to this email.
</p>

<p>
Regards,<br>
Event Team
</p>

</body>
</html>
""", subtype="html")

    qr_path = f"qr_codes/{reg_id}.png"

    with open(qr_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="image",
            subtype="png",
            filename=f"{reg_id}.png"
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(msg)


creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open(
    "Event Registration Form Responses"
).sheet1

rows = sheet.get_all_records()

for i, row in enumerate(rows, start=2):

    if not row["Your name?"]:
        continue

    if row.get("Registration ID"):
        continue

    registration_id = f"EVT-{uuid.uuid4().hex[:6].upper()}"

    generate_qr(
        row["Your name?"],
        row["Your email?"],
        registration_id
    )

    sheet.update_cell(i, 6, registration_id)

    send_email(
        row["Your name?"],
        row["Your email?"],
        registration_id
    )

    print(
        f"Generated QR and sent email to "
        f"{row['Your email?']} "
        f"({registration_id})"
    )