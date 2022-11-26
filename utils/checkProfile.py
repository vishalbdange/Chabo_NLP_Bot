from api.courseraProfile import getCourseraProfile
from utils.db import db
from api.text import sendText
from api.uploadMedia import uploadMedia 
from api.media import sendMedia

def checkProfile(receiver, langId, courseraProfileUrl, sessionId):
    statusCode = getCourseraProfile(courseraProfileUrl)
    if statusCode == '200':
        db["test"].update_one({ '_id': receiver }, { "$set": { 'courseraId': courseraProfileUrl }} )
        sendText(receiver, langId, "Awesome!🎯 We have noted your coursera profile successfully!", sessionId)
        return ''
    
    mediaId, mediaType = uploadMedia('courseraProfileHelp.jpg', 'static/helpMedia/courseraProfileHelp.jpg', 'jpg')
    print(mediaId, mediaType)
    sendText(receiver, langId, "It looks like you submitted an incorrect profile URL link.🤔 Please make sure that you submit the correct link that is displayed when you visit your profile in our portal. For reference, please consider the image attached!", sessionId)
    sendMedia(receiver, mediaId, mediaType, sessionId)
    
    return ''