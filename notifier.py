import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(house):
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ["EMAIL_RECIPIENT"]
    city = getattr(house, "city", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"New rental in {city}: {house.address} — €{house.price}/mo"
    msg["From"] = sender
    msg["To"] = recipient

    html = f"""
    <h2>New rental listing found!</h2>
    <table style="border-collapse:collapse;">
      <tr><td style="padding:4px 12px 4px 0"><strong>City</strong></td><td>{city}</td></tr>
      <tr><td style="padding:4px 12px 4px 0"><strong>Address</strong></td><td>{house.address}</td></tr>
      <tr><td style="padding:4px 12px 4px 0"><strong>Price</strong></td><td>€{house.price}/month</td></tr>
      <tr><td style="padding:4px 12px 4px 0"><strong>Area</strong></td><td>{house.living_area} m²</td></tr>
    </table>
    <p><a href="{house.URL}">View listing &rarr;</a></p>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, recipient, msg.as_string())
