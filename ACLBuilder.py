from random import randint
from Stream import Stream


class Acl:

    def generate_source_groupname(self):
        hosts,block = "", ""
        value1 = randint(0, 99999)
        value2 = randint(0, 20)
        object_name = "DM_INLINE_NETWORK_SOURCE_{}_{}".format(value1,value2)
        object_line = "object-group network {}".format(object_name)

        for ip in self.srcip:
            hosts = hosts + "\n\tnetwork-object {} {}".format(ip, self.srcmask)

        block = "{} {}".format(object_line, hosts)
        return object_name,block

    def generate_destination_groupname(self):
        hosts, block = "", ""

        value1 = randint(0, 99999)
        value2 = randint(0, 20)
        object_name = "DM_INLINE_NETWORK_DST_{}_{}".format(value1,value2)
        object_line = "object-group network {}".format(object_name)
        for ip in self.dstip:
            hosts = hosts + "\n\tnetwork-object {} {}".format(ip, self.dstmask)

        block = "{} {}".format(object_line, hosts)
        return object_name,block

    def generate_service_groupname(self):
        hosts, block, protocol = "", "", ""
        for prot in self.protocol:
            protocol = protocol + prot

        protocol = protocol.upper()

        value1 = randint(0, 99999)
        value2 = randint(0, 20)

        object_name = "DM_INLINE_SERVICE_PORT_{}_{}".format(value1,value2)
        object_line = "object-group service {}".format(object_name)
        for port in self.dstport:
                hosts = hosts + "\n\tservice-object {} destination eq {}".format(protocol, port)

        block = "{} {}".format(object_line, hosts)
        return object_name, block

    def create_acl(self):
        # controleer waar objectgroups voor aangemaakt dienen te worden
        aantal_source_ip = len(self.srcip)
        aantal_dest_ip = len(self.dstip)
        aantal_poorten = len(self.dstport)

        if aantal_source_ip > 1:
            object_name_source, source = self.generate_source_groupname()
            print(source)
            source = "object-group " + object_name_source
        else:
            source = str(self.srcip[0]) + " " + self.srcmask

        if aantal_dest_ip > 1:
            self.generate_destination_groupname()
            object_name_dest, destination = self.generate_destination_groupname()
            print(destination)
            destination = "object-group " + object_name_dest
        else:
            destination = str(self.dstip[0]) + " " + self.dstmask

        if aantal_poorten > 1:
            object_name_service, service = self.generate_service_groupname()
            print(service)
            service = "object-group " + object_name_service
            print("access-list {} extended permit {} {} {}\n!".format(Stream.interface, service, source, destination))

        else:
            protocol = ""
            service = str(self.dstport[0])
            for prot in self.protocol:
                protocol = protocol + prot
            protocol = protocol.upper()
            if protocol == "ICMP":
                print("access-list {} extended permit {} {} {}\n!".format(Stream.interface, protocol, source, destination))
            else:
                print("access-list {} extended permit {} {} {} eq {}\n!".format(Stream.interface, protocol, source, destination, service))



    def __init__(self, stream):
        self.srcip = stream.srcip
        self.srcmask = stream.srcmask
        self.dstip = stream.dstip
        self.dstmask = stream.dstmask
        self.dstport = stream.dstport
        self.protocol = stream.protocol



