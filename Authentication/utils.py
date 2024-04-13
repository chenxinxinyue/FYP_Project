from django.core.mail import send_mail


def send_verification_email_for_register(email, verification_code):
    try:
        send_mail(
            'Verify Your Email',
            'Your verification code is: {}'.format(verification_code),
            'no-reply@cjob.com',
            [email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False


def send_verification_email_for_reset_password(email, message_html):
    try:
        send_mail(
            'Password Reset for YourAccount',
            '',
            'no-reply@cjob.com',
            [email],
            fail_silently=False,
            html_message=message_html,
        )
        return True

    except Exception as e:
        print("Failed to send email:", e)
    return False
