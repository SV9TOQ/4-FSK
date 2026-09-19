import numpy as np

# ===== Parameters =====
sample_rate = 48000
baud = 800
T = 1.0 / baud
num_samples = int(sample_rate * T)
bit_freq = [400, 1200, 2000, 2800]

pre_freq = 300
pre_duration = 300 # Time in ms

# ===== Functions =====
# === Text/bit conversions ===

def text_to_bits(text):
    bits = ''
    for char in text:
        bits += format(ord(char), '08b')
    return bits

def bits_to_text(bits):
    bits = bits[:len(bits) - (len(bits) % 8)]
    chars = []
    for i in range(0, len(bits), 8):
        chars.append(chr(int(bits[i:i+8], 2)))
    return ''.join(chars)

# === Transmit Sequence ===
def encode(bits):

    return tx_signal

# gen_pre is used to trigger the radio's vox similar to how it is used in APRS AFSK
def gen_pre():
    num_samples = int(sample_rate*pre_duration/1000)
    t = np.arange(num_samples)/sample_rate
    return np.sin(2*np.pi*pre_freq*t)


# ===== UI ======
def menu():
    while True:
        print("Please select one of the following numbers.")
        print("1. Send text")
        print("2. Decode recent text")
        print("3. Exit")

        try:
            selected = int(input("Enter a number: "))
        except ValueError:
            print("Invalid input. Please enter an integer.")   

        if(selected == 1):
            text = input("Enter the text: ")
            bits = text_to_bits(text)
            print(bits)
        elif(selected == 2):
            rx_text = bits_to_text(bits)
            print(rx_text)
        elif(selected == 3):
            return 0

        print("\n")
            

if __name__ == '__main__':
    menu()