from slacker import Slacker

slack = Slacker('xoxb-1615709181554-1615920445683-z2ER8SCXxSwk6ZnNIAwZeker')
def send_slack(text):
    try:
        slack.chat.post_message('#jsw', text)
    except Exception as ex:
        print("Error sending webhook single message: " + str(ex))
