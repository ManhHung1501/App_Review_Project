import os

def get_project_directory() -> str:
    current_file_path = os.path.abspath(__file__)
    current_directory = os.path.dirname(current_file_path)
    return os.path.dirname(current_directory)
