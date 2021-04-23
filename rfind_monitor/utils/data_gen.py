import numpy as np
import h5py
import datetime
from dateutil import tz

import rfind_monitor.const as const


##* What to simulate
# Carriers
fcs = [25e6, 85e6, 41e6, 900e6, -400e6, -401e6, -402e6]
phase_incrs = [0]*len(fcs)

# FM signals
fms = [
    (-900e6,200e3), #fc, bw
    (-915e6,200e3),
    (-925e6,200e3),
    (-935e6,200e3),
    (-950e6,200e3),
    (-550e6,20e6),
    (375e6,35e6)
]

# band limited noise
# limited_noises = [
#     (-600e6,-500e6, 1.5), #f1, f2, sigma^2
#     (350e6, 400e6, 3)
# ]
limited_noises=[]
# sweeps = [(92e6,94e6,0.1), (-350e6,-15e6, 0.3)] #f1,f2,T
sweeps=[]

t_int = const.NBINS/const.FS # so that each fft is one integration


# def band_limited_noise(f1, f2, noise_pwr, t_arr):
#     """
#     f1: start frequency
#     f2: end frequency
#     fs: sample rate
#     t: duration
#     """

#     tempFreqs = np.abs(np.fft.fftfreq(len(t_arr), const.FS))


#     noise = np.random.normal(0,np.sqrt(noise_pwr), len(t_arr)) + 1j*np.random.normal(0,np.sqrt(noise_pwr), len(t_arr))
#     BW = (f2-f1) / 2
#     fc = (f1+f2) / 2

#     # bands = [0, BW, BW+BW/2, fs/2]

#     taps = remez(numtaps=1000, bands=bands, desired=[1,0], fs=fs)

#     x = np.zeros(len(t_arr)).astype(np.complex)
#     x[0]=1
#     x = lfilter(b=taps, a=1, x=x)

#     rotator = np.exp(2j*np.pi*fc*t_arr)

#     return x*rotator

def FM(fc, BW, t_arr):
    BW/=2
    fm = 1e5
    Am=1
    mt = Am*np.cos(2*np.pi*fm*t_arr)
    beta = BW/fm
    Ac=1
    st = Ac*np.exp(1j*(2*np.pi*fc*t_arr+beta*mt))
    return st


def integrated_spec_gen(noise_pwr, time) -> np.ndarray:
    t_incr = 0

    while t_incr <= time:
        t_arr = np.linspace(t_incr, t_incr+t_int, const.NBINS)

        output = np.random.normal(0,np.sqrt(noise_pwr), const.NBINS) + 1j*np.random.normal(0,np.sqrt(noise_pwr), const.NBINS)

        for fc in fcs:
            output += np.exp(2j*np.pi*fc*t_arr)
        # for f1,f2,T in sweeps:
        #     output += np.exp(1j*(np.pi*((f2-f1)/T)*np.square(t_arr)))
        for fc, bw in fms:
            output += FM(fc,bw,t_arr)
        # for f1,f2 in limited_noises:
        #     output += band_limited_noise(f1,f2,const.FS,t_arr)

        output = 10.*np.log10(np.abs(np.fft.fftshift(np.fft.fft(output))))

        yield output.astype(const.DTYPE)
        t_incr += t_int
    return

'''
Time is in seconds
'''
def write_to_h5(noise_pwr, time):

    with h5py.File('data.h5','w') as h5f:
        h5f.attrs['fs'] = const.FS
        h5f.attrs['NFFT'] = const.NBINS
        h5f.attrs['noise_var'] = noise_pwr
        h5f.attrs['duration'] = time

        n_integrations = np.ceil(time/t_int)

        start_times = datetime.datetime.now(tz=tz.tzstr('America/Vancouver')) - np.arange(n_integrations) * datetime.timedelta(seconds=1)

        start_timestamps=[int(t.timestamp()) for t in start_times[::-1]]



        h5f.create_dataset('spec', (n_integrations, const.NBINS), dtype=const.DTYPE)
        h5f.create_dataset('freqs', data=const.FULL_FREQS)
        h5f.create_dataset('times', data=start_timestamps)

        for i, output in enumerate(integrated_spec_gen(noise_pwr, time)):
            print(f"{i+1}/{n_integrations}")
            h5f['spec'][i]=output


if __name__ == "__main__":
    write_to_h5(1, 0.1)

