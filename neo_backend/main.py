from rhobot.bot import RhoBot
from rhobot import configuration
from rhobot.components.storage.enums import Commands
from neo_backend.components.commands import load_commands
from neo_backend.components import load_components
import optparse

load_commands()
load_components()

parser = optparse.OptionParser()
parser.add_option('-c', dest="filename", help="Configuration file for the bot", default='neo_backend.rho')
(options, args) = parser.parse_args()

configuration.load_file(options.filename)

bot = RhoBot()
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

# Connect to the XMPP server and start processing XMPP stanzas.
if bot.connect():
    bot.process(block=True)
else:
    print("Unable to connect.")
