from scapy.all import * #conf, Ether, ARP, srp, sniff
from twilio.rest import Client
from time import sleep, time
from mac_vendor_lookup import MacLookup


account_sid = 'TWILIO_ACCOUNT_SID' 
auth_token = 'TWILIO_AUTH_TOKEN'

client = Client(account_sid, auth_token)

#twilio
def intruder():

    message = client.messages.create( 
                                body="\U0001F3F9 You were attacked by " + response_mac + " - " + vendor,
                                from_='whatsapp:+TWILIO_WA_BOT',   
                                to='whatsapp:+WA_NUMBER' 
                            )
    print("[!] Alert sent!")
    sleep(10)

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
                    print("[!] Detected")
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
