import cv2
import numpy as np
from pathlib import Path
from scipy import stats
import pandas as pd
from webcolors import rgb_to_name, hex_to_rgb

def read_image(input_path: Path) -> np.ndarray:
    """
    Read the image from the given path using OpenCV.
    """
    img = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
    return img

def save_image(output_path: Path, img: np.ndarray) -> None:
    """
    Save the processed image to the given path using OpenCV.
    """
    cv2.imwrite(str(output_path), img)

def calculate_most_common_color(square: np.ndarray) -> np.ndarray:
    """
    Calculate the most common color of the given square.
    """
    reshaped_square = square.reshape(-1, square.shape[-1])
    mode_color = stats.mode(reshaped_square, axis=0)[0]
    return mode_color

def draw_square(image: np.ndarray, 
                x: int, 
                y: int, 
                square_size: int, 
                border_color: tuple, 
                fill_color: tuple) -> None:
    """
    Draw a square with a specified border and 
    fill color on the image at the specified location.
    """
    image[y:y+square_size, x:x+square_size] = fill_color[:3]  # Remove the alpha channel
    image[y:y+1, x:x+square_size] = border_color[:3]  # Remove the alpha channel
    image[y+square_size-1:y+square_size, x:x+square_size] = border_color[:3]  # Remove the alpha channel
    image[y:y+square_size, x:x+1] = border_color[:3]  # Remove the alpha channel
    image[y:y+square_size, x+square_size-1:x+square_size] = border_color[:3]  # Remove the alpha channel


def get_html_color_name(color: tuple) -> str:
    """
    Get the HTML color name for a given RGB color.
    """
    hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
    try:
        color_name = rgb_to_name(hex_to_rgb(hex_color))
    except ValueError:
        color_name = hex_color
    return color_name

def process_image(image: np.ndarray, square_size: int) -> np.ndarray:
    """
    Process the image by replacing each square with its most common color 
    and creating a new image with white or light gray squares.
    """
    output_image = np.zeros_like(image)
    height, width, _ = image.shape
    color_mapping = []

    for i in range(0, height, square_size):
        for j in range(0, width, square_size):
            square = image[i:i+square_size, j:j+square_size]
            most_common_color = calculate_most_common_color(square)
            html_color_name = get_html_color_name(tuple(most_common_color[0][:3]))
            color_mapping.append({"coordinates": (j, i), 
                                  "color": most_common_color.tolist(), 
                                  "color_name": html_color_name})

            if html_color_name == "#f7f7f7":
                fill_color = (192, 192, 192, 255)
            else:
                fill_color = (255, 255, 255, 255)

            draw_square(output_image, 
                        j, 
                        i, 
                        square_size, 
                        (192, 192, 192, 255), 
                        fill_color)

    return output_image, color_mapping

def write_csv(output_path: Path, color_mapping: list) -> None:
    """
    Write the color mapping to a CSV file.
    """
    df = pd.DataFrame(color_mapping)
    df.to_csv(output_path, index=False)