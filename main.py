import numpy as np

# ===== Parameters =====
sample_rate = 48000
baud = 800
T = 1.0 / baud
num_samples = int(sample_rate * T)
bit_freq = [400, 1200, 2000, 2800]

pre_freq = 1000
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


if __name__ == '__main__':
    text = input("Enter the text: ")
    bits = text_to_bits(text)
    print(bits)
    rx_text = bits_to_text(bits)
    print(rx_text)