import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import argparse
import sys


parser = argparse.ArgumentParser(description="Histogramas de um ficheiro WAV")
parser.add_argument("file", type=str)
parser.add_argument("--k",  type=int, default=3)
args = parser.parse_args()

try:
    rate, data = wavfile.read(args.file)
except FileNotFoundError:
    print(f"Erro: o ficheiro '{args.file}' não existe")
    sys.exit(1)
except ValueError: # vê mesmo o cabeçalho em sim ent desde que esteja lá wav tá chill
    print(f"Erro: '{args.file}' não é um ficheiro WAV válido")
    sys.exit(1)

if data.ndim > 1 and data.shape[1] > 2:     # mono passsa logo 
    print("Erro: só são suportados ficheiros mono ou estéreo")
    sys.exit(1)
if data.shape[0] == 0:
    print("Erro: o ficheiro não tem amostras")
    sys.exit(1)

k = args.k
if not (0 <= k < 16):
    print("Erro: k tem de estar entre 0 e 15")
    sys.exit(1)
group_size = 2**k


def mid_side(left, right):
    mid = (left + right) // 2
    side = (left - right) // 2
    return mid, side

def reconstruct(mid, side, parity):
    # para reconstituir o canal
    left = mid + side + parity          # aqui porque a sub anulam-se, mas na adição elas disfarça ent tenho que meter explicito
    right = mid - side
    return left, right

def plot_hist(ax, x, bins, title, color):
    ax.hist(x, bins=bins, color=color, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Amplitude")


def main():
    if data.ndim > 1 and data.shape[1] == 2:
        left_channel = data[:, 0].astype(np.int32)
        right_channel = data[:, 1].astype(np.int32)
        mid_channel, side_channel = mid_side(left_channel, right_channel)

        parity = (left_channel - right_channel) % 2     # na divisão resto perde-se, ent precisamos de adicionar esse 1
        re_left, re_right = reconstruct(mid_channel, side_channel, parity)
        assert np.array_equal(re_left, left_channel) and np.array_equal(re_right, right_channel)

        min_val = min(left_channel.min(), right_channel.min(), mid_channel.min(), side_channel.min())
        max_val = max(left_channel.max(), right_channel.max(), mid_channel.max(), side_channel.max())
        bin_range = np.arange(min_val, max_val + group_size, group_size)

        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        plot_hist(axs[0, 0], left_channel,  bin_range, "Canal Esquerdo (Left)", "blue")
        plot_hist(axs[0, 1], right_channel, bin_range, "Canal Direito (Right)", "red")
        plot_hist(axs[1, 0], mid_channel,   bin_range, "Canal Mid (L + R) / 2", "green")
        plot_hist(axs[1, 1], side_channel,  bin_range, "Canal Side (L - R) / 2", "magenta")

    else:
        mono = data.astype(np.int32)
        bin_range = np.arange(mono.min(), mono.max() + group_size, group_size)
        plot_hist(plt.gca(), mono, bin_range, "Canal Mono", "blue")

    plt.tight_layout()
    plt.show()

main()
