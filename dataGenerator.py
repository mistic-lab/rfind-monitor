from os import write
import numpy as np
import h5py

fs = 125e6
fcs = [25e6, 85e6]
phase_incrs = [0]*len(fcs)

NFFT = 1024
t_int = NFFT/fs

t_arr = np.linspace(0, t_int, NFFT)

freqs = np.fft.fftshift(np.fft.fftfreq(NFFT, 1/fs))

def integrated_spec_gen(noise_pwr, time):
    t_incr = 0
    while t_incr <= time:
        output = np.random.normal(0,np.sqrt(noise_pwr), NFFT) + 1j*np.random.normal(0,np.sqrt(noise_pwr), NFFT)
        for i, fc in enumerate(fcs):
            output += np.exp(2j*np.pi*fc*t_arr+phase_incrs[i])
            phase_incrs[i] = (phase_incrs[i] +  t_int*(2*np.pi)*fc) % (2*np.pi) #TODO check this I'm not thinking straight rn
        output = 10.*np.log10(np.abs(np.fft.fft(output)))

        yield (output, t_incr)
        t_incr += t_int
    return

'''
Time is in seconds
'''
def write_to_h5(noise_pwr, time):

    with h5py.File('data.h5','w') as h5f:
        h5f.attrs['fs'] = fs
        h5f.attrs['NFFT'] = NFFT
        h5f.attrs['noise_var'] = noise_pwr
        h5f.attrs['duration'] = time

        n_integrations = np.ceil(time/t_int)

        h5f.create_dataset('spec', (n_integrations,NFFT))
        h5f.create_dataset('freqs',data=freqs)
        h5f.create_dataset('times', (n_integrations,))

        for i, (output, t) in enumerate(integrated_spec_gen(noise_pwr, time)):
            h5f['spec'][i]=output
            h5f['times'][i]=t



write_to_h5(0.5, 0.05)

