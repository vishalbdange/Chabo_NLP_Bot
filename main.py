# Utils
from utils.gradeReport import studentProgress
from utils.video import youtube
from utils.sendMessage import send_message
# from utils.quiz import quiz_bot
from utils.dialogflowQuery import dialogflow_query
from utils.webSearch import google_search
from utils.organisationInfo import organisationIntroduction
# from utils.quiz import quiz_bot
from utils.dialogflowQuery import dialogflow_query
from utils.TrialFlow import trialFlow
from utils.db import db
from utils.schedule import getTimeSlot
from utils.schedule import bookTimeSlot
from utils.reschedule import rescheduleAppointment
from utils.checkProfile import checkProfile
from utils.quizPicture import getQuizPicture

from api.text import sendText
from api.quizButtons import sendQuiz
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
    
    message_ = request.form.get('Body')
    print(request.form)
    langId = langid.classify(message_)[0]
    if langId != 'en':
        message = GoogleTranslator(
            source="auto", target="en").translate(message_)
    else:
        message = message_
    response_df = dialogflow_query(message)

    user = db['test'].find_one({'_id': request.form.get('WaId')})

    if user == None and response_df.query_result.intent.display_name != 'Register' and response_df.query_result.intent.display_name != 'Organisation':
        # send button to register
        # sendTwoButton(request.form.get('WaId'), "Welcome to our world of education", "register", "I want to register right now!", "surf",  "I am just here to surf and explore!")
        welcome_text = ["Welcome to our world of education",
                        "It's a better place if you register today!",
                        "Trust me! Registering with us will brighten your future",
                        "Vishal, the business tycoon recommends us, register now!"]
        print(message)
        # print(response_df.query_result.language_code)

        sendTwoButton(request.form.get('WaId'), langId, welcome_text[random.randint(
            0, 3)], ["register", "roam"], ["Register right now!", "Just exploring!"])
        return ''

    if user == None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):
        db["test"].insert_one({'_id': request.form.get(
            'WaId'), 'name': '', 'email': '', 'langId': langId})
        sendText(request.form.get('WaId'), langId,response_df.query_result.fulfillment_text)
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation':
        organisationIntroduction(request.form.get('WaId'), langId)
        return ''

    if user == None and response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
        sendText(request.form.get('WaId'), langId, response_df.query_result.fulfillment_text)
        return ''

    if user != None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):
        if user['name'] == '':
            name_ = str(response_df.query_result.output_contexts[0].parameters.fields.get(
                'person.original'))
            name = name_.split("\"")[1]
            db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'name': name}})
            sendText(request.form.get('WaId'), user['langId'], response_df.query_result.fulfillment_text)
            return ''

        elif user['email'] == '':
            email_ = str(response_df.query_result.output_contexts[0].parameters.fields.get(
                'email.original'))
            email = email_.split("\"")[1]
            # emailUnique = db['test'].create_index([("email", pymongo.ASCENDING)], unique=True,)
            db['test'].update_many({'_id': request.form.get('WaId')}, {"$set": {'email': email.lower(), 'courses': [], 'courseraId': '', 'offersAvailed': [], 'UNIT-TESTING': ''}})
            # email.clear()
            # print('FINSIHEDDD ' + finishedRegistration)
            sendText(request.form.get('WaId'),user['langId'], response_df.query_result.fulfillment_text)
            return ''

    # if user != None and (response_df.query_result.intent.display_name == 'Register' or response_df.query_result.intent.display_name == 'Register-Follow'):


    workflow(user, request, response_df, langId)
    return ''


def workflow(user, request, response_df, langId):
    print(response_df.query_result.intent.display_name)

    if response_df.query_result.intent.display_name == 'Organisation':
        organisationIntroduction(request.form.get('WaId'), user['langId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Organisation - history' or response_df.query_result.intent.display_name == 'Organisation - vision' or response_df.query_result.intent.display_name == 'Organisation - visit':
        sendText(request.form.get('WaId'), user['langId'], response_df.query_result.fulfillment_text)
        return ''
    
    if response_df.query_result.intent.display_name == 'Schedule':
        timeSlots = getTimeSlot()
        print(timeSlots)
        sendList(request.form.get('WaId'), user["langId"], "Please choose your preferred time for tomorrow!", "Free slots tomorrow!", timeSlots, timeSlots, None, True)
        return ''
    
    if response_df.query_result.intent.display_name == 'Schedule - time':
        bookTimeSlot(request.form.get('Body'), request.form.get('WaId'), user['langId'])
        return ''
    
    if response_df.query_result.intent.display_name == 'Schedule - time - yes' or response_df.query_result.intent.display_name == 'Schedule - time - no':
        desiredTime_ = str(
            response_df.query_result.output_contexts[0].parameters.fields.get('time.original'))
        desiredTime = desiredTime_.split("\"")[1]
        rescheduleAppointment(response_df.query_result.intent.display_name, request.form.get('WaId'), user['langId'], desiredTime)
        return ''
    
    if response_df.query_result.intent.display_name == 'Quiz':
        
        db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': 'true'}})
        
        # coursesRank = []
        userCourses =  []
        
        if len(user['courses']) == 0:
            db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': 'false'}})
            sendText(request.form.get('WaId'), user['langId'], "You haven't enrolled in any courses that contain quizzes. Why not explore more quizzes right now!")
            return ''
        
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()) and user['courses'][i]['courseType'] == 'static':
                # coursesRank.append(str(i + 1))
                userCourses.append(user['courses'][i]['courseId'])
                
        print(userCourses)
        if len(userCourses) == 0:
            db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': 'false'}})
            sendText(request.form.get('WaId'), user['langId'], "You haven't enrolled in any courses that contain quizzes. Why not explore more quizzes right now!")
            return ''
        
        sendList(request.form.get('WaId'), user['langId'], "Please choose the course for which you want to test yourself", "Choose Quiz", userCourses, userCourses, None, False)
        return ''
    
    if user['quizBusy'] != 'false':
        date_format_str = '%d/%m/%Y %H:%M:%S'
        userCourses = []
        for i in range(0, len(user['courses'])):
            if user['courses'][i]['coursePayment'] is True and user['courses'][i]['courseEndDate'] > str(date.today()) and user['courses'][i]['courseType'] == 'static':
                # coursesRank.append(str(i + 1))
                userCourses.append((user['courses'][i]['courseId']))
                
        if user['quizBusy'] == 'true':
            
            if request.form.get('Body') in userCourses: 
            
                courseChosen = db["course"].find_one({ '_id': request.form.get('Body') })
                courseChosenName = courseChosen['_id']

                index  = -1
                for i in range(0, len(user['courses'])):
                    if user['courses'][i]['courseId'] == courseChosen['_id'] and len(courseChosen['courseQuizzes']) >= len(user['courses'][i]['courseQuizzes']):
                        index = i
                        quizNumber = len(user['courses'][index]['courseQuizzes'])

                quizId = courseChosen['courseQuizzes'][quizNumber]

                quizChosen = db["questions"].find_one({ '_id': quizId})

                if quizNumber == len(user['courses'][index]['courseQuizzes']):
                    db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseId':courseChosenName}, {'$push': {'courses.$.courseQuizzes': {
                        'quizId': quizId,
                        'quizStart': datetime.now().strftime(date_format_str),
                        'quizMarks':[],
                        'quizScore': 0
                    }}})

                quizOptions = []
                updatedUser = db['test'].find_one({'_id': request.form.get('WaId')})
                questionNumber_ = len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1
                questionNumber = str(len(updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
                quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]

                quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
                db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': quizBusy}})
                quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])

                sendQuizQuestion(request.form.get('WaId'), user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)

                return ''
            
            else:
                db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': 'false'}})
                sendText(request.form.get('WaId'), user['langId'], "Invalid selection of course! The quiz has terminated. Please try again!")
                return ''

        if request.form.get('Body') in ['A', 'B', 'C']:
            
            index = int(user['quizBusy'].split("-")[0])
            quizNumber = int(user['quizBusy'].split("-")[1])
            quizId = user['quizBusy'].split("-")[2]
            questionNumber = user['quizBusy'].split("-")[3]
            quizChosen = db["questions"].find_one({ '_id': quizId})
            markPerQuestion = int(quizChosen['quizMarks'] / quizChosen['quizCount'])
            if int(questionNumber) >= quizChosen['quizCount']:
                if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1 ==  (quizChosen['quizCount']) and int(questionNumber) == quizChosen['quizCount']:
                    if request.form.get('Body') == quizChosen[questionNumber]['answer']:
                        
                        db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
                        db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})

                    else:
                        db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
                        db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizEnd': datetime.now().strftime(date_format_str)}})
                    
                updatedUser = db['test'].find_one({'_id': request.form.get('WaId')})
                completeMarks_ = updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']
                secondsTaken = int((datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizEnd']), date_format_str) - datetime.strptime((updatedUser['courses'][index]['courseQuizzes'][quizNumber]['quizStart']), date_format_str)).total_seconds())
                completeMarks = sum(completeMarks_) - (secondsTaken * 0.01)
                db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseQuizzes.quizId':quizId}, {'$set': {'courses.$.courseQuizzes.$[].quizScore': completeMarks}})
                
                sendText(request.form.get('WaId'), user['langId'], "Your quiz is over! You have scored " + str(completeMarks) + '!')
                db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': 'false'}})
                return ''

            if len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) < quizChosen['quizCount']:
                quizOptions = []
                questionNumber_ = int(questionNumber) + 1
                questionNumber = str(questionNumber_)
                # questionNumber = str(len(user['courses'][index]['courseQuizzes'][quizNumber]['quizMarks']) + 1)
                quizOptions = [quizChosen[questionNumber]['A'], quizChosen[questionNumber]['B'], quizChosen[questionNumber]['C']]
                
                if questionNumber_ > 1:
                    if request.form.get('Body') == quizChosen[str(questionNumber_ - 1)]['answer']:
                        db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': markPerQuestion}})
                        print('COERCTE')
                
                    else:
                        db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseQuizzes.quizId':quizId}, {'$push': {'courses.$.courseQuizzes.$[].quizMarks': 0}})
                        print('INCORCET')
                
                quizBusy = str(index) +'-'+str(quizNumber)+'-'+quizId+'-'+questionNumber
                db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': quizBusy}})
                quizImageId = getQuizPicture(quizChosen[questionNumber]['image'])
                sendQuizQuestion(request.form.get('WaId'), user['langId'], quizChosen[questionNumber]['question'], quizOptions, quizImageId)
                return ''    
        
        quizId = user['quizBusy'].split("-")[2]
        quizChosen = db["questions"].find_one({ '_id': quizId})
        courseChosenName = quizChosen['courseId']
        db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'quizBusy': 'false'}})
        sendText(request.form.get('WaId'), user['langId'], "Invalid selection! The quiz has been terminated. Please try again!")
        db['test'].update_one({'_id': request.form.get('WaId'), 'courses.courseId':courseChosenName}, {'$pop': {'courses.$.courseQuizzes': 1}})
        
        return ''
        
    
    if response_df.query_result.intent.display_name == 'Progress':
        sendTwoButton(request.form.get('WaId'), user['langId'], "Do you want to check progress for yourself?", ["myself", "someone"], ["Yes", "No"])
        return ''
    
    if response_df.query_result.intent.display_name == 'Progress - no':
        sendText(request.form.get('WaId'), user['langId'], "Please specify the mobile number of that person starting with '91'. For example, 919876543210.")
        return ''
    
    if response_df.query_result.intent.display_name == 'Progress - yes' or response_df.query_result.intent.display_name == 'Progress - no - number':
        specifiedUser = ''
        if (request.form.get('Body')).startswith("91"):
            foundUser = db['test'].find_one({'_id': request.form.get('Body')})
            if foundUser is None:
                sendText(request.form.get('WaId'), user['langId'], "Invalid number. Please check if the provided number was correct.")
            else:
                specifiedUser = foundUser
        
        else:
            specifiedUser = user
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
            sendText(request.form.get('WaId'), user['langId'], "No progress to show sadly!")
            return ''
        
        db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'resultBusy': { 'busy':'true', 'user': specifiedUser['_id']}}})
        sendList(request.form.get('WaId'), user['langId'], "Please choose the course to check progress", "Course", userCourses, userCourses, None, False)
        return ''
        
    if user['resultBusy']['busy'] == 'true':
        userCourses = []
        specifiedUser = db['test'].find_one({'_id': user['resultBusy']['user']})
        for i in range(0, len(specifiedUser['courses'])):
            if specifiedUser['courses'][i]['courseStartDate'] <= str(date.today()):
                # coursesRank.append(str(i + 1))
                userCourses.append((specifiedUser['courses'][i]['courseId']))
                
        if request.form.get('Body') in userCourses: 
            db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'resultBusy': { 'busy':'false', 'user': ''}}})
            studentProgress(request.form.get('WaId'), user['resultBusy']['user'], request.form.get('Body'))
            return ''
            
        else:
            db['test'].update_one({'_id': request.form.get('WaId')}, { "$set": {'resultBusy': { 'busy':'false', 'user': ''}}})
            sendText(request.form.get('WaId'), user['langId'], "Invalid course selection!")
            return ''
        return ''
    
    if user['UNIT-TESTING'] == '':
        # sendTwoButton(request.form.get('WaId'), user["langId"], "Why not explore the courses we offer? \n You can also know more about us!", ["courses", "organisation"], ["Explore courses now!", "Know more about us!"])
        # studentProgress(request.form.get('WaId'))
        # checkProfile(request.form.get('WaId'), user['langId'],'https://www.coursera.org/user/93bf6a1a88d976c68fabeeebf253f65')
        # sendTwoButton(request.form.get('WaId'), user['langId'], "Do you want to check progress for yourself or someone else?", ["myself", "someone"], ["For Myself", "For Someone Else"])
        print(getMedia('822272705766858'))
        return ''
        
        courseSelected = db["course"].find_one({'_id': 'math'})
        
        for i in range(0, len(user['courses'])):
            if user['courses'][1]['courseId'] == courseSelected['_id']:
                sendText(request.form.get('WaId'), user['langId'], "You have already enrolled in this course!")
                return ''
        
        db["test"].update_one({'_id': request.form.get('WaId')}, {"$push": {'courses':
        {
            'courseId': courseSelected['_id'],
            'courseType': courseSelected['courseType'],
            'courseStartDate': str(date.today()),
            'courseEndDate':  str(date.today() + timedelta(weeks=courseSelected['courseDuration'])),
            'courseQuizzes': [],
            'coursePayment': True,
        }
        }})
        # print(getCourseraProfile('https://www.coursera.org/user/93bf6a1a88d976c68fabeeebf253f65'))
        return ''
    
    if response_df.query_result.intent.display_name == 'Videos':
        result_videos = youtube(response_df.query_result.query_text)
        print(result_videos)
        for video in result_videos:
            sendText(request.form.get('WaId'), langId, video['url'] + ' | ' + video['title'])
        return ''
    
    if response_df.query_result.intent.display_name == 'WebSearch':  # Google JEE datde
        result_search = google_search(response_df.query_result.query_text)
        sendText(request.form.get('WaId'), langId, result_search)
    
    else:
        # quiz_bot(db, 'M1')
        now = datetime.datetime.now()
        print(now.year, now.month, now.day,now.hour, now.minute, now.second)
        print(type(now.year), type(now.month), type(now.day),type(now.hour), type(now.minute), type(now.second))
        print(request.form.get('From'))
        # send_message(request.form.get('From'), response_df.query_result.fulfillment_text,'')
        print(response_df.query_result.fulfillment_text)
        print(response_df.query_result.intent.display_name)
        print(request.form)
        sendText(request.form.get('WaId'),user['langId'], response_df.query_result.fulfillment_text)
    
    return ''


if __name__ == '__main__':
    app.run(debug=False)
