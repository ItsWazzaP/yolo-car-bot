import os

# Putanje do foldera sa slikama i anotacijama
images_dir = "/projects/ano/sponge/images/train"
labels_dir = "/projects/ano/sponge/labels/train"

# Ekstrakcija imena fajlova (bez ekstenzije)
image_files = {os.path.splitext(f)[0] for f in os.listdir(images_dir) if f.endswith('.jpg')}
label_files = {os.path.splitext(f)[0] for f in os.listdir(labels_dir) if f.endswith('.txt')}

# Pronalazak anotacija koje nemaju odgovarajuću sliku
extra_labels = label_files - image_files

if extra_labels:
    print("Anotacije bez pripadajuće slike:")
    for label in extra_labels:
        print(f"{label}.txt")
else:
    print("Sve anotacije imaju odgovarajuće slike.")
