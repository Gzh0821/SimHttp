import ssl


class SimSSLWrapper:
    def __init__(self):
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    def wrap(self, sock):
        return self.context.wrap_socket(sock, server_side=True)
