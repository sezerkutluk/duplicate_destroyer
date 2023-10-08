import os
import pathlib
from filecmp import cmp, clear_cache

folder_1 = "/users/skutluk/desktop/folder 1"
folder_2 = "/users/skutluk/desktop/folder 2"

files_1 = set()
files_2 = set()
diff = []

for root, dirs, files in os.walk(folder_1):
    for file in files:
        file_path = os.path.join(root, file)
        p = file_path.removeprefix(folder_1 + "/")
        if p not in files_1:
            files_1.add(p)
        else:
            print("ITEM NOT UNIQUE!")

for root, dirs, files in os.walk(folder_2):
    for file in files:
        file_path = os.path.join(root, file)
        p = file_path.removeprefix(folder_2 + "/")
        if p not in files_2:
            files_2.add(p)
        else:
            print("ITEM NOT UNIQUE!")

for file in files_1.copy():
    if file in files_2:
        clear_cache()
        check = cmp(os.path.join(folder_1, file), os.path.join(folder_2, file), shallow=False)
        if check is True:
            files_1.remove(file)
            files_2.remove(file)
        else:
            diff.append("Files are different: " + os.path.join(folder_1, file) + " and " + os.path.join(folder_2, file))
    else:
        diff.append(("Only in " + folder_1 + ": " + os.path.join(folder_1, file)))

for file in files_2:
    if file in files_1:
        print("SOMETHING WEIRD HAPPENED")
    else:
        diff.append(("Only in " + folder_2 + ": " + os.path.join(folder_2, file)))

print(*diff, sep = "\n")