import colorama
from colorama import Fore, Back, Style
colorama.init(strip=False)

def printWarning(text):
    print(Back.YELLOW + Fore.WHITE + text + Fore.RESET + Back.RESET)
def printError(text):
    print(Back.RED + Fore.WHITE + text + Fore.RESET + Back.RESET)

#---PRINT COLOR---#

def printBlack(text):
    print(Back.RESET + Fore.BLACK + text + Fore.RESET)
def printBlue(text):
    print(Back.RESET + Fore.BLUE + text + Fore.RESET)
def printCyan(text):
    print(Back.RESET + Fore.CYAN + text + Fore.RESET)
def printGreen(text):
    print(Back.RESET + Fore.GREEN + text + Fore.RESET)
def printMagenta(text):
    print(Back.RESET + Fore.MAGENTA + text + Fore.RESET)
def printRed(text):
    print(Back.RESET + Fore.RED + text + Fore.RESET)
def printReset(text):
    print(Back.RESET + Fore.RESET + text + Fore.RESET)
def printWhite(text):
    print(Back.RESET + Fore.WHITE + text + Fore.RESET)
def printYellow(text):
    print(Back.RESET + Fore.YELLOW + text + Fore.RESET)

def printLightBlack(text):
    print(Back.RESET + Fore.LIGHTBLACK_EX + text + Fore.RESET)
def printLightBlue(text):
    print(Back.RESET + Fore.LIGHTBLUE_EX + text + Fore.RESET)
def printLightCyan(text):
    print(Back.RESET + Fore.LIGHTCYAN_EX + text + Fore.RESET)
def printLightGreen(text):
    print(Back.RESET + Fore.LIGHTGREEN_EX + text + Fore.RESET)
def printLightMagenta(text):
    print(Back.RESET + Fore.LIGHTMAGENTA_EX + text + Fore.RESET)
def printLightRed(text):
    print(Back.RESET + Fore.LIGHTRED_EX + text + Fore.RESET)
def printLightWhite(text):
    print(Back.RESET + Fore.LIGHTWHITE_EX + text + Fore.RESET)
def printLightYellow(text):
    print(Back.RESET + Fore.LIGHTYELLOW_EX + text + Fore.RESET)

#---PRINT WITH BACKGROUND---#

def printBlackB(text):
    print(Fore.WHITE + Back.BLACK + text + Fore.RESET + Back.RESET)
def printBlueB(text):
    print(Fore.WHITE + Back.BLUE + text + Fore.RESET + Back.RESET)
def printCyanB(text):
    print(Fore.WHITE + Back.CYAN + text + Fore.RESET + Back.RESET)
def printGreenB(text):
    print(Fore.BLACK + Back.GREEN + text + Fore.RESET + Back.RESET)
def printMagentaB(text):
    print(Fore.WHITE + Back.MAGENTA + text + Fore.RESET + Back.RESET)
def printRedB(text):
    print(Fore.WHITE + Back.RED + text + Fore.RESET + Back.RESET)
def printResetB(text):
    print(Fore.WHITE + Back.RESET + text + Fore.RESET + Back.RESET)
def printWhiteB(text):
    print(Fore.BLACK + Back.WHITE + text + Fore.RESET + Back.RESET)
def printYellowB(text):
    print(Fore.BLACK + Back.YELLOW + text + Fore.RESET + Back.RESET)

def printLightBlackB(text):
    print(Fore.WHITE + Back.LIGHTBLACK_EX + text + Fore.RESET + Back.RESET)
def printLightBlueB(text):
    print(Fore.WHITE + Back.LIGHTBLUE_EX + text + Fore.RESET + Back.RESET)
def printLightCyanB(text):
    print(Fore.WHITE + Back.LIGHTCYAN_EX + text + Fore.RESET + Back.RESET)
def printLightGreenB(text):
    print(Fore.WHITE + Back.LIGHTGREEN_EX + text + Fore.RESET + Back.RESET)
def printLightMagentaB(text):
    print(Fore.WHITE + Back.LIGHTMAGENTA_EX + text + Fore.RESET + Back.RESET)
def printLightRedB(text):
    print(Fore.WHITE + Back.LIGHTRED_EX + text + Fore.RESET + Back.RESET)
def printLightWhiteB(text):
    print(Fore.BLACK + Back.LIGHTWHITE_EX + text + Fore.RESET + Back.RESET)
def printLightYellowB(text):
    print(Fore.BLACK + Back.LIGHTYELLOW_EX + text + Fore.RESET + Back.RESET)