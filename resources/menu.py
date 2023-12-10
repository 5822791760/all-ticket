from resources.perform import PerformManager
from resources.libs import os, requests, datetime, time, load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")


class MenuManager:
    perform: PerformManager

    def __init__(self):
        self.base_data = self.get_base_data()
        self.concert_id = self.select_concert()
        self.perform = None

    def get_base_data(self):
        base_data = {
            "url": "https://www.allticket.com/",
            "headers": {"authorization": TOKEN, "Content-Type": "application/json"},
        }

        req = base_data.copy()
        req["url"] = "https://api.allticket.com/customer/get-purchase-history"
        req["json"] = {"headers": {"normalizedNames": {}, "lazyUpdate": None}}

        code = requests.post(**req).status_code
        if code != 200:
            raise Exception("Wrong Token Please fix your env")

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
