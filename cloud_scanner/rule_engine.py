import json
from decorator import autolog
from database_ops import fetch_entry_by_id

"""

Plan
run the 3 check scripts, save json to variable

reprocess json obj, separating 3s and 2s, outputting len() as "Risk Score"

Create simple REST API to allow zeroing in on what data class one would want.

"""
