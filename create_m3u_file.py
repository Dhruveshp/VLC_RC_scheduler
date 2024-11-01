import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_m3u(directory, output_file_name):
    output_file= output_file_name+'.m3u'
    with open(output_file, 'w') as f:
        # Write the M3U header
        f.write('#EXTM3U\n')

        # Iterate through all files in the given directory
        for filename in os.listdir(directory):
            if filename.endswith('.mp3') or filename.endswith('.mp4'):  # Adjust as needed for other formats
                file_path = os.path.join(directory, filename)
                f.write(f'#EXTINF:-1,{filename}\n')  # Use the filename as title
                f.write(f'{file_path}\n')

    logging.info(f'M3U playlist created: {output_file}')  # Log the message
    return os.path.abspath(output_file)  # Return the absolute path of the created file

