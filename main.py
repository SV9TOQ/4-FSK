import numpy as np
import matplotlib.pyplot as plt

# ===== Adjustable parameters =====
volume = 1

# ===== Parameters =====
sample_rate = 48000
baud = 1200
T = 1 / baud
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
    tx_signal = np.zeros(len(bits) // 2 * num_samples)
    # Pad to even bits (usually not used) 
    if(len(bits)%2 != 0):
        bits += '0'
    for i in range(0,len(bits),2):
        idx = int(bits[i:i+2],2)
        t = np.arange(num_samples)/sample_rate
        tx_signal[i//2*num_samples : (i//2+1)*num_samples] = \
            volume*np.sin(2*np.pi*bit_freq[idx]*t)
    return tx_signal

# gen_pre is used to trigger the radio's vox similar to how it is used in APRS AFSK
def gen_pre():
    num_samples = int(sample_rate*pre_duration/1000)
    t = np.arange(num_samples)/sample_rate
    return volume*np.sin(2*np.pi*pre_freq*t)

# === Decode Sequence ===
def decode(signal):
    # Skip the preamble
    pre_len = len(gen_pre())
    sig = signal[pre_len:]
    # Calculate the number of symbols and time for one 
    num_symbols = len(sig)//num_samples
    t_symbol = np.arange(num_samples)/sample_rate

    # Precompute reference complex exponentials (one per candidate freq)
    refs = [np.exp(-1j*2*np.pi*f*t_symbol) for f in bit_freq]

    bits = ''
    for i in range(num_symbols):
        chunk = sig[i * num_samples:(i + 1) * num_samples]

        # Score each candidate frequency
        scores = []
        for ref in refs:
            scores.append(np.abs(np.sum(chunk * ref)))

        # argmax gives the index of the best-matching frequency
        idx = int(np.argmax(scores))

        # Convert index back to 2 bits
        bits += format(idx, '02b')

    text = bits_to_text(bits)
    return text

def make_plot(tx):
    t = np.arange(len(tx))/sample_rate
    plt.figure(figsize=(8,4))

    plt.subplot(2,1,1)
    plt.plot(t,np.real(tx))
    plt.xlabel('Time(s)')
    plt.ylabel('Amplitude')
    plt.title('Signal in time')
    plt.grid()

    fourier = np.fft.fftshift(np.fft.fft(tx))
    N = len(fourier)
    fourier_freq = np.fft.fftshift(np.fft.fftfreq(N, d=1/sample_rate))

    plt.subplot(2,1,2)
    plt.plot(fourier_freq,np.real(fourier))
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.title('Signal in frequency')
    plt.grid()
    plt.show()

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
            continue

        # Transmit Select
        if(selected == 1):
            text = input("Enter the text: ")
            bits = text_to_bits(text)
            print(bits)

            # Create and mix the pre and message signals
            pre = gen_pre()
            signal = encode(bits)
            mid = np.zeros(len(pre)+len(signal))
            mid[:len(pre)] = pre
            mid[len(pre):] = signal
            tx_signal = mid

            # Make plots for testing
            #make_plot(tx_signal)

        # Receive Select
        elif(selected == 2):
            #rx_text = bits_to_text(bits)
            #print(rx_text)
            print(decode(tx_signal))
        elif(selected == 3):
            return 0

        print("\n")

if __name__ == '__main__':
    menu()