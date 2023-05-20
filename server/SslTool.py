import ssl


class SimSSLWrapper:

    def __init__(self, crt_path: str, key_path: str):
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(certfile=crt_path,
                                     keyfile=key_path)

    def wrap(self, sock):
        return self.context.wrap_socket(sock, server_side=True)
