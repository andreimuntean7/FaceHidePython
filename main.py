import tkinter as tk
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import cv2

# Global variables to hold selected image and photo image
image = None
original_photo = None
transformed_photo = None


def select_file():
    global image, original_photo
    filepath = fd.askopenfilename()
    image = Image.open(filepath)
    original_photo = ImageTk.PhotoImage(image=image)
    show_image()


def transform_img():
    global image, transformed_photo
    if image:
        transformed_image = transform_faces(image)
        transformed_photo = ImageTk.PhotoImage(image=Image.fromarray(transformed_image))
        show_image()


def transform_faces(original_image):
    """Transform the image by removing faces."""
    image = cv2.cvtColor(cv2.imread(original_image.filename), cv2.COLOR_BGR2RGB)
    face_detect = cv2.CascadeClassifier("./haarcascade_frontalface_alt.xml")
    face_data = face_detect.detectMultiScale(image, 1.3, 5)
    for x, y, w, h in face_data:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        roi = image[y : y + h, x : x + w]
        roi = cv2.GaussianBlur(roi, (23, 23), 30)
        image[y : y + roi.shape[0], x : x + roi.shape[1]] = roi
    return image


def show_image():
    global original_photo, transformed_photo
    if original_photo:
        width, height = image.size
        canvas.config(width=width, height=height)
        if transformed_photo:
            canvas.create_image(0, 0, image=transformed_photo, anchor="nw")
        else:
            canvas.create_image(0, 0, image=original_photo, anchor="nw")


root = tk.Tk()

open_button = tk.Button(root, text="Open", command=select_file)
open_button.pack()

remove_faces_button = tk.Button(root, text="Remove Faces", command=transform_img)
remove_faces_button.pack()

canvas = tk.Canvas(root)
canvas.pack()

root.mainloop()
