from kalash.utils import _interpolate_this_file, _interpolate_workdir


INTERPOLATION_MAP = {
    "$(ThisFile)": _interpolate_this_file,
    "$(WorkDir)": _interpolate_workdir,
}
