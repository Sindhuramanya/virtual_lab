import tkinter as tk
import json
import customtkinter
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math



class RotatingKnobWithNumbers:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.grid(row=4, column=3, rowspan=3, padx=(10, 0), pady=(10, 0), sticky="nsew")

        # Create a canvas to draw the knob
        self.canvas = tk.Canvas(self.frame, width=300, height=300, bg="purple")
        self.canvas.grid()

        # Create the knob circle
        self.knob = self.canvas.create_oval(100, 100, 200, 200, fill="yellow")
        
        # Initialize knob properties
        self.angle = 0  # Initial angle in degrees
        self.value = 0  # Current value
        self.numbers = 10  # Number of divisions (adjust as needed)

        # Bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.start_rotation)
        self.canvas.bind("<B1-Motion>", self.rotate)
        self.canvas.bind("<ButtonRelease-1>", self.stop_rotation)

        # Draw numbers around the knob's circumference
        self.draw_numbers()

    def draw_numbers(self):
        knob_radius = 60  # Adjust the radius as needed
        center_x, center_y = 150, 150  # Center of the canvas
        angle_increment = 360 / self.numbers

        for i in range(self.numbers):
            angle_deg = i * angle_increment
            angle_rad = math.radians(angle_deg)
            x = center_x + knob_radius * math.cos(angle_rad)
            y = center_y + knob_radius * math.sin(angle_rad)

            # Display numbers around the knob
            self.canvas.create_text(x, y, text=str(i), font=("Helvetica", 10))

    def start_rotation(self, event):
        # Calculate initial angle based on mouse click position
        x, y = event.x, event.y
        center_x, center_y = 150, 150  # Center of the canvas
        self.angle = math.degrees(math.atan2(y - center_y, x - center_x))

    def rotate(self, event):
        # Calculate the change in angle and update the knob
        x, y = event.x, event.y
        center_x, center_y = 150, 150  # Center of the canvas
        new_angle = math.degrees(math.atan2(y - center_y, x - center_x))
        angle_change = new_angle - self.angle
        self.angle = new_angle

        self.canvas.delete(self.knob)
        self.knob = self.canvas.create_oval(100, 100, 200, 200, fill="yellow")
        self.canvas.create_arc(100, 100, 200, 200, start=0, extent=angle_change, fill="blue")
        self.value += angle_change
        print(f"Value: {self.value:.2f}")

    def stop_rotation(self, event):
        pass

class App(tk.Tk):
    def __init__(self, config_data):
        super().__init__()
        self.title("VIRTUAL-LAB")
        self.configure(bg="orange")
        self.widgets = {}

        try:
            with open(config_data, "r") as json_file:
                config_data = json.load(json_file)
        except FileNotFoundError:
            print("Error: JSON file not found.")
            return
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return
        if "widgets" not in config_data:
            print("Error: 'widgets' key is missing in the JSON configuration.")
            return
        else:
            self.create_widgets(config_data["widgets"])

        if "figure" in config_data and "axes" in config_data:
            self.fig, self.ax, self.line, self.canvas = self.create_real_time_graph(
                config_data["figure"],
                config_data["axes"]
            )
            self.animate_graph(self.fig, self.ax, self.line)

    def create_rotating_knob(self, widget_data):
        knob = RotatingKnobWithNumbers(self)
        knob.numbers = widget_data.get("numbers", 10)
        knob.frame.grid(row=widget_data["row"], column=widget_data["column"], padx=widget_data["padx"],
                        pady=widget_data["pady"])
        self.widgets[widget_data.get("name", "rotating_knob")] = knob

    def create_widgets(self, widgets):
        for widget_data in widgets:
            widget_type = widget_data["type"]
            if widget_type == "button":
                self.create_button(widget_data)
            elif widget_type == "CTkSwitch":
                self.create_switch(widget_data)
            elif widget_type == "radio_button":
                self.create_radio_button(widget_data)
            elif widget_type == "frame":
                self.create_frame(widget_data)
            elif widget_type == "checkbox":
                self.create_checkbox(widget_data)
            elif widget_type == "CTkProgressBar":
                self.create_ctk_progressbar(widget_data)
            elif widget_type == "CTkSlider":
                self.create_ctk_slider(widget_data)
            elif widget_type == "RotatingKnobWithNumbers":
                self.create_rotating_knob(widget_data)

    def create_button(self, data):
        button_font = ("bold", 13)
        button = tk.Button(
            self,
            text=data["text"],
            command=self.sidebar_button_event,
            bg=data.get("bg", "white"),
            fg=data.get("fg", "black"),
            width=20,
            height=2,
            font=button_font,
            borderwidth=5,
            relief="ridge"
        )
        button.grid(
            row=data["row"],
            column=data["column"],
            padx=data["padx"],
            pady=data["pady"]
        )

    def create_switch(self, data):
        switch = customtkinter.CTkSwitch(
            self,
            text=data["text"],
            font=("Helvetica", 15, "bold")
        )
        switch.grid(
            row=data["row"],
            column=data["column"],
            padx=data["padx"],
            pady=data["pady"],
        )

    def create_radio_button(self, data):
        radio_button = tk.Radiobutton(
            self,
            text=data["text"],
            variable=data["variable"],
            value=data["value"],
            padx=data["padx"],
            pady=data["pady"],
            borderwidth=5,
            bg="blue",
            fg="black"
        )
        radio_button.grid(
            row=data["row"],
            column=data["column"]
        )

    def create_frame(self, data):
        frame = tk.Frame(
            self,
            padx=data.get("padx", 0),
            pady=data.get("pady", 0),
            bg=data.get("bg", "white")
        )
        frame.grid(
            row=data["row"],
            column=data["column"],
            padx=data.get("padx", 0),
            pady=data.get("pady", 0)
        )
        self.create_widgets(data.get("children", []))

    def create_checkbox(self, data):
        checkbox = tk.Checkbutton(
            self,
            text=data["text"],
            variable=tk.IntVar(),
            font=("bold", 13)
        )
        checkbox.grid(
            row=data["row"],
            column=data["column"],
            padx=data["padx"],
            pady=data["pady"],
        )

    def create_ctk_progressbar(self, progressbar_data):
        progressbar = customtkinter.CTkProgressBar(
            self,
            bg_color=progressbar_data.get("bg_color", "green"),
            width=progressbar_data.get("width", 20),
            height=progressbar_data.get("height", None)
        )
        progressbar.grid(
            row=progressbar_data["row"],
            column=progressbar_data["column"],
            padx=progressbar_data["padx"],
            pady=progressbar_data["pady"],
            sticky=progressbar_data.get("sticky", "")
        )

    def create_ctk_slider(self, slider_data):
        slider = customtkinter.CTkSlider(
            self,
            from_=slider_data["from"],
            to=slider_data["to"],
            number_of_steps=slider_data["number_of_steps"]
        )
        slider.grid(
            row=slider_data["row"],
            column=slider_data["column"],
            padx=slider_data["padx"],
            pady=slider_data["pady"],
            sticky=slider_data.get("sticky", "")
        )

    def sidebar_button_event(self):
        print("sidebar_button click")

    def create_real_time_graph(self, fig_settings, axes_settings):
        fig = Figure(figsize=fig_settings["figsize"], dpi=fig_settings["dpi"])
        ax = fig.add_subplot(111)
        ax.set_xlim(axes_settings["xlim"])
        ax.set_ylim(axes_settings["ylim"])
        line, = ax.plot([], [], lw=2)
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.get_tk_widget().grid(row=1, column=3, rowspan=3)
        return fig, ax, line, canvas

    def update_graph(self, fig, ax, line):
        x = np.linspace(0, 10, 50)
        y = np.sin(x)
        line.set_data(x, y)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()

    def animate_graph(self, fig, ax, line):
        self.update_graph(fig, ax, line)
        self.after(100, self.animate_graph, fig, ax, line)

if __name__ == "__main__":
    config_file_path = "C:/Users/lenovo/OneDrive/Desktop/Duxes/config.json"
    app = App(config_file_path)
    app.mainloop()
