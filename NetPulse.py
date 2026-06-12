import socket
import platform
import subprocess
import datetime
import os
import sys
from urllib.parse import urlparse


APP_NAME = "NetPulse"
APP_VERSION = "v1.0"
report_logs = []

USE_COLOR = sys.stdout.isatty()


def color(text, code):
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


CYAN = "96"
GREEN = "92"
YELLOW = "93"
RED = "91"
BLUE = "94"
BOLD = "1"


def add_to_report(title, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_logs.append(
        f"\n[{timestamp}] {title}\n"
        f"{'-' * 45}\n"
        f"{content}\n"
    )


def clear_screen():
    os.system("cls" if platform.system().lower() == "windows" else "clear")


def pause():
    input(color("\nPress Enter to return to the menu...", YELLOW))


def normalize_host(value):
    value = value.strip()

    if not value:
        return ""

    if "://" in value:
        parsed = urlparse(value)
        return parsed.hostname or value

    if "/" in value:
        value = value.split("/")[0]

    return value


def show_banner():
    print(color("=" * 55, CYAN))
    print(color(f"{APP_NAME.upper()} {APP_VERSION}".center(55), BOLD))
    print(color("Network Diagnostic Toolkit".center(55), BLUE))
    print(color("Built for NOC, IT Support, and Network Troubleshooting".center(55), GREEN))
    print(color("=" * 55, CYAN))


def show_menu():
    print()
    print(color("[1]", CYAN), "Ping Test")
    print(color("[2]", CYAN), "DNS Lookup")
    print(color("[3]", CYAN), "Traceroute")
    print(color("[4]", CYAN), "Port Check")
    print(color("[5]", CYAN), "System Information")
    print(color("[6]", CYAN), "Quick Health Check")
    print(color("[7]", CYAN), "Save Report")
    print(color("[8]", CYAN), "Clear Screen")
    print(color("[9]", CYAN), "Exit")


def run_command(command, title, timeout=90):
    try:
        print(color(f"\nRunning: {' '.join(command)}\n", YELLOW))

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += "\n" + result.stderr

        if not output.strip():
            output = "No output returned."

        print(output)
        add_to_report(title, output)
        return output

    except subprocess.TimeoutExpired:
        message = "Command timed out. Try another host or check your connection."
        print(color(message, RED))
        add_to_report(title, message)
        return message

    except FileNotFoundError:
        message = "Command not found on this system."
        print(color(message, RED))
        add_to_report(title, message)
        return message


def ping_test():
    host = normalize_host(input("Enter website or IP: "))

    if not host:
        print(color("Host cannot be empty.", RED))
        return

    if platform.system().lower() == "windows":
        command = ["ping", "-n", "4", host]
    else:
        command = ["ping", "-c", "4", host]

    run_command(command, f"Ping Test - {host}")


def dns_lookup():
    domain = normalize_host(input("Enter domain name: "))

    if not domain:
        print(color("Domain cannot be empty.", RED))
        return

    try:
        results = socket.getaddrinfo(domain, None)
        addresses = sorted({item[4][0] for item in results})

        output_lines = [f"{domain} resolves to:"]
        for address in addresses:
            output_lines.append(f"- {address}")

        output = "\n".join(output_lines)
        print(color(output, GREEN))
        add_to_report(f"DNS Lookup - {domain}", output)

    except socket.gaierror:
        output = "DNS lookup failed. Please check the domain name."
        print(color(output, RED))
        add_to_report(f"DNS Lookup - {domain}", output)


def traceroute():
    host = normalize_host(input("Enter website or IP: "))

    if not host:
        print(color("Host cannot be empty.", RED))
        return

    if platform.system().lower() == "windows":
        command = ["tracert", host]
    else:
        command = ["traceroute", host]

    run_command(command, f"Traceroute - {host}", timeout=120)


def port_check():
    host = normalize_host(input("Enter website or IP: "))
    port_input = input("Enter port number: ").strip()

    if not host:
        print(color("Host cannot be empty.", RED))
        return

    try:
        port = int(port_input)

        if port < 1 or port > 65535:
            output = "Invalid port number. Use a number between 1 and 65535."
        else:
            with socket.create_connection((host, port), timeout=5):
                output = f"Port {port} on {host} is OPEN."

    except ValueError:
        output = "Invalid port number."

    except socket.timeout:
        output = f"Port {port_input} on {host} timed out."

    except OSError:
        output = f"Port {port_input} on {host} is CLOSED or unreachable."

    print(color(output, GREEN if "OPEN" in output else RED))
    add_to_report(f"Port Check - {host}:{port_input}", output)


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            return "Unable to get local IP"


def system_info():
    hostname = socket.gethostname()
    local_ip = get_local_ip()

    output = f"""
System Information
------------------
Hostname: {hostname}
Local IP: {local_ip}
Operating System: {platform.system()} {platform.release()}
OS Version: {platform.version()}
Machine: {platform.machine()}
Processor: {platform.processor()}
Python Version: {platform.python_version()}
"""

    print(color(output, GREEN))
    add_to_report("System Information", output)


def quick_health_check():
    print(color("\nStarting quick health check...\n", YELLOW))

    dns_target = "google.com"
    port_target = "google.com"
    port_number = 443

    try:
        ip = socket.gethostbyname(dns_target)
        dns_output = f"DNS OK: {dns_target} resolves to {ip}"
    except socket.gaierror:
        dns_output = f"DNS FAILED: Unable to resolve {dns_target}"

    print(color(dns_output, GREEN if "OK" in dns_output else RED))
    add_to_report("Quick Health Check - DNS", dns_output)

    if platform.system().lower() == "windows":
        command = ["ping", "-n", "4", "1.1.1.1"]
    else:
        command = ["ping", "-c", "4", "1.1.1.1"]

    run_command(command, "Quick Health Check - Ping 1.1.1.1", timeout=30)

    try:
        with socket.create_connection((port_target, port_number), timeout=5):
            port_output = f"Port OK: {port_number} on {port_target} is OPEN."
    except OSError:
        port_output = f"Port FAILED: {port_number} on {port_target} is not reachable."

    print(color(port_output, GREEN if "OK" in port_output else RED))
    add_to_report("Quick Health Check - Port 443", port_output)


def save_report():
    if not report_logs:
        print(color("No report data to save yet. Run some tools first.", YELLOW))
        return

    filename = f"netpulse_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("=" * 55 + "\n")
            file.write("NETPULSE v1.0 - NETWORK DIAGNOSTIC REPORT\n")
            file.write("=" * 55 + "\n")
            file.write("\n".join(report_logs))

        print(color(f"Report saved successfully: {filename}", GREEN))

    except OSError as error:
        print(color(f"Failed to save report: {error}", RED))


def main():
    clear_screen()
    show_banner()

    while True:
        show_menu()
        choice = input(color("\nEnter your choice: ", YELLOW)).strip()

        if choice == "1":
            ping_test()
            pause()
        elif choice == "2":
            dns_lookup()
            pause()
        elif choice == "3":
            traceroute()
            pause()
        elif choice == "4":
            port_check()
            pause()
        elif choice == "5":
            system_info()
            pause()
        elif choice == "6":
            quick_health_check()
            pause()
        elif choice == "7":
            save_report()
            pause()
        elif choice == "8":
            clear_screen()
            show_banner()
        elif choice == "9":
            print(color("Exiting NetPulse. Goodbye!", GREEN))
            break
        else:
            print(color("Invalid option. Please choose a number from 1 to 9.", RED))


if __name__ == "__main__":
    main()