import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
import os

# ===== Adjustable parameters =====
volume = 1
mean = 0
variance = 5
global text

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
def encode(text):
    if text == '':
        return 0
    else:
        bits = text_to_bits(text)
        tx_signal = np.zeros(len(bits) // 2 * num_samples)
        # Pad to even bits (usually not used) 
        if(len(bits)%2 != 0):
            bits += '0'
        for i in range(0,len(bits),2):
            idx = int(bits[i:i+2],2)
            t = np.arange(num_samples)/sample_rate
            tx_signal[i//2*num_samples : (i//2+1)*num_samples] = \
                volume*np.sin(2*np.pi*bit_freq[idx]*t)
        # Combine pre and signal
        pre = gen_pre()
        mid = np.zeros(len(pre)+len(tx_signal))
        mid[:len(pre)] = pre
        mid[len(pre):] = tx_signal
        tx_signal = mid
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
        chunk = sig[i * num_samples:(i+1)*num_samples]

        # Score each candidate frequency
        scores = []
        for ref in refs:
            scores.append(np.abs(np.sum(chunk*ref)))

        # argmax gives the index of the best-matching frequency
        idx = int(np.argmax(scores))
        bits += format(idx, '02b')

    text = bits_to_text(bits)
    return text

# Testing with noise if needed
def make_noise(signal):
    noise = np.random.normal(mean,variance,len(signal))
    return signal + noise

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
    
                # Create and mix the pre and message signals
                pre = gen_pre()
                signal = encode(text)
                mid = np.zeros(len(pre)+len(signal))
                mid[:len(pre)] = pre
                mid[len(pre):] = signal
                tx_signal = mid
    
                # Make plots for testing
                make_plot(tx_signal)
    
            # Receive Select
            elif(selected == 2):
                #rx_signal = make_noise(tx_signal)
                rx_signal = tx_signal
                print(decode(rx_signal))
            elif(selected == 3):
                return 0
    
            print("\n")

# ===== UI ======
def app():
    root = tk.Tk()

    # Variables
    txText = tk.StringVar()


    # === Functions ===
    def log_write(msg):
        log.config(state="normal")
        log.insert("end", msg + "\n")
        log.see("end")
        log.config(state="disabled")

    # Used to trigger the TX button
    def submit():
        text = txText.get()
        if not text:
            return
        txText.set('')
        log_write(f"tx > {text}")     # <-- prints to the big frame
        txSignal = encode(text)
        #make_plot(txSignal)
        

    # Setting some window properties
    root.title("4-FSK")
    root.configure(background="lightgray")
    root.geometry("450x600")
    root.minsize(400,400)

    # Conversation Window
    textWindow = tk.Frame(root,width=350,height=300)
    textWindow.grid(row=0,column=1,sticky='ew')
    textWindow.columnconfigure(0, weight=1)
    textWindow.rowconfigure(0, weight=1)
    log = tk.Text(textWindow, height=10, wrap="word", font=("Consolas", 11),
                  background="#1e1e1e", foreground="#d4d4d4",
                  insertbackground="#d4d4d4", relief="flat")
    log.grid(row=0, column=0, sticky="ew")

    scrollbar = tk.Scrollbar(textWindow, orient="vertical", command=log.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    log.config(yscrollcommand=scrollbar.set, state="disabled")

    # TX Button
    tx_button = tk.Button(root,width=50,height=5,text='Transmit',command=submit,activebackground='red')
    tx_button.grid(row=2,column=1,sticky='ew')
    tk.Label(root, text="Message").grid(row=1,column=0)
    txInput = tk.Entry(root,textvariable=txText,width=60).grid(row=1,column=1,sticky='ew')

    close_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'icons','close.png')
    closeIcon = tk.PhotoImage(file=close_Path)
    endProgram = tk.Button(root, width=5, height=5,command=root.destroy,activebackground='red',image=closeIcon)
    endProgram.image = closeIcon
    endProgram.grid(row=0,column=2,sticky='ew')

    #tk.Label(root,text='Testing the 4-FSK app for the future').pack()
    #tk.Label(root,text='-SV9TOQ').pack()
    root.mainloop()

if __name__ == '__main__':
    app()