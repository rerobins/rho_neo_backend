import sleekxmpp
import logging
import logging.config
import json
import os
from rhobot import configuration, roster


if os.path.exists('logging.json'):
    with open('logging.json', 'rt') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
else:
    logging.basicConfig()

logger = logging.getLogger(__name__)

logger.info('Logging Configured')


class RhoBot(sleekxmpp.ClientXMPP):

    def __init__(self):
        jid = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                    configuration.JID_KEY)
        password = configuration.get_configuration().get(configuration.CONNECTION_SECTION_NAME,
                                                         configuration.PASSWORD_KEY)
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping
        self.register_plugin('xep_0045')  # MUC
        self.register_plugin('xep_0050')  # AdHoc Commands

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("muc::%s::got_online" %
                               configuration.get_configuration().get(configuration.MUC_SECTION_NAME,
                                                                     configuration.ROOM_KEY),
                               self._online_helper)

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

    def _online_helper(self, presence):
        logging.getLogger(__name__).info('Joined Room: %s' % presence)

        self['xep_0030'].get_info(jid=presence['from'],
                                  node='',
                                  callback=self._info_helper)

    def _info_helper(self, info):
        logging.getLogger(__name__).info('Joined Room (Info): %s' % info['disco_info']['identities'])





if __name__ == '__main__':

    # Setup logging.
    logging.basicConfig(level='DEBUG',
                        format='%(levelname)-8s %(message)s')

    configuration.load_file('rhobot.conf')

    xmpp = RhoBot()

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        print("Unable to connect.")

