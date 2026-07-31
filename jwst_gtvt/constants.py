import numpy as np
import os
import json
import glob

D2R = np.pi/180.0  # degrees to radians
EPSIOLON = 23.43929 * D2R  # obliquity of the ecliptic J2000
OBLIQUITY_OF_THE_ECLIPTIC = -23.439291 * D2R  # At J2000 equinox
PI2 = 2.0 * np.pi # 2 pi
R2D = 180.0 / np.pi  # radians to degrees 
UNIT_LIMIT = lambda x: min(max(-1.0,x),1.0)  # forces value to be in [-1,1]

# HWOE-266 7/26 EJAS: The rest of this code parameterizes spacecraft-dependent constants.

# Cache to store parameters dict.
saved_parameters = False

def get_parameters_json():
    global saved_parameters

    if saved_parameters:
        return saved_parameters

    filename_pattern = "*parameters*.json"
    path_pattern = os.path.join(os.path.dirname(__file__), "data", filename_pattern)
    path = glob.glob(path_pattern)[0]
    
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Could not find parameters JSON file at {str(path)}")

    with open(path, "r") as file:
        saved_parameters = json.load(file)
    
    return saved_parameters

def get_min_sun_pitch():
    return get_parameters_json()["minSunPitch"]

def get_max_sun_pitch():
    return get_parameters_json()["maxSunPitch"]

def get_max_sun_roll():
    return get_parameters_json()["maxSunRoll"]

# Not used
def get_sun_pitch_pad():
    return get_parameters_json()["sunPitchPad"]

def get_sun_roll_pad():
    return get_parameters_json()["sunRollPad"]

def get_url():
    return get_parameters_json()["url"]

def get_launch_date():
    return get_parameters_json()["launchDate"]
