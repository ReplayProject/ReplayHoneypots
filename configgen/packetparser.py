from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Raw, Packet, Padding
import json
import math

portResultsMap = {}
interesting_packet_count = 0
packetID = 0

FIN = 0x01
SYN = 0x02
RST = 0x04
PSH = 0x08
ACK = 0x10
URG = 0x20
ECE = 0x40
CWR = 0x80

def process_pcap(file_name, target, ports):
    global packetID
    for port in ports:
        portResultsMap[port] = []
    
    count = 0
    
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        count += 1
        
        ether_pkt = Ether(pkt_data)
        if 'type' not in ether_pkt.fields:
            # LLC frames will have 'len' instead of 'type'.
            # We disregard those
            continue

        if ether_pkt.type != 0x0800:
            # disregard non-IPv4 packets
            continue

        ip_pkt = ether_pkt[IP]

        direction = None # true if inbound false if outbound
        if ip_pkt.src == target:
            direction = False
        elif ip_pkt.dst == target:
            direction = True
        else:
            continue

        if (ip_pkt.flags == 'MF') or (ip_pkt.frag != 0):
            print('No support for fragmented IP packets')
            break

        # Protocol numbers are the standard defined numbers here: https://en.wikipedia.org/wiki/List_of_IP_protocol_numbers
        if ip_pkt.proto == 6: # TCP
            handleTCPPacket(ip_pkt, direction, ports)
        elif ip_pkt.proto == 17: # UDP
            handleUDPPacket(ip_pkt, direction, ports)
        # elif ip_pkt.proto == 1: # ICMP
        #     handleICMPPacket(ip_pkt, direction, ports)
        else:
            continue

        packetID += 1

    # print('{} contains {} packets ({} interesting)'.
    #     format(file_name, count, interesting_packet_count))

    return compileRequestResponseModel()
    # return intelligentResponseModel()

def handleTCPPacket(packet, direction, ports):
    global interesting_packet_count
    global packetID
    tcp_pkt = packet[TCP]

    # Process the payload
    tcp_payload_len = packet.len - (packet.ihl * 4) - (tcp_pkt.dataofs * 4)
    payload = None
    if tcp_payload_len > 0:
        payload = tcp_pkt.payload
        if isinstance(payload, Raw):
            payload = payload.load.hex()

    # Process the flags on the packet
    pkt_flags = tcp_pkt.flags
    flags = []

    if pkt_flags & FIN:
        flags.append("FIN")
    if pkt_flags & SYN:
        flags.append("SYN")
    if pkt_flags & RST:
        flags.append("RST")
    if pkt_flags & PSH:
        flags.append("PSH")
    if pkt_flags & ACK:
        flags.append("ACK")
    if pkt_flags & URG:
        flags.append("URG")
    if pkt_flags & ECE:
        flags.append("ECE")
    if pkt_flags & CWR:
        flags.append("CWR")

    # Create record for handling later
    if direction == True and tcp_pkt.dport in ports:
        portResultsMap[tcp_pkt.dport].append({
            "id": packetID,
            "direction": direction,
            "protocol": packet.proto,
            "flags": flags,
            "payload": payload,
            "seq": tcp_pkt.seq,
            "ack": tcp_pkt.ack
        })
        interesting_packet_count += 1
    elif direction == False and tcp_pkt.sport in ports:
        portResultsMap[tcp_pkt.sport].append({
            "id": packetID,
            "direction": direction,
            "protocol": packet.proto,
            "flags": flags,
            "payload": payload,
            "seq": tcp_pkt.seq,
            "ack": tcp_pkt.ack
        })
        interesting_packet_count += 1

def handleUDPPacket(packet, direction, ports):
    global interesting_packet_count
    global packetID
    udp_pkt = packet[UDP]

    if direction == True and udp_pkt.dport in ports:
        portResultsMap[udp_pkt.dport].append({
            "id": packetID,
            "direction": direction,
            "protocol": packet.proto,
            "payload": udp_pkt.payload.hex()
        })
        interesting_packet_count += 1
    elif direction == False and udp_pkt.sport in ports:
        portResultsMap[udp_pkt.sport].append({
            "id": packetID,
            "direction": direction,
            "protocol": packet.proto,
            "payload": udp_pkt.payload.hex()
        })
        interesting_packet_count += 1

# def handleICMPPacket(packet, direction, ports):
#     global interesting_packet_count
#     print("ICMP Packet")

def compileRequestResponseModel():
    # Exchange objects look like:
    # {
    #     "request": {
    #         # A packet representative object from the global list of packets
    #     },
    #     "responses": [
    #         # A list of packet representative objects from the global list of packets
    #     ]
    # }
    requestResponseModel = {}
    
    for port in portResultsMap:
        requestResponseModel[port] = []
        modelEntry = {
            "request": None,
            "responses": []
        }

        for packet in portResultsMap[port]:
            # Read through all packets - mark when found incoming request
            # Read through all packets until the next request - all interim packets are "response" to first request
            if packet["direction"] == True:
                # If request payload is empty, we group it with the last request
                if packet["payload"] == None:
                    continue
                # Save the model 
                if len(modelEntry["responses"]) != 0:
                    requestResponseModel[port].append(modelEntry)
                del packet["id"]
                del packet["direction"]
                del packet["flags"]
                modelEntry = {
                    "request": packet,
                    "responses": []
                }
            elif packet["payload"] != None:
                del packet["id"]
                del packet["direction"]
                del packet["flags"]
                modelEntry["responses"].append(packet)

    return requestResponseModel

# if __name__ == "__main__":
#     process_pcap("nmaplog.pcap", "45.33.32.156", [22, 80, 54543])
#     compileRequestResponseModel()

# Utilizes the structure of TCP to match requests and responses
# using sequence and ACK numbers. When encountering any other form of packet, this falls
# back to dumber logic, like assuming packets in the PCAP are in order of sending.
def intelligentResponseModel():
    requestResponseModel = {}
    
    for port in portResultsMap:
        requestResponseModel[port] = []
        modelEntry = {
            "request": None,
            "responses": []
        }

        intoPacketList = 0
        portResults = portResultsMap[port]
        for packet in portResults:
            print(packet)
            if packet["protocol"] == 6 and packet["direction"] == True: # and packet["payload"] != None: # incoming w/ payload
                responses = []
                print(packet["payload"], len(packet["payload"]))
                ackWanted = packet["seq"] + math.ceil((len(packet["payload"]) / 2)) # divide length of payload by 2 due to octets vs. raw hex string (tcp expectation vs. what we have)
                print(ackWanted)
                for index in range(intoPacketList,len(portResults)):
                    if portResults[index]["protocol"] != 6: # TCP
                        continue
                    if "FIN" in portResults[index]["flags"]: # Ending Connection
                        break
                    print(portResults[index]["ack"], ackWanted)
                    if portResults[index]["direction"] == False and portResults[index]["ack"] == ackWanted:
                        addPacket = portResults[index]
                        del addPacket["id"]
                        del addPacket["direction"]
                        del addPacket["flags"]
                        responses.append(addPacket)
                
                if len(responses) != 0:
                    requestResponseModel[port].append({
                        "request": packet,
                        "responses": responses
                    })

            intoPacketList += 1



        # for packet in portResultsMap[port]:
        #     # Read through all packets - mark when found incoming request
        #     # Read through all packets until the next request - all interim packets are "response" to first request
        #     if packet["direction"] == True:
        #         # If request payload is empty, we group it with the last request
        #         if packet["payload"] == None:
        #             continue
        #         # Save the model 
        #         if len(modelEntry["responses"]) != 0:
        #             requestResponseModel[port].append(modelEntry)
        #         del packet["id"]
        #         del packet["direction"]
        #         del packet["flags"]
        #         modelEntry = {
        #             "request": packet,
        #             "responses": []
        #         }
        #     elif packet["payload"] != None:
        #         del packet["id"]
        #         del packet["direction"]
        #         del packet["flags"]
        #         modelEntry["responses"].append(packet)

    return requestResponseModel