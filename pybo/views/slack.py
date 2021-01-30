from slacker import Slacker

slack = Slacker('')

def send_slack(text):
    try:
        slack.chat.post_message('#jsw', text)
    except Exception as ex:
        print("Error sending webhook single message: " + str(ex))
