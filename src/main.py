import server
import larkbot
import log


def main():
    log_ctx = log.create_log_ctx()
    server.init_http_server(log_ctx, larkbot.send_message_to_lark)
    larkbot.run(log_ctx, server.send_request)


if __name__ == '__main__':
    main()
