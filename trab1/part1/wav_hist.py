import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

rate, data = wavfile.read("sample07.wav")

k = 3
group_size = 2**k

if len(data.shape) > 1 and data.shape[1] == 2:
    left_channel = data[:, 0].astype(np.int32)
    right_channel = data[:, 1].astype(np.int32)
    mid_channel = (left_channel+right_channel)//2
    side_channel = (left_channel-right_channel)//2

    # para reconstituir o canal
    parity = (left_channel-right_channel) % 2
    re_left = mid_channel+side_channel + parity
    re_right = mid_channel-side_channel

    min_val = min(left_channel.min(), right_channel.min(), mid_channel.min(), side_channel.min())
    max_val = max(left_channel.max(), right_channel.max(), mid_channel.max(), side_channel.max())
    bin_range = np.arange(min_val, max_val+group_size, group_size)

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    axs[0, 0].hist(left_channel, bins=bin_range, color="blue", alpha=0.7)
    axs[0, 0].set_title("Canal Esquerdo (Left)")
    axs[0, 0].set_xlabel("Amplitude")

    axs[0, 1].hist(right_channel, bins=bin_range, color="red", alpha=0.7)
    axs[0, 1].set_title("Canal Direito (Right)")
    axs[0, 1].set_xlabel("Amplitude")

    axs[1, 0].hist(mid_channel, bins=bin_range, color="green", alpha=0.7)
    axs[1, 0].set_title("Canal Mid (L + R) / 2")
    axs[1, 0].set_xlabel("Amplitude")

    axs[1, 1].hist(side_channel, bins=bin_range, color="magenta", alpha=0.7)
    axs[1, 1].set_title("Canal Side (L - R) / 2")
    axs[1, 1].set_xlabel("Amplitude")

    plt.tight_layout()
    plt.show()
    
else:
    left_channel = data
    mid_channel = left_channel

    min_val = left_channel.min()
    max_val = left_channel.max()
    bin_range = np.arange(min_val, max_val+group_size, group_size)


    plt.hist(mid_channel, bins=bin_range, color="blue", alpha=0.7)
    plt.title("Canal Mid (Áudio Mono)")
    plt.show()
