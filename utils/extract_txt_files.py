import os
import shutil

def extract_txt_files():
    # Define source and destination paths
    source_dir = "test_files/legal docs"
    dest_dir = "test_files/txt files"

    # Create the destination directory if it doesn't exist
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created directory: {dest_dir}")

    # Loop through folders numbered 1 to 46
    # range(1, 47) includes 1 but stops before 47
    for i in range(1, 47):
        current_folder_path = os.path.join(source_dir, str(i))
        
        # Check if this specific numbered folder actually exists
        if os.path.exists(current_folder_path):
            
            # Counter for the 'x' in '1_x', '2_x', etc.
            file_counter = 1
            
            # Loop through all files in the current numbered folder
            for filename in os.listdir(current_folder_path):
                
                # Check if the file is a .txt file
                if filename.lower().endswith(".txt"):
                    
                    # Construct the old file path
                    old_file_path = os.path.join(current_folder_path, filename)
                    
                    # Construct the new filename (e.g., "1_1.txt", "1_2.txt")
                    new_filename = f"{i}_{file_counter}.txt"
                    new_file_path = os.path.join(dest_dir, new_filename)
                    
                    # Copy the file to the new destination
                    # We use copy2 to preserve file metadata (timestamps, etc.)
                    shutil.copy2(old_file_path, new_file_path)
                    
                    print(f"Copied: {old_file_path} -> {new_file_path}")
                    
                    # Increment counter for the next txt file in this folder
                    file_counter += 1
        else:
            print(f"Folder {i} not found in '{source_dir}', skipping...")

if __name__ == "__main__":
    extract_txt_files()
    print("Extraction complete.")