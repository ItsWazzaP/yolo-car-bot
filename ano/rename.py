import os

# Putanje do foldera sa slikama i anotacijama
images_dir = "/projects/ano/sponge/images/train"
labels_dir = "/projects/ano/sponge/labels/train"

# Dobijanje i sortiranje imena fajlova
image_files = sorted([f for f in os.listdir(images_dir) if f.endswith('.jpg')])
label_files = sorted([f for f in os.listdir(labels_dir) if f.endswith('.txt')])

# Provera da li broj slika i anotacija odgovara
if len(image_files) != len(label_files):
    print("Upozorenje: Broj slika i anotacija se ne poklapa!")

# Preimenovanje fajlova
for i, (img, lbl) in enumerate(zip(image_files, label_files), start=1):
    new_name = f"s_{i:07d}"
    
    # Stare i nove putanje
    old_img_path = os.path.join(images_dir, img)
    old_lbl_path = os.path.join(labels_dir, lbl)
    new_img_path = os.path.join(images_dir, f"{new_name}.jpg")
    new_lbl_path = os.path.join(labels_dir, f"{new_name}.txt")
    
    # Preimenovanje
    os.rename(old_img_path, new_img_path)
    os.rename(old_lbl_path, new_lbl_path)
    
    print(f"Preimenovano: {img} -> {new_name}.jpg, {lbl} -> {new_name}.txt")

print("Preimenovanje završeno!")
