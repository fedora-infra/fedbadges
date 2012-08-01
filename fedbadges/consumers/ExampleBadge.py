from badges import FedoraBadgesConsumer
import logging
log = logging.getLogger("moksha.hub")

class ExampleBadgesConsumer(FedoraBadgesConsumer):
    """
    An Example subclass of FedoraBadgesConsumer. It sets the name and topic
    and then parses messages coming off the fedmsg bus to award badges

    :type hub: Moksha hub
    :param hub: The Moksha hub we are receiving messages from
    """
    topic = "org.fedoraproject.*"

    def __init__(self, hub):
        self.name = "examplebadge"
        super(ExampleBadgesConsumer, self).__init__(hub, self.name)

    def consume(self, msg):
        """
        Consume a single message off the bus and award badges based on it
        to award a badge call self.award_badge with the Person email, and the
        ID of the badge you want to award

        :type msg: dict
        :param msg: the message coming off the fedmsg bus
        """

        topic, body = msg.get('topic'), msg.get('body')
        if type(body) == type(""):
            return
        body = body.get('msg')
        print body.get('action')
        if body.get('action') == 'This guy did some awesome thing!':
            email = body.get('email')
            log.info("Awarding 'Example Badge' to {0}".format(email))
            badge_id = "example_badge"
            self.award_badge(email, badge_id)




