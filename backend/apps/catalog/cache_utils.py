import hashlib

CACHE_TTL_PRODUCT_DETAIL = 7200
CACHE_TTL_PRODUCTS_LIST = 300
CACHE_TTL_PRODUCTS_FEATURED = 3600
CACHE_TTL_PRODUCT_RELATED = 3600
CACHE_TTL_CATEGORIES = 7200
CACHE_TTL_BRANDS = 7200
CACHE_TTL_SEARCH = 120
CACHE_TTL_CMS_HOME = 3600


def products_list_cache_key(request) -> str:
    params = sorted(request.query_params.items())
    digest = hashlib.md5(str(params).encode()).hexdigest()
    return f'products_list:{digest}'
