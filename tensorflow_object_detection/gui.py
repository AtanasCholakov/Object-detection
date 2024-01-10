import threading
import tkinter as tk
from Detector import *
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, filedialog
from PIL import Image, ImageTk

class gui:
    def __init__(self):
        self.detector = Detector()
        self.detector.readClasses("coco.names")
        self.detector.downloadModel("http://download.tensorflow.org/models/object_detection/tf2/20200711/faster_rcnn_resnet152_v1_640x640_coco17_tpu-8.tar.gz")
        self.detector.loadModel()
        
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\alexa\Desktop\tensorflow_object_detection\build\assets\frame0")


        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)
        
        self.root = tk.Tk()
        
        self.root.geometry("800x400")
        self.root.configure(bg = "#FFFFFF")
        
        self.camera_running = False
        self.cap = None
        
        self.canvas = Canvas(
            self.root,
            bg = "#FFFFFF",
            height = 400,
            width = 800,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )

        self.canvas.place(x = 0, y = 0)
        image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        image_1 = self.canvas.create_image(
            400.0,
            200.0,
            image=image_image_1
        )

        image_image_2 = PhotoImage(
            file=relative_to_assets("image_2.png"))
        image_2 = self.canvas.create_image(
            400.0,
            45.0,
            image=image_image_2
        )

        self.canvas.create_text(
            262.0,
            31.0,
            anchor="nw",
            text="OBJECT RECOGNITION",
            fill="#C231DC",
            font=("Inter Bold", 25 * -1)
        )

        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.detect_moving_object,
            relief="flat"
        )
        button_1.place(
            x=441.0,
            y=238.0,
            width=320.0,
            height=95.83419799804688
        )

        button_image_2 = PhotoImage(
            file=relative_to_assets("button_2.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.detect_object,
            relief="flat"
        )
        button_2.place(
            x=67.0,
            y=243.0,
            width=320.0,
            height=105.43046569824219
        )

        button_image_3 = PhotoImage(
            file=relative_to_assets("button_3.png"))
        button_3 = Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.toggle_camera,
            relief="flat"
        )
        button_3.place(
            x=526.0,
            y=83.0,
            width=222.0,
            height=113.0
        )
        
        self.camera_started = False

        image_image_3 = PhotoImage(
            file=relative_to_assets("image_3.png"))
        image_3 = self.canvas.create_image(
            492.0,
            139.0,
            image=image_image_3
        )

        image_image_4 = PhotoImage(
            file=relative_to_assets("image_4.png"))
        image_4 = self.canvas.create_image(
            314.0,
            139.0,
            image=image_image_4
        )

        image_image_5 = PhotoImage(
            file=relative_to_assets("image_5.png"))
        image_5 = self.canvas.create_image(
            206.0,
            45.0,
            image=image_image_5
        )

        image_image_6 = PhotoImage(
            file=relative_to_assets("image_6.png"))
        image_6 = self.canvas.create_image(
            591.0,
            45.0,
            image=image_image_6
        )

        button_image_4 = PhotoImage(
            file=relative_to_assets("button_4.png"))
        button_4 = Button(
            image=button_image_4,
            borderwidth=0,
            highlightthickness=0,
            command=self.select_file,
            relief="flat"
        )
        button_4.place(
            x=71.0,
            y=99.0,
            width=216.0,
            height=75.0
        )
        self.root.resizable(False, False)
        self.root.mainloop()

    def select_file(self):
            file_path = filedialog.askopenfilename()
            if file_path:
                self.canvas.create_text(
                    75.0,
                    175.0,
                    anchor="nw",
                    text=f"ИЗБРАН ФАЙЛ: \n{file_path}",
                    fill="#FFFFFF",
                    font=("Inter Black", 17 * -1)
                )
                self.selected_file_path = file_path

    def detect_object(self):
        if self.camera_running:
            threshold = 0.65
            self.detector.predictVideo(self.selected_file_path, threshold)
        elif hasattr(self, 'selected_file_path'):
            threshold = 0.65
            self.detector.predictVideo(self.selected_file_path, threshold)
        else:
            self.canvas.create_text(
                    75.0,
                    175.0,
                    anchor="nw",
                    text=f"Моля, изберете файл или стартирайте камерата!",
                    fill="#FFFFFF",
                    font=("Inter Black", 17 * -1)
                )

    def detect_moving_object(self):
        if self.camera_running:
            ret, frame = self.cap.read()
            if ret:
                self.detector.detectMovingObjects(frame)
            else:
                self.canvas.create_text(
                    75.0,
                    175.0,
                    anchor="nw",
                    text="Не може да се прочете от камерата!",
                    fill="#FFFFFF",
                    font=("Inter Black", 17 * -1)
                )
        elif hasattr(self, 'selected_file_path'):
            self.detector.detectMovingObjects(self.selected_file_path)
        else:
            self.canvas.create_text(
                    75.0,
                    175.0,
                    anchor="nw",
                    text=f"Моля, изберете файл или стартирайте камерата!",
                    fill="#FFFFFF",
                    font=("Inter Black", 17 * -1)
                )

    def toggle_camera(self):
        if not self.camera_running:
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        if not self.camera_running:
            self.selected_file_path = 0
            self.camera_running = True

    def stop_camera(self):
        if self.camera_running:
            self.camera_running = False
            if self.cap:
                self.cap.release()

    def run(self):
        self.root.mainloop()
        
ui = gui()
ui.run()