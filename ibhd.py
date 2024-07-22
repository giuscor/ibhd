# All purpose imports
import os
import json
import statistics

# UI imports
import tkinter as tk
from tkinter import filedialog, Listbox, Label, Frame, ttk, Text

# Image manipulation imports
from PIL import Image, ImageTk
from threading import Thread
import numpy as np
import matplotlib.pyplot as plt
import queue

##############################
#     Image Processing       #
##############################

# Function to compute numerical stats
def compute_stats(image_array):
    stats = {
        "mean": np.mean(image_array),
        "std_dev": np.std(image_array),
        "min": int(np.min(image_array)),
        "max": int(np.max(image_array)),
        "median": np.median(image_array)
    }
    return stats

# Function to round stats
def round_stats(stats):
    rounded_stats = {
        "mean": round(stats["mean"], 2),
        "std_dev": round(stats["std_dev"], 2),
        "min": stats["min"],
        "max": stats["max"],
        "median": round(stats["median"], 2)
    }
    return rounded_stats

# Function to blend two images, calculate the stats of the blended image and append them to the json file
def blend_images(image1_path, image2_path, output_folder, q, image_list, json_data, all_stats):
    try:
        # Open images
        image1 = Image.open(image1_path).convert("L")
        image2 = Image.open(image2_path).convert("L")
        
        # Ensure images are the same size
        if image1.size != image2.size:
            image2 = image2.resize(image1.size)
        
        # Generate a random alpha value
        alpha = np.random.random()
        
        # Blend images
        blended_image = Image.blend(image2, image1, alpha)
        
        # Create the output filename
        image1_name = os.path.splitext(os.path.basename(image1_path))[0]
        image2_name = os.path.splitext(os.path.basename(image2_path))[0]
        output_filename = f"{image1_name}_{image2_name}_alpha_{alpha:.2f}.bmp"
        output_path = os.path.join(output_folder, output_filename)
        
        # Save the blended image
        blended_image.save(output_path)

        # Compute stats
        image_array = np.array(blended_image)
        stats = compute_stats(image_array)

        # Add stats to all_stats for aggregate calculations
        for key in all_stats.keys():
            all_stats[key].append(stats[key])

        # Append data to JSON
        json_data["processed_images"].append({
            "original_images": [image1_path, image2_path],
            "alpha": round(alpha, 2),
            "blended_image_path": output_path,
            "stats": round_stats(stats)
        })

        # Update the queue and image list
        q.put(1)
        image_list.append(output_path)

    except Exception as e:
        print(f"Error processing images {image1_path} and {image2_path}: {e}")

# Function to compute aggregate stats
def compute_aggregate_stats(json_data, all_stats):
    aggregate_stats = {}
    for key, values in all_stats.items():
        aggregate_stats[key] = {
            "mean": round(float(np.mean(values)), 2),
            "std_dev": round(float(np.std(values)), 2)
        }
    
    json_data["aggregate_stats"] = aggregate_stats

# Function to process all image pairs in parallel
def parallel_process(input_folder, output_folder, progress_bar, total_tasks, image_list, status_text, json_data):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get list of all BMP images in the input folder
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.bmp')]
    
    # Create all possible pairs of images
    image_pairs = [(os.path.join(input_folder, image_files[i]), os.path.join(input_folder, image_files[j]))
                   for i in range(len(image_files)) for j in range(i + 1, len(image_files))]
    
    q = queue.Queue()
    
    all_stats = {
        "mean": [],
        "std_dev": [],
        "min": [],
        "max": [],
        "median": []
    }
    
    # Start a thread to update the progress bar and status text
    def update_progress_bar():
        processed_count = 0
        for _ in range(total_tasks):
            q.get()
            progress_bar.step(1)
            processed_count += 1
            status_text.config(state=tk.NORMAL)
            status_text.delete(1.0, tk.END)
            status_text.insert(tk.END, f"Processed {processed_count}/{total_tasks} images")
            status_text.config(state=tk.DISABLED)
            q.task_done()
    
    progress_thread = Thread(target=update_progress_bar)
    progress_thread.start()
    
    # Create and start threads for image blending
    threads = []
    for image1_path, image2_path in image_pairs:
        thread = Thread(target=blend_images, args=(image1_path, image2_path, output_folder, q, image_list, json_data, all_stats))
        threads.append(thread)
        thread.start()
    
    # Join all threads
    for thread in threads:
        thread.join()
    
    q.join()
    progress_thread.join()

    # Compute aggregate stats
    compute_aggregate_stats(json_data, all_stats)

    # Save JSON data to file
    with open(os.path.join(output_folder, "image_stats.json"), "w") as json_file:
        json.dump(json_data, json_file, indent=4)

def select_input_folder():
    input_folder = filedialog.askdirectory()
    if input_folder:
        input_folder_entry.delete(0, tk.END)
        input_folder_entry.insert(0, input_folder)

def select_output_folder():
    output_folder = filedialog.askdirectory()
    if output_folder:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, output_folder)

def process_images():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    if not input_folder or not output_folder:
        return
    
    # Get the total number of tasks
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.bmp')]
    total_tasks = len(image_files) * (len(image_files) - 1) // 2
    
    progress_bar["maximum"] = total_tasks
    progress_bar["value"] = 0
    
    # Clear the Listbox
    image_listbox.delete(0, tk.END)
    
    # Initialize JSON data
    json_data = {"processed_images": []}
    
    # Run the parallel process
    image_list = []
    def run_parallel_process():
        parallel_process(input_folder, output_folder, progress_bar, total_tasks, image_list, status_text, json_data)
        # Update the Listbox with processed images
        for image_path in image_list:
            image_listbox.insert(tk.END, os.path.basename(image_path))
    
    Thread(target=run_parallel_process).start()

def show_image_and_histogram(event):
    selected_image = image_listbox.get(image_listbox.curselection())
    output_folder = output_folder_entry.get()
    image_path = os.path.join(output_folder, selected_image)
    
    # Display image
    img = Image.open(image_path)
    img.thumbnail((400, 400))
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    
    # Display histogram
    pixel_values = np.array(img.convert("L")).flatten()
    plt.hist(pixel_values, bins=32, range=(0, 256), density=True)
    plt.xlabel('Pixel value')
    plt.ylabel('Frequency')
    plt.title('Histogram')
    plt.savefig("histogram.png")
    plt.close()
    
    hist_img = Image.open("histogram.png")
    hist_img.thumbnail((400, 400))
    hist_img_tk = ImageTk.PhotoImage(hist_img)
    histogram_label.config(image=hist_img_tk)
    histogram_label.image = hist_img_tk
    os.remove('histogram.png')

##############################
#             UI             #
##############################

root_window = tk.Tk()
root_window.title("Image Blending and Histogram Display")

folder_frame = Frame(root_window)
folder_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky='ew')

# Input Folder
tk.Label(folder_frame, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5)
input_folder_entry = tk.Entry(folder_frame, width=50)
input_folder_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(folder_frame, text="Browse", command=select_input_folder).grid(row=0, column=2, padx=10, pady=5)

# Output Folder
tk.Label(folder_frame, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5)
output_folder_entry = tk.Entry(folder_frame, width=50)
output_folder_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(folder_frame, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=10, pady=5)

# Process Button
tk.Button(folder_frame, text="Process", command=process_images).grid(row=2, column=0, padx=10, pady=20)

# Progress Bar and status text
progress_frame = Frame(folder_frame)
progress_frame.grid(row=2, column=1, padx=10, pady=20)

progress_bar = ttk.Progressbar(progress_frame, length=300)
progress_bar.grid(row=0, column=0, padx=5)

status_text = Text(progress_frame, height=1, width=20, state=tk.DISABLED)
status_text.grid(row=0, column=1, padx=5)

# Listbox for Image Names
tk.Label(root_window, text="Processed Images:").grid(row=1, column=0, padx=10, pady=5)
image_listbox = Listbox(root_window, width=50, height=10)
image_listbox.grid(row=1, column=1, padx=10, pady=5)
image_listbox.bind('<<ListboxSelect>>', show_image_and_histogram)

# Image Display Area
image_label = Label(root_window)
image_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

# Histogram Display Area
histogram_label = Label(root_window)
histogram_label.grid(row=2, column=2, columnspan=1, padx=10, pady=5)

# Grid management
for i in range(4):
    root_window.columnconfigure(i, weight=1, minsize=75)
    root_window.rowconfigure(i, weight=1, minsize=50)
root_window.minsize(800, 600)

# keeps the window on screen; blocks any code that comes after it from running until you close the window where you called it
root_window.mainloop()
