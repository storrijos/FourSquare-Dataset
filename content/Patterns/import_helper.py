def processing_import_helper():
    # Import
    import os
    import sys
    curent_file_abs_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(curent_file_abs_path) + "/../../Processing"
    carpeta2_abs_path = os.path.abspath(current_dir)
    sys.path.insert(0, carpeta2_abs_path)
