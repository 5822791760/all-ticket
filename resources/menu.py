from resources.account import AccountManager
from resources.libs import (
    os,
    requests,
    datetime,
    time,
    load_dotenv,
    grequests,
    json,
    threading,
    sys,
)

load_dotenv()

TOKEN = os.getenv("TOKEN")
TOKENS = json.loads(os.getenv("TOKENS"))


class MenuManager:
    def __init__(self):
        self.concert_id = None
        self.concert_name = None
        self.accounts = self.populate_account()
        self.select_concert()

    def populate_account(self):
        greqs = []
        payload = {
            "url": "https://www.allticket.com/",
            "headers": {"authorization": TOKEN, "Content-Type": "application/json"},
        }

        for token in TOKENS:
            payload = {
                "url": "https://api.allticket.com/customer/get-purchase-history",
                "headers": {"authorization": token, "Content-Type": "application/json"},
                "json": {"headers": {"normalizedNames": {}, "lazyUpdate": None}},
            }

            greqs.append(grequests.post(**payload))

        accounts = []
        for i, res in grequests.imap_enumerated(greqs):
            token = TOKENS[i]

            if res.status_code != 200:
                input(f"Token at index {i} is incorrent fix it")
                continue

            data = res.json()["data"]
            accounts.append(AccountManager(token, data["email"]))

        return accounts

    def filter_page(self, items):
        user_i = self.get_user_input("Type in name (eng): ").lower()
        print()
        items = list(filter(lambda x: user_i in x["name"].lower(), items))
        return self.select_concert(items)

    def select_concert(self, items=None) -> str:
        if items is None:
            req = {
                "url": "https://api.allticket.com/content/get-all-events",
                "headers": {
                    "authorization": "",
                    "Content-Type": "application/json",
                },
                "json": {"groupKey": "concert"},
            }

            res = requests.post(**req).json()
            items = res["data"]["event"]["items"]

        user_i = ""
        while not user_i.isnumeric():
            print("==================================")
            for i, item in enumerate(items):
                print(f"ID: {i}")
                print(f"Name: {item['name']}")
                print(f"ชื่อ: {item['namePos']}")
                print()

            print("==================================")
            print("[f] To filter")
            print("[r] To reset")
            print("[b] to book")
            user_i = self.get_user_input("Select ID: ")
            user_i = user_i.lower()
            print()

            if user_i == "f":
                return self.filter_page(items)

            if user_i == "r":
                return self.select_concert()

            if user_i == "b":
                return self.select_book_options()

        self.concert_id = items[int(user_i)]["id"]
        self.concert_name = items[int(user_i)]["name"]

        return self.select_seat_needed()

    def select_seat_needed(self):
        account_length = len(self.accounts)

        for _ in range(account_length):
            print()

            print("Select User:")
            print()
            self.show_account_info()

            user_index = -1
            while not (0 <= user_index <= account_length):
                user_index = self.get_user_input("User ID: ", convert_int=True)
                print()

            seat_need = self.get_user_input("Select seats amount: ", True, True)
            print()

            self.accounts[user_index].ready_set(seat_need)

        return self.select_concert()

    def get_user_input(
        self,
        message="Select Concert By ID: ",
        convert_int=False,
        hide_exit=False,
    ):
        if not hide_exit:
            print("[e] To exit")

        user_i = input(message).strip()

        if not hide_exit and user_i == "e":
            print("EXITED")
            sys.exit()

        if convert_int:
            if not user_i.isnumeric():
                return self.get_user_input(message, convert_int)

            user_i = int(user_i)

        return user_i

    def show_account_info(self, ready_only=False):
        checks = []

        print("==================================")
        for i, acc in enumerate(self.accounts):
            if ready_only and not acc.ready:
                checks.append(False)
                continue

            checks.append(True)
            print(f"ID: {i}")
            acc.show_profile()

        print("==================================")
        return any(checks)

    def book_all_accounts(self):
        threads = []
        start = time.time()

        for acc in self.accounts:
            if not acc.ready:
                continue

            thread = threading.Thread(
                target=acc.thread_book_ticket, args=(self.concert_id,)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if not threads:
            print("NOONE IS READY")

        print()
        print("==================================")
        print(f"TIME TOOK: {round(time.time() - start, 2)}")
        print("==================================")

    def book_now(self):
        print()
        print("Booking Start!")
        print()

        self.book_all_accounts()
        return self

    def book_later(self):
        target_time = self.get_user_input(
            "Please Input Time in this format %H:%M:%S: "
        ).split(":")
        for i in range(3 - len(target_time)):
            target_time.append("00")

        target_hour, target_minute, target_second = map(int, target_time)

        now = datetime.datetime.now()
        target_datetime = datetime.datetime(
            now.year, now.month, now.day, target_hour, target_minute, target_second
        )

        if now > target_datetime:
            target_datetime += datetime.timedelta(days=1)

        count_down_sec = 5
        notify_time = target_datetime - datetime.timedelta(seconds=count_down_sec)

        time_difference = notify_time - now
        total_seconds = time_difference.total_seconds()

        print()
        print(f"Booking Start At: {':'.join(target_time)}")
        print(f"In {total_seconds + count_down_sec} Seconds")
        print()
        time.sleep(total_seconds)

        for i in range(count_down_sec, 0, -1):
            print(f"Countdown: {i} seconds")
            time.sleep(1)

        print()
        print("Booking Start!")
        print()

        self.book_all_accounts()

        return self

    def select_book_options(self):
        dic = {"n": self.book_now, "s": self.book_later}

        ready = self.show_account_info(ready_only=True)
        if not ready:
            input("No one select seat yet")
            return self.select_concert()

        print("[n] Book Now")
        print("[s] Schedule Book")
        print("[b] Back")

        user_i = self.get_user_input(message="Select Action: ")
        if user_i.lower() == "b":
            return self.select_concert()

        while user_i not in dic:
            input("Wrong Action")
            user_i = self.get_user_input(message="Select Action: ")

        return dic[user_i]()
