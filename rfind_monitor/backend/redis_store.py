import subprocess
import rfind_monitor.const as const


if __name__ == "__main__":
    shell_cmd = f"redis-server {const.REDIS_CONF}"
    print(shell_cmd)
    subprocess.call(shell_cmd, shell=True)
