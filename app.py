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

<<<<<<< Updated upstream
# Initialize the database
=======
# Database initialization at app startup
>>>>>>> Stashed changes
with app.app_context():
    if not os.path.exists('schedules.db'):
        db.create_all()
        logging.info("Database created and table initialized.")

class VLCController:
    """Controller to manage VLC operations through socket-based RC interface."""

    def __init__(self, host='127.0.0.1', port=44500):
        """Initialize VLC controller with host and port for RC interface."""
        self.host = host
        self.port = port
        self.sock = None
        self.vlc_process = None
        self.is_playing = False

    def is_vlc_running(self):
        """Check if VLC process is running."""
        return self.vlc_process is not None and self.vlc_process.poll() is None

    def start_vlc(self, media_path=None):
        """Start VLC process and connect to the RC interface."""
        try:
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
            time.sleep(2)
            self.connect()
        except Exception as e:
            logging.error(f"Error starting VLC: {e}")
            self.close()

    def connect(self):
        """Establish a socket connection to VLC's RC interface."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logging.info(f"Connected to VLC on {self.host}:{self.port}")
        except Exception as e:
            logging.error(f"Error connecting to VLC: {e}")
            self.close()

    def send_command(self, command):
        """Send a command string to VLC over the socket connection."""
        if self.sock:
            try:
                self.sock.sendall(bytes(command + '\n', "utf-8"))
                logging.info(f"Sent command: {command}")
            except Exception as e:
                logging.error(f"Error sending command: {e}")
                self.close()

    def close(self):
        """Close the socket and terminate the VLC process if running."""
        if self.sock:
            self.sock.close()
            logging.info("Connection to VLC closed.")
        if self.vlc_process:
            self.vlc_process.terminate()
            self.vlc_process = None
            logging.info("VLC process terminated.")

    def play(self):
<<<<<<< Updated upstream
        """Send play command to VLC if media is loaded."""
        try:
            if not self.is_playing:
                self.send_command("play")
                self.is_playing = True
        except Exception as e:
            logging.error(f"Error playing media: {e}")
            self.close()

    def stop(self):
        """Send stop command to VLC to pause media playback."""
        try:
            self.send_command("stop")
            self.is_playing = False
        except Exception as e:
            logging.error(f"Error stopping media: {e}")
            self.close()
=======
        """Play the currently loaded media."""
        if not self.is_playing:
            self.send_command("play")
            self.is_playing = True

    def stop(self):
        """Stop playback of the current media."""
        self.send_command("stop")
        self.is_playing = False
>>>>>>> Stashed changes

    def add_to_playlist(self, media_path):
        """Add a media file to VLC's playlist."""
        try:
            self.send_command(f"add {media_path}")
        except Exception as e:
            logging.error(f"Error adding media to playlist: {e}")
            self.close()

    def set_volume(self, volume):
        """Set VLC playback volume (0 to 100)."""
        try:
            if 0 <= volume <= 100:
                self.send_command(f"volume {volume}")
            else:
                logging.error("Volume must be between 0 and 100.")
        except Exception as e:
            logging.error(f"Error setting volume: {e}")
            self.close()

def normalize_path(path):
    """Convert path to a normalized format for the current OS."""
    return os.path.normpath(path)

def play_music(music_folder):
    """Play a random music file from a specified folder using VLC."""
    try:
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

<<<<<<< Updated upstream
        time.sleep(2)
        if vlc.sock:
=======
    time.sleep(2)

    if vlc.sock:
        try:
>>>>>>> Stashed changes
            vlc.play()
            vlc.set_volume(100)
    except Exception as e:
        logging.error(f"Error in play_music function: {e}")
        vlc.close()

def stop_music():
    """Stop the currently playing music in VLC."""
    try:
        vlc.stop()
    except Exception as e:
        logging.error(f"Error in stop_music function: {e}")
        vlc.close()

def convert_days_to_ap_scheduler_format(days):
    """Convert a list of day names to APScheduler-compatible format."""
    day_map = {
        "Monday": "mon",
        "Tuesday": "tue",
        "Wednesday": "wed",
        "Thursday": "thu",
        "Friday": "fri",
        "Saturday": "sat",
        "Sunday": "sun"
    }
    try:
        converted_days = [day_map[day] for day in days if day in day_map]
        return converted_days
    except Exception as e:
        logging.error(f"Error converting days: {e}")
        vlc.close()
        return []

def load_schedules_from_db():
<<<<<<< Updated upstream
    """Load schedule entries from the database."""
    try:
        with app.app_context():
            schedules = Schedule.query.all()
            return [
                {
                    'play_music_folder': schedule.play_music_folder,
                    'start_time': schedule.start_time,
                    'end_time': schedule.end_time.split('.')[0] if schedule.end_time else None,
                    'days': schedule.days.split(',')
                }
                for schedule in schedules
            ]
    except Exception as e:
        logging.error(f"Error loading schedules from database: {e}")
        vlc.close()
        return []

def schedule_music(job):
    """Play music based on schedule job details, and set a stop time if applicable."""
    current_day = datetime.now().strftime("%A")
    try:
        if current_day in job['days']:
            play_music(job['play_music_folder'])

        if job['end_time']:
            end_time = datetime.strptime(job['end_time'], '%H:%M:%S').time()
            current_time = datetime.now().time()
            if current_time < end_time:
                days_for_scheduler = convert_days_to_ap_scheduler_format(job['days'])
                if days_for_scheduler:
                    stop_id = f"stop_{job['start_time']}_{'_'.join(job['days'])}_{random.randint(1000, 9999)}"
                    scheduler.add_job(
                        stop_music, 'cron', 
                        day_of_week=','.join(days_for_scheduler), 
                        hour=end_time.hour, 
                        minute=end_time.minute, 
                        id=stop_id
                    )
    except Exception as e:
        logging.error(f"Error scheduling music: {e}")
        vlc.close()
=======
    """Load schedules from the database with app context."""
    with app.app_context():
        schedules = Schedule.query.all()
        return [
            {
                'play_music_folder': schedule.play_music_folder,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time.split('.')[0] if schedule.end_time else None,
                'days': schedule.days.split(',')
            }
            for schedule in schedules
        ]

def schedule_music(job):
    """Play music if the current day matches the job's specified days."""
    current_day = datetime.now().strftime("%A")
    if current_day in job['days']:
        try:
            logging.info(f"Playing scheduled music for {current_day}")
            play_music(job['play_music_folder'])
        except Exception as e:
            logging.error(f"Failed to schedule music: {e}")

    if job['end_time']:
        end_time = datetime.strptime(job['end_time'], '%H:%M:%S').time()
        current_time = datetime.now().time()
        if current_time < end_time:
            days_for_scheduler = convert_days_to_ap_scheduler_format(job['days'])
            if days_for_scheduler:
                stop_id = f"stop_{job['start_time']}_{'_'.join(job['days'])}_{random.randint(1000, 9999)}"
                scheduler.add_job(
                    stop_music, 'cron', 
                    day_of_week=','.join(days_for_scheduler), 
                    hour=end_time.hour, 
                    minute=end_time.minute, 
                    id=stop_id
                )
>>>>>>> Stashed changes

def main():
    """Main function to initialize VLC controller, load schedules, and start scheduler."""
    global vlc, scheduler
    vlc = VLCController()
    scheduler = BackgroundScheduler()
<<<<<<< Updated upstream

    try:
        vlc.start_vlc()
    except Exception as e:
        logging.error(f"Failed to start VLC: {e}")
        return

    try:
        with app.app_context():
            schedule_data = load_schedules_from_db()

        for job in schedule_data:
            days_for_scheduler = convert_days_to_ap_scheduler_format(job['days'])
            if days_for_scheduler:
                job_id = f"{job['start_time']}_{'_'.join(job['days'])}_{random.randint(1000, 9999)}"
                scheduler.add_job(
                    schedule_music, 'cron', 
                    day_of_week=','.join(days_for_scheduler), 
                    hour=int(job['start_time'].split(':')[0]), 
                    minute=int(job['start_time'].split(':')[1]),
                    args=[job],
                    id=job_id
                )

        scheduler.start()

=======

    with app.app_context():
        schedule_data = load_schedules_from_db()

    for job in schedule_data:
        days_for_scheduler = convert_days_to_ap_scheduler_format(job['days'])
        if days_for_scheduler:
            job_id = f"{job['start_time']}_{'_'.join(job['days'])}_{random.randint(1000, 9999)}"
            scheduler.add_job(
                schedule_music, 'cron', 
                day_of_week=','.join(days_for_scheduler), 
                hour=int(job['start_time'].split(':')[0]), 
                minute=int(job['start_time'].split(':')[1]),
                args=[job],
                id=job_id
            )

    scheduler.start()

    try:
>>>>>>> Stashed changes
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutting down due to user interruption.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        scheduler.shutdown()
        vlc.close()
        logging.info("Scheduler and VLC terminated.")

if __name__ == "__main__":
    main()
