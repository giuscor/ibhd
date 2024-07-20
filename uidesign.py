import tkinter as tk
from tkinter import filedialog, Listbox, Label, Frame
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt

# for fancier looks (substitute all relevant instances of tk with tk.ttk)
# import tkinter.ttk as ttk

# select input and output folder functions

def select_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, folder_selected)

def select_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_selected)

# Temporary image processing
def process_images():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    image_listbox.delete(0, tk.END)

    # Get list of BMP files and sort them alphabetically
    bmp_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".bmp")])

    for filename in bmp_files:
        image_listbox.insert(tk.END, filename)
        # Copy the image to the output folder (placeholder for processing)
        img = Image.open(os.path.join(input_folder, filename))
        img.save(os.path.join(output_folder, filename))

def show_image_and_histogram(event):
    selected_image = image_listbox.get(image_listbox.curselection())
    input_folder = input_folder_entry.get()
    image_path = os.path.join(input_folder, selected_image)
    
    # Display image
    img = Image.open(image_path)
    img.thumbnail((200, 200))
    img_tk = ImageTk.PhotoImage(img)
    image_label.config(image=img_tk)
    image_label.image = img_tk
    
    # # Display histogram (temporary)
    # plt.hist(img.convert("L").ravel(), bins=256, range=(0, 256), density=True)
    # plt.xlabel('Pixel value')
    # plt.ylabel('Frequency')
    # plt.title('Histogram')
    # plt.savefig("histogram.png")
    # plt.close()
    
    # hist_img = Image.open("histogram.png")
    # hist_img.thumbnail((200, 200))
    # hist_img_tk = ImageTk.PhotoImage(hist_img)
    # histogram_label.config(image=hist_img_tk)
    # histogram_label.image = hist_img_tk

# UI code starts here

root_window = tk.Tk()
root_window.title("BMP Image Folder Selector") #to be modified 

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
tk.Button(folder_frame, text="Process", command=process_images).grid(row=2, column=1, padx=10, pady=20)

# Listbox for Image Names
tk.Label(root_window, text="Processed\nImages:").grid(row=1, column=0, padx=10, pady=5)
image_listbox = Listbox(root_window, width=50, height=10)
image_listbox.grid(row=1, column=1, padx=10, pady=5)
image_listbox.bind('<<ListboxSelect>>', show_image_and_histogram)

# Image Display Area
image_label = Label(root_window)
image_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

# # Histogram Display Area
# histogram_label = Label(root_window)
# histogram_label.grid(row=4, column=2, columnspan=2, padx=10, pady=5)

# Grid management
for i in range(4):
    root_window.columnconfigure(i, weight=1, minsize=75)
    root_window.rowconfigure(i, weight=1, minsize=50)
root_window.minsize(800, 600)

# keeps the window on screen; blocks any code that comes after it from running until you close the window where you called it
root_window.mainloop()
