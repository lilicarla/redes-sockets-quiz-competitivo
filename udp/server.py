from socket import socket, AF_INET, SOCK_DGRAM
import time

UDPServerSocket = socket(AF_INET, SOCK_DGRAM)

UDPServerSocket.bind(('localhost', 9500))
