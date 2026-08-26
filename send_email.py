import os
import base64
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from app import app


def generate_report():
    """
    Calls the existing Flask report endpoint internally.

    This does NOT start a web server.
    It simply runs the same analytics engine that we already tested
    successfully in GitHub Actions.
    """

    api_key = os.getenv("APP_API_KEY", "github-action")

    client = app.test_client()

    response = client.get(
        "/report?cadence=weekly",
        headers={"X-API-Key": api_key}
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Report generation failed with status "
            f"{response.status_code}: {response.data.decode()}"
        )

    return response.get_json()


def send_email():
    """
    Generates the Traya Retail Performance Flash
    and sends it through Gmail.
    """

    # -----------------------------------------------
    # 1. Read secure values from GitHub Secrets
    # -----------------------------------------------

    gmail_user = os.environ["GMAIL_USER"]

    # Google sometimes displays app passwords with spaces.
    # Removing spaces makes the SMTP login safer.
    gmail_password = os.environ["GMAIL_APP_PASSWORD"].replace(" ", "")

    recipient_string = os.environ["RECIPIENT_EMAIL"]

    # Allows one or multiple recipients:
    # abc@gmail.com,xyz@gmail.com
    recipients = [
        email.strip()
        for email in recipient_string.split(",")
        if email.strip()
    ]

    if not recipients:
        raise ValueError("No recipient email address provided.")

    # -----------------------------------------------
    # 2. Run the analytics engine
    # -----------------------------------------------

    print("Generating Traya weekly retail flash...")

    report = generate_report()

    html_body = report["html_body"]
    images = report.get("images", {})

    print(
        f"Report generated successfully. "
        f"HTML size: {len(html_body)} characters."
    )

    # -----------------------------------------------
    # 3. Build the email
    # -----------------------------------------------

    subject = "Traya Retail Performance Flash | Weekly"

    message = MIMEMultipart("related")

    message["From"] = gmail_user
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    # Alternative container lets email clients understand
    # that HTML is the main email body.
    alternative = MIMEMultipart("alternative")

    message.attach(alternative)

    plain_text = """
Traya Retail Performance Flash

This email contains the weekly retail performance analysis.
Please view this message in an HTML-compatible email client.
"""

    alternative.attach(
        MIMEText(
            plain_text,
            "plain",
            "utf-8"
        )
    )

    alternative.attach(
        MIMEText(
            html_body,
            "html",
            "utf-8"
        )
    )

    # -----------------------------------------------
    # 4. Add inline charts
    #
    # renderer.py refers to:
    #
    # cid:funnel
    # cid:matrix
    #
    # These Content IDs make the images appear directly
    # inside the email instead of as normal attachments.
    # -----------------------------------------------

    for image_name, encoded_image in images.items():

        image_bytes = base64.b64decode(encoded_image)

        image = MIMEImage(
            image_bytes,
            _subtype="png"
        )

        image.add_header(
            "Content-ID",
            f"<{image_name}>"
        )

        image.add_header(
            "Content-Disposition",
            "inline",
            filename=f"{image_name}.png"
        )

        message.attach(image)

        print(f"Embedded image: {image_name}")

    # -----------------------------------------------
    # 5. Send using Gmail
    # -----------------------------------------------

    print(
        "Connecting to Gmail..."
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            gmail_user,
            gmail_password
        )

        smtp.sendmail(
            gmail_user,
            recipients,
            message.as_string()
        )

    print(
        f"Email sent successfully to: "
        f"{', '.join(recipients)}"
    )


if __name__ == "__main__":
    send_email()