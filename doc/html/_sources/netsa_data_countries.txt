:mod:`netsa.data.countries` --- Country and Region Codes
========================================================

.. automodule:: netsa.data.countries

    .. autofunction:: get_area_numeric(code : int or str) -> int

    .. autofunction:: get_area_name(code : int or str) -> str

    .. autofunction:: get_area_tlds(code : int or str) -> str list

    .. autofunction:: get_country_numeric(code : int or str) -> int

    .. autofunction:: get_country_name(code : int or str) -> str

    .. autofunction:: get_country_alpha2(code : int or str) -> str

    .. autofunction:: get_country_alpha3(code : int or str) -> str
    
    .. autofunction:: get_country_tlds(code : int or str) -> str list

    .. autofunction:: iter_countries() -> int iter

    .. autofunction:: get_region_numeric(code : int or str) -> int

    .. autofunction:: get_region_name(code : int or str) -> str

    .. autofunction:: get_region_tlds(code : int or str) -> str list

    .. autofunction:: iter_regions() -> int iter

    .. autofunction:: iter_region_subregions(code : int or str) -> int iter

    .. autofunction:: iter_region_countries(code : int or str) -> int iter
