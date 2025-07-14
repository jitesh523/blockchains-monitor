def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_linear(rgb_value: int) -> float:
    """Convert RGB value to linear color space."""
    c = rgb_value / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def calculate_luminance(hex_color: str) -> float:
    """Calculate relative luminance of a color."""
    r, g, b = hex_to_rgb(hex_color)
    r_linear = rgb_to_linear(r)
    g_linear = rgb_to_linear(g)
    b_linear = rgb_to_linear(b)
    return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate contrast ratio between two colors."""
    lum1 = calculate_luminance(hex1) + 0.05
    lum2 = calculate_luminance(hex2) + 0.05
    return lum1 / lum2 if lum1 > lum2 else lum2 / lum1

def check_contrast(hex1: str, hex2: str, min_ratio: float = 4.5) -> bool:
    """Check if contrast ratio meets minimum requirement."""
    return calculate_contrast_ratio(hex1, hex2) >= min_ratio

# Example usage
if __name__ == "__main__":
    # Test with known good contrast
    primary_light = '#212529'
    background_light = '#FFFFFF'
    ratio = calculate_contrast_ratio(primary_light, background_light)
    is_contrast_sufficient = check_contrast(primary_light, background_light)
    print(f"Contrast ratio: {ratio:.2f}:1")
    print(f"Contrast sufficient: {is_contrast_sufficient}")
    
    # Test with potential poor contrast
    yellow = '#FFD43B'
    white = '#FFFFFF'
    ratio2 = calculate_contrast_ratio(yellow, white)
    is_contrast_sufficient2 = check_contrast(yellow, white)
    print(f"Yellow on white ratio: {ratio2:.2f}:1")
    print(f"Yellow on white sufficient: {is_contrast_sufficient2}")

