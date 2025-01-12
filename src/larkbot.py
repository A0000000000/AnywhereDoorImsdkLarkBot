import os
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import constant


def send_message_to_lark(msg: str) -> None:
    send_data = json.dumps({
        'text': msg
    })
    print('send msg to lark: ', send_data)
    open_id = os.getenv(constant.ENV_OPEN_ID)
    client = lark.Client.builder().app_id(lark.APP_ID).app_secret(lark.APP_SECRET).build()
    request_body = (CreateMessageRequestBody
                    .builder()
                    .receive_id(open_id)
                    .msg_type('text')
                    .content(send_data)
                    .build())
    request = (CreateMessageRequest
               .builder()
               .receive_id_type('open_id')
               .request_body(request_body)
               .build()
               )
    resp = client.im.v1.message.create(request)
    if not resp.success():
        print('发送消息失败. resp = ', resp.data)


def run(fn_on_rev_msg):
    def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
        if data.event.message.message_type == "text":
            text = json.loads(data.event.message.content)["text"]
            index = 0
            while index < len(text):
                if text[index] == ' ':
                    break
                index = index + 1
            if index == 0 or index == len(text):
                send_message_to_lark(constant.ERROR_CMD_FORMAT)
                return
            fn_on_rev_msg(text[:index], text[index + 1:])
        else:
            print('非Text类型消息, 忽略. 类型: ', data.event.message.message_type)

    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
        .build()
    )

    ws_client = lark.ws.Client(
        lark.APP_ID,
        lark.APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.DEBUG,
    )

    ws_client.start()
