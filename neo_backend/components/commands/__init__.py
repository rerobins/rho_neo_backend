from neo_backend.components.commands.create_node import storage_create_node
from neo_backend.components.commands.update_node import storage_update_node
from neo_backend.components.commands.find_node import storage_find_node
from neo_backend.components.commands.get_node import storage_get_node
from neo_backend.components.commands.execute_cypher import storage_cypher
from neo_backend.components.commands.configure_neo4j import configure_neo4j
from neo_backend.components.commands.test_connection import test_connection

from sleekxmpp.plugins.base import register_plugin


def load_commands():
    """
    Load the commands into the sleekxmpp plugins.
    :return:
    """
    register_plugin(storage_create_node)
    register_plugin(storage_update_node)
    register_plugin(storage_find_node)
    register_plugin(storage_get_node)
    register_plugin(storage_cypher)
    register_plugin(configure_neo4j)
    register_plugin(test_connection)
