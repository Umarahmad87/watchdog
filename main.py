import os
import sys
import time
from watchdog.observers.polling import PollingObserver as Observer

from watchdog.events import FileSystemEventHandler


def read_last_n_lines_from_file(file_path, n):
    """
    Returns last N error logs line
    @param file_path:
    @param n: number of lines
    @return:
    """
    error_logs = []
    with open(file_path) as file:
        for line in (file.readlines()[-n:]):
            error_logs.append(line)

    return error_logs


class MonitorFolder(FileSystemEventHandler):
    FILE_SIZE = 10000
    WAIT_TIME = 60

    def on_change(self, event):
        print(event.src_path, event.event_type)
        last_status, time_ = self.get_status(event.src_path)

        if 'should restart' in last_status:
            print(f'{time_} WAITING {self.WAIT_TIME} seconds')
            time.sleep(self.WAIT_TIME)
            last_status, time_ = self.get_status(event.src_path)

        if 'should restart' in last_status:
            os.system('./script.sh')
            print(f'Restarting status:{last_status}')
        else:
            print(f'{time_} status:{last_status}')

    def get_status(self, path):
        appended_data = read_last_n_lines_from_file(path, 1)
        last_row = appended_data[-1].strip()
        last_status = last_row.split(',')
        return last_status[1], last_status[0]

    def on_created(self, event):
        self.on_change(event)

    def on_modified(self, event):
        self.on_change(event)


if __name__ == "__main__":
    src_path = sys.argv[1]
    print(src_path)

    event_handler = MonitorFolder()
    observer = Observer()
    observer.schedule(event_handler, path=src_path, recursive=False)
    print("Monitoring started")
    observer.start()
    try:
        while True:
            time.sleep(10)

    except KeyboardInterrupt:
        observer.stop()
        observer.join()
