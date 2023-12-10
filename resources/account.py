from resources.perform import PerformManager
from resources.libs import asyncio


class AccountManager:
    def __init__(self, token, email):
        self.token = token
        self.email = email
        self.seat = None
        self.payload = self.get_payload()
        self.perform = None
        self.ready = False
        self.have_ticket = False

    async def book_ticket(self, concert_id):
        perform = await PerformManager(concert_id, self.payload, self.seat).book_seats()

        self.perform = perform
        if perform.booked_seat:
            self.have_ticket = True

    def thread_book_ticket(self, concert_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.book_ticket(concert_id))
        loop.close()

    def get_payload(self):
        return {
            "url": "https://www.allticket.com/",
            "headers": {
                "authorization": self.token,
                "Content-Type": "application/json",
            },
        }

    def show_profile(self):
        print(f"Email: {self.email}")
        print(f"Seat: {self.seat}")
        print()

    def ready_set(self, seat):
        self.seat = seat

        if seat <= 0:
            self.ready = False
            return

        self.ready = True

    def show_seats(self):
        if not self.have_ticket:
            print(f"{self.email} Booking failed")
            return

        print()
        print(f"{self.email}:")
        for i, seat in enumerate(self.perform.booked_seat):
            print(f"Ticket {i + 1}")
            print(", ".join(seat.ids))
            print()
