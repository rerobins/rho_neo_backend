from rhobot.bot import RhoBot
from rhobot import configuration
from rhobot.components.storage.enums import Commands
from neo_backend.components.commands import load_commands
import optparse

load_commands()

parser = optparse.OptionParser()
parser.add_option('-c', dest="filename", help="Configuration file for the bot", default='neo_backend.rho')
(options, args) = parser.parse_args()

configuration.load_file(options.filename)

bot = RhoBot()
bot.register_plugin(Commands.CREATE_NODE.value)
bot.register_plugin(Commands.UPDATE_NODE.value)
bot.register_plugin(Commands.FIND_NODE.value)
bot.register_plugin(Commands.GET_NODE.value)
bot.register_plugin(Commands.CYPHER.value)

# Connect to the XMPP server and start processing XMPP stanzas.
if bot.connect():
    bot.process(block=True)
else:
    print("Unable to connect.")
