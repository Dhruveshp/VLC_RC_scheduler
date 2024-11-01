import os

def create_m3u(directory, output_file='playlist.m3u'):
    with open(output_file, 'w') as f:
        # Write the M3U header
        f.write('#EXTM3U\n')

        # Iterate through all files in the given directory
        for filename in os.listdir(directory):
            if filename.endswith('.mp3') or filename.endswith('.mp4'):  # Adjust as needed for other formats
                file_path = os.path.join(directory, filename)
                f.write(f'#EXTINF:-1,{filename}\n')  # Use the filename as title
                f.write(f'{file_path}\n')

    print(f'M3U playlist created: {output_file}')

# Example usage:
if __name__ == "__main__":
    path = r"C:\Users\admin\OneDrive - DePaul University\OOP\Desktop(1)\mp3\08. Thal Manasi"
    create_m3u(path)
