from scratchAPI import *
from abc import ABC, abstractmethod


class ScratchData(ABC):

    SCRATCH_BASE_URL = "https://scratch.mit.edu/"
    PROJECT_URL = SCRATCH_BASE_URL + "projects/"
    STUDIO_URL = SCRATCH_BASE_URL + "studios/"

    levelCount = {}
    urlsToDownload = set({})
    projectsToDownload = {}

    class LevelCountTypes(Enum):
        DONE = "Done"
        TOTAL = "Total"

    def incrementTasks(self):
        if self.level not in self.levelCount.keys():
            self.levelCount[self.level] = {}
            for levelCountType in self.LevelCountTypes:
                self.levelCount[self.level][levelCountType] = 0
        self.levelCount[self.level][self.LevelCountTypes.TOTAL] += 1
        print(
            ("\t" * self.level)
            + str(self.levelCount[self.level][self.LevelCountTypes.DONE])
            + " / "
            + str(self.levelCount[self.level][self.LevelCountTypes.TOTAL])
        )

    def incrementTasks(self):
        self.levelCount[self.level][self.LevelCountTypes.DONE] += 1
        print(
            ("\t" * self.level)
            + str(self.levelCount[self.level][self.LevelCountTypes.DONE])
            + " / "
            + str(self.levelCount[self.level][self.LevelCountTypes.TOTAL])
            + "\t"
            + self.outputPath
        )

    def resetTracking(self):
        self.levelCount = {}
        self.urlsToDownload = set({})
        self.projectsToDownload = {}

    def __init__(
        self,
        dataID,
        baseURL,
        sourceData=None,
        level=0,
        outputPath="./",
        displayProgress=True,
        dataName="data",
    ):
        self.dataID = dataID
        self.baseURL = baseURL

        self.sourceData = sourceData
        self.level = level
        self.outputPath = outputPath
        self.baseOutputPath = outputPath
        self.displayProgress = displayProgress
        self.dataName = (dataName,)

        self.data = {}

    def markProjectForDownload():
        pass

    @abstractmethod
    async def getBasicInfo(self):
        pass

    @abstractmethod
    def getFileID(self):
        pass

    async def setUpData(self):
        data = {"level": self.level}
        dataInfoString = self.dataName + "Info"
        data[dataInfoString] = await self.getBasicInfo()
        dataCollectionFailed = "id" not in data[dataInfoString]
        useSource = dataCollectionFailed and self.sourceData is not None
        badData = dataCollectionFailed and useSource is None
        if useSource:
            data[dataInfoString] = self.sourceData
        return data

    async def getData(self):
        self.incrementTasks()

        self.urlsToDownload.add(self.baseURL + str(self.dataID))
        self.markProjectForDownload()

        self.data = self.setUpData()

        fileID = self.getFileID()
        fileName = get_valid_filename(fileID)
        self.outputPath = self.baseOutputPath + get_valid_path(fileID) + "/"
        print(self.outputPath)

        jsonCheck, jsonFileName = await checkForJSON(fileName, self.outputPath)



class UserData(ScratchData):

    USER_URL_ADDITION = "users/"

    def __init__(
        self,
        userName,
        dataName="user",
        **kwargs,
    ):
        baseURL = super().SCRATCH_BASE_URL + self.USER_URL_ADDITION
        super().__init__(dataID=userName, baseURL=baseURL, dataName=dataName, **kwargs)

    async def getBasicInfo(self):
        return await getUserInfo(self.dataID)

    def getFileID(self):
        return self.dataID
