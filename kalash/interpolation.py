from typing import Callable, Dict

from kalash.spec import Spec

InterpolableStr = str
InterpolationTag = str
ReplacementStr = str
State = Spec  # `Spec` is aliased as `State` in case we want to change which class
# is responsible for the state injection
InterpolatorFunc = Callable[[InterpolableStr, InterpolationTag, State], ReplacementStr]
InterpolationMap = Dict[str, InterpolatorFunc]

# TODO: centralize internal configuration
# At the moment this is messy, `spec.py`, `spec.yaml`, `internal-config.yaml`, this one calls
# for another config (this time programmatic) which sould populate the `interpolation_map`...
# I suspect we need to go from declarative back to procedural for all those topics


class AmbigouosInterpolationException(Exception):
    pass


def _disambiguate_interpolation_map(interpolation_map: InterpolationMap):
    lowercase_interp_map = map(lambda k: k.lower(), interpolation_map.keys())
    if len(set(lowercase_interp_map)) != len(list(lowercase_interp_map)):
        raise AmbigouosInterpolationException(
            "At least two tags in the interpolation map are the same when "
            "brought to lowercase. All your map items should be unique keys "
            "and case-insensitive."
        )


def interpolate(ipt: InterpolableStr, interpolation_map: InterpolationMap):
    """Takes in any interpolable input string and replaces values like
    `$(ID)` or `$(TestClassName)` to vaules injected from the
    `interpolation_map`

    Returns a closure that accepts a state object that allows context-aware
    interpolation of values.
    """
    def wrapper(state: State):
        output = ipt
        for tag, replacement_str_callback in interpolation_map.items():
            output = replacement_str_callback(ipt, tag, state)
            output = replacement_str_callback(ipt, tag.lower(), state)
        return output
    return wrapper
