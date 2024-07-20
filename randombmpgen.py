from PIL import Image
import numpy as np
import os

# Function to create a bitmap image with random colors
def create_bitmap_image(file_path, width=200, height=200):
    # Create a random array of RGB values
    data = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    # Create an image from the random array
    image = Image.fromarray(data, 'RGB')
    # Save the image as a BMP file
    image.save(file_path)

# Generate bitmap files
how_many = 10
for i in range(1, how_many+1):
    numero = str(i).zfill(len(str(how_many)))
    create_bitmap_image(f'trialin/test_image_{numero}.bmp')

# List generated files
os.listdir('trialin')