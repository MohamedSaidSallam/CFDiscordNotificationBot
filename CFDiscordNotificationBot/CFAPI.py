import requests


class Contest:

    def __init__(self, id, name, type, phase, frozen, durationSeconds=None, startTimeSeconds=None,
                 relativeTimeSeconds=None):
        self.id = id
        self.name = name
        self.type = type
        self.phase = phase
        self.frozen = frozen
        self.durationSeconds = durationSeconds
        self.startTimeSeconds = startTimeSeconds
        self.relativeTimeSeconds = relativeTimeSeconds


class APICallFailedException(Exception):
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return f"{type(self).__name__}: Comment({self.comment})"


URL = "https://codeforces.com/api/contest.list"
PARAMS = {"gym": False, "lang": "en"}


def getBeforeContests():
    """" Calls CF API to get Contests with phase before
    Args:
        None

    Returns:
        list: Contains Objects of type Contest of the contests with phase "before".

    Raises:
        APICallFailedException: when the call to CF API fails, The exception contains the comment returned from the API.
    """

    r = requests.get(url=URL, params=PARAMS)
    data = r.json()

    if data["status"] == "OK":
        contests = []
        for contest in data["result"]:
            if contest["phase"] != 'BEFORE':
                break
            contests.append(Contest(**contest))
        return contests
    else:
        raise APICallFailedException(data["comment"])
