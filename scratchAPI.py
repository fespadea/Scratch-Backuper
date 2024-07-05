from helperFunctions import *


async def getCommentsWithReplies(url):
    comments = await getAllResults(url)
    async with trio.open_nursery() as nursery:
        for comment in comments:
            if "reply_count" in comment.keys() and comment["reply_count"] > 0:
                # async def getReplies():
                #     comment["replies"] = await getAllResults(url + "/" + str(comment["id"]) + "/replies")
                # nursery.start_soon(getReplies)
                nurseryReturn(
                    nursery,
                    comment,
                    "replies",
                    getAllResults,
                    url + "/" + str(comment["id"]) + "/replies",
                )

            else:
                comment["replies"] = {}
                comment["reply_count"] = 0
    return comments


# project calls

projectsInfoAPIAddition = "/projects/"
projectInfoAPI = SCRATCH_API + projectsInfoAPIAddition


async def getProjectInfo(projectID):
    return await apiRequest(projectInfoAPI + str(projectID))


projectRemixesAPIAddition = "/remixes"


async def getProjectRemixes(projectID):
    return await getAllResults(
        projectInfoAPI + str(projectID) + projectRemixesAPIAddition
    )


# bonus helper function
userIDs = {}


async def getProjectUserName(projectID, userID=None):
    if userID is None or userID not in userIDs.keys():
        projectInfo = await getProjectInfo(projectID)
        if "author" in projectInfo:
            userIDs[userID] = projectInfo["author"]["username"]
            return userIDs[userID]
        else:
            return ""
    else:
        return userIDs[userID]


# studio calls

studioInfoAPIAddition = "/studios/"
studioInfoAPI = SCRATCH_API + studioInfoAPIAddition


async def getStudioInfo(studioID):
    return await apiRequest(studioInfoAPI + str(studioID))


studioActivityAPIAddition = "/activity"


async def getStudioActivity(studioID):
    return await getAllResults(
        studioInfoAPI + str(studioID) + studioActivityAPIAddition
    )


studioCommentsAPIAddition = "/comments"


async def getStudioComments(studioID):
    return await getCommentsWithReplies(
        studioInfoAPI + str(studioID) + studioCommentsAPIAddition
    )


studioCuratorsAPIAddition = "/curators"


async def getStudioCurators(studioID):
    return await getAllResults(
        studioInfoAPI + str(studioID) + studioCuratorsAPIAddition
    )


studioManagersAPIAddition = "/managers"


async def getStudioManagers(studioID):
    return await getAllResults(
        studioInfoAPI + str(studioID) + studioManagersAPIAddition
    )


studioProjectsAPIAddition = "/projects"


async def getStudioProjects(studioID):
    studioProjects = await getAllResults(
        studioInfoAPI + str(studioID) + studioProjectsAPIAddition
    )
    # async with trio.open_nursery() as nursery:
    #     for i in range(len(studioProjects)):
    #         nurseryReturn(nursery, studioProjects, i, getProjectInfo, studioProjects[i]["id"])
    return studioProjects


studioUserRoleAPIAddition = "/users/"


async def getStudioUserRole(studioID, userName, authToken):
    return await getAllResults(
        studioInfoAPI
        + str(studioID)
        + studioUserRoleAPIAddition
        + userName
        + AUTH_ADDITION
        + authToken
    )


# user calls

userInfoAPIAddition = "/users/"
userInfoAPI = SCRATCH_API + userInfoAPIAddition


async def getUserInfo(userName):
    return await apiRequest(userInfoAPI + str(userName))


userFavoritesAPIAddition = "/favorites"


async def getUserFavorites(userName):
    projects = await getAllResults(
        userInfoAPI + str(userName) + userFavoritesAPIAddition
    )
    async with trio.open_nursery() as nursery:
        for project in projects:
            nurseryReturn(
                nursery,
                project["author"],
                "username",
                getProjectUserName,
                project["id"],
                project["author"]["id"],
            )
    return projects


userFollowersAPIAddition = "/followers"


async def getUserFollowers(userName):
    return await getAllResults(userInfoAPI + str(userName) + userFollowersAPIAddition)


userFollowingAPIAddition = "/following"


async def getUserFollowing(userName):
    return await getAllResults(userInfoAPI + str(userName) + userFollowingAPIAddition)


userFollowingStudiosAPIAddition = userFollowingAPIAddition + "/studios/projects"


async def getUserFollowingStudios(userName, authToken):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userFollowingStudiosAPIAddition
        + AUTH_ADDITION
        + authToken
    )


userFollowingUsersActivityAPIAddition = userFollowingAPIAddition + "/users/activity"


async def getUserFollowingUsersActivity(userName, authToken):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userFollowingUsersActivityAPIAddition
        + AUTH_ADDITION
        + authToken
    )


userFollowingUsersLovesAPIAddition = userFollowingAPIAddition + "/users/loves"


async def getUserFollowingUsersLoves(userName, authToken):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userFollowingUsersLovesAPIAddition
        + AUTH_ADDITION
        + authToken
    )


userFollowingUsersProjectsAPIAddition = userFollowingAPIAddition + "/users/projects"


async def getUserFollowingUsersProjects(userName, authToken):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userFollowingUsersProjectsAPIAddition
        + AUTH_ADDITION
        + authToken
    )


userInvitesAPIAddition = "/invites"


async def getUserInvites(userName, authToken):
    return await getAllResults(
        userInfoAPI + str(userName) + userInvitesAPIAddition + AUTH_ADDITION + authToken
    )


userMessagesAPIAddition = "/messages"


async def getUserMessages(userName, authToken):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userMessagesAPIAddition
        + AUTH_ADDITION
        + authToken
    )


userAlertsAPIAddition = "/messages/admin"


async def getUserAlerts(userName, authToken):
    return await getAllResults(
        userInfoAPI + str(userName) + userAlertsAPIAddition + AUTH_ADDITION + authToken
    )


userUnreadMessagesCountAPIAddition = "/messages/count"


async def getUserUnreadMessagesCount(userName, authToken):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userUnreadMessagesCountAPIAddition
        + AUTH_ADDITION
        + authToken
    )


userProjectsAPIAddition = "/projects"


async def getUserProjects(userName):
    projects = await getAllResults(
        userInfoAPI + str(userName) + userProjectsAPIAddition
    )
    for project in projects:
        project["author"]["username"] = userName
    return projects


userRecentlyViewedAPIAddition = "/projects/recentlyviewed"


async def getUserRecentlyViewed(userName, authToken):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userRecentlyViewedAPIAddition
        + AUTH_ADDITION
        + authToken
    )


userProjectCommentsAPIAddition = "/comments"
userProjectsAPIAdditionMiddle = "/projects/"


async def getUserProjectComments(userName, projectID):
    return await getCommentsWithReplies(
        userInfoAPI
        + str(userName)
        + userProjectsAPIAdditionMiddle
        + str(projectID)
        + userProjectCommentsAPIAddition
    )


userProjectStudiosAPIAddition = "/studios"


async def getUserProjectStudiosAPI(userName, projectID):
    return await getAllResults(
        userInfoAPI
        + str(userName)
        + userProjectsAPIAdditionMiddle
        + str(projectID)
        + userProjectStudiosAPIAddition
    )


userUnsharedProjectAPIAddition = "/visibility"


async def getUserUnsharedProject(userName, projectID):
    return await getCommentsWithReplies(
        userInfoAPI
        + str(userName)
        + userProjectsAPIAdditionMiddle
        + str(projectID)
        + userUnsharedProjectAPIAddition
    )


userStudiosAPIAddition = "/studios/curate"


async def getUserStudios(userName):
    return await getAllResults(userInfoAPI + str(userName) + userStudiosAPIAddition)
