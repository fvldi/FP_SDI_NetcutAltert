from scapy.all import conf, Ether, ARP, srp, sniff
from twilio.rest import Client
from mac_vendor_lookup import MacLookup

#twilio
def intruder():
    account_sid = 'AC8ed2a1615eaec60e151fe752a5f777dd' 
    auth_token = '3c228b3d2c51b753c495252937b94f20' 
    client = Client(account_sid, auth_token)

    message = client.messages.create( 
                                from_='whatsapp:+14155238886',  
                                body="\U0001F3F9 You were attacked by " + response_mac + " - " + vendor,   
                                to='whatsapp:+6285107777421' 
                            )
    print("[!] Alert sent!")

#ngambil mac address gateway
def get_mac(ip):
    """
    Returns MAC address dari `ip`, jika tidak terdeteksi
    lalu throws `IndexError`
    """
    p = Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip)
    result = srp(p, timeout=3, verbose=False)[0]
    return result[0][1].hwsrc

def process(packet):
    # jika packet merupakan ARP packet
    if packet.haslayer(ARP):
        # jika merupakan ARP response (ARP reply)
        if packet[ARP].op == 2:
            try:
                # get real MAC address dari gateway
                global real_mac
                real_mac = get_mac(packet[ARP].psrc)
                # get MAC address dari packet yang terkirim ke kita
                global response_mac
                response_mac = packet[ARP].hwsrc
                global vendor
                vendor = MacLookup().lookup(response_mac.upper())
                # jika berbeda, berarti telah terjadi netcut
                if real_mac != response_mac:
                    intruder()

            except IndexError:
                # Gagal menemukan real mac
                # Bisa jadi IP Palsu atau paket telah diblokir firewall
                pass

if __name__ == "__main__":
    import sys
    try:
        iface = sys.argv[1]
    except IndexError:
        iface = conf.iface
    sniff(store=False, prn=process, iface=iface)
