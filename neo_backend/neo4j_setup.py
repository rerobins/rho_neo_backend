"""
Set up the bot for execution.
"""
from rhobot.application import Application
from rhobot.components.storage.enums import Commands
from neo_backend.components.commands import load_commands
from neo_backend.components import load_components

application = Application()

# Register all of the components that are defined in this application.
application.pre_init(load_commands)
application.pre_init(load_components)

@application.post_init
def register_plugins(bot):
    # Register Components
    bot.register_plugin('neo4j_wrapper')

    # Register Commands
    bot.register_plugin(Commands.CREATE_NODE.value)
    bot.register_plugin(Commands.UPDATE_NODE.value)
    bot.register_plugin(Commands.FIND_NODE.value)
    bot.register_plugin(Commands.GET_NODE.value)
    bot.register_plugin(Commands.CYPHER.value)
    bot.register_plugin('configure_neo4j')
    bot.register_plugin('test_connection')
