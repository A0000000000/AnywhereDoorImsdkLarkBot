import server
import larkbot


def main():
    server.init_http_server(larkbot.send_message_to_lark)
    larkbot.run(server.send_request)


if __name__ == '__main__':
    main()
