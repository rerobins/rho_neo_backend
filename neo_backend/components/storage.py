"""
Storage Plugin for handling new data to be stored in the database.  It is assumed that all of the storage functionality
should be known across all bots.
"""
from sleekxmpp.plugins.base import base_plugin
from rhobot.components.storage_client import CREATE_NODE_COMMAND
from neo_backend.components.commands import create_node


class Storage(base_plugin):
    """
    Neo4j Storage plugin for storing data.
    """
    name = 'storage'
    description = 'Neo4j Storage Plugin'
    dependencies = {'xep_0030', 'xep_0050'}

    def plugin_init(self):
        self.xmpp['xep_0050'].add_command(node=CREATE_NODE_COMMAND, name='Create Node',
                                          handler=create_node.starting_point)

    def post_init(self):
        """
        Post initialization, set the identity to be storage.
        :return:
        """
        self.xmpp['xep_0030'].add_identity('store', 'neo4j')

storage = Storage
