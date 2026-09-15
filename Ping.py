import time
import socket
import os
import select
import struct
import sys


def get_IP(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror:
        print(f"This domain does not exist maybe you have made a typo")
        sys.exit(1)


def create_socket():
    try:
        return socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    except PermissionError:
        print(f"You dont have enough permissions run this script as admin!")
        sys.exit(1)


def checksum(source_byte):
    total = 0
    length = len(source_byte)

    for i in range(0, length, 2):
        if i + 1 < length:
            total += ((source_byte[i] << 8) + source_byte[i+1])
        else:
            total += source_byte[i] << 8

    while total >> 16:
        total = (total >> 16) + (total & 0xffff)
    return ~total & 0xffff


def create_packet(seq = 1):
    my_id = os.getpid() & 0xffff
    header = struct.pack("!BBHHH", 8, 0, 0, my_id, 1)
    payload_data = b"Ping to python"

    packet = header + payload_data
    calc_checksum = checksum(packet)

    header = struct.pack("!BBHHH", 8, 0, calc_checksum, my_id, seq)
    return header + payload_data~~~


def ping(hostname, timeout=2, count = 4):
    ip = get_IP(hostname)
    created_socket = create_socket()
    for seq in range(1, count + 1):
        packet = create_packet(seq)
        send_time = time.time()
        created_socket.sendto(packet, (ip, 0))
        ready = select.select([created_socket], [], [], timeout)
        if ready[0] == []:
            print(f"Request timed out for {hostname} ({ip}) of the sequence number {seq}")
            continue
        else:
            recv_time = time.time()
            recv_bytes, recv_address =created_socket.recvfrom(1024)
            actual_time = recv_time - send_time
            print(f"Pinging back from {ip} with the time of {actual_time * 1000:.2f}ms of the sequence number {seq}")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        ping(sys.argv[1])
    else:
        print(f"You havent entered a domain please enter one")