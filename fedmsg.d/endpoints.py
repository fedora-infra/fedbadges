import socket
hostname = socket.gethostname()

config = dict(
    endpoints={
        "fedbadges.%s" % hostname: [
            "tcp://127.0.0.1:3003",
        ],
    }
)
