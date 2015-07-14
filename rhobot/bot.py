import sleekxmpp
import logging
import logging.config
import json
import os
from rhobot import configuration


if os.path.exists('logging.json'):
    with open('logging.json', 'rt') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
else:
    logging.basicConfig()

logger = logging.getLogger(__name__)

logger.info('Logging Configured')


class RhoBot(sleekxmpp.ClientXMPP):

    def __init__(self, components=None):
        jid = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                    configuration.JID_KEY)
        password = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                         configuration.PASSWORD_KEY)
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0045')  # MUC

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        self._components = []
        if components is None:
            components = []

        for component in components:
            self.register_component(component)

    def register_component(self, component):
        """
        Register the component.
        :param component:
        :return:
        """
        component.configure(self)

    def start(self, event):
        """
        Process the session_start event.
        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.
        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        self.send_presence()
        self.get_roster()

        self.plugin['xep_0045'].joinMUC(configuration.get_configuration().get(configuration.MUC_SECTION_NAME,
                                                                              configuration.ROOM_KEY),
                                        configuration.get_configuration().get(configuration.MUC_SECTION_NAME,
                                                                              configuration.ROOM_NICK_KEY),
                                        wait=True)


if __name__ == '__main__':

    import optparse
    from rhobot.commands import CommandComponent
    from rhobot.roster import RosterComponent

    parser = optparse.OptionParser()
    parser.add_option('-c', dest="filename", help="Configuration file for the bot", default='rhobot.conf')

    (options, args) = parser.parse_args()

    configuration.load_file(options.filename)

    xmpp = RhoBot(components=[RosterComponent(), CommandComponent()])

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        print("Unable to connect.")

