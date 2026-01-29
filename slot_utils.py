from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def ensure_timezone(dt, tz):
	tzinfo = ZoneInfo(tz)
	if dt.tzinfo is None:
		return dt.replace(tzinfo=tzinfo)
	return dt.astimezone(tzinfo)


def parse_google_time(time_str):
	if time_str.endswith("Z"):
		time_str = time_str.replace("Z", "+00:00")
	return datetime.fromisoformat(time_str)


def generate_working_slots(
	start,
	end,
	duration_minutes=30,
	work_hours=(9, 18),
	tz="Asia/Kolkata",
):
	start = ensure_timezone(start, tz)
	end = ensure_timezone(end, tz)
	slots = []

	current_day = start.date()
	end_day = end.date()

	while current_day <= end_day:
		day_start = datetime.combine(
			current_day,
			datetime.min.time(),
			tzinfo=ZoneInfo(tz),
		).replace(hour=work_hours[0], minute=0)

		day_end = datetime.combine(
			current_day,
			datetime.min.time(),
			tzinfo=ZoneInfo(tz),
		).replace(hour=work_hours[1], minute=0)

		window_start = max(day_start, start)
		window_end = min(day_end, end)

		slot_start = window_start
		while slot_start + timedelta(minutes=duration_minutes) <= window_end:
			slot_end = slot_start + timedelta(minutes=duration_minutes)
			slots.append((slot_start, slot_end))
			slot_start = slot_end

		current_day = current_day + timedelta(days=1)

	return slots


def subtract_busy_slots(slots, busy, tz="Asia/Kolkata"):
	busy_ranges = []
	for item in busy:
		busy_start = ensure_timezone(parse_google_time(item["start"]), tz)
		busy_end = ensure_timezone(parse_google_time(item["end"]), tz)
		busy_ranges.append((busy_start, busy_end))

	available = []
	for slot_start, slot_end in slots:
		overlaps = False
		for busy_start, busy_end in busy_ranges:
			if slot_end > busy_start and slot_start < busy_end:
				overlaps = True
				break
		if not overlaps:
			available.append((slot_start, slot_end))
	return available


def format_slots(slots, tz="Asia/Kolkata"):
	if not slots:
		return "No available slots."
	tzinfo = ZoneInfo(tz)
	lines = []
	for start, end in slots:
		start = start.astimezone(tzinfo)
		end = end.astimezone(tzinfo)
		lines.append(f"{start:%Y-%m-%d %H:%M} - {end:%H:%M} {tz}")
	return "\n".join(lines)
