import json
import socket
import subprocess
import glob
import os
import random
from datetime import datetime
import time
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Schedule model
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    play_music_folder = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)  # HH:MM format
    end_time = db.Column(db.String(20), nullable=True)  # HH:MM:SS format
    days = db.Column(db.String(50), nullable=False)  # Comma-separated days

# Create the database and the schedule table if it doesn't exist
if not os.path.exists('schedules.db'):
    db.create_all()
    logging.info("Database created and table initialized.")

class VLCController:
    def __init__(self, host='127.0.0.1', port=44500):
        self.host = host
        self.port = port
        self.sock = None
        self.vlc_process = None
        self.is_playing = False  # Track playback status

    def is_vlc_running(self):
        """Check if VLC is already running."""
        return self.vlc_process is not None and self.vlc_process.poll() is None

    def start_vlc(self, media_path=None):
        if self.is_vlc_running():
            logging.warning("VLC is already running.")
            return

        vlc_command = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            "--intf", "rc",
            "--rc-host", f"{self.host}:{self.port}"
        ]
        if media_path:
            vlc_command.append(media_path)
        
        self.vlc_process = subprocess.Popen(vlc_command)
        logging.info("VLC started with RC interface.")
        time.sleep(2)  # Increased delay to ensure VLC is ready to receive commands

        self.connect()

    def connect(self):
        """Establish a connection to the VLC RC interface."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logging.info(f"Connected to VLC on {self.host}:{self.port}")
        except Exception as e:
            logging.error(f"Error connecting to VLC: {e}")

    def send_command(self, command):
        """Send a command to VLC."""
        if self.sock:
            try:
                self.sock.sendall(bytes(command + '\n', "utf-8"))
                logging.info(f"Sent command: {command}")
            except Exception as e:
                logging.error(f"Error sending command: {e}")

    def close(self):
        """Close the connection to VLC and terminate the VLC process."""
        if self.sock:
            self.sock.close()
            logging.info("Connection to VLC closed.")
        if self.vlc_process:
            self.vlc_process.terminate()
            self.vlc_process = None
            logging.info("VLC process terminated.")

    def play(self):
        """Play the currently loaded media."""
        if not self.is_playing:
            self.send_command("play")
            self.is_playing = True  # Set playing status

    def stop(self):
        """Stop playback of the current media."""
        self.send_command("stop")
        self.is_playing = False  # Reset playing status

    def add_to_playlist(self, media_path):
        """Add media to the VLC playlist."""
        self.send_command(f"add {media_path}")

    def set_volume(self, volume):
        """Set the volume to a specific level."""
        if 0 <= volume <= 100:
            self.send_command(f"volume {volume}")
        else:
            logging.error("Volume must be between 0 and 100.")

def normalize_path(path):
    """Normalize the path to use the correct separators."""
    return os.path.normpath(path)

def play_music(music_folder):
    """Select and play a random music file from the specified folder."""
    music_folder = normalize_path(music_folder)
    music_files = [f for f in glob.glob(os.path.join(music_folder, '*')) if f.endswith(('.mp3', '.wav'))]

    if not music_files:
        logging.warning(f"No music files found in {music_folder}")
        return

    music_to_play = random.choice(music_files)
    logging.info(f"Now playing: {music_to_play}")

    if not os.path.isfile(music_to_play):
        logging.error(f"File does not exist: {music_to_play}")
        return

    if not vlc.is_vlc_running():
        vlc.start_vlc(media_path=music_to_play)
    else:
        vlc.add_to_playlist(music_to_play)

    time.sleep(2)  # Wait for VLC to get ready

    if vlc.sock:
        try:
            vlc.play()
            vlc.set_volume(100)
            logging.info("Playback started successfully.")
        except Exception as e:
            logging.error(f"Error during playback: {e}")
    else:
        logging.error("VLC is not connected. Cannot send play command.")

def stop_music():
    """Stop the music playback."""
    vlc.stop()
    logging.info("Music playback stopped.")

def convert_days_to_ap_scheduler_format(days):
    """Convert day names to APScheduler format."""
    day_map = {
        "Monday": "mon",
        "Tuesday": "tue",
        "Wednesday": "wed",
        "Thursday": "thu",
        "Friday": "fri",
        "Saturday": "sat",
        "Sunday": "sun"
    }
    converted_days = [day_map[day] for day in days if day in day_map]
    
    if not converted_days:
        logging.warning(f"No valid days found for input: {days}")
        
    return converted_days

def load_schedules_from_db():
    """Load schedules from the database."""
    schedules = Schedule.query.all()
    return [
        {
            'play_music_folder': schedule.play_music_folder,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time.split('.')[0] if schedule.end_time else None,  # Remove microseconds
            'days': schedule.days.split(',')  # Convert to a list of days
        }
        for schedule in schedules
    ]

def schedule_music(job):
    """Schedule music playback based on the provided job details."""
    current_day = datetime.now().strftime("%A")
    logging.info(f"Current day: {current_day}")

    if current_day in job['days']:
        logging.info(f"Scheduling music for {current_day}")
        play_music(job['play_music_folder'])
        
        if job['end_time']:
            # Parse end_time correctly
            end_time_str = job['end_time'].split('.')[0]  # Take only 'HH:MM:SS'
            end_time = datetime.strptime(end_time_str, '%H:%M:%S').time()
            current_time = datetime.now().time()
            
            if current_time < end_time:
                days_for_scheduler = convert_days_to_ap_scheduler_format(job['days'])
                if days_for_scheduler:
                    scheduler.add_job(stop_music, 'cron', 
                                      day_of_week=','.join(days_for_scheduler), 
                                      hour=end_time.hour, 
                                      minute=end_time.minute,
                                      id=f"stop_{job['start_time']}_{'_'.join(job['days'])}")
                else:
                    logging.warning("No valid days to schedule stop_music job.")

def main():
    global vlc, scheduler
    vlc = VLCController()
    
    # Start VLC without a media file for initial setup
    vlc.start_vlc()

    scheduler = BackgroundScheduler()
    
    # Load schedules from the database
    schedule_data = load_schedules_from_db()

    for job in schedule_data:
        # Normalize the music folder path from the job
        job['play_music_folder'] = normalize_path(job['play_music_folder'])

        days_for_scheduler = convert_days_to_ap_scheduler_format(job['days'])
        if days_for_scheduler:  # Ensure that this is not empty
            job_id = f"{job['start_time']}_{'_'.join(job['days'])}"  # Create a unique ID based on time and days
            scheduler.add_job(schedule_music, 'cron', 
                              day_of_week=','.join(days_for_scheduler), 
                              hour=int(job['start_time'].split(':')[0]), 
                              minute=int(job['start_time'].split(':')[1]),
                              args=[job],
                              id=job_id)  # Use the generated ID
        else:
            logging.warning(f"No valid days for scheduling job: {job}")

    scheduler.start()

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        vlc.close()

if __name__ == "__main__":
    main()
