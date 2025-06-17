import requests
import time
import random
import string
import threading
import keyboard
from colorama import Fore, Style, init

init()

paused = False
username_length = 5
pause_lock = threading.Event()
pause_lock.set()  # initially not paused, so event is set


def get_username_length():
    while True:
        try:
            length = int(input(Fore.CYAN + "How many characters should the username have? (1–20): " + Style.RESET_ALL))
            if 1 <= length <= 20:
                return length
            else:
                print(Fore.RED + "Please enter a number between 1 and 20." + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)


def ask_change_length():
    while True:
        choice = input(Fore.CYAN + "Do you want to change the username length? (y/n): " + Style.RESET_ALL).strip().lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print(Fore.RED + "Please enter 'y' or 'n'." + Style.RESET_ALL)


def toggle_pause_key():
    global paused, username_length
    while True:
        keyboard.wait("p")
        if paused:
            # unpausing
            print(Fore.CYAN + "\n[UNPAUSING]" + Style.RESET_ALL)
            # Ask if want to change length (blocking call)
            if ask_change_length():
                username_length = get_username_length()
            paused = False
            pause_lock.set()  # unblock main loop
            print(Fore.CYAN + "[RESUMED]" + Style.RESET_ALL)
        else:
            # pausing
            paused = True
            pause_lock.clear()  # block main loop
            print(Fore.CYAN + "\n[PAUSED] Press 'p' again to unpause." + Style.RESET_ALL)


def generate_username(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def check_username(username):
    url = f"https://auth.roblox.com/v1/usernames/validate?Username={username}&Birthday=2000-01-01"
    try:
        response = requests.get(url)
        response_data = response.json()

        code = response_data.get("code")
        if code == 0:
            print(Fore.GREEN + f"VALID: {username}" + Style.RESET_ALL)
        elif code == 1:
            print(Fore.LIGHTBLACK_EX + f"TAKEN: {username}" + Style.RESET_ALL)
        elif code == 2:
            print(Fore.RED + f"CENSORED: {username}" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"Unknown ({code}): {username}" + Style.RESET_ALL)

    except requests.exceptions.RequestException as e:
        print(Fore.YELLOW + f"Error {username}: {e}" + Style.RESET_ALL)


def main():
    global username_length

    username_length = get_username_length()
    print(Fore.CYAN + "Press 'P' anytime to pause or unpause." + Style.RESET_ALL)

    threading.Thread(target=toggle_pause_key, daemon=True).start()

    while True:
        pause_lock.wait()  # blocks if paused

        username = generate_username(username_length)
        check_username(username)
        time.sleep(0.05)


if __name__ == "__main__":
    main()