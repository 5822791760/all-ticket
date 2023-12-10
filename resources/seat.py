from typing import TYPE_CHECKING
from resources.libs import aiohttp, asyncio, requests

if TYPE_CHECKING:
    from resources.zone import ZoneManager


class SeatManager:
    screen_label: str
    ids: list
    booking_id = None
    booking_wait_time = 5
    booking_time_out = 20
    booking_retry = 9
    reserve_id = None
    booked = False

    def __init__(self, zone, screen_label, seat_ids, seat_count) -> None:
        self.zone: ZoneManager = zone
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
