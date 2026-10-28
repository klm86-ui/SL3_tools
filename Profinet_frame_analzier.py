import json
import binascii

def extract_hex_frames(json_data, field="pn_rt_raw"):
    """
    Pobiera hex-stringi z całego JSON-a Wiresharka.
    Zakłada, że hex jest w polu field[0].
    """
    frames = []

    for packet in json_data:
        try:
            hex_string = packet["_source"]["layers"][field][0]
            frames.append(hex_string)
        except KeyError:
            continue

    return frames


def count_byte_changes(frames_hex, offset):
    """
    Liczy zmiany wartości bajtu na danym offsetcie.
    Zwraca: lista wartości bajtu, liczba zmian.
    """
    values = []
    previous = None
    changes = 0

    for hex_string in frames_hex:
        frame = binascii.unhexlify(hex_string)
        if offset >= len(frame):
            raise ValueError(f"Offset {offset} poza długością ramki ({len(frame)} bajtów)")

        value = frame[offset]
        values.append(value)

        if previous is not None and value != previous:
            changes += 1

        previous = value

    return values, changes


# -----------------------------
# PRZYKŁADOWE UŻYCIE
# -----------------------------

# Wczytaj JSON z Wiresharka
with open("125Hz.json", "r") as f:
    data = json.load(f)

# Pobierz wszystkie ramki z pola pn_rt_raw
frames = extract_hex_frames(data, field="pn_rt_raw")

# Offset bajtu, który chcesz śledzić
offset = 22# Pin 4 port 4 -20, Pin 4 port 5 - 22, Pin 2 Port 5 - 6

# Policz zmiany
values, changes = count_byte_changes(frames, offset)

print("Wartości bajtu kolejno:", values)
print("Liczba zmian wartości:", changes)
