from colorama import Fore

RESET = Fore.RESET


def with_color(text, color):
    return getattr(Fore, color) + str(text) + RESET


red = lambda text: with_color(text, 'RED')
green = lambda text: with_color(text, 'GREEN')
yellow = lambda text: with_color(text, 'YELLOW')
blue = lambda text: with_color(text, 'BLUE')
magenta = lambda text: with_color(text, 'MAGENTA')
cyan = lambda text: with_color(text, 'CYAN')
gr = lambda text, cond: with_color(text, 'GREEN' if cond else 'RED')
