"""
Roster information for the bot.

This can be a singleton since we don't plan on joining any other rooms at the moment.
"""
import logging
from rhobot import configuration
from rhobot.component import BaseComponent


logger = logging.getLogger(__name__)


class _RosterComponent(BaseComponent):

    def __init__(self):
        super(_RosterComponent, self).__init__()

        self._channel_name = None
        self._nick = None
        self._presence_objects = dict(bot=set(), web=set())

    def _configure(self):
        """
        Configure this module to start handling the muc issues.
        :param xmpp:
        :return:
        """

        self._channel_name = configuration.get_configuration().get(configuration.MUC_SECTION_NAME,
                                                                   configuration.ROOM_KEY)
        self._nick = configuration.get_configuration().get(configuration.MUC_SECTION_NAME, configuration.ROOM_NICK_KEY)

        # Make sure that MUC has been loaded.
        self.xmpp.register_plugin('xep_0045')

        self.xmpp.add_event_handler("muc::%s::got_online" % self._channel_name,
                                    self._online_helper)

        self.xmpp.add_event_handler("muc::%s::got_offline" % self._channel_name,
                                    self._offline_helper)

    def _online_helper(self, presence):
        """
        Handler for online presence information.
        :param presence: presence object.
        :return:
        """
        if presence['muc']['nick'] == self._nick:
            logger.info('Self')
        else:
            logger.info('Joined Room: %s' % presence)

            self.xmpp['xep_0030'].get_info(jid=presence['from'],
                                           node='',
                                           callback=self._info_helper)

    def _offline_helper(self, presence):
        """
        Remove the presence information, unless it is our nick, then remove all presence information.
        :param presence:
        :return:
        """
        logger.info('%s' % presence)
        from_string = str(presence['from'])
        for connections in self._presence_objects.values():
            if from_string in connections:
                connections.remove(from_string)

        logger.info('%s' % self._presence_objects)

    def _info_helper(self, info):
        """
        Figure out how to categorize the objects.
        :param info:
        :return:
        """
        logger.info('Joined Room (Info): %s' % info['disco_info']['identities'])

        identities = info['disco_info']['identities']

        for key in self._presence_objects.keys():
            for _idents in identities:
                if key in _idents:
                    self._presence_objects[key].add(str(info['from']))

        logger.info('Received: %s' % self._presence_objects)

roster_component = _RosterComponent()