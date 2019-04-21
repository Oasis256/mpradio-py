import threading
import time
import platform
from configuration import config


class RdsUpdater:

    __interval = None
    __termination = None
    __song = None
    __step = None
    __output = None
    __rds_ctl = None
    __updated = False

    def __init__(self):
        self.__termination = threading.Event()
        self.__rds_ctl = config.get_rds_ctl()

        if platform.machine() == "x86_64":
            self.__output = print
        else:
            self.__output = self.write_rds_to_pipe

        self.__interval = int(config.get_settings()["RDS"]["updateInterval"])
        self.__step = int(config.get_settings()["RDS"]["charsJump"])

    def set(self, song):
        if song != self.__song:
            self.__song = song
            self.__updated = True

    def write_rds_to_pipe(self, text):
        with open(self.__rds_ctl, "w") as f:
            text = text.strip() + "\n"
            f.write("PS "+text)
            f.write("RT "+text)

    def __run(self):
        while not self.__termination.is_set():
            # wait for the song to be set.
            if self.__song is None:
                time.sleep(0.2)
                continue

            for qg in self.q_gram(self.__song["title"]+" - "+self.__song["artist"]):
                self.__output(qg)
                if self.__termination.is_set():
                    return
                if self.__updated:
                    self.__updated = False
                    break
                time.sleep(self.__interval)

    # print q-grams of the given title
    def q_gram(self, text):
        q = []

        if len(text) < 9:
            q.append(text)
            return q

        for i in range(0, len(text), self.__step):
            start = i
            end = i + 8
            if end > len(text):
                break
            s = text[start:end]
            q.append(s)
        return q

    def run(self):
        threading.Thread(target=self.__run).start()

    def stop(self):
        self.__termination.set()
