from rhobot.bot import RhoBot
from rhobot import configuration
import optparse

parser = optparse.OptionParser()
parser.add_option('-c', dest="filename", help="Configuration file for the bot", default='neo_backend.rho')
(options, args) = parser.parse_args()

configuration.load_file(options.filename)

bot = RhoBot()
bot.register_plugin('storage_create_node', module='neo_backend.components.commands')
bot.register_plugin('storage_update_node', module='neo_backend.components.commands')
bot.register_plugin('storage_find_node', module='neo_backend.components.commands')

# Connect to the XMPP server and start processing XMPP stanzas.
if bot.connect():
    bot.process(block=True)
else:
    print("Unable to connect.")
