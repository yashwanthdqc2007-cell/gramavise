from typing import Dict, Tuple, Optional
import re


CATEGORY_TAG_RULES = {
    # Food kiosks, snacks, breakfast, eateries
    "food_kiosk": {
        "direct_tags": [
            ("amenity", "fast_food"),
            ("amenity", "cafe"),
            ("shop", "bakery"),
            ("amenity", "food_court"),
            ("cuisine", "snacks"),
            ("cuisine", "indian_snacks")
        ],
        "adjacent_tags": [
            ("amenity", "restaurant"),
            ("shop", "convenience"),
            ("shop", "tea"),
            ("shop", "confectionery"),
            ("shop", "dairy")
        ]
    },
    # Bakery / Sweets
    "bakery": {
        "direct_tags": [
            ("shop", "bakery"),
            ("shop", "pastry"),
            ("shop", "confectionery")
        ],
        "adjacent_tags": [
            ("amenity", "cafe"),
            ("amenity", "fast_food"),
            ("shop", "dairy"),
            ("shop", "convenience")
        ]
    },
    # Grain & Flour Milling / Processing
    "flour_milling": {
        "direct_tags": [
            ("craft", "flour_mill"),
            ("industrial", "mill"),
            ("industrial", "food_processing")
        ],
        "adjacent_tags": [
            ("shop", "agrarian"),
            ("shop", "general"),
            ("shop", "spices")
        ]
    },
    # Spices / Agro-processing / Garlic / Onion Processing
    "agro_processing": {
        "direct_tags": [
            ("industrial", "food_processing"),
            ("shop", "spices"),
            ("craft", "food_processor"),
            ("shop", "agrarian")
        ],
        "adjacent_tags": [
            ("craft", "flour_mill"),
            ("shop", "general"),
            ("shop", "convenience")
        ]
    },
    # Tailoring / Garments
    "tailoring": {
        "direct_tags": [
            ("shop", "tailor"),
            ("craft", "dressmaker"),
            ("shop", "clothes"),
            ("shop", "boutique")
        ],
        "adjacent_tags": [
            ("shop", "fabric"),
            ("craft", "weaver"),
            ("shop", "shoes"),
            ("shop", "fashion_accessories")
        ]
    },
    # Handloom / Weaving
    "handloom": {
        "direct_tags": [
            ("craft", "weaver"),
            ("shop", "fabric"),
            ("shop", "handicraft")
        ],
        "adjacent_tags": [
            ("shop", "tailor"),
            ("shop", "clothes"),
            ("shop", "boutique")
        ]
    },
    # Grocery / Kirana / General Retail
    "grocery": {
        "direct_tags": [
            ("shop", "convenience"),
            ("shop", "general"),
            ("shop", "supermarket"),
            ("shop", "grocery")
        ],
        "adjacent_tags": [
            ("shop", "bakery"),
            ("shop", "dairy"),
            ("shop", "spices")
        ]
    },
    # Dairy / Milk chilling & sweets
    "dairy": {
        "direct_tags": [
            ("shop", "dairy"),
            ("amenity", "milk_center")
        ],
        "adjacent_tags": [
            ("shop", "bakery"),
            ("shop", "convenience"),
            ("amenity", "cafe")
        ]
    },
    # Footwear / Leather
    "footwear": {
        "direct_tags": [
            ("shop", "shoes"),
            ("craft", "shoemaker"),
            ("shop", "leather")
        ],
        "adjacent_tags": [
            ("shop", "clothes"),
            ("shop", "fashion_accessories")
        ]
    },
    # Carpentry / Furniture
    "carpentry": {
        "direct_tags": [
            ("craft", "carpenter"),
            ("shop", "furniture"),
            ("craft", "woodworker")
        ],
        "adjacent_tags": [
            ("shop", "hardware"),
            ("shop", "trade")
        ]
    }
}

# Synonyms for business category normalization
CATEGORY_KEY_MAPPINGS = {
    "flour": "flour_milling",
    "mill": "flour_milling",
    "milling": "flour_milling",
    "atta": "flour_milling",
    "chakki": "flour_milling",
    "grain": "flour_milling",
    "bakery": "bakery",
    "baker": "bakery",
    "cake": "bakery",
    "bread": "bakery",
    "pastry": "bakery",
    "snack": "food_kiosk",
    "snacks": "food_kiosk",
    "kiosk": "food_kiosk",
    "food": "food_kiosk",
    "fast food": "food_kiosk",
    "breakfast": "food_kiosk",
    "canteen": "food_kiosk",
    "eatery": "food_kiosk",
    "millet": "food_kiosk",
    "millet kiosk": "food_kiosk",
    "millet snacks": "food_kiosk",
    "spice": "agro_processing",
    "spices": "agro_processing",
    "garlic": "agro_processing",
    "chilli": "agro_processing",
    "tomato": "agro_processing",
    "processing": "agro_processing",
    "food processing": "agro_processing",
    "tailor": "tailoring",
    "tailoring": "tailoring",
    "clothes": "tailoring",
    "garment": "tailoring",
    "garments": "tailoring",
    "boutique": "tailoring",
    "weaver": "handloom",
    "weaving": "handloom",
    "handloom": "handloom",
    "fabric": "handloom",
    "saree": "handloom",
    "grocery": "grocery",
    "kirana": "grocery",
    "general store": "grocery",
    "dairy": "dairy",
    "milk": "dairy",
    "footwear": "footwear",
    "shoes": "footwear",
    "chappal": "footwear",
    "carpenter": "carpentry",
    "carpentry": "carpentry",
    "furniture": "carpentry",
}


def resolve_business_category_key(category: str) -> Optional[str]:
    """Map raw business category string to canonical category key."""
    if not category:
        return None
    cleaned = category.strip().lower()
    if cleaned in CATEGORY_KEY_MAPPINGS:
        return CATEGORY_KEY_MAPPINGS[cleaned]
    
    # Check token overlap
    tokens = re.findall(r"\w+", cleaned)
    for tok in tokens:
        if tok in CATEGORY_KEY_MAPPINGS:
            return CATEGORY_KEY_MAPPINGS[tok]
    
    return None


def match_competitor_category(
    business_category: str,
    tags: Dict[str, str]
) -> Tuple[str, Optional[str], Optional[str]]:
    """Determine relationship between enterprise category and an OSM POI's tags.
    
    Returns:
        Tuple of (relationship, match_reason, subcategory)
        relationship is one of: 'DIRECT', 'ADJACENT', 'UNRELATED'
    """
    cat_key = resolve_business_category_key(business_category)
    if not cat_key or not tags:
        # Fallback check for direct tag match on category name
        cleaned_cat = (business_category or "").strip().lower()
        for k, v in tags.items():
            if v.lower() == cleaned_cat:
                return "DIRECT", f"Matched because {k}={v} (DIRECT)", v
        return "UNRELATED", None, None

    rules = CATEGORY_TAG_RULES.get(cat_key, {})
    direct_tags = rules.get("direct_tags", [])
    adjacent_tags = rules.get("adjacent_tags", [])

    # 1. Check Direct Tags
    for tag_key, tag_val in direct_tags:
        if tags.get(tag_key, "").lower() == tag_val.lower():
            return "DIRECT", f"Matched because {tag_key}={tag_val} (DIRECT)", tag_val

    # 2. Check Adjacent Tags
    for tag_key, tag_val in adjacent_tags:
        if tags.get(tag_key, "").lower() == tag_val.lower():
            return "ADJACENT", f"Matched because {tag_key}={tag_val} (ADJACENT)", tag_val

    # 3. Unrelated
    return "UNRELATED", None, None
