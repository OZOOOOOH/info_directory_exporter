import argparse
import logging
import os
import time
from glob import glob

from prometheus_client import REGISTRY, CollectorRegistry, Gauge, start_http_server

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Setting the arguments
parser = argparse.ArgumentParser()

# required arg
parser.add_argument("-d", "--dir", required=True, help="target dir path")
parser.add_argument("-t", "--time", required=True, help="sleep time", type=int)
parser.add_argument("-e", "--extension", required=False, help="extension to check")
args = parser.parse_args()


class CustomExporter:
    def __init__(self, dir: str, sleep_time: int) -> None:
        self.dir = dir
        self.metric_dict = {}
        self.sleep_time = sleep_time
        self.registry = CollectorRegistry()
        self.job_name = "custom_exporter"

    def count_items_in_dir(self) -> int:
        pass

    def create_gauge_for_metric(self, metric_name: str, description: str) -> None:
        if self.metric_dict.get(metric_name) is None:
            self.metric_dict[metric_name] = Gauge(
                metric_name,
                description,
                registry=self.registry,
            )

    def set_value(self, metric_name: str) -> None:
        self.metric_dict[metric_name].set(self.count_items_in_dir())

    def main(self, metric_name: str, description: str) -> None:
        # exporter_port = int(os.environ.get("EXPORTER_PORT", "9877"))
        self.create_gauge_for_metric(metric_name, description)
        start_http_server(9877, registry=self.registry)
        REGISTRY.register(self.registry)
        while True:
            self.create_gauge_for_metric(metric_name, description)
            self.set_value(metric_name)
            time.sleep(self.sleep_time)


class FileExtExporter(CustomExporter):
    def __init__(self, dir: str, ext: str, sleep_time: int) -> None:
        super().__init__(dir, sleep_time)
        self.ext = ext
        self.job_name = "file_ext_exporter"

    def count_items_in_dir(self) -> int:
        file_list = list(glob(f"{self.dir}/*.{self.ext}"))
        logging.info(
            f"Founds {len(file_list)} file(s) in dir {self.dir} with extension {self.ext}"
        )
        return len(file_list)

    def main(self):
        metric_name = f"cust_{self.ext}_files_in{self.dir.replace('/', '_')}_total"
        description = f"number of *{self.ext} files in {self.dir}"
        super().main(metric_name, description)


class DirNumExporter(CustomExporter):
    def __init__(self, dir: str, sleep_time: int) -> None:
        super().__init__(dir, sleep_time)
        self.job_name = "dir_num_exporter"

    def count_items_in_dir(self) -> int:
        entries = os.listdir(self.dir)
        dirs = [
            entry for entry in entries if os.path.isdir(os.path.join(self.dir, entry))
        ]
        logging.info(f"Found {len(dirs)} dir(s) in {self.dir}")
        return len(dirs)

    def main(self):
        metric_name = f"cust_dirs_in_{'_'.join(self.dir.split('/')[-2:])}_total"
        description = f"number of dirs in {self.dir}"
        super().main(metric_name, description)


if __name__ == "__main__":
    dir_path, sleep_time = args.dir, args.time
    c = DirNumExporter(dir_path, sleep_time)
    c.main()
