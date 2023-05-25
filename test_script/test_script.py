import requests
import uuid
import multiprocessing

URL = 'http://service:5001/log'


def send_request():
    count = 10
    for _ in range(count):
        payload = {
            "id": str(uuid.uuid4()),
            "unix_ts": 1684129671,
            "user_id": 123456,
            "event_name": "login"
        }
        response = requests.head(URL, json=payload)
        if response.status_code != 204:
            print('Failed to send log:', response.status_code)
    print(f'Sent {count} logs.')


def main():
    processes = []
    for _ in range(5):
        process = multiprocessing.Process(target=send_request)
        processes.append(process)
        process.start()
    print('STARTED.')

    for process in processes:
        process.join()

    print('FINISHED.')


if __name__ == '__main__':
    main()
