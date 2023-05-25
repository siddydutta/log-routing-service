import atexit
import json
import os
import queue
import threading
from datetime import datetime

import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, Response

app = Flask(__name__)

# Database connection
db_connection = psycopg2.connect(
    host='database',
    port='5045',
    dbname='logs',
    user='postgres',
    password='password'
)

# Log buffering and synchronization
log_buffer = queue.Queue()
buffer_lock = threading.Lock()

# Initialize log file
log_file = None


def create_log_file():
    global log_file

    # Generate unique filename based on timestamp
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f'log_{timestamp}.txt'
    log_file = open(filename, 'w+')


create_log_file()


def flush_logs():
    global log_file

    current_log = log_file
    with buffer_lock:
        create_log_file()

    if current_log is None:
        return

    # Read log file data
    current_log.seek(0)
    logs = current_log.readlines()
    if len(logs) > 0:
        insert_query = 'INSERT INTO logs(data) VALUES {}'.format(','.join(['(%s)'] * len(logs)))
        cursor = db_connection.cursor()
        cursor.execute(insert_query, logs)
        db_connection.commit()
        cursor.close()

    # Close and delete the log file
    current_log.close()
    os.remove(current_log.name)


def process_log_buffer():
    while True:
        while not log_buffer.empty():
            log_data = log_buffer.get()
            with buffer_lock:
                log_entry = json.dumps(log_data) + '\n'
                log_file.write(log_entry)


def at_exit():
    global log_file
    flush_logs()
    scheduler.shutdown()
    log_file.close()
    os.remove(log_file.name)


# Start log buffer processing thread
log_buffer_thread = threading.Thread(target=process_log_buffer, daemon=True)
log_buffer_thread.start()

scheduler = BackgroundScheduler()
scheduler.add_job(func=flush_logs, trigger="interval", seconds=30)
scheduler.start()

atexit.register(at_exit)


@app.route('/log', methods=['POST', 'HEAD'])
def receive_log():
    log_buffer.put(request.get_json())
    return Response(status=204)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
