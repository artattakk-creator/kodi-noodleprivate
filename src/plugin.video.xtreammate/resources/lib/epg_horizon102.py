"""Programme start counts and per-channel calendar-day continuity."""
from bisect import bisect_right
from datetime import date, timedelta
import hashlib
import time

DAYS = 21
MAX_CHANNELS = 100000


class Coverage:
    def __init__(self, now=None):
        from guide_store import day_window

        now = time.time() if now is None else now
        today = date.fromtimestamp(now)
        self.dates = [(today + timedelta(days=i)).isoformat() for i in range(DAYS)]
        self.boundaries = [day_window(i, now)[0] for i in range(DAYS + 1)]
        self.counts = [0] * DAYS
        self.channels = [0] * DAYS
        self.masks = {}
        self.channel_limit = False
        self.first = self.last = None

    def add(self, cid, start, stop):
        if self.first is None or start < self.first:
            self.first = start
        if self.last is None or stop > self.last:
            self.last = stop
        day = bisect_right(self.boundaries, start) - 1
        if 0 <= day < DAYS:
            self.count(cid, day, 1)

    def count(self, cid, day, programmes):
        self.counts[day] += programmes
        if self.channel_limit:
            return
        if len(cid) > 256:
            cid = hashlib.sha256(cid.encode('utf-8')).digest()
        mask = self.masks.get(cid, 0)
        bit = 1 << day
        if not mask and len(self.masks) >= MAX_CHANNELS:
            self.channel_limit = True
            return
        if not mask & bit:
            self.channels[day] += 1
            self.masks[cid] = mask | bit

    def result(self):
        # The lowest unset bit gives the first uncovered local date for a sender.
        # Taking the maximum afterwards prevents stitching together other senders.
        continuous = max(((~mask & (mask + 1)).bit_length() - 1
                          for mask in self.masks.values()), default=0)
        return dict(first=self.first, last=self.last,
                    last_contiguous_day=self.dates[continuous - 1] if continuous and not self.channel_limit else None,
                    channel_limit=self.channel_limit,
                    days=[dict(date=day, channels=None if self.channel_limit else channels, programmes=programmes)
                          for day, channels, programmes in zip(self.dates, self.channels, self.counts)])


def stored(db, now, pid, source=None, first=None, last=None):
    coverage = Coverage(now)
    coverage.first, coverage.last = first, last
    indices = {day: i for i, day in enumerate(coverage.dates)}
    if source is None:
        table, predicate, params = 'programmes', 'pid=?', (pid,)
    else:
        table, predicate, params = 'guide44_inputs', 'pid=? AND source_id=?', (pid, source)
    sql = (f'SELECT cid, date(start,\'unixepoch\',\'localtime\') AS day, count(*) '
           f'FROM {table} WHERE {predicate} AND start>=? AND start<? GROUP BY cid,day')
    for cid, day, count in db.execute(sql, params + (coverage.boundaries[0], coverage.boundaries[-1])):
        coverage.count(cid, indices[day], count)
    return coverage.result()
