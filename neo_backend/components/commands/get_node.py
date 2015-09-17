"""
Module that will contain the work flow for fetching a node from the database.
"""
import logging
from neo_backend import command_handler
from rhobot.components.commands.base_command import BaseCommand
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload


logger = logging.getLogger(__name__)

class GetNode(BaseCommand):
    """
    Neo4j Storage plugin for finding data.
    """
    name = Commands.GET_NODE.value
    description = 'Neo4j Get Node'
    dependencies = BaseCommand.default_dependencies.union({'xep_0030', 'xep_0122'})

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        super(GetNode, self).post_init()
        self._discovery = self.xmpp['xep_0030']

        self._discovery.add_identity('store', 'neo4j')

    def command_start(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        logger.info('Get Node iq: %s' % iq)
        logger.info('Initial_session: %s' % initial_session)

        payload = StoragePayload(initial_session['payload'])

        logger.debug('about: %s' % payload.about)

        node = command_handler.get_node(payload.about, create=False)

        if node:
            result_payload = StoragePayload()
            result_payload.about = node.uri

            # Get the types into place.
            for label in node.labels:
                result_payload.add_type(label)

            # Gather up all of the references
            for relationship in node.match_outgoing():
                result_payload.add_reference(relationship.type, relationship.end_node.uri)

            # Gather up all of the properties
            for key, value in node.properties.iteritems():
                if isinstance(value, list):
                    for val in value:
                        result_payload.add_property(key, val)
                else:
                    result_payload.add_property(key, value)

            initial_session['payload'] = result_payload.populate_payload()

        return initial_session

storage_get_node = GetNode
