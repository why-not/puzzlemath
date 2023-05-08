import cv2
import numpy as np
from scipy import stats
from pathlib import Path
import pandas as pd

def calculate_most_common_color(square: np.ndarray) -> np.ndarray:
    """
    Calculate the most common color of the given square.
    """
    reshaped_square = square.reshape(-1, square.shape[-1])
    mode_color = stats.mode(reshaped_square, axis=0)[0]
    return mode_color

def calculate_top_colors(image: np.ndarray, size: int, top_n: int) -> np.ndarray:
    """
    Calculate the top N most common colors in the input image by considering size x size squares.
    """
    rows, cols, _ = image.shape
    num_rows = rows // size
    num_cols = cols // size
    
    color_counts = {}
    
    for i in range(num_rows):
        for j in range(num_cols):
            square = image[i*size:(i+1)*size, j*size:(j+1)*size]
            most_common_color = tuple(calculate_most_common_color(square).flatten())
            if most_common_color in color_counts:
                color_counts[most_common_color] += 1
            else:
                color_counts[most_common_color] = 1
    
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    top_colors = np.array([color for color, _ in sorted_colors[:top_n]])
    
    return top_colors

def nearest_color(color: np.ndarray, colors: np.ndarray) -> np.ndarray:
    """
    Find the nearest color in the colors array to the given color.
    """
    distances = np.linalg.norm(colors - color, axis=1)
    nearest_color_index = np.argmin(distances)
    return colors[nearest_color_index]

def replace_squares_with_nearest_top_color(image: np.ndarray, size: int, top_colors: np.ndarray) -> np.ndarray:
    """
    Replace each size x size square in the input image with the nearest color from the top_colors list.
    """
    rows, cols, _ = image.shape
    num_rows = rows // size
    num_cols = cols // size
    
    output_image = np.zeros_like(image)
    
    for i in range(num_rows):
        for j in range(num_cols):
            square = image[i*size:(i+1)*size, j*size:(j+1)*size]
            most_common_color = calculate_most_common_color(square)
            nearest_top_color = nearest_color(most_common_color, top_colors)
            output_image[i*size:(i+1)*size, j*size:(j+1)*size] = nearest_top_color
            
    return output_image

def main():
    base_folder = Path("/Users/senthilgandhi/Dropbox/parent/workspace/pixel_puzzle_math")
    
    input_image_path = base_folder / "input_image.png"
    image = cv2.imread(str(input_image_path), cv2.IMREAD_UNCHANGED)
    
    size = 16  # You can modify this value based on your requirement
    top_n = 10  # You can modify this value based on your requirement
    
    # First pass: Calculate the top 10 most common colors in the input image
    top_colors = calculate_top_colors(image, size, top_n)
    
    # Second pass: Replace each square with the nearest color from the top_colors list
    output_image = replace_squares_with_nearest_top_color(image, size, top_colors)
    
    # Convert the output image from RGBA to RGB format
    output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_RGBA2RGB)
    
    # Save the output image
    output_image_path = base_folder / "output_image.png"
    cv2.imwrite(str(output_image_path), output_image_rgb)

if __name__ == "__main__":
    main()