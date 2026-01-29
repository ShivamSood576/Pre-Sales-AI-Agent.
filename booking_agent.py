import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from calendar_service import (
	DEFAULT_CALENDAR_ID,
	DEFAULT_TIME_ZONE,
	book_event,
	get_free_busy,
)
from slot_utils import (
	ensure_timezone,
	format_slots,
	generate_working_slots,
	subtract_busy_slots,
)


class BookingAgent:
	def __init__(
		self,
		calendar_id=DEFAULT_CALENDAR_ID,
		time_zone=DEFAULT_TIME_ZONE,
		work_hours=(9, 18),
		slot_minutes=30,
	):
		self.calendar_id = calendar_id
		self.time_zone = time_zone
		self.work_hours = work_hours
		self.slot_minutes = slot_minutes

	def get_available_slots(
		self,
		days_ahead=1,
		start_date=None,
		duration_minutes=None,
	):
		duration = duration_minutes or self.slot_minutes
		tz = ZoneInfo(self.time_zone)
		now = datetime.now(tz)

		if start_date:
			start = datetime.combine(start_date, datetime.min.time(), tzinfo=tz)
		else:
			start = now

		end = start + timedelta(days=days_ahead)
		busy = get_free_busy(start, end, calendar_id=self.calendar_id)
		slots = generate_working_slots(
			start,
			end,
			duration_minutes=duration,
			work_hours=self.work_hours,
			tz=self.time_zone,
		)
		available = subtract_busy_slots(slots, busy, tz=self.time_zone)
		return available

	def book_slot(self, start_time, duration_minutes, user_email, summary=None):
		start_time = ensure_timezone(start_time, self.time_zone)
		end_time = start_time + timedelta(minutes=duration_minutes)
		return book_event(
			start_time,
			end_time,
			user_email,
			summary=summary or "Consultation",
			calendar_id=self.calendar_id,
			time_zone=self.time_zone,
		)


def parse_date(date_str):
	return datetime.strptime(date_str, "%Y-%m-%d").date()


def parse_time(time_str):
	return datetime.strptime(time_str, "%H:%M").time()


def parse_datetime(date_str, time_str, tz_name):
	tz = ZoneInfo(tz_name)
	return datetime.combine(parse_date(date_str), parse_time(time_str), tzinfo=tz)


def main():
	parser = argparse.ArgumentParser(description="Calendar booking agent")
	subparsers = parser.add_subparsers(dest="command", required=True)

	availability = subparsers.add_parser("availability", help="List free slots")
	availability.add_argument("--days", type=int, default=1)
	availability.add_argument("--date", type=str)
	availability.add_argument("--duration", type=int, default=30)

	book = subparsers.add_parser("book", help="Book a slot")
	book.add_argument("--date", required=True)
	book.add_argument("--time", required=True)
	book.add_argument("--duration", type=int, default=30)
	book.add_argument("--email", required=True)
	book.add_argument("--summary", default="Consultation")

	args = parser.parse_args()

	agent = BookingAgent()

	if args.command == "availability":
		start_date = parse_date(args.date) if args.date else None
		slots = agent.get_available_slots(
			days_ahead=args.days,
			start_date=start_date,
			duration_minutes=args.duration,
		)
		print(format_slots(slots, tz=agent.time_zone))

	if args.command == "book":
		start_time = parse_datetime(args.date, args.time, agent.time_zone)
		result = agent.book_slot(
			start_time,
			duration_minutes=args.duration,
			user_email=args.email,
			summary=args.summary,
		)
		print("Event created:")
		print(f"Event link: {result.get('event_link')}")
		print(f"Meet link: {result.get('meet_link')}")


if __name__ == "__main__":
	main()
