"""ECMWF parameter database entries that have a netCDF encoding.

Scraped from https://codes.ecmwf.int/grib/param-db?encoding=netcdf&ordering=id
(via the parameter-database REST API) on 2026-09-09.

These are the parameters DestinE data can be requested with: the ``param`` keys
used in polytope requests are these numeric ids, while the variables in the
Cache B zarr stores carry the matching ``shortname``. The dictionary is the
lookup table for coupling those ids to the CMOR variable names used by
ESMValTool/eWaterCycle (see :data:`ewatercycle_destine.forcing.RENAME_DESTINE`).
"""

# paramId -> parameter metadata, ordered by id, as published by ECMWF.
ECMWF_NETCDF_PARAMS: dict[int, dict[str, str]] = {
    31: {
        "shortname": "ci",
        "name": "Sea ice area fraction",
        "units": "(0 - 1)",
    },
    129: {
        "shortname": "z",
        "name": "Geopotential",
        "units": "m**2 s**-2",
    },
    130: {
        "shortname": "t",
        "name": "Temperature",
        "units": "K",
    },
    131: {
        "shortname": "u",
        "name": "U component of wind",
        "units": "m s**-1",
    },
    132: {
        "shortname": "v",
        "name": "V component of wind",
        "units": "m s**-1",
    },
    133: {
        "shortname": "q",
        "name": "Specific humidity",
        "units": "kg kg**-1",
    },
    134: {
        "shortname": "sp",
        "name": "Surface pressure",
        "units": "Pa",
    },
    135: {
        "shortname": "w",
        "name": "Vertical velocity",
        "units": "Pa s**-1",
    },
    137: {
        "shortname": "tcwv",
        "name": "Total column vertically-integrated water vapour",
        "units": "kg m**-2",
    },
    138: {
        "shortname": "vo",
        "name": "Vorticity (relative)",
        "units": "s**-1",
    },
    139: {
        "shortname": "stl1",
        "name": "Soil temperature level 1",
        "units": "K",
    },
    140: {
        "shortname": "swl1",
        "name": "Soil wetness level 1",
        "units": "m of water equivalent",
    },
    141: {
        "shortname": "sd",
        "name": "Snow depth",
        "units": "m of water equivalent",
    },
    142: {
        "shortname": "lsp",
        "name": "Large-scale precipitation",
        "units": "m",
    },
    143: {
        "shortname": "cp",
        "name": "Convective precipitation",
        "units": "m",
    },
    144: {
        "shortname": "sf",
        "name": "Snowfall",
        "units": "m of water equivalent",
    },
    145: {
        "shortname": "bld",
        "name": "Time-integrated boundary layer dissipation",
        "units": "J m**-2",
    },
    146: {
        "shortname": "sshf",
        "name": "Time-integrated surface sensible heat net flux",
        "units": "J m**-2",
    },
    147: {
        "shortname": "slhf",
        "name": "Time-integrated surface latent heat net flux",
        "units": "J m**-2",
    },
    151: {
        "shortname": "msl",
        "name": "Mean sea level pressure",
        "units": "Pa",
    },
    155: {
        "shortname": "d",
        "name": "Divergence",
        "units": "s**-1",
    },
    156: {
        "shortname": "gh",
        "name": "Geopotential height",
        "units": "gpm",
    },
    157: {
        "shortname": "r",
        "name": "Relative humidity",
        "units": "%",
    },
    158: {
        "shortname": "tsp",
        "name": "Tendency of surface pressure",
        "units": "Pa s**-1",
    },
    164: {
        "shortname": "tcc",
        "name": "Total cloud cover",
        "units": "(0 - 1)",
    },
    169: {
        "shortname": "ssrd",
        "name": "Surface short-wave (solar) radiation downwards",
        "units": "J m**-2",
    },
    172: {
        "shortname": "lsm",
        "name": "Land-sea mask",
        "units": "(0 - 1)",
    },
    173: {
        "shortname": "sr",
        "name": "Surface roughness (climatological)",
        "units": "m",
    },
    174: {
        "shortname": "al",
        "name": "Albedo (climatological)",
        "units": "(0 - 1)",
    },
    176: {
        "shortname": "ssr",
        "name": "Surface net short-wave (solar) radiation",
        "units": "J m**-2",
    },
    177: {
        "shortname": "str",
        "name": "Surface net long-wave (thermal) radiation",
        "units": "J m**-2",
    },
    178: {
        "shortname": "tsr",
        "name": "Top net short-wave (solar) radiation",
        "units": "J m**-2",
    },
    179: {
        "shortname": "ttr",
        "name": "Top net long-wave (thermal) radiation",
        "units": "J m**-2",
    },
    180: {
        "shortname": "ewss",
        "name": "Time-integrated eastward turbulent surface stress",
        "units": "N m**-2 s",
    },
    181: {
        "shortname": "nsss",
        "name": "Time-integrated northward turbulent surface stress",
        "units": "N m**-2 s",
    },
    182: {
        "shortname": "e",
        "name": "Evaporation",
        "units": "m of water equivalent",
    },
    185: {
        "shortname": "ccc",
        "name": "Convective cloud cover",
        "units": "(0 - 1)",
    },
    203: {
        "shortname": "o3",
        "name": "Ozone mass mixing ratio",
        "units": "kg kg**-1",
    },
    206: {
        "shortname": "tco3",
        "name": "Total column ozone",
        "units": "kg m**-2",
    },
    210: {
        "shortname": "ssrc",
        "name": "Surface net short-wave (solar) radiation, clear sky",
        "units": "J m**-2",
    },
    211: {
        "shortname": "strc",
        "name": "Surface net long-wave (thermal) radiation, clear sky",
        "units": "J m**-2",
    },
    238: {
        "shortname": "tsn",
        "name": "Temperature of snow layer",
        "units": "K",
    },
    3063: {
        "shortname": "acpcp",
        "name": "Convective precipitation (water)",
        "units": "kg m**-2",
    },
    3066: {
        "shortname": "sde",
        "name": "Snow depth",
        "units": "m",
    },
    3072: {
        "shortname": "ccc",
        "name": "Convective cloud cover",
        "units": "%",
    },
    3121: {
        "shortname": "lhf",
        "name": "Latent heat flux",
        "units": "W m**-2",
    },
    3122: {
        "shortname": "shf",
        "name": "Sensible heat flux",
        "units": "W m**-2",
    },
    3123: {
        "shortname": "bld",
        "name": "Boundary layer dissipation",
        "units": "W m**-2",
    },
    151129: {
        "shortname": "thetao",
        "name": "Sea water potential temperature",
        "units": "deg C",
    },
    151130: {
        "shortname": "so",
        "name": "Sea water practical salinity",
        "units": "psu",
    },
    151131: {
        "shortname": "ocu",
        "name": "Eastward surface sea water velocity",
        "units": "m s**-1",
    },
    151132: {
        "shortname": "ocv",
        "name": "Northward surface sea water velocity",
        "units": "m s**-1",
    },
    151133: {
        "shortname": "wo",
        "name": "Upward sea water velocity",
        "units": "m s**-1",
    },
    151138: {
        "shortname": "sigmat",
        "name": "Sea water sigma theta",
        "units": "kg m**-3",
    },
    151145: {
        "shortname": "zos",
        "name": "Sea surface height",
        "units": "m",
    },
    151147: {
        "shortname": "stfbarot",
        "name": "Ocean barotropic stream function",
        "units": "m**3 s**-1",
    },
    151153: {
        "shortname": "taueo",
        "name": "Surface downward eastward stress",
        "units": "N m**-2",
    },
    151154: {
        "shortname": "tauno",
        "name": "Surface downward northward stress",
        "units": "N m**-2",
    },
    151163: {
        "shortname": "t20d",
        "name": "Depth of 20C isotherm",
        "units": "m",
    },
    151189: {
        "shortname": "tos",
        "name": "Sea surface temperature in degC",
        "units": "deg C",
    },
    151213: {
        "shortname": "hfds",
        "name": "Surface downward heat flux in sea water",
        "units": "W m**-2",
    },
    151214: {
        "shortname": "hc300m",
        "name": "Ocean heat content 0-300m",
        "units": "J m**-2",
    },
    151219: {
        "shortname": "sos",
        "name": "Sea surface practical salinity",
        "units": "psu",
    },
    151222: {
        "shortname": "tauvo",
        "name": "Surface downward y stress",
        "units": "N m**-2",
    },
    151223: {
        "shortname": "tauuo",
        "name": "Surface downward x stress",
        "units": "N m**-2",
    },
    151224: {
        "shortname": "mlotdev",
        "name": "Ocean mixed layer thickness defined by vertical tracer diffusivity threshold",
        "units": "m",
    },
    151225: {
        "shortname": "mlotst010",
        "name": "Ocean mixed layer thickness defined by sigma theta 0.01 kg/m3",
        "units": "m",
    },
    151228: {
        "shortname": "mlott02",
        "name": "Ocean mixed layer thickness defined by temperature 0.2C",
        "units": "m",
    },
    151235: {
        "shortname": "sc300m",
        "name": "Integrated salinity 0-300m",
        "units": "psu*m",
    },
    151250: {
        "shortname": "voy",
        "name": "Sea water y velocity",
        "units": "m s**-1",
    },
    151251: {
        "shortname": "uox",
        "name": "Sea water x velocity",
        "units": "m s**-1",
    },
    174092: {
        "shortname": "sialb",
        "name": "Sea ice albedo",
        "units": "(0 - 1)",
    },
    174093: {
        "shortname": "sitemptop",
        "name": "Sea ice surface temperature",
        "units": "deg C",
    },
    174097: {
        "shortname": "sisnthick",
        "name": "Sea ice snow thickness",
        "units": "m",
    },
    174098: {
        "shortname": "sithick",
        "name": "Sea-ice thickness",
        "units": "m",
    },
    174112: {
        "shortname": "siue",
        "name": "Sea ice velocity along x",
        "units": "m s**-1",
    },
    174113: {
        "shortname": "sivn",
        "name": "Sea ice velocity along y",
        "units": "m s**-1",
    },
    210061: {
        "shortname": "co2",
        "name": "Carbon dioxide mass mixing ratio",
        "units": "kg kg**-1",
    },
    210062: {
        "shortname": "ch4",
        "name": "Methane",
        "units": "kg kg**-1",
    },
    210063: {
        "shortname": "n2o",
        "name": "Nitrous oxide",
        "units": "kg kg**-1",
    },
    210066: {
        "shortname": "tcn2o",
        "name": "Total column Nitrous oxide",
        "units": "kg m**-2",
    },
    210072: {
        "shortname": "pm1",
        "name": "Particulate matter d <= 1 um",
        "units": "kg m**-3",
    },
    210073: {
        "shortname": "pm2p5",
        "name": "Particulate matter d <= 2.5 um",
        "units": "kg m**-3",
    },
    210074: {
        "shortname": "pm10",
        "name": "Particulate matter d <= 10 um",
        "units": "kg m**-3",
    },
    210121: {
        "shortname": "no2",
        "name": "Nitrogen dioxide mass mixing ratio",
        "units": "kg kg**-1",
    },
    210122: {
        "shortname": "so2",
        "name": "Sulphur dioxide mass mixing ratio",
        "units": "kg kg**-1",
    },
    210123: {
        "shortname": "co",
        "name": "Carbon monoxide mass mixing ratio",
        "units": "kg kg**-1",
    },
    210124: {
        "shortname": "hcho",
        "name": "Formaldehyde",
        "units": "kg kg**-1",
    },
    210125: {
        "shortname": "tcno2",
        "name": "Total column Nitrogen dioxide",
        "units": "kg m**-2",
    },
    210126: {
        "shortname": "tcso2",
        "name": "Total column Sulphur dioxide",
        "units": "kg m**-2",
    },
    210127: {
        "shortname": "tcco",
        "name": "Total column Carbon monoxide",
        "units": "kg m**-2",
    },
    210128: {
        "shortname": "tchcho",
        "name": "Total column Formaldehyde",
        "units": "kg m**-2",
    },
    210181: {
        "shortname": "ra",
        "name": "Radon",
        "units": "kg kg**-1",
    },
    210183: {
        "shortname": "tcra",
        "name": "Total column Radon",
        "units": "kg m**-2",
    },
    210203: {
        "shortname": "go3",
        "name": "Ozone mass mixing ratio (full chemistry scheme)",
        "units": "kg kg**-1",
    },
    210206: {
        "shortname": "gtco3",
        "name": "GEMS Total column ozone",
        "units": "kg m**-2",
    },
    217003: {
        "shortname": "h2o2",
        "name": "Hydrogen peroxide",
        "units": "kg kg**-1",
    },
    217004: {
        "shortname": "ch4_c",
        "name": "Methane (chemistry)",
        "units": "kg kg**-1",
    },
    217006: {
        "shortname": "hno3",
        "name": "Nitric acid",
        "units": "kg kg**-1",
    },
    217010: {
        "shortname": "c2h4",
        "name": "Ethene",
        "units": "kg kg**-1",
    },
    217013: {
        "shortname": "pan",
        "name": "Peroxyacetyl nitrate",
        "units": "kg kg**-1",
    },
    217016: {
        "shortname": "c5h8",
        "name": "Isoprene",
        "units": "kg kg**-1",
    },
    217018: {
        "shortname": "dms",
        "name": "Dimethyl sulfide",
        "units": "kg kg**-1",
    },
    217019: {
        "shortname": "nh3",
        "name": "Ammonia mass mixing ratio",
        "units": "kg kg**-1",
    },
    217027: {
        "shortname": "no",
        "name": "Nitrogen monoxide mass mixing ratio",
        "units": "kg kg**-1",
    },
    217030: {
        "shortname": "oh",
        "name": "Hydroxyl radical",
        "units": "kg kg**-1",
    },
    217032: {
        "shortname": "no3",
        "name": "Nitrate radical",
        "units": "kg kg**-1",
    },
    217033: {
        "shortname": "n2o5",
        "name": "Dinitrogen pentoxide",
        "units": "kg kg**-1",
    },
    217042: {
        "shortname": "ch3oh",
        "name": "Methanol",
        "units": "kg kg**-1",
    },
    217043: {
        "shortname": "hcooh",
        "name": "Formic acid",
        "units": "kg kg**-1",
    },
    217045: {
        "shortname": "c2h6",
        "name": "Ethane",
        "units": "kg kg**-1",
    },
    217046: {
        "shortname": "c2h5oh",
        "name": "Ethanol",
        "units": "kg kg**-1",
    },
    217047: {
        "shortname": "c3h8",
        "name": "Propane",
        "units": "kg kg**-1",
    },
    217048: {
        "shortname": "c3h6",
        "name": "Propene",
        "units": "kg kg**-1",
    },
    217049: {
        "shortname": "c10h16",
        "name": "Terpenes",
        "units": "kg kg**-1",
    },
    217063: {
        "shortname": "oclo",
        "name": "Chlorine dioxide",
        "units": "kg kg**-1",
    },
    217064: {
        "shortname": "clono2",
        "name": "Chlorine nitrate",
        "units": "kg kg**-1",
    },
    217065: {
        "shortname": "hocl",
        "name": "Hypochlorous acid",
        "units": "kg kg**-1",
    },
    217068: {
        "shortname": "hbr",
        "name": "Hydrogen bromide",
        "units": "kg kg**-1",
    },
    217070: {
        "shortname": "hobr",
        "name": "Hypobromous acid",
        "units": "kg kg**-1",
    },
    217078: {
        "shortname": "ch3cl",
        "name": "Methyl chloride",
        "units": "kg kg**-1",
    },
    217080: {
        "shortname": "ch3br",
        "name": "Methyl bromide",
        "units": "kg kg**-1",
    },
    217085: {
        "shortname": "h2so4",
        "name": "Sulfuric acid",
        "units": "kg kg**-1",
    },
    217086: {
        "shortname": "hono",
        "name": "Nitrous acid",
        "units": "kg kg**-1",
    },
    217096: {
        "shortname": "ch3cooh",
        "name": "Acetic acid",
        "units": "kg kg**-1",
    },
    217174: {
        "shortname": "clo",
        "name": "Chlorine monoxide",
        "units": "kg kg**-1",
    },
    217176: {
        "shortname": "bro",
        "name": "Bromine monoxide",
        "units": "kg kg**-1",
    },
    217194: {
        "shortname": "brono2",
        "name": "Bromine nitrate",
        "units": "kg kg**-1",
    },
    217200: {
        "shortname": "hcl",
        "name": "Hydrogen chloride",
        "units": "kg kg**-1",
    },
    218003: {
        "shortname": "tc_h2o2",
        "name": "Total column hydrogen peroxide",
        "units": "kg m**-2",
    },
    218004: {
        "shortname": "tc_ch4",
        "name": "Total column methane",
        "units": "kg m**-2",
    },
    218006: {
        "shortname": "tc_hno3",
        "name": "Total column nitric acid",
        "units": "kg m**-2",
    },
    218010: {
        "shortname": "tc_c2h4",
        "name": "Total column ethene",
        "units": "kg m**-2",
    },
    218013: {
        "shortname": "tc_pan",
        "name": "Total column  peroxyacetyl nitrate",
        "units": "kg m**-2",
    },
    218016: {
        "shortname": "tc_c5h8",
        "name": "Total column  isoprene",
        "units": "kg m**-2",
    },
    218018: {
        "shortname": "tc_dms",
        "name": "Total column dimethyl sulfide",
        "units": "kg m**-2",
    },
    218019: {
        "shortname": "tc_nh3",
        "name": "Total column ammonia",
        "units": "kg m**-2",
    },
    218020: {
        "shortname": "tc_so4",
        "name": "Total column  sulfate",
        "units": "kg m**-2",
    },
    218027: {
        "shortname": "tc_no",
        "name": "Total column nitrogen monoxide",
        "units": "kg m**-2",
    },
    218030: {
        "shortname": "tc_oh",
        "name": "Total column hydroxyl radical",
        "units": "kg m**-2",
    },
    218032: {
        "shortname": "tc_no3",
        "name": "Total column nitrate radical",
        "units": "kg m**-2",
    },
    218033: {
        "shortname": "tc_n2o5",
        "name": "Total column dinitrogen pentoxide",
        "units": "kg m**-2",
    },
    218042: {
        "shortname": "tc_ch3oh",
        "name": "Total column methanol",
        "units": "kg m**-2",
    },
    218043: {
        "shortname": "tc_hcooh",
        "name": "Total column formic acid",
        "units": "kg m**-2",
    },
    218045: {
        "shortname": "tc_c2h6",
        "name": "Total column  ethane",
        "units": "kg m**-2",
    },
    218046: {
        "shortname": "tc_c2h5oh",
        "name": "Total column ethanol",
        "units": "kg m**-2",
    },
    218047: {
        "shortname": "tc_c3h8",
        "name": "Total column propane",
        "units": "kg m**-2",
    },
    218048: {
        "shortname": "tc_c3h6",
        "name": "Total column propene",
        "units": "kg m**-2",
    },
    218049: {
        "shortname": "tc_c10h16",
        "name": "Total column terpenes",
        "units": "kg m**-2",
    },
    218063: {
        "shortname": "tc_oclo",
        "name": "Total column of chlorine dioxide",
        "units": "kg m**-2",
    },
    218064: {
        "shortname": "tc_clono2",
        "name": "Total column of chlorine nitrate",
        "units": "kg m**-2",
    },
    218065: {
        "shortname": "tc_hocl",
        "name": "Total column of hypochlorous acid",
        "units": "kg m**-2",
    },
    218068: {
        "shortname": "tc_hbr",
        "name": "Total column of hydrogen bromide",
        "units": "kg m**-2",
    },
    218070: {
        "shortname": "tc_hobr",
        "name": "Total column of hypobromous acid",
        "units": "kg m**-2",
    },
    218078: {
        "shortname": "tc_ch3cl",
        "name": "Total column of methyl chloride",
        "units": "kg m**-2",
    },
    218080: {
        "shortname": "tc_ch3br",
        "name": "Total column of methyl bromide",
        "units": "kg m**-2",
    },
    218086: {
        "shortname": "tc_hono",
        "name": "Total column of nitrous acid",
        "units": "kg m**-2",
    },
    218096: {
        "shortname": "tc_ch3cooh",
        "name": "Total column of acetic acid",
        "units": "kg m**-2",
    },
    218174: {
        "shortname": "tc_clo",
        "name": "Total column of chlorine monoxide",
        "units": "kg m**-2",
    },
    218176: {
        "shortname": "tc_bro",
        "name": "Total column of bromine monoxide",
        "units": "kg m**-2",
    },
    218194: {
        "shortname": "tc_brono2",
        "name": "Total column of bromine nitrate",
        "units": "kg m**-2",
    },
    218200: {
        "shortname": "tc_hcl",
        "name": "Total column of hydrogen chloride",
        "units": "kg m**-2",
    },
    260509: {
        "shortname": "al",
        "name": "Forecast albedo",
        "units": "%",
    },
    262100: {
        "shortname": "sos",
        "name": "Sea surface practical salinity",
        "units": "g kg**-1",
    },
    262104: {
        "shortname": "t20d",
        "name": "Depth of 20 C isotherm",
        "units": "m",
    },
    262113: {
        "shortname": "mlotst010",
        "name": "Ocean mixed layer depth defined by sigma theta 0.01 kg m-3",
        "units": "m",
    },
    262124: {
        "shortname": "zos",
        "name": "Sea surface height",
        "units": "m",
    },
    262133: {
        "shortname": "hfcorr",
        "name": "Heat flux correction",
        "units": "W m**-2",
    },
}


# Reverse index. A handful of shortnames (al, bld, ccc, mlotst010, sos, t20d,
# zos) are reused by more than one paramId, so the values are lists rather
# than single ids.
SHORTNAME_TO_IDS: dict[str, list[int]] = {}
for _id, _param in ECMWF_NETCDF_PARAMS.items():
    SHORTNAME_TO_IDS.setdefault(_param["shortname"], []).append(_id)


def ids_for_shortname(shortname: str) -> list[int]:
    """Return the paramId(s) published under `shortname`, empty if unknown."""
    return SHORTNAME_TO_IDS.get(shortname, [])


def shortname_for_id(param_id: int) -> str | None:
    """Return the shortname for `param_id`, or None if it has no netCDF encoding."""
    param = ECMWF_NETCDF_PARAMS.get(param_id)
    return param["shortname"] if param else None
