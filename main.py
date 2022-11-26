# Utils
from utils.gradeReport import studentProgress
from utils.video import youtube
from utils.dialogflowQuery import dialogflow_query
from utils.webSearch import google_search
from utils.organisationInfo import organisationIntroduction
# from utils.quiz import quiz_bot
from utils.dialogflowQuery import dialogflow_query
from utils.db import db
from utils.schedule import getTimeSlot
from utils.schedule import bookTimeSlot
from utils.reschedule import rescheduleAppointment
from utils.checkProfile import checkProfile
from utils.quizPicture import getQuizPicture

from api.text import sendText
from api.oneButton import sendOneButton
from api.twoButton import sendTwoButton
from api.threeButton import sendThreeButton
from api.list import sendList
from api.courseraProfile import getCourseraProfile
from api.quizTemplate import sendQuizQuestion
from api.downloadMedia import getMedia

# Extra imports
from pymongo import MongoClient
import pymongo as pymongo
import datetime
import json
import os
import json
import random
from deep_translator import GoogleTranslator
import langid
from datetime import date, timedelta, datetime

# import requests to make API call
import requests
# import dotenv for loading the environment variables
from dotenv import load_dotenv
# import flask for setting up the web server
from flask import Flask, Response, request
# Extra imports
from pymongo import MongoClient


load_dotenv()


# creating the Flask object
app = Flask(__name__)





@app.route('/', methods=['POST'])
def reply():
    # request_data = json.loads(request.data)
    # print(request_data)
    
    # if "businessId" not in request_data:
    #     return ''
    
      #___Testing____
    request_data = {
        'from': request.form.get('WaId'),
        'sessionId': '7575757575757',
        'message': {
            'text': {
                'body':request.form.get('Body')
            }
        }
        
    }
    # ___________
    
    message_ = request_data['message']['text']['body']
    print(request.form)
    isEmoji = dialogflow_query(message_)
    if isEmoji.query_result.intent.display_name == 'Emoji handling - Activity' or isEmoji.query_result.intent.display_name == 'Emoji handling - Animals & Nature' or isEmoji.query_result.intent.display_name == 'Emoji handling - Flags' or isEmoji.query_result.intent.display_name == 'Emoji handling - Food & Drink' or isEmoji.query_result.intent.display_name == 'Emoji handling - Objects' or isEmoji.query_result.intent.display_name == 'Emoji handling - Smileys & People' or isEmoji.query_result.intent.display_name == 'Emoji handling - Symbols' or isEmoji.query_result.intent.display_name == 'Emoji handling - Travel & Places':
        user_ = db['test'].find_one({'_id':  request_data['from']})
        sendText(request_data['from'], user_['langId'], isEmoji.query_result.fulfillment_text, request_data['sessionId']) 
        return ''    
    langId = langid.classify(message_)[0]
    if langId != 'en':
        message = GoogleTranslator(
            source="auto", target="en").translate(message_)
    else:
        message = message_
    response_df = dialogflow_query(message)

    user = db['test'].find_one({'_id':  request_data['from']})

    if user == None and response_df.query_result.intent.display_name != 'Register' and response_df.query_result.intent.display_name != 'Organisation':
        
        welcome_text = ["Welcome to our world of education",
                        "It's a better place if you register today!",
                        "Trust me! Registering with us will brighten your future",
                        "Vishal, the business tycoon recommends us, register now!"]
        print(message)
        

        sendTwoButton( request_data['from'], langId, welcome_text[random.randint(0, 3)], ["register", "roam"], ["Register right now!", "Just exploring!"], request_data['sessionId'])
        return ''

    if user == None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):
        db["test"].insert_one({'_id': request.form.get('WaId'), 'name': '', 'email': '', 'langId': langId})
        sendText(request_data['from'], langId,response_df.query_result.fulfillment_text, request_data['sessionId'])
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation':
        organisationIntroduction( request_data['from'], langId, request_data['sessionId'])
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
        sendText(request_data['from'], langId, response_df.query_result.fulfillment_text, request_data['sessionId'])
        return ''

    if user != None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):
        if user['name'] == '':
            name_ = str(response_df.query_result.output_contexts[0].parameters.fields.get(
                'person.original'))
            name = name_.split("\"")[1]
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'name': name}})
            sendText(request_data['from'], user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
            return ''

        elif user['email'] == '':
            email_ = str(response_df.query_result.output_contexts[0].parameters.fields.get(
                'email.original'))
            email = email_.split("\"")[1]
            db['test'].update_many({'_id': request_data['from']}, {"$set": {'email': email.lower(), 'courses': [], 'courseraId': '', 'offersAvailed': [], 'UNIT-TESTING': ''}})
            sendText(request_data['from'],user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
            return ''




    workflow(user, request_data, response_df, langId)
    return ''


def workflow(user, request_data, response_df, langId):
    print(response_df.query_result.intent.display_name)

    if response_df.query_result.intent.display_name == 'Organisation':
        organisationIntroduction(request_data['from'], user['langId'], request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
        sendText(request_data['from'], user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Schedule':
        timeSlots = getTimeSlot()
        print(timeSlots)
        sendList(request_data['from'], user["langId"], "Please choose your preferred time for tomorrow!", "Free slots tomorrow!", timeSlots, timeSlots, None, True, request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Schedule - time':
        bookTimeSlot(request_data['from'], request_data['from'], user['langId'], request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Schedule - time - yes' or response_df.query_result.intent.display_name == 'Schedule - time - no':
        desiredTime_ = str(
            response_df.query_result.output_contexts[0].parameters.fields.get('time.original'))
        desiredTime = desiredTime_.split("\"")[1]
        rescheduleAppointment(response_df.query_result.intent.display_name, request_data['from'], user['langId'], desiredTime, request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'New-Resource':
        
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'true'}})

        userCourses =  []
        
        if len(user['courses']) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses for notes ! Please Enroll in the course to get resource !", request_data['sessionId'])
            return ''
        
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()):
                # coursesRank.append(str(i + 1))
                userCourses.append(user['courses'][i]['courseId'])
                
        print(userCourses)
        if len(userCourses) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses for notes ! Please Enroll in the course to get resource !", request_data['sessionId'])
            return ''
        
        sendList(request_data['from'], user['langId'], "Please choose the course for which you want resource", "Select Courses", userCourses, userCourses, None, False, request_data['sessionId'])
        return ''
    if response_df.query_result.intent.display_name == 'New-Resource - course':
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': request_data['message']['text']['body']}})
        sendThreeButton(request_data['from'], user['langId'],"Please select below which resource you want for" + request_data['message']['text']['body'],['books','notes','both'],['Books','Notes','Both'], request_data['sessionId'])
        return ''

    if response_df.query_result.intent.display_name == 'New-Resource - course - books':
        subject_name = db['test'].find_one({'_id': request_data['from']})['resource']
        
        sendText(request_data['from'], user['langId'], "Sending you " + subject_name  + " Books... \n"  + db['course'].find_one({'_id': subject_name})['courseBook'], request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
        return ''


    if response_df.query_result.intent.display_name == 'New-Resource - course - notes':

        subject_name = db['test'].find_one({'_id': request_data['from']})['resource']

        sendText(request_data['from'], user['langId'], "Sending you " + subject_name  + " Notes... \n"  + db['course'].find_one({'_id': subject_name})['courseNotes'], request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
        return ''

    if response_df.query_result.intent.display_name == 'New-Resource - course - both':

        subject_name = db['test'].find_one({'_id': request_data['from']})['resource']

        sendText(request_data['from'], user['langId'], "Sending you " + subject_name  + " Books... \n"  + db['course'].find_one({'_id': subject_name})['courseBook'], request_data['sessionId'])
        sendText(request_data['from'], user['langId'], "Sending you " + subject_name + " Notes... \n"  + db['course'].find_one({'_id': subject_name})['courseBook'], request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resource': 'false'}})
        return ''


    
    if response_df.query_result.intent.display_name == 'Quiz':
        
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'true'}})
        
        # coursesRank = []
        userCourses =  []
        
        if len(user['courses']) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses that contain quizzes. Why not explore more quizzes right now!", request_data['sessionId'])
            return ''
        
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()) and user['courses'][i]['courseType'] == 'static':
                courseListItem = db['course'].find_one({'_id': user['courses'][i]['courseId']})
                print(len(courseListItem['courseQuizzes']))
                print(len(user['courses'][i]['courseQuizzes']))
                print(user['courses'][i]['courseId'])
                if len(courseListItem['courseQuizzes']) > len(user['courses'][i]['courseQuizzes']):
                    # coursesRank.append(str(i + 1))
                    userCourses.append((user['courses'][i]['courseId']))
                
        print(userCourses)
        if len(userCourses) == 0:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
            sendText(request_data['from'], user['langId'], "You haven't enrolled in any courses that contain quizzes for now. Why not explore more quizzes right now!", request_data['sessionId'])
            return ''
        
        sendList(request_data['from'], user['langId'], "Please choose the course for which you want to test yourself", "Choose Quiz", userCourses, userCourses, None, False, request_data['sessionId'])
        return ''
    
    if user['quizBusy'] != 'false':
        date_format_str = '%d/%m/%Y %H:%M:%S'
        userCourses = []
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()) and user['courses'][i]['courseType'] == 'static':
                courseListItem = db['course'].find_one({'_id': user['courses'][i]['courseId']})
                if len(courseListItem['courseQuizzes']) > len(user['courses'][i]['courseQuizzes']):
                    # coursesRank.append(str(i + 1))
                    userCourses.append((user['courses'][i]['courseId']))
                
        if user['quizBusy'] == 'true':
            
            if request_data['message']['interactive']['list_reply']['id'] in userCourses: 
            
                courseChosen = db["course"].find_one({ '_id': request_data['message']['interactive']['list_reply']['id'] })
                courseChosenName = courseChosen['_id']

                index  = -1
                for i in range(0, len(user['courses'])):
                    if user['courses'][i]['courseId'] == courseChosen['_id'] and len(courseChosen['courseQuizzes']) >= len(user['courses'][i]['courseQuizzes']):
                        index = i
                        quizNumber = len(user['courses'][index]['courseQuizzes'])

                quizId = courseChosen['courseQuizzes'][quizNumber]

                quizChosen = db["questions"].find_one({ '_id': quizId})

                if quizNumber == len(user['courses'][index]['courseQuizzes']):
                    db['test'].update_one({'_id': request_data['from'], 'courses.courseId':courseChosenName}, {'$push': {'courses.$.courseQuizzes': {
                        'quizId': quizId,
                        'quizStart': datetime.now().strftime(date_format_str),
                        'quizMarks':[],
                        'quizScore': 0
                    }}})

                quizOptions = []
                updatedUser = db['test'].find_one({'_id': request_data['from']})
                questionNumber_ = len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1
                questionNumber = str(len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
                quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]

                quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': quizBusy}})
                quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])

                sendQuizQuestion(request_data['from'], user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)

                return ''
            
            else:
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
                sendText(request_data['from'], user['langId'], "Invalid selection of course! The quiz has terminated. Please try again!", request_data['sessionId'])
                return ''

        if request_data['message']['interactive']['button_reply']['id'] in ['A', 'B', 'C']:
            
            index = int(user['quizBusy'].split("-")[0])
            quizNumber = int(user['quizBusy'].split("-")[1])
            quizId = user['quizBusy'].split("-")[2]
            questionNumber = user['quizBusy'].split("-")[3]
            quizChosen = db["questions"].find_one({ '_id': quizId})
            markPerQuestion = int(quizChosen['quizMarks'] / quizChosen['quizCount'])
            if int(questionNumber) >= quizChosen['quizCount']:
                if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1 ==  (quizChosen['quizCount']) and int(questionNumber) == quizChosen['quizCount']:
                    if request_data['message']['interactive']['button_reply']['id'] == quizChosen[questionNumber]['answer']:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': markPerQuestion}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizEnd': datetime.now().strftime(date_format_str)}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})

                    else:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': 0}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizEnd': datetime.now().strftime(date_format_str)}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})
                    
                updatedUser = db['test'].find_one({'_id': request_data['from']})
                completeMarks_ = updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']
                secondsTaken = int((datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizEnd']), date_format_str) - datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizStart']), date_format_str)).total_seconds())
                completeMarks = sum(completeMarks_) - (secondsTaken * 0.01)

                db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizScore': completeMarks}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                
                sendText(request_data['from'], user['langId'], "Your quiz is over! You have scored " + str(completeMarks) + '!', request_data['sessionId'])
                if completeMarks >= (quizChosen['quizMarks'] * 0.8):
                    discountBagged = db["discounts"].find_one({ '_id': quizId})
                    discountPercentage = (1.0 - discountBagged['discountOffered']) * 100
                    db['test'].update_one({'_id': request_data['from'] }, {'$push': {'offersAvailed': {
                        'discountId': quizId,
                        'discountRedeemed': False
                    }}})
                    sendText(request_data['from'], user['langId'], "Congratulations! You have bagged a discount coupon!  Use code *" + str(quizId) + "* next time to avail a discount of " + str(int(discountPercentage))+ "% on your next payment!", request_data['sessionId'])
                    
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
                return ''

            if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) < quizChosen['quizCount']:
                quizOptions = []
                questionNumber_ = int(questionNumber) + 1
                questionNumber = str(questionNumber_)
                # questionNumber = str(len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
                quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]
                
                if questionNumber_ > 1:
                    if request_data['message']['interactive']['button_reply']['id'] == quizChosen[str(questionNumber_ - 1)]['answer']:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': markPerQuestion}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
                        print('COERCTE')
                
                    else:
                        db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$[courses].courseQuizzes.$[courseQuizzes].quizMarks': 0}}, array_filters=[{"courses.courseId": {"$eq": quizChosen['courseId']}},{"courseQuizzes.quizId": {"$eq": quizId}}], upsert=True)
                        # db['test'].update_one({'_id': request_data['from'], 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
                        print('INCORCET')
                
                quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
                db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': quizBusy}})
                quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])
                sendQuizQuestion(request_data['from'], user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)
                return ''    
        
        quizId = user['quizBusy'].split("-")[2]
        quizChosen = db["questions"].find_one({ '_id': quizId})
        courseChosenName = quizChosen['courseId']
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'quizBusy': 'false'}})
        sendText(request_data['from'], user['langId'], "Invalid selection! The quiz has been terminated. Please try again!", request_data['sessionId'])
        db['test'].update_one({'_id': request_data['from'], 'courses.courseId':courseChosenName}, {'$pop': {'courses.$.courseQuizzes': 1}})
        
        return ''
        
    
    if response_df.query_result.intent.display_name == 'Progress':
        sendTwoButton(request_data['from'], user['langId'], "Do you want to check progress for yourself?", ["myself", "someone"], ["Yes", "No"], request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Progress - no':
        sendText(request_data['from'], user['langId'], "Please specify the mobile number of that person starting with '91'. For example, 919876543210.", request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Progress - yes' or response_df.query_result.intent.display_name == 'Progress - no - number':
        specifiedUser = ''
        if (request_data['message']['text']['body']).startswith("91"):
            foundUser = db['test'].find_one({'_id': request_data['message']['text']['body']})
            if foundUser is None:
                sendText(request_data['from'], user['langId'], "Invalid number. Please check if the provided number was correct.", request_data['sessionId'])
            else:
                specifiedUser = foundUser
        
        elif response_df.query_result.intent.display_name == 'Progress - yes':
            specifiedUser = user
            
        else:
            sendText(request_data['from'], user['langId'], "Exited the progress report procedure!", request_data['sessionId'])
            return ''
            
        userCourses = []
        for i in range(0, len(specifiedUser['courses'])):
            if specifiedUser['courses'][i]['courseStartDate'] <= str(date.today()):
                # coursesRank.append(str(i + 1))
                if specifiedUser['courses'][i]['courseType'] == 'static':
                    if len(specifiedUser['courses'][i]['courseQuizzes']) > 0:
                        userCourses.append((specifiedUser['courses'][i]['courseId']))
                        continue
                
                if specifiedUser['courses'][i]['courseType'] == 'dynamic':
                    if specifiedUser['courses'][i]['courseFeedback'] != '':
                        userCourses.append((specifiedUser['courses'][i]['courseId']))
                        continue
        
        if len(userCourses) == 0:
            sendText(request_data['from'], user['langId'], "No progress to show sadly!", request_data['sessionId'])
            return ''
        
        db['test'].update_one({'_id': request_data['from']}, { "$set": {'resultBusy': { 'busy':'true', 'user': specifiedUser['_id']}}})
        sendList(request_data['from'], user['langId'], "Please choose the course to check progress", "Course", userCourses, userCourses, None, False, request_data['sessionId'])
        return ''
        
    if user['resultBusy']['busy'] == 'true':
        userCourses = []
        specifiedUser = db['test'].find_one({'_id': user['resultBusy']['user']})
        for i in range(0, len(specifiedUser['courses'])):
            if specifiedUser['courses'][i]['courseStartDate'] <= str(date.today()):
                # coursesRank.append(str(i + 1))
                userCourses.append((specifiedUser['courses'][i]['courseId']))
                
        if request_data['message']['interactive']['list_reply']['id'] in userCourses: 
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resultBusy': { 'busy':'false', 'user': ''}}})
            studentProgress(request_data['from'], user['resultBusy']['user'], request.form.get('Body'), request_data['sessionId'])
            return ''
            
        else:
            db['test'].update_one({'_id': request_data['from']}, { "$set": {'resultBusy': { 'busy':'false', 'user': ''}}})
            sendText(request_data['from'], user['langId'], "Invalid course selection!", request_data['sessionId'])
            return ''
        return ''
    
    if user['UNIT-TESTING'] == 'blue':
        return ''
        
    
    if response_df.query_result.intent.display_name == 'Videos':
        result_videos = youtube(response_df.query_result.query_text)
        print(result_videos)
        for video in result_videos:
            sendText(request_data['from'], langId, video['url'] + ' | ' + video['title'], request_data['sessionId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'WebSearch': 
        result_search = google_search(response_df.query_result.query_text)
        sendText(request_data['from'], langId, result_search, request_data['sessionId'])
    
    else:
        print(response_df.query_result.fulfillment_text)
        print(response_df.query_result.intent.display_name)
        sendText(request_data['from'],user['langId'], response_df.query_result.fulfillment_text, request_data['sessionId'])
    
    return ''


if __name__ == '__main__':
    app.run(debug=False)
