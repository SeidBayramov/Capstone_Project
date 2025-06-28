import smtplib

sender = "seidbayramovpb25@gmail.com"
password = "ykamyydefqthtbgz"  # boşluqsuz versiya
receiver = "seidbayramli2004@gmail.com"  # buraya şəxsi emailini yaz

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    message = "Subject: Test Email\n\nThis is a test email."
    server.sendmail(sender, receiver, message)
    server.quit()
    print("Email uğurla göndərildi!")
except Exception as e:
    print("Email göndərilmədi:", str(e))
