import os
from PIL import Image, ImageFilter, ImageEnhance


class ImageManager:
    def __init__(self, folder="./img"):
        self.folder = folder
        self.im_map = {}

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def save(self, name: str, im, output_dir=None, format="png"):
        # fall back to the default folder
        output_dir = output_dir or self.folder

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        im.save(f"{output_dir}/{name}.{format}")

        self.im_map[name] = im  # Store im ref it dict > / log.txt

    def remove(self, name: str, output_dir=None, format="png"):
        output_dir = output_dir or self.folder
        file_path = f"{output_dir}/{name}.{format}"
        try:
            os.remove(file_path)
            if name in self.im_map:
                # remove from dict > / log.txt as well before close save >> to log.txt
                del self.im_map[name]
            # logger(Image <name>.<format> removed.)
        except FileNotFoundError:
            raise Exception(
                f"File {name}.png not found \nCheck to correct name.")

    def rename(self, name, other, output_dir=None, format="png"):
        output_dir = output_dir or self.folder
        name_path = os.path.join(output_dir, f"{name}.{format}")
        other_path = os.path.join(output_dir, f"{other}.{format}")
        try:
            os.rename(name_path, other_path)
            self.im_map[other] = self.im_map.pop(name)  # Update key
        except FileNotFoundError:
            raise Exception(
                f"File {name}.png not found \nCheck to correct name.")
        except FileExistsError:
            raise Exception(
                f"File {other}.png already exists. \nChange to another name.")
        output_dir = output_dir or self.folder
        name_path = os.path.join(output_dir, f"{name}.{format}")
        other_path = os.path.join(output_dir, f"{other}.{format}")
        try:
            os.rename(name_path, other_path)
            self.im_map[other] = self.im_map.pop(name)  # Update key
        except FileNotFoundError:
            raise Exception(
                f"File {name}.png not found \nCheck to correct name.")
        except FileExistsError:
            raise Exception(
                f"File {other}.png already exists. \nChange to another name.")


class imageEditor:
    def __init__(self, folder="./edit/"):
        self.im = None
        self.original_im = None
        self.folder = folder

        if not os.path.exists(self.folder) or not os.path.isdir(self.folder):
            os.mkdir(self.folder)

    # Key methods
    def func(self):
        ...
    
    # Editor Methods
    def other(self):
        ...

    # Event Handling Methods
    def handler(self):
        ...



def mapping_func():
    """parsing all func names dinamically n filter at no needable or if has very many filter by images_functionality
        filtering by type by isistance to get func var only for Image.Image;
        yield cuz more memory-efficient way
    """
    for name, obj in globals().items():
        if isinstance(obj, Image.Image) and name not in 'im func'.split():
            yield name, obj


# for name, func in mapping_func():
#     remove(name)

# for name in new_names:
#     im_manager.remove(name)

# for k, v in im_manager.im_map.items():
#     print(k, v)
