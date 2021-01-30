import requests
import json

KAKAO_TOKEN = "xJCxYAYr6F_qkVfc4VSrDNcB9VfwEaBN9eF2tgorDNMAAAF3PkbtXQ"
def send_to_kakao(text):
    header = {"Authorization": 'Bearer ' + KAKAO_TOKEN}
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    post = {
        "object_type": "list",
        "header_title": "삼성 덕에 '코로나 백신 주사기' 뚝딱…한 달 만에 일낸 中企",
        "header_link": {
            "web_url": "https://www.hankyung.com/economy/article/202101197786i",
            "mobile_web_url": "https://www.hankyung.com/economy/article/202101197786i",
            "android_execution_params": "",
            "ios_execution_params": ""
        },
        "contents": [
            {
                "title": "코로나 백신 주사기",
                "description": "아메리카노, 빵, 케익",
                "image_url": "http://mud-kage.kakao.co.kr/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
                "image_width": 640,
                "image_height": 640,
                "link": {
                    "web_url": "http://www.daum.net",
                    "mobile_web_url": "http://m.daum.net",
                    "android_execution_params": "contentId=100",
                    "ios_execution_params": "contentId=100"
                }
            },
            {
                "title": "코로나 백신 주사기",
                "description": "아메리카노, 빵, 케익",
                "image_url": "http://mud-kage.kakao.co.kr/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
                "image_width": 640,
                "image_height": 640,
                "link": {
                    "web_url": "http://www.daum.net",
                    "mobile_web_url": "http://m.daum.net",
                    "android_execution_params": "contentId=100",
                    "ios_execution_params": "contentId=100"
                }
            }
        ]
    }

    # post = {
    #     "object_type": "text",
    #     "text": text,
    #     "link": {
    #         "web_url": "https://developers.kakao.com",
    #         "mobile_web_url": "https://developers.kakao.com"
    #     },
    #     "content": {
    #         "title": "디저트 사진",
    #         "description": "아메리카노, 빵, 케익",
    #         "image_url": "http://mud-kage.kakao.co.kr/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
    #         "image_width": 640,
    #         "image_height": 640,
    #         "link": {
    #             "web_url": "http://www.daum.net",
    #             "mobile_web_url": "http://m.daum.net",
    #             "android_execution_params": "contentId=100",
    #             "ios_execution_params": "contentId=100"
    #         }
    #     }
    # }

    data = {"template_object": json.dumps(post)}
    print(data)
    return requests.post(url, headers=header, data=data).text


def send_to_kakao_for_friend(text):
    header = {
        "Authorization": 'Bearer ' + KAKAO_TOKEN
    }
    url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
    post = {
        "object_type": "feed",
        "content": {
            "title": "디저트 사진",
            "description": "아메리카노, 빵, 케익",
            "image_url": "http://mud-kage.kakao.co.kr/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
            "image_width": 640,
            "image_height": 640,
            "link": {
            "web_url": "http://www.daum.net",
            "mobile_web_url": "http://m.daum.net",
            "android_execution_params": "contentId=100",
            "ios_execution_params": "contentId=100"
            }
        },
    }

    data = {"template_object": json.dumps(post), "receiver_uuids":  "[\"y_PK8sr-zPzQ49Lk0Ojc6Nn1wfjB9sf_jQ\"]"}
    return requests.post(url, headers=header, data=data).text


def get_kakao_friend():
    header = {
        "Authorization": 'Bearer ' + KAKAO_TOKEN
    }
    url = "https://kapi.kakao.com/v1/api/talk/friends?friend_order=favorite&limit=100&order=asc"
    return requests.get(url, headers=header).text

def get_kakao_profile():
    header = {
        "Authorization": 'Bearer ' + KAKAO_TOKEN
    }
    url = "https://kapi.kakao.com/v1/api/talk/profile"
    return requests.get(url, headers=header).text
