import time
import os
from dotenv import load_dotenv
import pyodbc
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from dbconnection import dbconnection

load_dotenv()

class AuditNotifier:
  def __init__(self):
    self.connection_string = dbconnection()
    self.sendgrid_key = os.environ.get("SENDGRID_KEY")
    
  def run(self):
    while True:
      new_audits = self.check_for_new_audits()
      if new_audits:
        for audit in new_audits:
          self.send_audit(audit)
        time.sleep(300)
    
  def check_for_new_audits(self):
    with pyodbc.connect(self.connection_string) as connection:
      with connection.cursor() as cursor:
        cursor.execute("SELECT Audit_ID FROM Audits WHERE Audit_ID = 5")
        rows = cursor.fetchall()
        return rows if rows else None

  def send_audit(self, audit):
    audit_id = audit[0]
    to_emails, from_email = self.fetch_audit_emails(audit_id)
    if to_emails and from_email:
      self.send_audit_emails(from_email, to_emails, templateID='d-a6f21258e2c04655b93b41397127ccac')

  def fetch_audit_emails(self, audit_id):
    sql = 'EXEC api_CORE_SendAuditInformation @auditID=?'
    with pyodbc.connect(self.connection_string) as connection:
      with connection.cursor() as cursor:
        cursor.execute(sql, audit_id)
        to_emails = [row[0] for row in cursor.fetchall()]
        cursor.nextset()
        from_email = cursor.fetchall()[0][0]
        return to_emails, from_email

  def send_audit_emails(self, from_email, to_emails, templateID=None, template=None):
    message = Mail(
      from_email=from_email, 
      to_emails=[To(email) for email in to_emails]
      )
    if templateID:
      message.template_id = templateID
    sg = SendGridAPIClient(api_key=self.sendgrid_key)
    response = sg.send(message)
    print(response.status_code, response.body, response.headers)