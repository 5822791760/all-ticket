from resources.menu import MenuManager
from resources.libs import asyncio

if __name__ == "__main__":
    menu = MenuManager()
    if menu.concert_id:
        menu = asyncio.run(menu.select_book_options())

    perform = menu.perform
    if perform and perform.have_ticket:
        print()
        print("Booked Seat:")
        for i, seat in enumerate(perform.booked_seat):
            print(f"Set {i + 1}")
            print(", ".join(seat.ids))
            print()
