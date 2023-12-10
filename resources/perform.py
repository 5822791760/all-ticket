from resources.zone import ZoneManager
from resources.seat import SeatManager
from resources.libs import grequests, asyncio, requests


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
