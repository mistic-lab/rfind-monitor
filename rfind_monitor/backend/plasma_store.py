import subprocess
import rfind_monitor.const as const


if __name__ == "__main__":
    shell_cmd = f"plasma_store -m {const.PLASMA_SIZE_BYTES} -s {const.PLASMA_SOCKET}"
    print(shell_cmd)
    subprocess.call(shell_cmd, shell=True)
