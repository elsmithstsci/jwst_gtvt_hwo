"""
Test hwo_gtvt utils.py module
"""

import pytest
from hwo_gtvt.utils import check_hwo_instrument_name


@pytest.mark.parametrize(
    "instrument_name",
    [
        # "nircam",
        # "nirspec",
        # "miri",
        # "fgs",
        "v3pa",
        pytest.param("nircam", marks=pytest.mark.xfail(reason="JWST Instrument")),
        # pytest.param("acs", marks=pytest.mark.xfail(reason="Hubble Instrument")),
        # pytest.param("cos", marks=pytest.mark.xfail(reason="Hubble Instrument")),
        # pytest.param("wfc3", marks=pytest.mark.xfail(reason="Hubble Instrument")),
        # pytest.param("stis", marks=pytest.mark.xfail(reason="Hubble Instrument")),
        pytest.param("dsfkjhsdkjfg,/ew3765903", marks=pytest.mark.xfail(reason="Random characters")),
    ],
)
def test_check_hwo_instrument_name(instrument_name):
    check_hwo_instrument_name(instrument_name)
