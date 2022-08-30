# Mike Bangham | mike.bangham@controlf.co.uk | Control-F 2022
# Requires Python 3
__version__ = '0.06'

import json
from subprocess import Popen, PIPE
import urllib.request
import lzma
import sys
import time


def init_frida_server(upgrade):
    # Ensure the adbd daemon is running in admin mode
    Popen('adb root', stdout=PIPE)

    if upgrade == 'y':
        print('[*] Upgrading Frida')
        # remove old traces of frida
        Popen('adb shell rm -r /data/local/tmp/re.frida.server/', stdout=PIPE, stderr=PIPE)
        Popen('adb shell rm /data/local/tmp/frida.server', stdout=PIPE, stderr=PIPE)

        # Get the architecture of the processor chip. armeabi-v7a == arm
        p = Popen("adb shell getprop ro.product.cpu.abi", stdout=PIPE)
        arch = p.stdout.read().decode().strip()
        if arch == 'armeabi-v7a':
            arch = 'arm'

        print('\tDetected architecture: {}'.format(arch))

        # Fetch frida repository dictionary of latest frida binaries
        print('\tAnalysing Frida repo for latest version...')
        with urllib.request.urlopen('https://api.github.com/repos/frida/frida/releases') as f:
            html = json.loads(f.read().decode('utf-8'))

        # Analyse JSON and extract the download URL for the latest version of frida-server
        for dic in html[0]['assets']:
            if dic['name'].startswith('frida-server') and dic['name'].endswith('-android-{}.xz'.format(arch)):
                print('\tDownloading: {}...'.format(dic['browser_download_url']))
                urllib.request.urlretrieve(dic['browser_download_url'], "frida-server.xz")

        # unpack the compressed frida-server binary
        with lzma.open('frida-server.xz', mode='rb') as fid:
            with open('frida-server', 'wb') as fout:
                for line in fid:
                    fout.write(line)

        # push the new version of the frida-server to /data/local/tmp
        p = Popen('adb push frida-server /data/local/tmp/frida-server', stdout=PIPE)
        p.wait()

        # give frida-server permissions to execute
        p = Popen('adb shell "chmod 755 /data/local/tmp/frida-server"', stdout=PIPE)
        p.wait()

    else:
        print('[*] Re-initiating Frida...')

    # check if frida-server is already running on the android emulator
    p = Popen("adb shell ps -e | grep frida-server", stdout=PIPE)
    p.wait()
    frida_process = p.stdout.read().decode()
    if frida_process:
        # if it is, kill it. Otherwise it will hog the required IP
        pid = frida_process.split()
        print('\tFound an instance of frida-server running with process ID: {0}.\n'
              '\tKilling {0}...'.format(pid[1]))
        Popen("adb shell kill -9 {}".format(pid[1]), stdout=PIPE)
        time.sleep(2)

    # Execute frida-server as a background service
    print('\tExecuting frida-server as a background process...')
    p = Popen('adb shell ./data/local/tmp/frida-server &')
    time.sleep(4)
    print('\tDone!\n\n')
    sys.exit()


if __name__ == '__main__':
    print("\n\n"
          "                                                        ,%&&,\n"
          "                                                    *&&&&&&&&,\n"
          "                                                  /&&&&&&&&&&&&&\n"
          "                                               #&&&&&&&&&&&&&&&&&&\n"
          "                                           ,%&&&&&&&&&&&&&&&&&&&&&&&\n"
          "                                        ,%&&&&&&&&&&&&&&#  %&&&&&&&&&&,\n"
          "                                     *%&&&&&&&&&&&&&&%       %&&&&&&&&&%,\n"
          "                                   (%&&&&&&&&&&&&&&&&&&&#       %&%&&&&&&&%\n"
          "                               (&&&&&&&&&&&&&&&%&&&&&&&&&(       &&&&&&&&&&%\n"
          "              ,/#%&&&&&&&#(*#&&&&&&&&&&&&&&%,    #&&&&&&&&&(       &&&&&&&\n"
          "          (&&&&&&&&&&&&&&&&&&&&&&&&&&&&&#          %&&&&&&&&&(       %/\n"
          "       (&&&&&&&&&&&&&&&&&&&&&&&&&&&&&(               %&&&&&&&&&/\n"
          "     /&&&&&&&&&&&&&&&&&&%&&&&&&&%&/                    %&&&&&,\n"
          "    #&&&&&&&&&&#          (&&&%*                         #,\n"
          "   #&&&&&&&&&%\n"
          "   &&&&&&&&&&\n"
          "  ,&&&&&&&&&&                           Control-F\n"
          "   %&&&&&&&&&                           Android Frida-Server Install/Upgrade\n"
          "   (&&&&&&&&&&,             /*          mike.bangham@controlf.co.uk\n"             
          "    (&&&&&&&&&&&/        *%&&&&&#       2020-2022\n"
          "      &&&&&&&&&&&&&&&&&&&&&&&&&&&&&%    v{}\n"
          "        &&&&&&&&&&&&&&&&&&&&&&&&&%\n"
          "          *%&&&&&&&&&&&&&&&&&&#,\n"
          "                *(######/,".format(__version__))

    print("\n[*] Instructions:\nAppend 'y' to upload or upgrade frida-server. "
          "Append 'n' to re-initiate the frida-server.")
    print('[*] Example usage:\tpython install_frida_android.py y\n')
    try:
        if not sys.argv[1] in ['y', 'n']:
            raise IndexError
        init_frida_server(sys.argv[1])
    except IndexError:
        print("[!] Argument 1 (upgrade argument): not supplied or not recognised. Must be either 'y' or 'n'\n"
              "[!] Aborted\n")
        sys.exit()
