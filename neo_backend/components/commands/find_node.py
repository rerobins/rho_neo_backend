"""
Command that will find a specific node based on the details in the payload.
"""
"""
Module that will contain the work flow for parsing the incoming data for creating a node.
"""
import logging

from rhobot.components.commands.base_command import BaseCommand
from rhobot.components.storage.enums import Commands
from rhobot.components.storage import StoragePayload, ResultCollectionPayload, ResultPayload
from rhobot.components.storage.enums import FindFlags, FindResults

logger = logging.getLogger(__name__)

class FindNode(BaseCommand):
    """
    Neo4j Storage plugin for finding data.
    """
    name = Commands.FIND_NODE.value
    description = 'Neo4j Find Node'
    dependencies = BaseCommand.default_dependencies.union({'xep_0122', 'neo4j_wrapper'})

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        super(FindNode, self).post_init()
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
            payload = StoragePayload(initial_session['payload'])

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug('Find Node iq: %s' % iq)
                logger.debug('Initial_session: %s' % initial_session)
                logger.debug('about: %s' % payload.about)
                logger.debug('relationships: %s' % payload.references)
                logger.debug('properties: %s' % payload.properties)
                logger.debug('types: %s' % payload.types)

            created = False
            nodes = self._command_handler.find_nodes(payload.types, **payload.properties)

            if not nodes and FindFlags.CREATE_IF_MISSING.fetch_from(payload.flags):
                node = self._command_handler.create_node(types=payload.types, properties=payload.properties,
                                                         relationships=payload.references)
                created = True
                nodes.append(node)

            # Build up the form response containing the newly created uri
            result_collection_payload = ResultCollectionPayload()
            for node in nodes:
                payload = ResultPayload(about=node.uri, types=node.labels)
                if created:
                    payload.add_flag(FindResults.CREATED, True)

                result_collection_payload.append(payload)

            initial_session['payload'] = result_collection_payload.populate_payload()

        return initial_session

storage_find_node = FindNode
