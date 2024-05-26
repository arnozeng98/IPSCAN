import asyncio
import socket
import subprocess
from pywebio.input import *
from pywebio.output import *
from pywebio import start_server

async def home_page():
    """Render the home page with buttons for 'PING IP' and 'PING PORT'"""
    put_buttons(['PING IP', 'PING PORT'], onclick=[ping_ip_page, ping_port_page])

async def ping_ip_page():
    """Render the page for pinging IP addresses"""
    ip_prefix = await input("Enter the IP prefix (e.g., 192.168.0):", type=TEXT)

    put_text("Pinging IP addresses...")

    # Perform IP ping scans
    available_ips, unavailable_ips = await ping_ips(ip_prefix)

    # Display available and unavailable IP addresses in separate tables
    put_text("Available IP addresses:")
    put_table(_split_list(sorted(available_ips, key=lambda x: int(x.split('.')[-1])), 8))

    put_text("Unavailable IP addresses:")
    put_table(_split_list(sorted(unavailable_ips, key=lambda x: int(x.split('.')[-1])), 8))

def _split_list(lst, n):
    """Split list into sublists of length n"""
    return [lst[i:i+n] for i in range(0, len(lst), n)]

async def ping_ips(ip_prefix):
    """Perform ping scans on IP addresses in the specified prefix"""
    available_ips = []
    unavailable_ips = []
    tasks = []
    # Scan all IP addresses in the prefix
    for i in range(256):
        ip_address = f"{ip_prefix}.{i}"
        tasks.append(ping_ip(ip_address, available_ips, unavailable_ips))
    # Wait for all ping tasks to complete
    await asyncio.gather(*tasks)
    return available_ips, unavailable_ips

async def ping_ip(ip_address, available_ips, unavailable_ips):
    """Ping a single IP address"""
    # Execute ping command for the IP address
    result = await asyncio.create_subprocess_shell(
        f"ping -n 1 {ip_address}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Wait for the ping command to complete
    await result.communicate()
    # Check the return code to determine if the IP is available or not
    if result.returncode == 0:
        available_ips.append(ip_address)
    else:
        unavailable_ips.append(ip_address)

async def ping_port_page():
    """Render the page for port scanning"""
    put_text("Enter the IP Address, start port number, and end port number:")

    ip_address = await input("IP Address:", type=TEXT)
    start_port = await input("Start port number:", type=NUMBER)
    end_port = await input("End port number:", type=NUMBER)

    put_text("Scanning ports...")

    # Perform port scanning
    available_ports = []
    unavailable_ports = []
    for port in range(start_port, end_port + 1):
        if await check_port(ip_address, port):
            available_ports.append(port)
        else:
            unavailable_ports.append(port)

    # Display available and unavailable ports in tables
    put_text("Available ports:")
    put_table(_split_list(available_ports, 19))

    put_text("Unavailable ports:")
    put_table(_split_list(unavailable_ports, 19))

def _split_list(lst, n):
    """Split list into sublists of length n"""
    return [lst[i:i+n] for i in range(0, len(lst), n)]

async def check_port(ip_address, port):
    """Check if a port is open on the specified IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((ip_address, port))
        return True  # Port is open
    except (socket.timeout, ConnectionRefusedError):
        return False  # Port is closed

if __name__ == "__main__":
    # Start the PyWebIO server
    start_server(home_page, port=8888, debug=True)
