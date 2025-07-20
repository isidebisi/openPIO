##  Author: Delphine Allimann
##  EPFL - TCL 2025

# TUN virtual interface, to send packet to the simulation
# From this example : https://docs.cocotb.org/en/v1.1/ping_tun_tap.html

import fcntl
import os
import struct
import subprocess

from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, UDP
from cocotbext.eth import GmiiFrame

import ipbus_pkt

def create_tun():

    # Some constants used to ioctl the device file.
    TUNSETIFF = 0x400454ca
    TUNSETOWNER = TUNSETIFF + 2
    IFF_TUN = 0x0001
    IFF_TAP = 0x0002
    IFF_NO_PI = 0x1000

    # Open TUN device file
    # tun = open('dev/net/tun', 'r+b')
    tun = os.open('/dev/net/tun', os.O_RDWR)
    # tun = os.open('/dev/net/tun', 'rw')
    # Tell it we want a TUN device 
    # ifr = struct.pack('16sH', b'tun1', IFF_TUN | IFF_NO_PI)
    # fcntl.ioctl(tun, TUNSETIFF, ifr)
    # # Optionally, we want it be accessed by the normal user.
    # fcntl.ioctl(tun, TUNSETOWNER, 1000)
    # # Bring it up and assign addresses.
    # subprocess.check_call('ifconfig tun1 192.168.2.1 pointopoint 192.168.2.3 up',
    #         shell=True)
    print("tunnel created")
    return tun

def test_tun():
    return 

def build_arp(src="192.168.2.1", dst="192.168.2.3"):
    whohas = ARP(psrc=src, pdst=dst)
    eth = Ether(src='08:01:f0:d6:2c:74', dst='ff:ff:ff:ff:ff:ff')
    test_pkt = eth / whohas
    test_frame = GmiiFrame.from_payload(test_pkt.build())
    return test_frame, test_pkt

def check_arp_response(req_pkt, rsp_pkt):
    assert rsp_pkt.dst == req_pkt.src

def build_udp(mac_src = '08:01:f0:d6:2c:74',mac_dst = '00:60:d7:c0:ff:ee', ip_src="192.168.2.1", ip_dst="192.168.2.3", sport=53460, dport=50001, payload=[x % 256 for x in range(256)]):
    payload = bytes(payload)
    # eth = Ether(src='08:01:f0:d6:2c:74', dst='00:60:d7:c0:ff:ee')
    eth = Ether(src=mac_src, dst=mac_dst)
    ip = IP(src=ip_src, dst=ip_dst)
    udp = UDP(sport=sport, dport=dport)
    eth_frame = eth / ip / udp / payload
    frame_to_send = GmiiFrame.from_payload(eth_frame.build())
    return frame_to_send, eth_frame

def check_response(ipbus_req_pkt, ipbus_res_pkt):

    assert ipbus_req_pkt[Ether].src == ipbus_res_pkt[Ether].dst
    assert ipbus_req_pkt[Ether].dst == ipbus_res_pkt[Ether].src
    assert ipbus_req_pkt[IP].src    == ipbus_res_pkt[IP].dst
    assert ipbus_req_pkt[IP].dst    == ipbus_res_pkt[IP].src
    assert ipbus_req_pkt[UDP].sport == ipbus_res_pkt[UDP].dport
    assert ipbus_req_pkt[UDP].dport == ipbus_res_pkt[UDP].sport

    return

async def test_ipbus_class(tb):

    some_test_data = [83,111,109,101,32,116,101,115,116,32,100,97,116,97,32,32]
    some_other_test_data = [83,111,109,101,32,116,101,115,116,32,100,97,116,97,97,97]

    # req_ipbus_pkt = ipbus_pkt.IpbusPkt(tb)         #create an empty ipbus packet
    # wr = ipbus_pkt.IpbusTransaction(tb,id=1)       #create an empty ipbus transaction
    # wr.build_write(nbr_words=4,data=some_test_data)#make it a write transaction
    wr_trans = build_write_transaction(tb, id=1, nbr_words=4, data=some_test_data)
    # rd = ipbus_pkt.IpbusTransaction(tb,id=2)       #create an empty ipbus transaction
    # rd.build_read(nbr_words=4)                     #make it a read transaction
    rd_trans = build_read_transaction(tb, id=2, nbr_words=4)
    # rd.print_clean()
    # req_ipbus_pkt.add_transactions([wr_trans,rd_trans])        #add these transactions in the packet 
    
    frame_raw, req_frame, req_ipbus_pkt = send_ipbus_frame(tb, [wr_trans,rd_trans])
  
    req_ipbus_pkt.print_pkt()
    # frame_raw,req_frame = build_udp(payload=req_ipbus_pkt.get_pkt()) #make it an etheret frame

    await tb.rmii_phy.rx.send(frame_raw)           #send the frame  

    res_frame_raw = await tb.rmii_phy.tx.recv()    #receive rmii response frame
    res_frame = Ether(bytes(res_frame_raw.get_payload())) #make it ethernet frame

    check_response(req_frame, res_frame) 

    # tb.log.info("sent %s, received %s", request_frame[UDP].load, response_frame[UDP].load)

    tb.log.info("Ipbus packet received")
    res_ipbus_pkt = ipbus_pkt.IpbusPkt(tb)      
    res_ipbus_pkt.construct_pkt(res_frame[UDP].load) #interpret the received ipbus packet
    res_ipbus_pkt.print_pkt()

    tb.log.info("Send read request that should generate an error")
    wrong_addr_pkt = ipbus_pkt.IpbusPkt(tb)
    req = ipbus_pkt.IpbusTransaction(tb,3)
    req.build_read(addr=[0xff, 0xff, 0xff, 0xff])
    wrong_addr_pkt.add_transactions([req])
    wrong_addr_pkt.print_pkt()
    raw, req_frame = build_udp(payload=wrong_addr_pkt.get_pkt())

    await tb.rmii_phy.rx.send(raw)

    response_raw = await tb.rmii_phy.tx.recv()
    response_frame = Ether(bytes(response_raw.get_payload()))
    check_response(req_frame, response_frame)
    res_ipbus_pkt = ipbus_pkt.IpbusPkt(tb)
    res_ipbus_pkt.construct_pkt(response_frame[UDP].load)
    res_ipbus_pkt.print_pkt()

    return


def build_read_transaction(tb, id, nbr_words=2, addr=[0x00,0x10,0x00,0x00]):
    rd_trans = ipbus_pkt.IpbusTransaction(tb, id)
    rd_trans.build_read(nbr_words, addr)
    return rd_trans

def build_write_transaction(tb, id, nbr_words=2, addr=[0x00,0x10,0x00,0x00], data=[x for x in range(64)]):
    wr_trans = ipbus_pkt.IpbusTransaction(tb, id)
    wr_trans.build_write(nbr_words, addr, data)
    return wr_trans

def build_ipbus_packet(tb, trans):
    pkt = ipbus_pkt.IpbusPkt(tb)
    pkt.add_transactions(trans)
    # frame_to_send, eth_frame = build_udp(payload=pkt.get_pkt())

def send_ipbus_frame(tb, trans, mac_src='08:01:f0:d6:2c:74', mac_dst='00:60:d7:c0:ff:ee', ip_src="192.168.2.1", ip_dst="192.168.2.3", sport=53460, dport=50001):
    pkt = ipbus_pkt.IpbusPkt(tb)
    pkt.add_transactions(trans)
    # pkt.print_pkt() 
    frame_to_send,eth_frame = build_udp(mac_src, mac_dst, ip_src, ip_dst, sport, dport, payload=pkt.get_pkt())
    return frame_to_send, eth_frame, pkt
    # return pkt



    

