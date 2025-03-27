import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class YOLOAnnotationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLOv5 Annotation Tool")
        self.root.geometry("800x800")  # Fiksna veličina prozora
        
        # State variables
        self.image_folder = ''
        self.image_list = []
        self.current_image_index = -1
        self.annotations = {}
        self.current_boxes = []
        self.class_id_map = {'person': 0, 'sundjer': 80}
        self.id_class_map = {v: k for k, v in self.class_id_map.items()}
        
        # GUI setup
        self.class_var = tk.StringVar(value='sundjer')
        self.setup_gui()
        
        # Drawing variables
        self.start_x = None
        self.start_y = None
        self.current_rect = None

    def setup_gui(self):
        # Kontrolni frame
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Kontrolni elementi
        ttk.Button(control_frame, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Previous", command=self.prev_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Next", command=self.next_image).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Clear", command=self.clear_annotations).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export", command=self.export_dataset).pack(side=tk.LEFT)
        
        # Odabir klase
        class_combo = ttk.Combobox(control_frame, textvariable=self.class_var, 
                                  values=['person', 'sundjer'], state='readonly')
        class_combo.pack(side=tk.LEFT, padx=10)
        
        # Canvas za sliku
        self.canvas = tk.Canvas(self.root, width=640, height=640, bg='gray')
        self.canvas.pack(pady=10)
        
        # Statusna traka
        self.status = ttk.Label(self.root, text="Status: Nije učitan folder")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # Event bindings
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def open_folder(self):
        folder = filedialog.askdirectory(title="Izaberite folder sa slikama")
        if not folder:
            return
            
        # Provera strukture foldera
        base_dir = os.path.dirname(folder)
        labels_dir = os.path.join(base_dir, 'labels', 'train')
        
        self.image_list = [
            f for f in os.listdir(folder) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
        
        if not self.image_list:
            messagebox.showerror("Greška", "Nema slika u folderu!")
            return
            
        self.image_list.sort()
        self.image_folder = folder
        self.current_image_index = 0
        
        # Učitaj postojeće anotacije
        self.annotations = {}
        if os.path.exists(labels_dir):
            for img_file in self.image_list:
                base_name = os.path.splitext(img_file)[0]
                txt_file = os.path.join(labels_dir, f"{base_name}.txt")
                
                if os.path.exists(txt_file):
                    with open(txt_file, 'r') as f:
                        lines = [line.strip().split() for line in f.readlines()]
                    
                    valid_annots = []
                    for line in lines:
                        if len(line) == 5:
                            try:
                                ann = {
                                    'class_id': int(line[0]),
                                    'x_center': float(line[1]),
                                    'y_center': float(line[2]),
                                    'width': float(line[3]),
                                    'height': float(line[4])
                                }
                                valid_annots.append(ann)
                            except:
                                continue
                    
                    if valid_annots:
                        self.annotations[img_file] = valid_annots
        
        self.load_current_image()

    def load_current_image(self):
        filename = self.image_list[self.current_image_index]
        img_path = os.path.join(self.image_folder, filename)
        
        try:
            img = Image.open(img_path).resize((640, 640))
            self.tk_img = ImageTk.PhotoImage(img)
            
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
            
            # Prikaz statusa
            self.status.config(
                text=f"Slika {self.current_image_index+1}/{len(self.image_list)} | "
                     f"Anotacije: {len(self.annotations.get(filename, []))} | "
                     f"Trenutna: {filename}"
            )
            
            # Učitaj anotacije za trenutnu sliku
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
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline='red')
                    self.canvas.create_text(
                        x1+2, y1+2, 
                        text=self.id_class_map.get(ann['class_id'], '?'), 
                        fill='red', anchor=tk.NW, font=('Arial', 10, 'bold')
                    )
                    
        except Exception as e:
            messagebox.showerror("Greška", f"Ne mogu učitati sliku: {str(e)}")

    # Ostale metode (save_current_annotations, prev_image, next_image, 
    # on_press, on_drag, on_release, to_yolo_format, from_yolo_format 
    # export_dataset, clear_annotations) ostaju identične kao u prethodnoj verziji

if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOAnnotationApp(root)
    root.mainloop()
