import frappe


@frappe.whitelist()
def generateBarcode(string):

    from barcode import Code128
    from barcode.writer import ImageWriter
    from io import BytesIO
    import base64

    file_like_object = BytesIO()
    writer = ImageWriter()
    value = f'{string}'
    options = {
        "module_width": 0.1,
        "module_height": 1,
        "quiet_zone": 0,
        "write_text": False,
        "text_distance": 1,
    }

    Code128(value, writer=writer).write(
        file_like_object, options)

    encoded = base64.b64encode(file_like_object.getvalue()).decode("ascii")

    return f'<img src="data:image/png;base64,{encoded}"  />'


lookup = {
    " ": 0,
    "!": 1,
    '"': 2,
    "#": 3,
    "$": 4,
    "%": 5,
    "&": 6,
    "‘": 7,
    "(": 8,
    ")": 9,
    "*": 10,
    "+": 11,
    ",": 12,
    "-": 13,
    ".": 14,
    "/": 15,
    "0": 16,
    "1": 17,
    "2": 18,
    "3": 19,
    "4": 20,
    "5": 21,
    "6": 22,
    "7": 23,
    "8": 24,
    "9": 25,
    ":": 26,
    ";": 27,
    "<": 28,
    "=": 29,
    ">": 30,
    "?": 31,
    "@": 32,
    "A": 33,
    "B": 34,
    "C": 35,
    "D": 36,
    "E": 37,
    "F": 38,
    "G": 39,
    "H": 40,
    "I": 41,
    "J": 42,
    "K": 43,
    "L": 44,
    "M": 45,
    "N": 46,
    "O": 47,
    "P": 48,
    "Q": 49,
    "R": 50,
    "S": 51,
    "T": 52,
    "U": 53,
    "V": 54,
    "W": 55,
    "X": 56,
    "Y": 57,
    "Z": 58,
    "[": 59,
    "\\": 60,
    "]": 61,
    "^": 62,
    "_": 63,
    "`": 64,
    "a": 65,
    "b": 66,
    "c": 67,
    "d": 68,
    "e": 69,
    "f": 70,
    "g": 71,
    "h": 72,
    "i": 73,
    "j": 74,
    "k": 75,
    "l": 76,
    "m": 77,
    "n": 78,
    "o": 79,
    "p": 80,
    "q": 81,
    "r": 82,
    "s": 83,
    "t": 84,
    "u": 85,
    "v": 86,
    "w": 87,
    "x": 88,
    "y": 89,
    "z": 90,
    "{": 91,
    "|": 92,
    "}": 93,
    "~": 94,
    "Ã": 95,
    "Ä": 96,
    "Å": 97,
    "Æ": 98,
    "Ç": 99,
    "È": 100,
    "É": 101,
    "Ê": 102,
    "Ë": 103,
    "Ì": 104,
    "Í": 105
}


@frappe.whitelist()
def generateBarcodeGlyphs(data):
    code = chr(204)
    checksum = 104

    for i in range(len(data)):
        code += data[i]
        checksum += lookup[data[i]] * (i + 1)

    code += list(lookup.keys())[list(lookup.values()).index(checksum % 103)]

    # append stop
    code += chr(206)

    return code
