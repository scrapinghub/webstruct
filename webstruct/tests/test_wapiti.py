from webstruct.wapiti import WapitiCRF
from webstruct.utils import run_command

def test_is_wapiti_binary_present():
    run_command(['which', WapitiCRF.WAPITI_CMD])


