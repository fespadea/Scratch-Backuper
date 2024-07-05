import requests
from requests.adapters import HTTPAdapter, Retry
import time
import json
import re
import random
import os
import pickle
import trio
import subprocess
import shutil
from enum import Enum
from functools import partial

# import win32file
# win32file._setmaxstdio(8192)

PREVIOUS_REQUESTS_BACKUP_PATH = "./previousRequests/"

requestSession = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
requestSession.mount("", HTTPAdapter(max_retries=retries))


def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        return "ErrorFileName" + str(random.randrange(100000))
    return s


def get_valid_path(path):
    s = str(path).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w./]", "", s)
    if s in {"", ".", ".."}:
        return "ErrorFileName" + str(random.randrange(100000))
    if s[-1] == ".":
        s += "_"
    return s


async def dumpAPIRequest(fileName, data, path=PREVIOUS_REQUESTS_BACKUP_PATH):
    fullFileName = get_valid_path(path) + get_valid_filename(fileName) + ".pkl"
    os.makedirs(os.path.dirname(fullFileName), exist_ok=True)
    with open(fullFileName, "wb") as outputFile:
        pickle.dump(data, outputFile)
    return fullFileName


async def loadAPIRequest(fileName, path=PREVIOUS_REQUESTS_BACKUP_PATH):
    fullFileName = path + get_valid_filename(fileName) + ".pkl"
    if not os.path.exists(fullFileName):
        return {}
    with open(fullFileName, "rb") as inputFile:
        data = pickle.load(inputFile)
    return data


async def checkForAPIRequest(url, path=PREVIOUS_REQUESTS_BACKUP_PATH):
    return os.path.exists(path + get_valid_filename(url) + ".pkl")


async def dumpJSON(fileName, data, path="./"):
    fullFileName = get_valid_path(path) + get_valid_filename(fileName) + ".json"
    os.makedirs(os.path.dirname(fullFileName), exist_ok=True)
    with open(fullFileName, "w") as outputFile:
        json.dump(data, outputFile, indent=6)
    return fullFileName


async def loadJSON(fullFileName):
    if not os.path.exists(fullFileName):
        return {}
    with open(fullFileName, "r") as inputFile:
        data = json.load(inputFile)
    return data


async def checkForJSON(fileName, path):
    fullFileName = get_valid_path(path) + get_valid_filename(fileName) + ".json"
    try:
        return (
            loadJSON(fullFileName) if os.path.exists(fullFileName) else {}
        ), fullFileName
    except Exception as e:
        print(fullFileName)
        raise e
    # return fullFileName if os.path.exists(fullFileName) else {}


async def dumpGeneric(fileName, list, type="txt", path="./"):
    fullFileName = get_valid_path(path) + get_valid_filename(fileName) + "." + type
    os.makedirs(os.path.dirname(fullFileName), exist_ok=True)
    with open(fullFileName, "w") as outputFile:
        for item in list:
            outputFile.write(str(item) + "\n")
    return fullFileName


async def nurseryReturn(nursery, assignee, location, func, *args, **kwargs):
    async def getReturn():
        assignee[location] = await func(*args, **kwargs)

    nursery.start_soon(getReturn)


SCRATCH_API = "https://api.scratch.mit.edu"
# WAIT_TIME = 0.1
# lastRequestTime = 0
markedRequests = set({})
markedImages = set({})
FAILED_IMAGE = b"FAILED_IMAGE"
AUTH_ADDITION = "?x-token="
progressChecker = 0
lastCheckerTime = time.time()


async def apiRequest(url):
    if checkForAPIRequest(url):
        return await loadAPIRequest(url)

    if url in markedRequests:
        while url in markedRequests:
            await trio.sleep(10)
        if checkForAPIRequest(url):
            return await loadAPIRequest(url)
    else:
        markedRequests.add(url)

    # global lastRequestTime
    # sleepTime = max(lastRequestTime + WAIT_TIME - time.time(), 0)
    # await trio.sleep(sleepTime)
    # lastRequestTime = time.time()

    # response = requestSession.get(url)
    notDone = True
    while notDone:
        try:
            response = await requestSession.get(url)
            if not response.ok and response.status_code != 404:
                raise Exception
        except Exception:
            print("-----------------------------------ConnectionError with url: " + url)
            await trio.sleep(10)
        else:
            notDone = False
    data = response.json()  # if response.ok else {}

    await dumpAPIRequest(url, data)
    markedRequests.remove(url)

    global progressChecker
    progressChecker += 1
    if progressChecker % 100 == 0:
        currentTime = time.time()
        global lastCheckerTime
        print(
            str(progressChecker)
            + " requests in "
            + str(currentTime - lastCheckerTime)
            + " seconds since last check."
        )
        lastCheckerTime = currentTime

    return data


async def imageGet(url, path="./", backupPath=PREVIOUS_REQUESTS_BACKUP_PATH):
    imageName = re.search("[^/]*.png", url).group()
    imageBackupPath = backupPath + imageName

    if url in markedImages:
        while url in markedImages:
            await trio.sleep(10)
    elif not os.path.exists(imageBackupPath):
        markedImages.add(url)

        notDone = True

        async def requestImage():
            return requestSession.get(url, stream=True)

        while notDone:
            try:
                imageRequest = await requestImage()
                if (
                    not imageRequest.ok
                    and imageRequest.status_code != 668
                    and imageRequest.status_code != 500
                ):
                    raise Exception
            except Exception as e:
                print(
                    "-----------------------------------ConnectionError with url: "
                    + url
                )
                await trio.sleep(10)
            else:
                notDone = False

        os.makedirs(backupPath, exist_ok=True)
        with open(imageBackupPath, "wb") as imageFile:
            if imageRequest.ok or imageRequest.status_code == 668:
                imageRequest.raw.decode_content = True
                shutil.copyfileobj(imageRequest.raw, imageFile)
                markedImages.remove(url)
            else:
                imageFile.write(FAILED_IMAGE)
                markedImages.remove(url)
                print("Image not found: " + url)
                return

    with open(imageBackupPath, "rb") as imageFile:
        if imageFile.read() == FAILED_IMAGE:
            return
    imagePath = path + imageName
    os.makedirs(path, exist_ok=True)
    shutil.copy(imageBackupPath, imagePath)


async def getAllResults(url):
    limit = 40
    url = url + "?limit=" + str(limit) + "&offset="
    offset = 0
    singleList = await apiRequest(url + str(offset))
    all = singleList
    while len(singleList) >= limit:
        offset += limit
        singleList = await apiRequest(url + str(offset))
        if len(singleList) > 0:
            all += singleList
    return all


async def getAllResultsDateBased(url):
    limit = 40
    url = url + "?limit=" + str(limit)
    singleList = await apiRequest(url)
    all = singleList
    while len(singleList) >= limit:
        dateLimit = all[-1].datetime_created
        singleList = await apiRequest(url + "?dateLimit=" + str(dateLimit))
        if len(singleList) > 0:
            overlapIndex = singleList.index(all[-1]) + 1
            if overlapIndex < len(singleList):
                truncatedList = singleList[(singleList.index(all[-1]) + 1) :]
                if len(truncatedList) > 0:
                    all += truncatedList
    return all
