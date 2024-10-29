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
from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import tinytuya
import json


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///schedules.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Load device configuration from JSON file
def load_device_config():
    with open(r'C:\Users\admin\OneDrive - DePaul University\OOP\Desktop(1)\Python\python\Project\flask\RC control way\config.json', 'r') as file:
        return json.load(file)

# Initialize devices from configuration
device_config = load_device_config()
devices = []

for device in device_config['devices']:
    d = tinytuya.OutletDevice(
        dev_id=device['dev_id'],
        address=device['address'],
        local_key=device['local_key'],
        version=device['version']  # Use the version from the config
    )
    devices.append(d)


# Routes for controlling the TinyTuya devices
@app.route('/turn_on/<int:device_index>')
def turn_on(device_index):
    """Turn on the specified device."""
    devices[device_index].turn_on()
    return redirect(url_for('index'))

@app.route('/turn_off/<int:device_index>')
def turn_off(device_index):
    """Turn off the specified device."""
    devices[device_index].turn_off()
    return redirect(url_for('index'))




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
        """Start VLC with the given media path if provided."""
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
    converted_days = [day_map[day.strip()] for day in days if day.strip() in day_map]
    logging.info(f"Converted days: {converted_days}")  # Log converted days
    return ','.join(converted_days) if converted_days else None

def load_schedules_from_db():
    """Load schedules from the database."""
    schedules = Schedule.query.all()
    return [
        {
            'id': schedule.id,
            'play_music_folder': schedule.play_music_folder,
            'start_time': schedule.start_time,
            'end_time': schedule.end_time.split('.')[0] if schedule.end_time else None,  # Remove microseconds
            'days': schedule.days.split(',')  # Convert to a list of days
        }
        for schedule in schedules
    ]

def play_music(media_folder):
    """Play music from the specified folder."""
    if not vlc.is_vlc_running():
        vlc.start_vlc()

    media_files = glob.glob(os.path.join(media_folder, '*'))
    if media_files:
        selected_media = random.choice(media_files)
        vlc.add_to_playlist(selected_media)
        vlc.play()
        logging.info(f"Playing music: {selected_media}")
    else:
        logging.warning(f"No media files found in folder: {media_folder}")

def schedule_music(job):
    """Schedule music playback based on the provided job details."""
    current_day = datetime.now().strftime("%A")
    logging.info(f"Current day: {current_day}")

    if current_day in job['days']:
        logging.info(f"Scheduling music for {current_day}")
        play_music(job['play_music_folder'])

        if job['end_time']:
            end_time_str = job['end_time'].split('.')[0]  # Take only 'HH:MM:SS'
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            current_time = datetime.now().time()

            if current_time < end_time:
                days_for_scheduler = convert_days_to_ap_scheduler_format(job['days'])
                if days_for_scheduler:
                    stop_job_id = f"stop_{job['start_time']}_{'_'.join(job['days'])}"
                    # Ensure the stop job is not already scheduled
                    if not scheduler.get_job(stop_job_id):
                        scheduler.add_job(stop_music, 'cron',
                                          day_of_week=days_for_scheduler,
                                          hour=end_time.hour,
                                          minute=end_time.minute,
                                          id=stop_job_id)
                    else:
                        logging.warning(f"Stop job {stop_job_id} is already scheduled.")
                else:
                    logging.warning("No valid days to schedule stop_music job.")


def main():
    """Main entry point of the application."""
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
                              day_of_week=days_for_scheduler, 
                              hour=int(job['start_time'].split(':')[0]), 
                              minute=int(job['start_time'].split(':')[1]),
                              args=[job],
                              id=job_id)  # Use the generated ID
            logging.info(f"Added job: {job_id} for music folder {job['play_music_folder']} at {job['start_time']} on days {job['days']}")
        else:
            logging.warning(f"No valid days for scheduling job: {job}")

    scheduler.start()
    logging.info("Scheduler started")

    try:
        # Keep the Flask app running
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        logging.error(f"Error in the main loop: {e}")
    finally:
        vlc.close()  # Close VLC connection on shutdown
        scheduler.shutdown()  # Shut down the scheduler

@app.route('/')
def index():
    """Render the main page with scheduled music."""
    schedules = load_schedules_from_db()
    return render_template('index.html', schedules=schedules,devices=devices, range=range(len(devices)))

@app.route('/add_schedule', methods=['POST'])
def add_schedule():
    """Add a new schedule to the database."""
    play_music_folder = request.form.get('play_music_folder')  # Use .get() to avoid KeyError
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    days = request.form.getlist('days')

    if not play_music_folder or not start_time:  # Validate the essential fields
        logging.error("Missing required fields.")
        return redirect(url_for('index'))

    # Join the list of days into a comma-separated string
    days_str = ','.join(days)

    new_schedule = Schedule(
        play_music_folder=play_music_folder,
        start_time=start_time,
        end_time=end_time,
        days=days_str
    )

    db.session.add(new_schedule)
    db.session.commit()
    logging.info(f"Added new schedule: {play_music_folder}, Start: {start_time}, End: {end_time}, Days: {days_str}")

    return redirect(url_for('index'))


@app.route('/edit_schedule', methods=['POST'])
def edit_schedule():
    """Edit an existing schedule in the database."""
    schedule_id = request.form['id']
    play_music_folder = request.form['play_music_folder']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    days = request.form.getlist('days')

    # Find the schedule by ID and update its fields
    schedule = Schedule.query.get(schedule_id)
    if schedule:
        schedule.play_music_folder = play_music_folder
        schedule.start_time = start_time
        schedule.end_time = end_time
        schedule.days = ','.join(days)

        db.session.commit()
        logging.info(f"Updated schedule ID: {schedule_id} with new values.")

        job_id = f"{schedule.start_time}_{schedule.days.replace(',', '_')}"

        # Check if the job exists before trying to remove it
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logging.info(f"Removed job with ID: {job_id}")
        else:
            logging.warning(f"Job with ID: {job_id} not found, cannot remove.")

        # Add new job with updated schedule
        scheduler.add_job(schedule_music, 'cron',
                          day_of_week=convert_days_to_ap_scheduler_format(days),
                          hour=int(start_time.split(":")[0]),
                          minute=int(start_time.split(":")[1]),
                          args=[{
                              'id': schedule.id,
                              'play_music_folder': play_music_folder,
                              'start_time': start_time,
                              'end_time': end_time,
                              'days': days
                          }],
                          id=job_id)  # Unique ID based on time and days

        return redirect(url_for('index'))
    else:
        logging.warning(f"Schedule ID not found: {schedule_id}")
        return redirect(url_for('index'))

    
@app.route('/stop_schedule/<int:schedule_id>')
def stop_schedule(schedule_id):
    """Stop a scheduled music playback by schedule ID."""
    schedule = Schedule.query.get(schedule_id)
    if schedule:
        # Stop the music if it's currently playing
        stop_music()
        db.session.delete(schedule)
        db.session.commit()
        logging.info(f"Stopped and deleted schedule ID: {schedule_id}")
    else:
        logging.warning(f"Schedule ID not found: {schedule_id}")

    return redirect(url_for('index'))


if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000, debug=True)
