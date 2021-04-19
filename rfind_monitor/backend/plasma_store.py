import subprocess
import rfind_monitor.const as const

subprocess.run('plasma_store', '-m', const.PLASMA_SIZE_BYTES, '-s', const.PLASMA_SOCKET)