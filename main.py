import tkinter as tk
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import cv2

# Global variables to hold selected image and photo image
image = None
original_photo = None
transformed_photo = None
video = None
delay = 100  # Delay in milliseconds


def select_file():
    global image, original_photo
    filepath = fd.askopenfilename()
    image = Image.open(filepath)
    original_photo = ImageTk.PhotoImage(image=image)
    show_image()


def select_video():
    global video
    filepath = fd.askopenfilename()
    video = cv2.VideoCapture(filepath)
    show_video()


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


def blur_faces(frame):
    """Apply blur effect to detected faces."""
    face_cascade = cv2.CascadeClassifier("./haarcascade_frontalface_alt.xml")
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
    for x, y, w, h in faces:
        roi = frame[y : y + h, x : x + w]
        blurred_roi = cv2.GaussianBlur(roi, (23, 23), 30)
        frame[y : y + blurred_roi.shape[0], x : x + blurred_roi.shape[1]] = blurred_roi
    return frame


def show_video():
    global canvas, video
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    canvas.config(width=width, height=height)

    ret, frame = video.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = blur_faces(frame)  # Blur faces
        photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
        canvas.create_image(0, 0, image=photo, anchor="nw")
        canvas.photo = photo  # To prevent garbage collection of photo object
        canvas.after(delay, show_video)  # Update video after 'delay' milliseconds
    else:
        video.release()  # Release video capture object when video ends


def save_image():
    global canvas
    filename = fd.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("All files", "*.*"),
        ],
    )
    if filename:
        file_format = filename.split(".")[-1]  # Obține extensia fișierului
        if file_format.lower() == "png":
            canvas.postscript(file=filename + ".ps", colormode="color")
            img = Image.open(filename + ".ps")
            img.save(filename, format="PNG")  # Salvează imaginea în format PNG
        elif file_format.lower() == "jpg" or file_format.lower() == "jpeg":
            canvas.postscript(file=filename + ".ps", colormode="color")
            img = Image.open(filename + ".ps")
            img.save(filename, format="JPEG")  # Salvează imaginea în format JPEG
        else:
            canvas.postscript(file=filename + ".ps", colormode="color")
            img = Image.open(filename + ".ps")
            img.save(
                filename + ".png", format="PNG"
            )  # Dacă extensia nu este specificată sau nu este PNG sau JPEG, se va salva ca PNG implicit


root = tk.Tk()

open_button = tk.Button(root, text="Open Image", command=select_file)
open_button.pack()

remove_faces_button = tk.Button(root, text="Remove Faces", command=transform_img)
remove_faces_button.pack()

open_video_button = tk.Button(root, text="Open Video", command=select_video)
open_video_button.pack()

save_button = tk.Button(root, text="Save Image", command=save_image)
save_button.pack()

canvas = tk.Canvas(root)
canvas.pack()

root.mainloop()
