import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from jinja2 import Template
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)

# Email templates
SHORTLIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f4f4f4; padding: 10px; text-align: center; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Congratulations! You've been shortlisted</h1>
    </div>
    <div class="content">
        <p>Dear {{ candidate_name }},</p>
        
        <p>We are pleased to inform you that you have been <strong>shortlisted</strong> for the position of <strong>{{ job_title }}</strong>.</p>
        
        <p>Your application stood out among many candidates, and we would like to proceed to the next stage of our recruitment process.</p>
        
        <h3>Next Steps:</h3>
        <ul>
            <li>Our HR team will contact you within 2-3 business days</li>
            <li>Please keep your phone available for scheduling an interview</li>
            <li>Prepare any additional documents that may be requested</li>
        </ul>
        
        <p>We look forward to speaking with you soon!</p>
        
        <p>Best regards,<br>
        The Recruitment Team</p>
    </div>
    <div class="footer">
        <p>This is an automated message. Please do not reply to this email.</p>
    </div>
</body>
</html>
"""

def send_email(to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
    """Send an email using SMTP"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        
        # Create the HTML part
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        # Connect to server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_shortlist_notification(candidate: Dict, job_title: str) -> bool:
    """Send shortlist notification to candidate"""
    if not candidate.get("email"):
        print(f"No email found for candidate {candidate.get('name')}")
        return False
    
    # Render template
    template = Template(SHORTLIST_TEMPLATE)
    html_content = template.render(
        candidate_name=candidate.get("name", "Candidate"),
        job_title=job_title
    )
    
    # Create text version
    text_content = f"""
    Dear {candidate.get("name", "Candidate")},
    
    Congratulations! You have been shortlisted for the position of {job_title}.
    
    Our HR team will contact you within 2-3 business days to schedule an interview.
    
    Best regards,
    The Recruitment Team
    """
    
    subject = f"Shortlisted for {job_title} Position"
    
    return send_email(candidate["email"], subject, html_content, text_content)

def send_shortlist_email(candidate_email: str, candidate_name: str, position: str, interview_date: str):
    """Send shortlist notification email to candidate"""
    try:
        # Email configuration
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = candidate_email
        msg['Subject'] = f"Congratulations! You've been shortlisted for {position}"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Congratulations, {candidate_name}!</h2>
                
                <p>We are pleased to inform you that you have been <strong>shortlisted</strong> for the position of <strong>{position}</strong>.</p>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">Next Steps</h3>
                    <p><strong>Interview Date:</strong> {interview_date}</p>
                    <p>Please confirm your availability for the interview by replying to this email.</p>
                </div>
                
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0;">What to Expect:</h4>
                    <ul>
                        <li>Technical discussion about your experience</li>
                        <li>Behavioral interview questions</li>
                        <li>Q&A session about the role and company</li>
                    </ul>
                </div>
                
                <p>We look forward to meeting you and learning more about your qualifications.</p>
                
                <p>Best regards,<br>
                <strong>Talent Matcher Team</strong><br>
                HR Department</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, candidate_email, text)
        server.quit()
        
        print(f"Shortlist email sent successfully to {candidate_name} ({candidate_email})")
        return True
        
    except Exception as e:
        print(f"Failed to send shortlist email: {str(e)}")
        return False

def send_rejection_email(candidate_email: str, candidate_name: str, position: str, rejection_reasons: List[str]):
    """Send rejection notification email to candidate"""
    try:
        # Email configuration
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = candidate_email
        msg['Subject'] = f"Application Update - {position}"
        
        # Format rejection reasons
        reasons_html = ""
        for reason in rejection_reasons:
            reasons_html += f"<li>{reason}</li>"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c5aa0;">Thank you for your interest, {candidate_name}</h2>
                
                <p>Thank you for taking the time to apply for the <strong>{position}</strong> position with our company.</p>
                
                <p>After careful consideration of your application and qualifications, we have decided to move forward with other candidates whose profiles more closely align with our current requirements.</p>
                
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107;">
                    <h4 style="margin-top: 0; color: #856404;">Areas for consideration:</h4>
                    <ul style="margin-bottom: 0;">
                        {reasons_html}
                    </ul>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h4 style="margin-top: 0; color: #0c5460;">We encourage you to:</h4>
                    <ul style="margin-bottom: 0;">
                        <li>Continue developing your skills in the mentioned areas</li>
                        <li>Apply for future positions that match your profile</li>
                        <li>Stay connected with us for upcoming opportunities</li>
                    </ul>
                </div>
                
                <p>We appreciate your interest in our company and wish you the best in your career endeavors.</p>
                
                <p>Best regards,<br>
                <strong>Talent Matcher Team</strong><br>
                HR Department</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connect and send
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, candidate_email, text)
        server.quit()
        
        print(f"Rejection email sent successfully to {candidate_name} ({candidate_email})")
        return True
        
    except Exception as e:
        print(f"Failed to send rejection email: {str(e)}")
        return False

def send_bulk_shortlist_notifications(candidates: List[Dict], job_title: str) -> Dict:
    """Send shortlist notifications to multiple candidates"""
    results = {
        "sent": 0,
        "failed": 0,
        "errors": []
    }
    
    for candidate in candidates:
        try:
            if send_shortlist_notification(candidate, job_title):
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to send to {candidate.get('name')}")
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"Error with {candidate.get('name')}: {str(e)}")
    
    return results

def test_email_configuration() -> bool:
    """Test email configuration"""
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.quit()
        return True
    except Exception as e:
        print(f"Email configuration test failed: {e}")
        return False