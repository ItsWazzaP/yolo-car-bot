import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
#import shutil

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

        # Ispravna putanja do labels/train (sada traži u istom root folderu)
        labels_dir = os.path.join(folder, "labels", "train")

        # Proveri da li labels folder postoji
        if not os.path.exists(labels_dir):
            messagebox.showwarning("Upozorenje", labels_dir)
            messagebox.showwarning("Upozorenje", "Nije pronađen labels/train folder!")
        
        # Učitaj slike
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
                                # Konvertuj sve vrednosti u float i proveri da li su u [0,1]
                                class_id = int(line[0])
                                x_center = max(0.0, min(1.0, float(line[1])))
                                y_center = max(0.0, min(1.0, float(line[2])))
                                width = max(0.0, min(1.0, float(line[3])))
                                height = max(0.0, min(1.0, float(line[4])))
                                
                                valid_annots.append({
                                    'class_id': class_id,
                                    'x_center': x_center,
                                    'y_center': y_center,
                                    'width': width,
                                    'height': height
                                })
                            except:
                                continue
                    
                    if valid_annots:
                        self.annotations[img_file] = valid_annots
        
        self.load_current_image()

    def from_yolo_format(self, xc, yc, w, h):
        """Konvertuj YOLO koordinate u apsolutne piksele (640x640)"""
        # Množimo sve sa 640 i zaokružujemo na cele brojeve
        xc_abs = round(xc * 640)
        yc_abs = round(yc * 640)
        w_abs = round(w * 640)
        h_abs = round(h * 640)
        
        return (
            max(0, xc_abs - w_abs // 2),      # x1
            max(0, yc_abs - h_abs // 2),      # y1
            min(639, xc_abs + w_abs // 2),    # x2 (ne sme preći 639)
            min(639, yc_abs + h_abs // 2)     # y2 (ne sme preći 639)
        )

    def load_current_image(self):
        filename = self.image_list[self.current_image_index]
        img_path = os.path.join(self.image_folder, filename)
        
        try:
            # Učitaj i prikaži sliku
            img = Image.open(img_path).resize((640, 640))
            self.tk_img = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
            
            # Iscrtaj anotacije ako postoje
            self.current_boxes = []
            if filename in self.annotations:
                for ann in self.annotations[filename]:
                    x1, y1, x2, y2 = self.from_yolo_format(
                        ann['x_center'], 
                        ann['y_center'], 
                        ann['width'], 
                        ann['height']
                    )
                    
                    # Dodaj bounding box
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, 
                        outline='red', 
                        width=2, 
                        tags="annotation"
                    )
                    
                    # Dodaj tekst
                    self.canvas.create_text(
                        x1 + 3, y1 + 3,
                        text=self.id_class_map.get(ann['class_id'], '?'),
                        fill='red',
                        anchor=tk.NW,
                        font=('Arial', 10, 'bold'),
                        tags="annotation"
                    )
                    
                    # Sačuvaj za editovanje
                    self.current_boxes.append({
                        'coords': (x1, y1, x2, y2),
                        'class_id': ann['class_id']
                    })
            
            # Statusna traka
            self.status.config(
                text=f"Slika {self.current_image_index + 1}/{len(self.image_list)} | "
                     f"Anotacije: {len(self.current_boxes)} | "
                     f"Trenutna: {filename}"
            )
        except Exception as e:
            messagebox.showerror("Greška", f"Greška pri učitavanju: {str(e)}")

    def prev_image(self):
        if self.current_image_index > 0:
            self.save_current_annotations()
            self.current_image_index -= 1
            self.load_current_image()

    def next_image(self):
        if self.current_image_index < len(self.image_list) - 1:
            self.save_current_annotations()
            self.current_image_index += 1
            self.load_current_image()

    def clear_annotations(self):
        if self.current_image_index < 0:
            return
        
        filename = self.image_list[self.current_image_index]
        if filename in self.annotations:
            del self.annotations[filename]
        self.current_boxes = []
        self.load_current_image()
        messagebox.showinfo("Obrisano", f"Anotacije za sliku {filename} su obrisane.")

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
        class_id = self.class_id_map[self.class_var.get()]
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
            messagebox.showerror("Greška", "Nema anotacija za eksport!")
            return
        
        export_dir = filedialog.askdirectory(title="Izaberite folder za eksport")
        if not export_dir:
            return
        
        # Kreiraj strukturu foldera
        img_dir = os.path.join(export_dir, 'images', 'train')
        lbl_dir = os.path.join(export_dir, 'labels', 'train')
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(lbl_dir, exist_ok=True)
        
        # Procesuiraj svaku anotiranu sliku
        for filename in self.annotations:
            # Procesuiraj sliku
            img_path = os.path.join(self.image_folder, filename)
            try:
                # Otvaranje slike
                img = Image.open(img_path)

                # Provjera mode slike
                if img.mode != 'RGB':
                    # Konvertuj u RGB ako slika nije već u RGB mode
                    rgb_img = img.convert('RGB')
                    rgb_img.save(os.path.join(img_dir, filename))
                else:
                    # Ako je slika već u RGB mode, samo je spremi
                    img.save(os.path.join(img_dir, filename))

            except Exception as e:
                print(f"Greška pri kopiranju {filename}: {str(e)}")
                continue
            
            # Procesuiraj anotacije
            base_name = os.path.splitext(filename)[0]
            with open(os.path.join(lbl_dir, f"{base_name}.txt"), 'w') as f:
                for ann in self.annotations[filename]:
                    line = f"{ann['class_id']} {ann['x_center']:.6f} {ann['y_center']:.6f} {ann['width']:.6f} {ann['height']:.6f}\n"
                    f.write(line)
        
        # Kreiraj YAML fajl
        with open(os.path.join(export_dir, 'dataset.yaml'), 'w') as f:
            f.write(f"names:\n  0: person\n  80: sundjer\nnc: 2\ntrain: {os.path.relpath(img_dir, export_dir)}\nval: {os.path.relpath(img_dir, export_dir)}\n")
        
        messagebox.showinfo("Uspeh", f"Dataset uspešno eksportovan u:\n{export_dir}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOAnnotationApp(root)
    root.mainloop()
