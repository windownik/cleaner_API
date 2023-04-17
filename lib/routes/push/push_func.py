
import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

cred = credentials.Certificate("cleaner-app.json")
firebase_admin.initialize_app(cred)


def send_push(fcm_token: str, title: str, body: str, main_text: str, push_type: str):
    message = messaging.Message(
        data={'title': title,
              'body': body,
              'main_text': main_text,
              'push_type': push_type},
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=fcm_token
    )
    response = messaging.send(message)

#
# send_push(fcm_token='cLJnxualQXGqcFrFpM29EA:APA91bFvBA6UVeX3y-QVo5XgeT_7vaTZsCoqE4iKFwN-FnTTlMGMLb1xlVEv9OGJNdiKSFDC3MxJkBtcsFw84FVLymSkxSp1TSe_32Ef2e1yN5gpLnYKKnu67x8jIYvxBZLy-ltRZTPF',
#           title='Test text', body='11111111111', main_text='hi text', push_type='ewwrfvfrvd')