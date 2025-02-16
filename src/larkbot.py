import os
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
import constant


def send_message_to_lark(msg: str) -> None:
    send_data = json.dumps({
        constant.TEXT: msg
    })
    open_id = os.getenv(constant.ENV_OPEN_ID)
    client = lark.Client.builder().app_id(lark.APP_ID).app_secret(lark.APP_SECRET).build()
    request_body = (CreateMessageRequestBody
                    .builder()
                    .receive_id(open_id)
                    .msg_type(constant.TEXT)
                    .content(send_data)
                    .build())
    request = (CreateMessageRequest
               .builder()
               .receive_id_type(constant.OPEN_ID)
               .request_body(request_body)
               .build()
               )
    client.im.v1.message.create(request)


def run(log_ctx, fn_on_rev_msg):
    def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
        if data.event.message.message_type == constant.TEXT:
            text = json.loads(data.event.message.content)[constant.TEXT]
            index = 0
            while index < len(text):
                if text[index] == constant.WHITE_SPACE:
                    break
                index = index + 1
            if index == 0 or index == len(text):
                send_message_to_lark(constant.ERROR_CMD_FORMAT + constant.WHITE_SPACE + text)
                return
            fn_on_rev_msg(text[:index], text[index + 1:])

    event_handler = (
        lark.EventDispatcherHandler.builder(constant.EMPTY_STR, constant.EMPTY_STR)
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
