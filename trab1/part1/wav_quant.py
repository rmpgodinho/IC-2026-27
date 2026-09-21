import numpy
import soundfile


data, samplerate = soundfile.read('sample01.wav')

b = 16
a_max = numpy.max(numpy.abs(data))
delta = 2 * a_max / (2 ** b)
data_q = delta * numpy.round(data / delta)


soundfile.write('sample01_quant.wav', data_q, samplerate)