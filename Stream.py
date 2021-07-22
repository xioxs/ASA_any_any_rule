import json


class Stream:
    all_instances = set()
    interface = ''

    @staticmethod
    def mergeprotocols(unieke_Streams):
        dictionary = {}
        for stream in unieke_Streams:
            if stream.merge_protocols_key() in dictionary:
                dictionary.get(stream.merge_protocols_key()).protocol.append(stream.protocol[0])
            else:
                dictionary[stream.merge_protocols_key()] = stream
        return dictionary

    @staticmethod
    def merge_source_ip_addressess(unieke_Streams):
        dictionary = {}
        for stream in unieke_Streams:
            if stream.merge_same_source_adresses_key() in dictionary:
                dictionary.get(stream.merge_same_source_adresses_key()).srcip.append(stream.srcip[0])
            else:
                dictionary[stream.merge_same_source_adresses_key()] = stream
        return dictionary

    @staticmethod
    def merge_destination_ip_addressess(unieke_Streams):
        dictionary = {}
        for stream in unieke_Streams:
            if stream.merge_same_destination_adresses_key() in dictionary:
                dictionary.get(stream.merge_same_destination_adresses_key()).dstip.append(stream.dstip[0])
            else:
                dictionary[stream.merge_same_destination_adresses_key()] = stream
        return dictionary
    @staticmethod
    def filter_high_destination_ports(unieke_Streams,high_range):

        dictionary = {}
        for stream in unieke_Streams:
            if int(stream.dstport[0]) >= int(high_range):
                pass
            else:
                dictionary[stream.merge_same_source_adresses_key()] = stream
        return dictionary


    @staticmethod
    def mergeports(unieke_Streams):
        dictionary = {}
        for stream in unieke_Streams:
            if stream.merge_ports_key() in dictionary:
                dictionary.get(stream.merge_ports_key()).dstport.append(stream.dstport[0])
            else:
                dictionary[stream.merge_ports_key()] = stream
        return dictionary
    
    @staticmethod
    def print_all_instances():
        for stream in Stream.all_instances:
            print(stream)

    @staticmethod
    def from_json(document):
        data = json.loads(document)
        instance = Stream(data['source-ip'],data['source-mask'],data['dst-ip'],data['dst-mask'],data['dst-port'],data['protocol'])
        return instance

    def __init__(self, srcip,dstip,dstport,protocol,srcmask="255.255.255.255",dstmask="255.255.255.255"):
        self.srcip = []
        self.srcmask = srcmask
        self.dstip = []
        self.dstmask = dstmask
        self.dstport = []
        self.protocol = []
        self.srcip.append(srcip)
        self.dstip.append(dstip)
        self.dstport.append(dstport)
        self.protocol.append(protocol)
        Stream.all_instances.add(self)

    def __eq__(self, other):
        return isinstance(self, Stream) and \
            self.srcip == other.srcip and \
            self.srcmask == other.srcmask and \
            self.dstip == other.dstip and \
            self.dstmask == other.dstmask and \
            self.dstport == other.dstport and \
            self.protocol == other.protocol

    def __str__(self):
        return self.to_json()

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__,
                            "Source IP: {}"
                            ", Source mask: {} "
                            ", Destination IP: {} "
                            ", Destination mask: {} "
                            ", Destination port: {} "
                            ", Destination protocol: {}".format(sorted(self.srcip),
                                                                self.srcmask,
                                                                sorted(self.dstip),
                                                                self.dstmask,
                                                                sorted(self.dstport),
                                                                sorted(self.protocol)))

    def to_json(self):
        data = {
            'source-ip': sorted(self.srcip),
            'source-mask': self.srcmask,
            'dst-ip': sorted(self.dstip),
            'dst-mask': self.dstmask,
            'dst-port': sorted(self.dstport),
            'protocol': sorted(self.protocol)
            }
        return json.dumps(data)

    def merge_protocols_key(self):
        data = {
            'source-ip': sorted(self.srcip),
            'source-mask': self.srcmask,
            'dst-ip': sorted(self.dstip),
            'dst-mask': self.dstmask,
            'dst-port': sorted(self.dstport)
            }
        return json.dumps(data)

    def merge_same_source_adresses_key(self):
        data = {
            'dst-ip': sorted(self.dstip),
            'dst-mask': self.dstmask,
            'dst-port': sorted(self.dstport),
            'protocol': sorted(self.protocol)
            }
        return json.dumps(data)

    def merge_same_destination_adresses_key(self):
        data = {
            'source-ip': sorted(self.srcip),
            'source-mask': self.srcmask,
            'dst-mask': self.dstmask,
            'dst-port': sorted(self.dstport),
            'protocol': sorted(self.protocol)
            }
        return json.dumps(data)

    def merge_ports_key(self):
        data = {
            'source-ip': sorted(self.srcip),
            'source-mask': self.srcmask,
            'dst-mask': self.dstmask,
            'dst-ip': sorted(self.dstip),
            'protocol': sorted(self.protocol)
            }
        return json.dumps(data)


