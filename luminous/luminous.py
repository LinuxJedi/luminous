import sys
import readline
import argparse
import ConfigParser
import command_parser

from novaclient import client

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', help='Cofiguration file (default /etc/luminous/luminous.cnf)', type=file)
subparsers = parser.add_subparsers(dest='command')
parser_list = subparsers.add_parser('list', help='List known tennants')
parser_tennant = subparsers.add_parser('tennant', help='Connect to a tennant')
parser_tennant.add_argument('name', help='Name of tennant to use')
parser_tennant.add_argument('-e', '--exec', help='Execute a command in non-interactive mode', dest='exec_command')
options = parser.parse_args()

class Completer:
    def __init__(self, words):
        self.words = words
        self.prefix = None
    def complete(self, prefix, index):
        if prefix != self.prefix:
            # we have a new prefix!
            # find all words that start with this prefix
            self.matching_words = [
                w for w in self.words if w.startswith(prefix)
                ]
            self.prefix = prefix
        try:
            return self.matching_words[index]
        except IndexError:
            return None

if not options.config:
    conffp = open('/etc/luminous/luminous.cnf', 'r')
else:
    conffp = options.config

config = ConfigParser.ConfigParser()
config.readfp(conffp)

if options.command == 'list':
    for section in config.sections():
        print section
    exit(0)

words = "status", "tennant"

completer = Completer(words)

readline.parse_and_bind("tab: complete")
readline.set_completer(completer.complete)

api = client.HTTPClient(config.get(options.name, 'os_username'), config.get(options.name, 'os_password'), config.get(options.name, 'os_tenant_name'), config.get(options.name, 'os_auth_url'), region_name=config.get(options.name, 'os_region_name'), service_type='compute')

parser = command_parser.Parser(api)

if not options.exec_command:
    while 1:
        command = raw_input("luminous> ")
        parser.parse(command)
else:
    parser.parse(options.exec_command)
