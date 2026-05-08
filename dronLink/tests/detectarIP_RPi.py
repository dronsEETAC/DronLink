import subprocess

arp = subprocess.check_output("arp -a").decode("cp1252")

for line in arp.split("\n"):

    if "b8-27-eb" in line.lower() or "dc-a6-32" in line.lower() or "e4-5f-01" in line.lower():
        print("Raspberry Pi encontrada:", line)

