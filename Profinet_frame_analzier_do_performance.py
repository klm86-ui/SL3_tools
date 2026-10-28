import json
import binascii
from datetime import datetime

# ======================================
# KONFIGURACJA
# ======================================

JSON_FILE = "j5.json"

# MAC urządzenia, którego ramki mają być analizowane
SOURCE_MAC = "ec:1c:5d:9e:8d:68"  # siemens

# Numer bajtu w pn_rt_raw
OFFSET = 19

# Wartość docelowa
# np. 1 dla przejścia 0 -> 1
TARGET_VALUE = 1


# ======================================
# FUNKCJE
# ======================================

def get_timestamp(packet):

    ts = packet["_source"]["layers"]["frame"]["frame.time_epoch"]

    return datetime.fromisoformat(
        ts.replace("Z", "+00:00")
    )


def is_gpio_rising(packet):

    try:

        net = packet["_source"]["layers"]["netanalyzer"]
        #print(f"Gpio check in:{net}")
        return (
            net["netanalyzer.gpio_event.gpio_number"] == "0x01"
            and
            net["netanalyzer.gpio_event.gpio_edge"] == "0x00"
        )

    except KeyError:
        return False


# ======================================
# ODCZYT JSON
# ======================================

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# ======================================
# ANALIZA
# ======================================

last_rising_edge = None
previous_value = None
pnio_do_detected = None
value = None
results = []

for packet in data:

    # ----------------------------
    # Timestamp
    # ----------------------------
    try:
        timestamp = get_timestamp(packet)
    except Exception:
        continue

    # ----------------------------
    # GPIO Rising Edge
    # ----------------------------
    if is_gpio_rising(packet) and pnio_do_detected is not None:
        delay_ms = (
                    timestamp - pnio_do_detected
                   ).total_seconds() * 1000
        pnio_do_detected =None
        frame_no = layers["frame"]["frame.number"]
        print("GPIO found")
        results.append(delay_ms)

        print(
            f"Frame {frame_no} | "
            f"Value {previous_value}->{value} | "
            f"Delay = {delay_ms:.3f} ms"
        )
        print(
            f"PNIO DO detected frame: {timestamp}\n"
        )

    try:

        layers = packet["_source"]["layers"]

        # ----------------------------
        # Tylko ramki Ethernet
        # ----------------------------
        if "eth" not in layers:
            continue

        src_mac = layers["eth"]["eth.src"].lower()

        # ----------------------------
        # Filtr MAC
        # ----------------------------
        if src_mac != SOURCE_MAC.lower():
            continue

        # ----------------------------
        # Tylko PNIO
        # ----------------------------
        if "pn_rt_raw" not in layers:
            continue

        hex_string = layers["pn_rt_raw"][0]

        frame = binascii.unhexlify(hex_string)

        if OFFSET >= len(frame):
            continue

        value = frame[OFFSET]
        #print(f"Frame {frame} |\n BYTE {value} ")
        #print(value, previous_value)
        # ----------------------------
        # Wykrycie zmiany na TARGET_VALUE
        # ----------------------------
        if (
            previous_value is not None
            and previous_value != TARGET_VALUE
            and value == TARGET_VALUE


        ):
            pnio_do_detected = timestamp
            print(f"Pnio detected time: {pnio_do_detected} \n")



        previous_value = value
    except Exception as e:

        print(
            f"Błąd analizy ramki: {e}"
        )
        continue





# ======================================
# PODSUMOWANIE
# ======================================

print("\n========================")
print("SUMMARY")
print("========================")

if len(results) == 0:

    print("Nie znaleziono żadnych zdarzeń.")

else:
    for n in results:
        print(n)
    print(f"Measurements : {len(results)}")
    print(f"Min latency     : {min(results):.3f} ms")
    print(f"Max latency     : {max(results):.3f} ms")
    print(f"Avg latency     : {sum(results)/len(results):.3f} ms")