import os
import socket
import sys
import time

def play_audio_files(directory, host='127.0.0.1', port=4212):
    # Supported audio file extensions
    audio_extensions = ('.mp3', '.wav', '.ogg', '.flac')
    
    # Create a socket connection to VLC RC interface
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        # List all files in the directory and send play commands
        for filename in os.listdir(directory):
            if filename.endswith(audio_extensions):
                file_path = os.path.join(directory, filename)
                print(f"Playing: {file_path}")

                # Send command to VLC to play the file
                s.sendall(f'add {file_path}\n'.encode('utf-8'))
                time.sleep(1)  # Wait for a moment before playing the next file
            else:
                print(f"Skipped: {filename}")

        # Start playing the playlist
        s.sendall(b'play\n')

if __name__ == "__main__":
    # Check if the user provided a path
    directory_path = r'C:\Users\admin\OneDrive - DePaul University\OOP\Desktop(1)\mp3\08. Thal Manasi'
    
    # Check if the provided path is a directory
    if not os.path.isdir(directory_path):
        print("The provided path is not a valid directory.")
        sys.exit(1)

    # Play audio files in the directory
    play_audio_files(directory_path)
