from scipy.io import wavfile
import numpy as np
import argparse
import sys
import os



parser = argparse.ArgumentParser(description="Efeitos de áudio")
parser.add_argument("file", type=str)
parser.add_argument("--g", type=float, default=0.5)
parser.add_argument("--delay", type=float, default=0.3)
parser.add_argument("--f", type=float, default=5)
parser.add_argument("--D0", type=float, default=0.005)
parser.add_argument("--A", type=float, default=0.003)
args = parser.parse_args()

try:
    rate, data = wavfile.read(args.file)
except FileNotFoundError:
    print(f"Erro: o ficheiro '{args.file}' não existe")
    sys.exit(1)
except ValueError:
    print(f"Erro: '{args.file}' não é um ficheiro WAV válido")
    sys.exit(1)

if data.ndim > 1 and data.shape[1] > 2:
    print("Erro: só são suportados ficheiros mono ou estéreo")
    sys.exit(1)
if data.shape[0] == 0:
    print("Erro: o ficheiro não tem amostras")
    sys.exit(1)

for name in ("g", "delay", "f", "D0", "A"):
    if not np.isfinite(getattr(args, name)):
        print(f"Erro: {name} tem de ser um número finito")
        sys.exit(1)

g = args.g
delay = args.delay
f = args.f
d = int(delay * rate)
N = data.shape[0]
n = np.arange(N)
D0 = args.D0 * rate
A = args.A * rate

if not (0 < g < 1):
    print("Erro: g tem de estar entre 0 e 1")
    sys.exit(1)
if d < 1 or d >= N:
    print("Erro: delay inválido para este áudio")
    sys.exit(1)
if not (0 < f < rate / 2):
    print(f"Erro: f tem de estar entre 0 e {rate / 2} Hz")
    sys.exit(1)

if D0 <= 0:
    print("Erro: D0 tem de ser positivo")
    sys.exit(1)

if not (0 <= A <= D0):
    print("Erro: A tem de estar entre 0 e D0")
    sys.exit(1)

if D0 + A >= N:
    print("Erro: D0 + A tem de ser menor que a duração do áudio")
    sys.exit(1)



if data.ndim == 1:
    data = data.reshape(-1, 1)      # faz passar o mono por um de mais canais


def echo(x, d, g):
    y = x.copy()
    y[d:] = x[d:] + g * x[:-d]          # usamos este tipo de slicing para que um aúdio de um segundo não demore segundos a processar, com for estaria a haver verificações amostra a amostra
    return y

def mult_echo(x, d, g, ):
    y = x.copy()
    for k in range(d, len(x), d):
        end = min(k + d, len(x))            # caso o ultmo bloco ser menor caso o audio não ter um numero exato de blcos
        y[k:end]  += g * y[k - d:end - d]
    return y

def am(x, f, n, rate):
    m = np.cos((2*np.pi*f*(n/rate)))     
    y = x * m
    return y

def tv_delay(x, D0, A, f, g, n, rate):
    p = np.sin((2*np.pi*f*(n/rate)))    # y(n) = x(n) + g · x(n − D(n)),  com  D(n) = D0 + A · sin(2π f n / fs)
    D = D0 + A * p
    i = np.around(n- D).astype(int) # o indice que vai para o segundo x(), esta coisa td porque D é não int
    valid = i >= 0          # evita o caso em que estamos no início do file e não há audio pras essas amostras

    y = x.copy()
    y[valid] = x[valid] + g * x[i[valid]]       # instante válido do passado
    return y


def apply(effect, data, *params):
    channels = []
    for c in range(data.shape[1]):
        x = data[:, c].astype(np.float64)
        channels.append(effect(x, *params)) 
    return np.column_stack(channels)            # junta como coluna a coluna 



def save(name, sig):
    wavfile.write(name, rate, np.clip(np.round(sig), -32768, 32767).astype(np.int16))       # arredonda pra int, corta pros 16 bits e converte pro tipo

def main():
    base = os.path.splitext(args.file)[0]
    save(f"{base}_echo.wav",      apply(echo, data, d, g))
    save(f"{base}_mult_echo.wav", apply(mult_echo, data, d, g))
    save(f"{base}_am.wav",        apply(am, data, f, n, rate))
    save(f"{base}_tvdelay.wav",   apply(tv_delay, data, D0, A, f, g, n, rate))

main()