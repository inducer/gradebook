VT100_CODES = {
        'black':        '0;30',         'bright gray':  '0;37',
        'blue':         '0;34',         'white':                '1;37',
        'green':        '0;32',         'bright blue':  '1;34',
        'cyan':         '0;36',         'bright green': '1;32',
        'red':          '0;31',         'bright cyan':  '1;36',
        'purple':       '0;35',         'bright red':   '1;31',
        'yellow':       '0;33',         'bright purple':'1;35',
        'dark gray':'1;30',             'bright yellow':'1;33',
        'normal':       '0',
        'blink': '5',
}

def c(what):
    return "\033[%sm" % VT100_CODES[what]

