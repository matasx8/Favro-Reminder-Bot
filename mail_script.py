import smtplib
import imghdr
from email.message import EmailMessage


class mailer():
    def __init__(self, user_email, psw):
        self.email_from = user_email
        self.psw = psw

    def send_reminders(self, users_and_tasks, column):
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(self.email_from, self.psw)
            for user in users_and_tasks.values():
                msg = EmailMessage()
                msg["To"] = user["email"]
                msg["From"] = self.email_from
                msg["Subject"] = "Reminder about stuck tasks in favro!"
                msg.set_content(f"""
                Hi {user["name"]}!

                    It seems you have stuck tasks assigned to you on the {column} column in favro.
                Be sure to check these tasks out:
                {", ".join(user["tasks"])}
                """)
                smtp.send_message(msg)
