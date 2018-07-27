import os
import colorama


def banner():
    banner = """
    ================================================
        DE TAI NGHIEN CUU KHOA HOC - TOP 5 OWASP
        
        SVTH
            LE VAN CHON
            VO XUAN KHANG
        GVHD
            TS.HUYNH TRONG THUA

        10/2017
    ================================================
    """
    print(colorama.Fore.CYAN + banner +colorama.Fore.RESET)


def init():
    if os.name == 'nt':
        os.system ('cls')
    else:
        os.system ('clear')
