import datetime
import time
import grequests
import aiohttp
import asyncio
import requests

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IndlZ2V3b24yOTJAZ2V0bW9sYS5jb20iLCJ1cmxiYWNrIjoid3d3LmFsbHRpY2tldC5jb20iLCJwYXltZW50Q2hhbm5lbCI6IkMwNyIsInRpY2tldFR5cGUiOiIwMSIsImxhbmciOiJFIiwiZGF0YSI6Ijc5MzA2YWI1MjUzM2RmNzEzYTExMzU1NzdmODg4ZjY1YjA1NDBmOTIzMTU1NWI5N2MyMGYwMzU3YWZkODg3NTdiNTQ5NjliYzRmY2JiM2VhZTk0NzA5YTljNDAxYTk2M2I1M2Q2ZGM4ZmExZGI3NzA4ZjM0ZjhiYjI0YzZjZjYyOTNlMGQyYzdiNjU0YzZjNTc4ODk5NTgxOGFiOWYyZDY3MjgzNDU3ZmJhNjgxNTlhY2VhZjI5ZGNlYTJhNDc1MzBmMzdlMDJjMjVjMTQ0ZTQwNTgzMGMyZGFmNTVhNDc4ZjZhN2Q3NTQyMDgzYzljOTQzNWM3MTEzNjk3OWVhZmRhMzI2NjAzNTVkNjE4ZDQ4NjNhZGE5YjE2MmIwMzgxYTRlNDlmYTA0ODQ0ZGFmNDA3MWI4OTAyYTdiNjc4MWNlZWQ5OWEzNDEyOTIwZTI3Mjc2N2RlMTkwMzhlOGQ1ZTE0YTNkODI2Y2NjZTlhNmE4ZDdlZDdiNzhmZDc3ZDllZjE2NDc4MmIxODdiZWZhMTIxNGZjMmEwNmJkMDRmNzg1NGU3MDA5Mzc5ZmY3NzRlMWNkNDk0ZDIxYjhkMWZhNTEyMmFlMjRjMzZkYjU4YTlmM2QwMDFkYzY2YWNlNmVjNTQyYjQ3OGQ5NWFlZDRlY2Q1ZTQ4YjQ1MDkyMTZhNjQ1NTU5MGJmMWVlY2JlMWQ5NDU3YzIwNmY3YzE4MjM1MmM5ZDAwOTAzYmFiZjVkYzczNWVhNzI5Y2M1Zjg4NmJjODk3Y2Y5MzM5ZTBlNzEwNTJjNzQxNGRhNmM0NzdmZjJhMWZmMjE2NGQ2YzhhMjJlZTA0YzZmOWY4ZmU0ODZhOTAyYTkzZjExODIzZDcwOWY2M2M2MzQ5MWMxZjQ5MTU4YTdkNDQ5ZTI0MDFkOTlkODJkYjFmMDE1NWZhNTc0MDNiMThhY2U4ZWNlNzQzOWMxN2E2MGZhMGI2NzU1NzUwZmUiLCJ0aW1lU3RhbXAiOjAuMzE5ODg1NzQ5NDY5OTI5NjUsImlhdCI6MTcwMjIwMTI2OSwiZXhwIjoxNzAyMjEyMDY5LCJpc3MiOiJjc2F0azE4In0.N69YcEf36kMx5VJWJDz8h3P7HkTL945RoSIabKM57gQ"


class MenuManager:
    def __init__(self):
        self.base_data = self.get_base_data()
        self.concert_id = self.select_concert()
        self.perform = None

    def get_base_data(self):
        base_data = {
            "url": "https://www.allticket.com/",
            "headers": {"authorization": TOKEN, "Content-Type": "application/json"},
        }

        # req = base_data.copy()
        # req['url'] = 'https://api.allticket.com/customer/get-purchase-history'
        # req['json'] = { 'headers': { 'normalizedNames': {}, 'lazyUpdate': None } }

        # code = requests.post(**req).status_code
        # if code != 200:
        #     print("Wrong Token try again")
        #     return self.get_base_data()

        return base_data

    def filter_page(self, items):
        user_i = self.get_user_input("Type in name (eng): ").lower()
        print()
        items = list(filter(lambda x: user_i in x["name"].lower(), items))
        return self.select_concert(items)

    def select_concert(self, items=None) -> str:
        if items is None:
            req = self.base_data.copy()
            req["url"] = "https://api.allticket.com/content/get-all-events"
            req["json"] = {"groupKey": "concert"}
            res = requests.post(**req).json()
            items = res["data"]["event"]["items"]

        user_i = ""
        while not user_i.isnumeric():
            for i, item in enumerate(items):
                print(f"ID: {i}")
                print(f"Name: {item['name']}")
                print(f"ชื่อ: {item['namePos']}")
                print()

            print("[f] To filter")
            print("[r] To reset")
            user_i = self.get_user_input("Select ID: ")
            if user_i is None:
                return None

            user_i = user_i.lower()

            if user_i == "f":
                return self.filter_page(items)

            if user_i == "r":
                return self.select_concert()

        return items[int(user_i)]["id"]

    def select_seat_needed(self):
        # sets = []
        # print("If Done Type d or enter")
        print()
        seat_need = self.get_user_input("Select seats per set: ", convert_int=True)
        return seat_need

    def get_user_input(self, message="Select Concert By ID: ", convert_int=False):
        print("[e] To exit")
        user_i = input(message).strip()

        if user_i == "e":
            return None

        if convert_int:
            if not user_i.isnumeric():
                return self.get_user_input(message, convert_int)

            user_i = int(user_i)

        return user_i

    async def book_now(self, seat):
        self.perform = await PerformManager(
            self.concert_id, self.base_data, seat
        ).book_seats()
        return self

    async def book_later(self, seat):
        now = datetime.datetime.now()

        target_time = self.get_user_input("Please Input Time in this format %H:%M: ")

        target_hour, target_minute = map(int, target_time.split(":"))
        target_datetime = datetime.datetime(
            now.year, now.month, now.day, target_hour, target_minute
        )

        if now > target_datetime:
            target_datetime += datetime.timedelta(days=1)

        count_down_sec = 10
        notify_time = target_datetime - datetime.timedelta(seconds=count_down_sec)

        if now > notify_time:
            notify_time += datetime.timedelta(days=1)

        time_difference = notify_time - now
        total_seconds = time_difference.total_seconds()

        print()
        print(f"Booking Start At: {target_time}")
        print(f"In {total_seconds + count_down_sec} Seconds")
        print()
        time.sleep(total_seconds)

        for i in range(count_down_sec, 0, -1):
            print(f"Countdown: {i} seconds")
            time.sleep(1)

        print()
        print("Booking Start!")
        print()

        self.perform = await PerformManager(
            self.concert_id, self.base_data, seat
        ).book_seats()
        return self

    async def select_book_options(self):
        li = [
            self.book_now,
            self.book_later,
        ]

        print()
        print("[0] Book Now")
        print("[1] Schedule Book")

        user_i = self.get_user_input(message="Select Number: ", convert_int=True)
        if user_i is None:
            return self

        seat_need = self.select_seat_needed()

        return await li[user_i](seat_need)


class PerformManager:
    id: int
    round_id: int
    token: str
    event: str
    seat_needed: int
    zones: list
    booked_seat: list

    def __init__(self, id, base_data, seat_needed) -> None:
        self.id = id
        self.base_data = base_data
        self.seat_needed = seat_needed
        self.max_reserve_each = None
        self.max_reserve_all = None
        self.round_id = None
        self.have_ticket = False
        self.zone_greqs = []
        self.seat_greqs = []
        self.booked_seat = []
        self.zones = self.get_zones()
        self.seats = self.get_seats()

    def done(self):
        return self.seat_needed <= 0

    def get_base_data(self):
        return self.base_data.copy()

    def get_id(self):
        req = self.get_base_data()
        req["url"] = "https://api.allticket.com/content/get-all-events"
        req["json"] = {"groupKey": "concert"}
        res = requests.post(**req).json()
        items = res["data"]["event"]["items"]
        found_con = next(filter(lambda x: x["performUri"] == self.event, items), None)
        if not found_con:
            raise Exception("NOT FOUND CONCERT THIS NAME")

        self.id = found_con["id"]

    def get_round_id(self):
        if not self.id:
            self.get_id()

        req = self.get_base_data()
        req["url"] = "https://api.allticket.com/booking/get-round"
        req["json"] = {"performId": self.id}
        res = requests.post(**req).json()
        data = res["data"]["event_info"]
        self.max_reserve_each = data["maxReserve"]
        self.max_reserve_all = data["maxSelectSeatPerUser"]
        self.round_id = data["list_round"][0]["roundId"]

    def get_zones(self):
        if not self.round_id:
            self.get_round_id()

        req = self.get_base_data()
        req["url"] = "https://api.allticket.com/booking/seat-available"
        req["json"] = {"performId": self.id, "roundId": self.round_id}
        res = requests.post(**req).json()

        zones = []
        for zone in res["data"]["seat_available"]:
            if zone["amount"] <= self.seat_needed:
                continue

            zone_manager = ZoneManager(self, zone["id"])
            zones.append(zone_manager)
            self.zone_greqs.append(grequests.post(**zone_manager.req))

        return zones

    def get_seats(self):
        seat_needed = self.seat_needed

        if seat_needed > self.max_reserve_each:
            seat_needed = 1

        for i, res in grequests.imap_enumerated(self.zone_greqs):
            zone = self.zones[i]
            data = res.json()["data"]

            if not data:
                continue

            zone.zone_type = data["zone_type"]
            seats = []

            for seat_data in data["seats_available"]:
                screen_label = seat_data["screenLabel"]

                seat_ids = []
                count = 0
                for seat in seat_data["seat"]:
                    status = seat["status"]

                    if status != "A":
                        continue

                    seat_ids.append(f"{seat['rowName']}_{seat['seatNo']}")

                    count += 1

                    if count >= seat_needed:
                        seat_manager = SeatManager(zone, screen_label, seat_ids, count)
                        seats.append(seat_manager)
                        self.seat_greqs.append(grequests.post(**seat_manager.req))

                        count = 0
                        seat_ids = []

            return seats

    async def book_seats(self):
        payment_reqs = []

        for i, res in grequests.imap_enumerated(self.seat_greqs):
            seat = self.seats[i]
            response = res.json()
            data = response["data"]
            success = response["success"] == True

            # if not success:
            #     continue

            seat.booking_id = data["uuid"]
            seat.booking_wait_time = data["waitTime"]
            seat.booking_time_out = data["timeOut"]
            seat.booking_retry = data["retry"]

            payment_reqs.append(seat.get_payment_req())

        payment_reqs = await asyncio.gather(*payment_reqs)

        for seat in payment_reqs:
            if not seat:
                continue

            req = self.get_base_data()
            req["url"] = "https://api.allticket.com/payment/payment/outlet"
            req["json"] = {
                "payment_channel": "outlet",
                "performId": self.id,
                "reserveId": seat.reserve_id,
                "insureProducts": [],
            }

            # if self.done():
            #     break

            res = requests.post(**req).json()

            if res["success"] == True:
                self.seat_needed -= seat.seat_count
                self.booked_seat.append(seat)

        self.have_ticket = True
        return self


class ZoneManager:
    id: str
    zone_type: str
    perform: PerformManager
    seat_reqs = []
    seats: list

    def __init__(self, perform, zone_id) -> None:
        self.perform = perform
        self.id = zone_id
        self.req = self.get_req()

    def done(self):
        self.perform.seat_needed <= 0

    def get_base_data(self):
        return self.perform.base_data.copy()

    def get_req(self):
        if self.done():
            return []

        req = self.get_base_data()
        perform = self.perform

        req["url"] = "https://api.allticket.com/booking/get-seat"
        req["json"] = {
            "performId": perform.id,
            "roundId": perform.round_id,
            "zoneId": self.id,
        }

        return req


class SeatManager:
    screen_label: str
    ids: list
    zone: ZoneManager
    booking_id = None
    booking_wait_time = 5
    booking_time_out = 20
    booking_retry = 9
    reserve_id = None
    booked = False

    def __init__(self, zone, screen_label, seat_ids, seat_count) -> None:
        self.zone = zone
        self.screen_label = screen_label
        self.ids = seat_ids
        self.seat_count = seat_count
        self.req = self.get_req()

    def done(self):
        return self.zone.perform.seat_needed <= 0

    def get_base_data(self):
        return self.zone.perform.base_data.copy()

    def get_req(self):
        zone = self.zone
        perform = zone.perform

        req = self.get_base_data()
        req["url"] = "https://api.allticket.com/booking/handler-reserve"
        req["json"] = {
            "performId": perform.id,
            "roundId": perform.round_id,
            "zoneId": zone.id,
            "screenLabel": self.screen_label,
            "seatTo": {"seatType": zone.zone_type, "seats": self.ids},
            "shirtTo": [],
        }

        return req

    def book(self):
        res = requests.post(**self.req).json()
        data = res["data"]
        self.booking_id = data["uuid"]
        self.booking_wait_time = data["waitTime"]
        self.booking_time_out = data["timeOut"]
        self.booking_retry = data["retry"]

    async def get_payment_req(self):
        req = self.get_base_data()
        req["url"] = "https://api.allticket.com/booking/check-booking"
        req["json"] = {"uuid": self.booking_id}

        await asyncio.sleep(self.booking_wait_time)

        # if self.done():
        #     return None

        async with aiohttp.ClientSession() as session:
            async with session.post(**req) as response:
                res = await response.json()
                success = res["success"] == True

                if success:
                    data = res["data"]
                    self.reserve_id = data["reserveId"]
                    return self

                return None


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
