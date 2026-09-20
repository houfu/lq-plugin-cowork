"""The static site: one page per bundle and per skill, plus the guides.

``lqcowork site`` renders ``<out>/site/`` from the build in ``<out>/``. See
docs/CONTRACT.md section 9 for what it reads, what it writes and the rules
the pages keep.
"""

from __future__ import annotations

from .generate import SiteError, SiteResult, build_site, site_root

__all__ = ["SiteError", "SiteResult", "build_site", "site_root"]
