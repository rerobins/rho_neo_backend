from neo_backend.command_handler import get_node
import logging

logger = logging.getLogger(__name__)

# This will attempt to create a foreign node and make sure that it has been inserted into the database correctly.

# This should return none since the node should not exist.
node = get_node('http://www.google.com', create=False)

if node:
    logger.error('NODE SHOULD NOT EXIST, but does')

node = get_node('http://www.google.com', create=True)

if not node:
    logger.error('NODE SHOULD NOW EXIST')

# node.delete()



