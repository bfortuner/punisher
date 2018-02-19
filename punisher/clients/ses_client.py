import boto3
import punisher.config as cfg

EMAIL_CHARSET = 'UTF-8'
HEADER="<html>"
FOOTER="</html>"

ERROR_EMAIL_TEMPLATE='''
<p>Hello,</p>
<p>We've received the following application error.</p>
<p>{:s}</p>
<p>Thanks,<br>
Team</p>
'''

ERROR_EMAIL_BODY = (
   HEADER + ERROR_EMAIL_TEMPLATE + FOOTER
)

ERROR_EMAIL ={
    'subject' : 'Punisher Error',
    'body' : ERROR_EMAIL_BODY
}

def send_error_email(to_email, msg):
    body = ERROR_EMAIL['body'].format(msg)
    send_email(ERROR_EMAIL['subject'], body, to_email)

def get_client():
    return boto3.client('ses', aws_access_key_id=cfg.AWS_ACCESS_KEY,
                        aws_secret_access_key=cfg.AWS_SECRET_KEY,
                        region_name=cfg.SES_AWS_REGION)

def send_email(subject, body, to_email, from_email=cfg.ADMIN_EMAIL):
    response = get_client().send_email(
        Source=from_email,
        Destination={
            'ToAddresses': [
                to_email,
            ],
            'CcAddresses': [],
            'BccAddresses': []
        },
        Message={
            'Subject': {
                'Data': subject,
                'Charset': EMAIL_CHARSET
            },
            'Body': {
                'Text': {
                    'Data': body,
                    'Charset': EMAIL_CHARSET
                },
                'Html': {
                    'Data': body,
                    'Charset': EMAIL_CHARSET
                }
            }
        }
    )
    return response
