"""Provider pseudo-header classification, independent of EPG availability."""
import re
def header(row):
 if row.get('is_header') is True or row.get('type') in ('header','group'):return True
 name=str(row.get('name') or row.get('label') or '').strip()
 return bool(re.fullmatch(r'[#*=|_-]{3,}.*[#*=|_-]{3,}',name))
