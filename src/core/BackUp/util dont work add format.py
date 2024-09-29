import os


class ImageManager:
    """back Path Lib 
        to save at BASE_DIR where is file running start run.
    """
    def __init__(self, folder="./edits"):
    # def __init__(self, folder="edits/"):
        self.folder = folder
        self.filename = None
        self.fullname = None
        self.im_map = {}

        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        print("fullpath to folder: ", self.folder)

    def save(self, name: str, im, output_dir=None, format=None):
        # Fall back to the default folder
        output_dir = output_dir or self.folder

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if format is not None:
            im.save(f"{output_dir}/{name}.{format}")
        else:
            im.save(f"{output_dir}/{name}")

        self.filename = f"{name}.{format}"
        self.fullname = os.path.join(self.folder, self.filename)
        self.im_map[name] = im  # Store image reference in the dictionary

    def remove(self, name: str, output_dir=None, format=None):
        output_dir = output_dir or self.folder
        if format is not None:
            file_path = f"{output_dir}/{name}.{format}"
        else:
            file_path = f"{output_dir}/{name}"
        try:
            os.remove(file_path)
            if name in self.im_map:
                del self.im_map[name]
        except FileNotFoundError:
            raise Exception(
                f"File {name}.{format} not found. Check to correct name.")

    def rename(self, name, other, output_dir=None, format=None):
        output_dir = output_dir or self.folder
        if format is not None:
            name_path = os.path.join(output_dir, f"{name}.{format}")
            other_path = os.path.join(output_dir, f"{other}.{format}")
        else:
            name_path = os.path.join(output_dir, f"{name}")
            other_path = os.path.join(output_dir, f"{other}")
        try:
            os.rename(name_path, other_path)
            self.im_map[other] = self.im_map.pop(
                name)  # Update key in the dictionary
        except FileNotFoundError:
            raise Exception(
                f"File {name}.{format} not found. Check to correct name.")
        except FileExistsError:
            raise Exception(
                f"File {other}.{format} already exists. Change to another name.")


def filter_files_by_extensions(files, extensions):
    """Utils to func getWorkDirectory"""
    return [file for file in files if any(file.lower().endswith(ext) for ext in extensions)]
