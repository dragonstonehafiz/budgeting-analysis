"""Category color mapping and helper functions.

Central place to store category => color mappings. Other modules should
import `get_category_color` from here.
"""
from __future__ import annotations

from typing import Dict

category_colors: Dict[str, str] = {
    'Food & Beverages': '#D9D9D9',
    'Books & Literature': '#e9a9ff',
    'Gaming': '#bbe33d',
    'Digital Subscriptions': '#fbffa9',
    'Movies & Media': '#a05eff',
    'Music & Audio': '#ffa9f2',
    'Electronics & Accessories': '#729fcf',
    'Clothing & Apparel': '#D9D9D9',
    'Health & Personal Care': '#a9ffc4',
    'Collectibles': '#ffc85d',
    'Miscellaneous': '#D9D9D9'
}


def get_category_color(category: str) -> str:
    """Return a hex color string for the provided category.

    If the category is not present in the map, return the 'Miscellaneous'
    color. The function is defensive about None or unexpected inputs.
    """
    try:
        if category is None:
            return category_colors['Miscellaneous']
        key = str(category).strip()
        return category_colors.get(key, category_colors['Miscellaneous'])
    except Exception:
        return category_colors['Miscellaneous']
