#!/usr/bin/python3
from Stream import Stream
from ACLBuilder import Acl
from IPy import IP
import argparse, re

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def begin_parameters():
    parser = argparse.ArgumentParser(description='PYTHON3 GEBRUIKEN OM UIT TE VOEREN: Script gaat door hele syslog data op zoek naar unieke streams.')
    parser.add_argument('--nodes', '-n', help='Geef het maximum aantal nodes op dat 1 ACL mag bevatten. Default = 15', default=15)
    parser.add_argument('--highports', '-t', help='Geef deze optie mee als je high ports op de destination gefilterd wil hebben.'
                                                  'Voor windows starten de highports vanaf 49152')
    parser.add_argument('--pub', '-p', help='Stromen richting het internet komen vaak voor. Indien je deze algemeen wil maken kan je deze optie meegeven. Alle publieke destination '
                                            'adressen worden generiek gemaakt.',type=str2bool, nargs='?', const=True, default=False)
    parser.add_argument('--file', '-f', help='Locatie van het log bestand. Default waarde: log.txt', default="log.txt")
    args=parser.parse_args()
    return args


def maak_ACL_op_aantal_nodes(lijst,nodes):
    nieuwe_lijst = list()

    for stream in lijst.copy():
        cycle = 1
        if len(stream.srcip) > nodes:
            while len(stream.srcip) > nodes and cycle < 4:
                ipset = set()
                for ip in stream.srcip:
                    octets = ip.split(".")
                    if cycle == 1:
                        new_ip = octets[0]+"."+octets[1]+"."+octets[2]+".0"
                        stream.srcmask = "255.255.255.0"
                    elif cycle == 2:
                        new_ip = octets[0]+"."+octets[1]+".0.0"
                        stream.srcmask = "255.255.0.0"
                    else:
                        new_ip = octets[0]+".0.0.0"
                        stream.srcmask = "255.0.0.0"
                    ipset.add(new_ip)
                stream.srcip = list(ipset)
                cycle = cycle + 1
        nieuwe_lijst.append(stream)
    return nieuwe_lijst


def inlezen_file(checkpublic, file):
    f = open(file, "r")
    if f.mode == "r":
        acl_interface = ""

        for line in f:
            # Haal alle dubbele spaties weg uit de regel.
            line = re.sub('\s+',' ',line)

            # lees regel in en split op spatie.
            lineArray = line.split(" ")

            # Voeg waardes toe aan variabele voor verdere referentie in de code
            source_interface = lineArray[9].split("/")[0]
            src_ip_split = lineArray[9].split("/")[1]
            src_ip = src_ip_split.split("(")[0]
            src_port = src_ip_split.split("(")[1].replace(")"," ").rstrip()
            acl_interface = lineArray[6]
            protocol = lineArray[8].strip().lower()
            dst_ip_split = lineArray[11].split("/")[1]
            dst_ip = dst_ip_split.split("(")[0]
            dst_port = dst_ip_split.split("(")[1].replace(")", " ").rstrip()
            dst_interface = lineArray[11].split("/")[0]

            # Haal vanuit de syslog over welke interface ACL het gaat. Dit wordt in de klasse opgeslagen en later gebruikt om ASA CLI uit te printen
            Stream.interface = acl_interface

            # controleer of stream ping verkeer is
            if protocol == "icmp":
                src_port = "0"
                dst_port = "0"

            # controleer of het destination ip-adres publiek of private is. Indien publieke filtering aanstaat wordt het destination adres aangepast naar "any"
            if checkpublic is True:
                ip = IP(dst_ip)
                type_ip = ip.iptype()
                if type_ip == "PUBLIC":
                    dst_ip = "any"

            Stream(src_ip,dst_ip,dst_port,protocol)


if __name__ == '__main__':
    # opvragen van de parameters - Geen create_acl
    args = begin_parameters()
    nodes = int(args.nodes)
    spatie = 150
    teken = '#'
    filter_publieke_ip_adressen = args.pub
    filter_high_ports_range = args.highports
    bestand = args.file
    print(" Aantal nodes in source ip moeten kleiner zijn dan: {} ".format(nodes).center(spatie,teken))


    # file filteren en rekening houden met opgegeven paramaters. Hier worden ook de Streams aangemaakt en toegevoegd in een SET. De classe Streams houdt zelf alle streams bij!
    inlezen_file(filter_publieke_ip_adressen, bestand)




    # alle sourcen met dezelfde destination en destination port samenvoegen.
    unieke_lijst = list(Stream.all_instances.copy())

    if filter_high_ports_range is not None:
        #print('# filtering highports higher than: {}'.format(filter_high_ports_range))
        dictionary = Stream.filter_high_destination_ports(unieke_lijst,filter_high_ports_range)
        filtered = list(dictionary.values())
        dictionary = Stream.mergeprotocols(filtered)
    else:
        dictionary = Stream.mergeprotocols(unieke_lijst)

    #
    filtered = list(dictionary.values())
    dictionary = Stream.merge_source_ip_addressess(filtered)
    filtered = list(dictionary.values())
    filtered = maak_ACL_op_aantal_nodes(filtered,nodes)
    dictionary = Stream.merge_destination_ip_addressess(filtered)
    filtered = list(dictionary.values())
    dictionary = Stream.mergeports(filtered)





    for item in dictionary.values():
        print("source ip:",item.srcip)
        print("source mask:" ,item.srcmask)
        print("destination ip:",item.dstip)
        print("destination mask:",item.dstmask)
        print("ports:",item.dstport)
        print("protocol:",item.protocol)
        print()




    print(" Totaal aantal unieke stromen (ACL's): {} ".format(len(dictionary)).center(spatie,teken))

    antwoord = input("Wil je de ACL's en objecten hiervoor? (y/n)")
    if antwoord.lower() in ("y","ye","j","ja"):
        print(" Begin ACL's ".center(spatie,teken))
        for item in dictionary.values():
            lala = Acl(item)
            lala.create_acl()

    print(" Einde ".center(spatie,teken))











