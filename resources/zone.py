from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from resources.perform import PerformManager


class ZoneManager:
    id: str
    zone_type: str
    seat_reqs = []
    seats: list

    def __init__(self, perform, zone_id) -> None:
        self.perform: PerformManager = perform
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
