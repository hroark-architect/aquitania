########################################################################################################################
# |||||||||||||||||||||||||||||||||||||||||||||||||| AQUITANIA ||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||| To be a thinker means to go by the factual evidence of a case, not by the judgment of others |||||||||||||||||| #
# |||| As there is no group stomach to digest collectively, there is no group mind to think collectively. |||||||||||| #
# |||| Each man must accept responsibility for his own life, each must be sovereign by his own judgment. ||||||||||||| #
# |||| If a man believes a claim to be true, then he must hold to this belief even though society opposes him. ||||||| #
# |||| Not only know what you want, but be willing to break all established conventions to accomplish it. |||||||||||| #
# |||| The merit of a design is the only credential that you require. |||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
########################################################################################################################

"""
.. moduleauthor:: H Roark
"""

import math


def full_line(line_len=79):
    print('-' * line_len)


def blank_line(line_len=79):
    centered_line('', line_len)


def centered_line(text, line_len=79):
    length = len(text)
    brackets = '----'
    blank_space = line_len - length - len(brackets * 2)
    print(brackets + ' ' * int(blank_space / 2) + text + ' ' * int(math.ceil(blank_space / 2)) + brackets)


def indented_line(text, line_len=79):
    spaced_line(text, 4, line_len)


def double_indented_line(text, line_len=79):
    spaced_line(text, 8, line_len)


def spaced_line(text, n_spaces, line_len=79):
    brackets = '----'

    text_max = line_len - len(brackets * 2) - n_spaces - 1  # -1 because there needs to be a space in the end
    if len(text) > text_max:
        pos = text[:text_max].rfind(' ')

        if pos != -1:
            text_a = text[:pos]
            spaced_line(text_a, n_spaces, line_len=79)

            text_b = text[pos + 1:]
            spaced_line(text_b, n_spaces, line_len=79)
            return

    length = len(text)
    blank_space = line_len - length - len(brackets * 2) - n_spaces
    if len(text) > line_len - len(brackets * 2) - n_spaces:
        raise ValueError('Line too long, please correct it.')
    print(brackets + ' ' * n_spaces + text + ' ' * blank_space + brackets)


"""
-------------------------------------------------------------------------------
----                        LIVE ENVIRONMENT DISPLAY                       ----
-------------------------------------------------------------------------------
----                                                                       ----
----   NUMBER OF CONNECTED BROKERS                                         ----
----                                                                       ----
-------------------------------------------------------------------------------
----                    CURRENT STRATEGY LIVE PERFORMANCE                  ----
-------------------------------------------------------------------------------
----                                                                       ----
----   HISTORIC PERFORMANCE                                                ----
----   MONTHLY PERFORMANCE                                                 ----
----   WEEKLY PERFORMANCE                                                  ----
----                                                                       ----
-------------------------------------------------------------------------------
----                    STATUS WITH BROKER {BROKER_NAME}                   ----
-------------------------------------------------------------------------------
----                                                                       ----
----    ASSETS BEING TRADED (12 TOTAL):                                    ----
----        EUR_USD, USD_JPY, GBP_USD, USD_CAD, EUR_JPY, GBP_JPY, EUR_CAD  ----
----        AUD_USD, EUR_AUD, AUD_JPY, EUR_HKD, HKD_JPY                    ----
----                                                                       ----
----    STATUS: WORKING CONNECTION WITH {BROKER_NAME}                      ----
----                                                                       ----
----    ACCOUNT BALANCE:  88,902.88 USD                                    ----
----                                                                       ----
----    AVAILABLE MARGIN: 38,192.82 USD                                    ----
----                                                                       ----
----    MAX LEVERAGE: 100x                                                 ----
----                                                                       ----
-------------------------------------------------------------------------------
----                     OPEN POSITIONS {BROKER_NAME}                      ----
-------------------------------------------------------------------------------
----                                                                       ----
----    TOTAL OF OPEN POSITIONS:  01 TRADE                                 ----
----                                                                       ----
----    TRADE #1: AUD_USD - LONG                                           ----
----        ENTRY TIME:                                                    ----
----        ENTRY PRICE:                                                   ----
----        ORDER SIZE:                                                    ----
----        CURRENT PL:                                                    ----
----        MARGIN USED:                                                   ----
----                                                                       ----
-------------------------------------------------------------------------------
----                     EXPOSURE ON {BROKER_NAME}                         ----
-------------------------------------------------------------------------------
----                                                                       ----
----                                                                       ----
----                                                                       ----
-------------------------------------------------------------------------------
"""

"""
{'id': '1022', 
'instrument': 'AUD_USD', 
'price': '0.74892', 
'openTime': '2018-05-01T22:15:15.855215071Z', 
'initialUnits': '-1', 
'initialMarginRequired': '0.0075',
'state': 'OPEN', 
'currentUnits': '-1', 
'realizedPL': '0.0000', 
'financing': '0.0000', 
'unrealizedPL': '-0.0002', 
'marginUsed': '0.0075'}
"""

"""
'AUD_USD'
'0.74892'
'LONG/SHORT'
'order_size': '1'
'unrealizedPL': '-0.0002' + 'realizedPL': '0.0000', 
'marginUsed': '0.0075'
"""
