"""
Module that will contain the work flow for parsing the incoming data for creating a node.
"""
import logging
from neo_backend import command_handler
from rhobot.components.commands.base_command import BaseCommand
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload

logger = logging.getLogger(__name__)


class CreateNode(BaseCommand):
    """
    Neo4j Storage plugin for storing data.
    """
    name = Commands.CREATE_NODE.value
    description = 'Neo4j Create Node'
    dependencies = BaseCommand.default_dependencies.union({'xep_0030', 'xep_0122'})

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        super(CreateNode, self).post_init()
        self._discovery = self.xmpp['xep_0030']

        self._discovery.add_identity('store', 'neo4j')

    def command_start(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        logger.info('Create Node iq: %s' % iq)
        logger.info('Initial_session: %s' % initial_session)

        payload = StoragePayload(initial_session['payload'])

        logger.debug('relationships: %s' % payload.references)
        logger.debug('properties: %s' % payload.properties)
        logger.debug('types: %s' % payload.types)

        # Create the node
        node = command_handler.create_node(properties=payload.properties, types=payload.types,
                                           relationships=payload.references)

        # Build up the form response containing the newly created uri
        result = ResultCollectionPayload()
        result.append(ResultPayload(about=node.uri, types=node.labels))

        initial_session['payload'] = result.populate_payload()

        return initial_session

storage_create_node = CreateNode
