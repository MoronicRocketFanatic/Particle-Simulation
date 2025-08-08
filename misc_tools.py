import math
from pygame import Vector2

def rainbow_cycle(time:float) -> tuple[float, float, float]:
    """A function that "cycles" through colors with a given time, uses sine functions to achieve this.

    Args:
        time (float): _Given time value._

    Returns:
        (tuple[float, float, float\]): _RGB tuple._
    """    
    r = math.sin(time)
    g = math.sin(time + .33 * 2 * math.pi)
    b = math.sin(time + .66 * 2 * math.pi)

    return (255 * r*r, 255 * g*g, 255 * b*b)


def clamp(value, maximum, minimum):
    """Handy little function for clamping a value.

    Args:
        value (int or float): _Value to clamp._
        maximum (int or float): _Maximum possible output._
        minimum (int or float): _Minimum possible output._

    Returns:
        (int or float): _Clamped value._
    """    
    return max(min(value, maximum), minimum)


def color_temperature_rgb(temperature:int=1500) -> tuple[float, float, float]:
    """A function that will convert a given color temperature to a RGB tuple and return it.

    Args:
        temperature (int, optional): _Color temperature in kelvin._ Defaults to 1500k.

    Returns:
        (tuple[float, float, float]): _RGB tuple._
    """    
    temperature /= 100
    
    if temperature <=66:
        red = 255
        
        green = 99.4708025861 * math.log(temperature) - 161.1195681661
        
    else:
        red = 329.698727446 * ((temperature - 60) ** -0.1332047592)
        green = 288.1221695283 * ((temperature - 60) ** -0.0755148492)
        red = clamp(red, 255, 0)
        green = clamp(green, 255, 0)
    
    if temperature >= 66:
        blue = 255
    
    else:
        if temperature <= 19:
            blue = 0
        
        else:
            blue = 138.5177312231 * math.log((temperature - 10)) - 305.0447927307
            blue = clamp(blue, 255, 0)
    
    
    return (red, green, blue)



def to_camera(position:Vector2, display_scale:float, display_offset:Vector2) -> Vector2:
    return position * display_scale + display_offset

def from_camera(position:Vector2, display_scale:float, display_offset:Vector2) -> Vector2:
    return (position - display_offset) / display_scale



def test(i) -> int:
    return i
if __name__ == "__main__": # Simple test code
    for i in range(100):
        print(rainbow_cycle(i/10))
    
    print(clamp(10, 5, 1))
    
    print(color_temperature_rgb(1500))