import prettytable
import re

class Parser(object):
    def __init__(self, api):
        self.api = api

    def parse(self, data):
        words = data.split()
        try:
            getattr(self, 'do_' + words[0])(words)
        except AttributeError:
            print "No such command: '{cmd}'".format(cmd=words[0])

    def do_quit(self, words):
        exit(0)

    def do_list(self, words):
        words = words[1:]
        if not words[0]:
            print "List requires a subcommand"
            return
        else:
            cmd = words[0]
            try:
                getattr(self, 'do_list_' + cmd)(words)
            except AttributeError:
                print "No such List subcommand: '{cmd}'".format(cmd=cmd)

    def do_list_nodes(self, words):
        words = words[1:]
        search = ''
        if len(words) > 0:
            if words[0] == 'where':
                search = self._where(words)
            else:
                print "No such parameter: '{param}'".format(param=words[0])
                return
        url = "/servers/detail{search}".format(search=search)
        resp, body = self.api.get(url)
        columns = ['ID', 'Name', 'Status', 'Network']
        table = prettytable.PrettyTable(columns)
        for server in body['servers']:
            addresses = ''
            for network, address in server['addresses'].items():
                addresses += network + '='
                addresses_csv = []
                addr_data = ''
                for addr in address:
                    addresses_csv.append(addr['addr'])
                addr_data = ', '.join(addresses_csv)
                addresses += addr_data
            table.add_row([server['id'], server['name'], server['status'], addresses])
        print table

    def do_list_secgroups(self, words):
        url = "/os-security-groups"
        resp, body = self.api.get(url)
        columns = ['Name', 'Description']
        table = prettytable.PrettyTable(columns)
        for group in body['security_groups']:
            table.add_row([group['name'], group['description']])
        print table

    def _where(self, words):
        ret_data = ''
        first = True
        words = words[1:]
        word_data = ' '.join(words)
        regex = re.compile('(\w+)\s?=\s?(\w+)')
        for match in regex.finditer(word_data):
            if first:
                ret_data += '?'
                first = False
            else:
                ret_data += '&'
            ret_data += '{key}={value}'.format(key=match.groups()[0], value=match.groups()[1])
        return ret_data

