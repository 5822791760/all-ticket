from resources.menu import MenuManager
from resources.libs import resource

if __name__ == "__main__":
    resource.setrlimit(resource.RLIMIT_NOFILE, (8192, 8192))
    menu = MenuManager()
    accounts = menu.accounts
    print()
    print("Booked Seat:")
    if accounts:
        for acc in accounts:
            acc.show_seats()
