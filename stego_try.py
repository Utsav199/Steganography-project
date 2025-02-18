import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import numpy as np

def load_image():
    global img, img_path
    img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if img_path:
        img = cv2.imread(img_path)
        display_image(img_path)

def display_image(path):
    image = Image.open(path)
    image = image.resize((250, 250))
    photo = ImageTk.PhotoImage(image)
    img_label.config(image=photo)
    img_label.image = photo

def encrypt_message():
    global img
    if img is None:
        messagebox.showerror("Error", "Please select an image first!")
        return
    
    msg = msg_entry.get() + "####END####"  # Add a delimiter to identify end of message
    password = pass_entry.get()
    
    if not msg or not password:
        messagebox.showerror("Error", "Message and password cannot be empty!")
        return
    
    binary_msg = ''.join(format(ord(char), '08b') for char in msg)  # Convert message to binary
    msg_length = len(binary_msg)
    
    flat_img = img.flatten().astype(np.uint8)  # Ensure uint8 type
    if msg_length > len(flat_img):
        messagebox.showerror("Error", "Message too large for selected image!")
        return
    
    for i in range(msg_length):
        flat_img[i] = (flat_img[i] & 254) | int(binary_msg[i])  # Modify LSB safely
    
    img = flat_img.reshape(img.shape)
    enc_path = "encryptedImage.png"  # Save as PNG for lossless compression
    cv2.imwrite(enc_path, img)
    os.system(f"start {enc_path}")
    messagebox.showinfo("Success", "Message encrypted and saved as encryptedImage.png")

def decrypt_message():
    global img
    img_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if not img_path:
        messagebox.showerror("Error", "Please select an image first!")
        return
    
    pas = simpledialog.askstring("Password", "Enter the decryption password:", show='*')
    
    if not pas or pas != pass_entry.get():
        messagebox.showerror("Error", "Incorrect password!")
        return
    
    img = cv2.imread(img_path)
    flat_img = img.flatten()
    binary_msg = ''.join(str(flat_img[i] & 1) for i in range(len(flat_img)))
    
    message = ''
    for i in range(0, len(binary_msg) - 7, 8):  # Ensure we have at least 8 bits
        char = chr(int(binary_msg[i:i+8], 2))
        message += char
        if message.endswith("####END"):
            message = message[:-9]  # Remove delimiter
            break
    
    # Debugging output
    print("Binary Message Length:", len(binary_msg))
    print("Decrypted Message:", message)

    if message == '':
        messagebox.showinfo("Decrypted Message", "No message found.")
    else:
        messagebox.showinfo("Decrypted Message", f"Message: {message}")

# GUI Setup
root = tk.Tk()
root.title("Image Steganography")
root.geometry("500x500")  # Increased window width

img_label = tk.Label(root)
img_label.pack()

tk.Button(root, text="Load Image", command=load_image).pack()

tk.Label(root, text="Enter Message(ending with !!):").pack()
msg_entry = tk.Entry(root, width=50 )  # Increased width for message entry
msg_entry.pack()

tk.Label(root, text="Enter Password:").pack()
pass_entry = tk.Entry(root, show="*", width=50)  # Increased width for password entry
pass_entry.pack()

tk.Button(root, text="Encrypt", command=encrypt_message).pack()
tk.Button(root, text="Decrypt", command=decrypt_message).pack()

root.mainloop()