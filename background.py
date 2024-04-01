import time
import os
from dotenv import load_dotenv
import pyodbc
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dbconnection import dbconnection

load_dotenv()

class AuditNotifier:
  def __init__(self):
    self.connection_string = dbconnection()
    self.sendgrid_key = os.environ.get("SENDGRID_KEY")
    
  def run(self):
    while True:
      print("Checking for Audits")

      new_audits = self.check_for_new_audits()
      if new_audits:
        for audit in new_audits:
          print("New Audit", audit)
          self.send_audit(audit)
        time.sleep(300)
      else: 
        time.sleep(300)
        
  def check_for_new_audits(self):
    with pyodbc.connect(self.connection_string) as connection:
      with connection.cursor() as cursor:
        cursor.execute("SELECT Audit_ID FROM Audits WHERE DATEDIFF(minute, Audit_Date, GETDATE()) BETWEEN 0 AND 5;")
        rows = cursor.fetchall()
        return rows if rows is not None and len(rows) > 0 else None

  def send_audit(self, audit):
    audit_id = audit[0]
    to_emails, from_email = self.fetch_audit_emails(audit_id)
    if to_emails and from_email:
      self.send_audit_emails(from_email, to_emails, templateID='d-4d777363439e446facf13553ad702ddd', audit_ID=audit_id)

  def fetch_audit_emails(self, audit_id):
    sql = 'EXEC api_CORE_SendAuditInformation @auditID=?'
    with pyodbc.connect(self.connection_string) as connection:
      with connection.cursor() as cursor:
        cursor.execute(sql, audit_id)
        to_emails = [row for row in cursor.fetchall()]
        cursor.nextset()
        from_email = cursor.fetchall()[0][0]
        return to_emails, from_email

  def send_audit_emails(self, from_email, to_emails, audit_ID, templateID=None, template=None):
      # Loop through each email address individually
      for email in to_emails:
          # Create a new Mail object for each email

          message = Mail(from_email=from_email, to_emails=email[0])
          
          # If a template ID is provided, use it
          if templateID:
              message.template_id = templateID
          # If a template is provided instead (assuming template is a dict with 'subject' and 'content'),
          # set the subject and body of the email. This part might need adjustments based on your actual template structure.
          elif template:
              message.subject = template.get('subject', '')
              message.html_content = template.get('content', '')
          
          try:
              
              # Initialize SendGrid client with your API key
              sg = SendGridAPIClient(api_key=self.sendgrid_key)
              # Send the email
              response = sg.send(message)
              # Retrieve the message ID from headers for tracking
              message_id = response.headers.get('X-Message-Id')
              print("Email sent to:", email[0], "Message ID:", message_id, "Contact ID:", email[1])
              

              sql = 'INSERT INTO Audit_Details(Contact_ID, Failed, Audit_ID, Sendgrid_Email_ID) VALUES(?, 0, ?, ?)'
              with pyodbc.connect(self.connection_string) as connection:
                with connection.cursor() as cursor:
                  cursor.execute(sql, email[1], audit_ID, message_id)
              # Your conditional logic or processing here, using `message_id` or other info as needed
              # For example:
              # if some_condition:
              #     do_something()
              
          except Exception as e:
              print(f"An error occurred while sending email to {email}: {e}")
