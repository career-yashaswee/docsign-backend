from math import ceil
from flask import request


def get_pagination_params(default_page=1, default_page_size=20, max_page_size=100):
    try:
        page = int(request.args.get("page", default_page))
    except ValueError:
        page = default_page
    try:
        page_size = int(request.args.get("limit", default_page_size))
    except ValueError:
        page_size = default_page_size

    page = max(1, page)
    page_size = min(max(1, page_size), max_page_size)
    offset = (page - 1) * page_size
    return page, page_size, offset


def build_paginated_response(items, total, page, page_size):
    total_pages = ceil(total / page_size) if page_size else 1
    return {
        "data": items,
        "meta": {
            "page": page,
            "limit": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    }
