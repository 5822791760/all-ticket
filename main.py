from resources.menu import MenuManager

if __name__ == "__main__":
    menu = MenuManager()
    accounts = menu.accounts
    print()
    print("Booked Seat:")
    if accounts:
        for acc in accounts:
            acc.show_seats()
