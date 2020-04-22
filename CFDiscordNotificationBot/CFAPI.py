import requests

class Contest:

    def __init__(self, id, name, type, phase, frozen, durationSeconds, startTimeSeconds, relativeTimeSeconds):
        self.id = id
        self.name = name
        self.type = type
        self.phase = phase
        self.frozen = frozen
        self.durationSeconds = durationSeconds # ! Can be absent.
        self.startTimeSeconds = startTimeSeconds # ! Can be absent.
        self.relativeTimeSeconds = relativeTimeSeconds # ! Can be absent.

class APICallFailedException(Exception):
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return f"APICallFailedException: Comment({self.comment})"



URL = "https://codeforces.com/api/contest.list"
PARAMS = {"gym": False, "lang": "en"}

# ! limit


def getContests():
    r = requests.get(url = URL, params = PARAMS)
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

if __name__ == "__main__":
    getContests()