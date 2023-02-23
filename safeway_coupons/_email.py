import collections
import os
import subprocess
from email.mime.text import MIMEText
from typing import List, Optional

from .accounts import Account
from .errors import ClipError, Error, TooManyClipErrors
from .models import Offer
import smtplib, ssl

from .utils import TARGET_OFFER_NAME


def _send_email(
    account: Account,
    subject: str,
    mail_message: List[str],
    debug_level: int,
    send_email: bool,
) -> None:
    mail_message_str = os.linesep.join(mail_message)
    if debug_level >= 1:
        if send_email:
            print(f"Sending email to {account.mail_to}")
        else:
            print(f"Would send email to {account.mail_to}")
        print(">>>>>>")
        print(mail_message_str)
        print("<<<<<<")
    if not send_email:
        return
    # email_data = MIMEText(mail_message_str)
    # email_data["To"] = account.mail_to
    # email_data["From"] = account.mail_from
    # if subject:
    #     email_data["Subject"] = subject
    # p = subprocess.Popen(
    #     ["/usr/sbin/sendmail", "-f", account.mail_to, "-t"],
    #     stdin=subprocess.PIPE,
    # )
    # p.communicate(bytes(email_data.as_string(), "UTF-8"))

    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "alanttan1@gmail.com"  #put in your email address here
    receiver_email = "alan.tan.tian@outlook.com"  # put in your receiver email address here
    password = "tjqrhgchjuukxmsd"
    print(mail_message_str + 'Email sent')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        msg = MIMEText(mail_message_str)
        msg['Subject'] = subject
        msg['From'] = sender_email
        server.sendmail(sender_email, receiver_email, msg.as_string())


def email_clip_results(
    account: Account,
    offers: List[Offer],
    error: Optional[Error],
    clip_errors: Optional[List[ClipError]],
    debug_level: int,
    send_email: bool,
) -> None:
    offers_by_type = collections.defaultdict(list)
    # for offer in offers:
    #     offers_by_type[offer.offer_pgm].append(offer)

    target_offers = [offer for offer in offers if TARGET_OFFER_NAME == offer.description]
    expire_dates = os.linesep.join([f"{offer.end_date}" for offer in target_offers])
    mail_subject = f"Safeway coupons clipped"
    mail_message: List[str] = [
        f"Safeway account: {account.cell}\n",
        f"{account.username}\n{account.password}",
        f"Number of $5 off $5: {len(target_offers)}, expires at {expire_dates}"
    ]
    if account.username != '6508850269' or len(target_offers) > 0:
        _send_email(account, mail_subject, mail_message, debug_level, send_email)


def email_error(
    account: Account,
    error: Error,
    debug_level: int,
    send_email: bool,
) -> None:
    mail_subject = f"Safeway coupons: {error.__class__.__name__} error"
    mail_message: List[str] = [
        f"Safeway account: {account.username}",
        f"Error: {error}",
    ]
    if isinstance(error, TooManyClipErrors) and error.clipped_offers:
        mail_message += ["Clipped coupons:", ""]
        for offer in error.clipped_offers:
            mail_message += str(offer)
    _send_email(account, mail_subject, mail_message, debug_level, send_email)
