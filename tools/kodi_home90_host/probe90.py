"""Allow the complete inherited gates plus the full 900-second Home soak.

The .87 supervisor's 30 minutes expire at the final .90 sample after
100 navigation cycles, 305-second sticky-art checks and the 15-minute soak.
Only this synthetic test supervisor receives 45 minutes. No Kodi/add-on
timeout or assertion changes; error receipts are still checked every tick.
"""
from pathlib import Path

base = Path('/base_probe87.py').read_text(encoding='utf-8')
assert base.count('range(18000)') == 1
base = base.replace('range(18000)', 'range(27000)')
exec(compile(base, '/base_probe87.py', 'exec'), globals())
