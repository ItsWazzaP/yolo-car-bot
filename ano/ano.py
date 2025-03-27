import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class YOLOAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLOv5 Annotation Tool")
        
        # Application state variables
        self.image_folder = ''
        self.image_list = []
        self.current_image_index = -1
        self.annotations = {}  # Stores annotations for all images
        self.current_boxes = []  # Bounding boxes for current image
        self.class_var = tk.StringVar(value='sundjer')  # Selected class
        
        # Initialize GUI components
        self.setup_gui()
        
        # Drawing variables
        self.start_x = None
        self.start_y = None
        self.current_rect = None

    def setup_gui(self):
        # Control frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Control buttons
        ttk.Button(control_frame, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Next", command=self.next_image).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Export Dataset", command=self.export_dataset).pack(side=tk.LEFT, padx=5)
        
        # Class selection
        class_combo = ttk.Combobox(control_frame, textvariable=self.class_var, values=['sundjer', 'marker'], state='readonly')
        class_combo.pack(side=tk.LEFT, padx=5)
        
        # Image canvas
        self.canvas = tk.Canvas(self.root, width=640, height=640)
        self.canvas.pack()
        
        # Status bar
        self.status = ttk.Label(self.root, text="Open a folder to start")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Mouse bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def open_folder(self):
        self.image_folder = filedialog.askdirectory(title="Select Image Folder")
        if not self.image_folder:
            return
        
        self.image_list = [f for f in os.listdir(self.image_folder) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not self.image_list:
            messagebox.showerror("Error", "No images found in folder")
            return
            
        self.image_list.sort()
        self.current_image_index = 0
        self.load_current_image()

    def load_current_image(self):
        filename = self.image_list[self.current_image_index]
        img_path = os.path.join(self.image_folder, filename)
        
        # Load and resize image
        img = Image.open(img_path).resize((640, 640))
        self.tk_img = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        
        # Load existing annotations
        self.current_boxes = []
        if filename in self.annotations:
            for ann in self.annotations[filename]:
                x1, y1, x2, y2 = self.from_yolo_format(
                    ann['x_center'], ann['y_center'], 
                    ann['width'], ann['height']
                )
                self.current_boxes.append({
                    'coords': (x1, y1, x2, y2),
                    'class_id': ann['class_id']
                })
                # Draw existing boxes
                self.canvas.create_rectangle(x1, y1, x2, y2, outline='red')
                self.canvas.create_text(x1, y1, 
                    text=['sundjer', 'marker'][ann['class_id']], 
                    fill='red', anchor=tk.NW)
        
        self.status.config(text=f"{self.current_image_index+1}/{len(self.image_list)}: {filename}")

    def save_current_annotations(self):
        if self.current_image_index < 0:
            return
        
        filename = self.image_list[self.current_image_index]
        yolo_annotations = []
        
        for box in self.current_boxes:
            x1, y1, x2, y2 = box['coords']
            xc, yc, w, h = self.to_yolo_format(x1, y1, x2, y2)
            yolo_annotations.append({
                'class_id': box['class_id'],
                'x_center': xc,
                'y_center': yc,
                'width': w,
                'height': h
            })
        
        self.annotations[filename] = yolo_annotations

    def prev_image(self):
        if self.current_image_index > 0:
            self.save_current_annotations()
            self.current_image_index -= 1
            self.load_current_image()

    def next_image(self):
        if self.current_image_index < len(self.image_list)-1:
            self.save_current_annotations()
            self.current_image_index += 1
            self.load_current_image()

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, 
            self.start_x, self.start_y, outline='red')

    def on_drag(self, event):
        if self.current_rect:
            self.canvas.coords(self.current_rect,
                self.start_x, self.start_y, 
                event.x, event.y)

    def on_release(self, event):
        # Get final coordinates
        x1 = min(max(0, self.start_x), max(0, event.x))
        x2 = max(min(639, self.start_x), min(639, event.x))
        y1 = min(max(0, self.start_y), max(0, event.y))
        y2 = max(min(639, self.start_y), min(639, event.y))
        
        # Ensure proper box dimensions
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])
        
        # Add to current boxes
        class_id = 0 if self.class_var.get() == 'sundjer' else 1
        self.current_boxes.append({
            'coords': (x1, y1, x2, y2),
            'class_id': class_id
        })
        
        # Draw permanent box and label
        self.canvas.create_rectangle(x1, y1, x2, y2, outline='red')
        self.canvas.create_text(x1, y1, 
            text=self.class_var.get(), 
            fill='red', anchor=tk.NW)
        
        self.current_rect = None

    def to_yolo_format(self, x1, y1, x2, y2):
        """Convert pixel coordinates to YOLO format"""
        return (
            (x1 + x2) / 2 / 640,
            (y1 + y2) / 2 / 640,
            (x2 - x1) / 640,
            (y2 - y1) / 640
        )

    def from_yolo_format(self, xc, yc, w, h):
        """Convert YOLO format to pixel coordinates"""
        xc *= 640
        yc *= 640
        w *= 640
        h *= 640
        return (
            xc - w/2,
            yc - h/2,
            xc + w/2,
            yc + h/2
        )

    def export_dataset(self):
        if not self.image_folder or not self.annotations:
            messagebox.showerror("Error", "No annotations to export")
            return
        
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
        
        # Create directory structure
        img_dir = os.path.join(export_dir, 'images', 'train')
        lbl_dir = os.path.join(export_dir, 'labels', 'train')
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(lbl_dir, exist_ok=True)
        
        # Process each annotated image
        for filename in self.annotations:
            # Process image
            img_path = os.path.join(self.image_folder, filename)
            try:
                img = Image.open(img_path).resize((640, 640))
                img.save(os.path.join(img_dir, filename))
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
            
            # Process annotations
            base_name = os.path.splitext(filename)[0]
            with open(os.path.join(lbl_dir, f"{base_name}.txt"), 'w') as f:
                for ann in self.annotations[filename]:
                    line = f"{ann['class_id']} {ann['x_center']:.6f} {ann['y_center']:.6f} {ann['width']:.6f} {ann['height']:.6f}\n"
                    f.write(line)
        
        # Create YAML file
        with open(os.path.join(export_dir, 'dataset.yaml'), 'w') as f:
            f.write(f"names:\n  0: sundjer\n  1: marker\nnc: 2\ntrain: {os.path.relpath(img_dir, export_dir)}\nval: {os.path.relpath(img_dir, export_dir)}\n")
        
        messagebox.showinfo("Success", f"Dataset exported to:\n{export_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOAnnotationApp(root)
    root.mainloop()