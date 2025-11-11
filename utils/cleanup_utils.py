import os

def cleanup_file(path: str):
    if os.path.exists(path):
        os.remove(path)


def cleanup_temp_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

if __name__ == "__main__":
    # Example usage
    temp_file_path = "./documents/ebook_final_cover.png"
    # Create a temporary file for demonstration
    # with open(temp_file_path, "w") as f:
    #     f.write("This is a temporary file.")
    
    print(f"Created temporary file at: {temp_file_path}")
    
    # Cleanup the temporary file
    cleanup_file(temp_file_path)
    print(f"Cleaned up temporary file at: {temp_file_path}")