"""
Module that will contain the work flow for parsing the incoming data for creating a node.
"""
import logging

from rhobot.components.commands.base_command import BaseCommand
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload

logger = logging.getLogger(__name__)

class UpdateNode(BaseCommand):
    """
    Neo4j Storage plugin for storing data.
    """
    name = Commands.UPDATE_NODE.value
    description = 'Neo4j Update Node'
    dependencies = BaseCommand.default_dependencies.union({'xep_0122', 'neo4j_wrapper'})

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        super(UpdateNode, self).post_init()
        self._command_handler = self.xmpp['neo4j_wrapper']

    def command_start(self, iq, initial_session):
        """
        Starting point for creating a new node.
        :param iq:
        :param initial_session:
        :return:
        """
        if not initial_session['payload']:
            initial_session['notes'] = [('error', 'Cannot execute without a payload')]
        else:
            logger.info('Update Node iq: %s' % iq)
            logger.info('Initial_session: %s' % initial_session)

            payload = StoragePayload(initial_session['payload'])

            logger.debug('relationships: %s' % payload.references)
            logger.debug('properties: %s' % payload.properties)
            logger.debug('types: %s' % payload.types)
            logger.debug('about: %s' % payload.about)

            node = self._command_handler.get_node(payload.about)

            self._command_handler.update_node(node, payload.references, payload.properties)

            # Build up the form response containing the newly created uri
            result = ResultCollectionPayload()
            result.append(ResultPayload(about=str(node.uri), types=node.labels))

            initial_session['payload'] = result.populate_payload()

        return initial_session

storage_update_node = UpdateNode
