from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from myapp_RC.models import *
from django.contrib.auth.models import User # using a django in built library to store or register the user in our database
from django.contrib import messages  # to display messagess after the the user has registered successfully
from django.shortcuts import redirect, render #to use the 'redirect' function in line 28
from django.contrib.auth import login,authenticate, logout  #refer line 39, 42
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import re
import numpy as np
import random
import datetime
import requests
import time
import json
from django.http import JsonResponse

def home(request):
    return render(request, "myapp_RC/signin.html")

def signup(request):
    
    if request.method == "POST":
        nusername = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        nemail = request.POST['email']
        pass2 = request.POST['pass2']
        pass1 = request.POST['pass1']
        mobno = request.POST['mobno']
        category = request.POST['categories']
        
        if User.objects.filter(username = nusername).exists() :
            messages.error(request,"Username already  Exists")
        elif  User.objects.filter(email = nemail).exists():
            messages.error(request,"Email is already register")
        elif pass1 != pass2 :
            messages.error(request,"Confirmed Password did not match the entered Password")
        elif (len(pass1) < 8):
            messages.error(request,"Password should contain atleast 8 characters")
        elif not re.search("[a-z]", pass1):
            messages.error(request,"Password should contain atleast one Lowercase letter")
        elif not re.search("[A-Z]", pass1):
            messages.error(request,"Password should contain atleast one Uppercase letter")
        elif not re.search("[0-9]", pass1):
            messages.error(request,"Password should contain atleast one Number")
        elif not re.search("[_@!#%$]", pass1):
            messages.error(request,"Password should contain atleast one Special character")
        elif mobno.isnumeric() == False or len(mobno) != 10 :
            messages.error(request,"Enter a valid Mobile number")
        else :    
            myuser=User.objects.create_user(username=nusername, password=pass1, email=nemail)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.save()
            if category == '1':
                newuserprofile=Profile(user = myuser, mob_no = mobno, category = True)

            elif category == '0':
                newuserprofile=Profile(user = myuser, mob_no = mobno, category = False)
            # newuserprofile=Profile(user = myuser, mob_no = mobno)
            newuserprofile.save()

            messages.success(request, "Your account has been successfully created!")
            return redirect('/signin')   # to redirect the user to the signin page once the successful registration messages is displayed
        return redirect('/gquwa12evrat')
    return render(request, "myapp_RC/signup.html")

def signin1(request):
    context ={}
    try :
        if request.method == 'POST':
            username = request.POST['username']
            pass1 = request.POST['pass1']
            team_value = request.POST.get('flexRadioDefault') # 1 for team, 2 for individual
            user = authenticate(username = username, password = pass1)

            if user is not None:
                login(request, user)
                fname = user.first_name

                # =====================
                profile = Profile.objects.get(user = user)

                if profile.category == True:   # True for Junior
                    allQues = Question.objects.filter(is_junior = True)
                else:   #False for Senior
                    allQues = Question.objects.filter(is_junior = False)
                
                # allQues = Question.objects.all()
                # queIndex = np.arange(1, len(allQues)).tolist()
                queIndex = [q.id for q in allQues]
                random.shuffle(queIndex)

                queIndex = queIndex[:11]

                profile.questionIndexList = str(queIndex)
                if profile.newlogin == False :
                    profile.newlogin = True
                else :
                    messages.error(request, "Already Logged in via other device")
                    return render(request, 'myapp_RC/signin.html', context)
                profile.save()
                # =====================
                return redirect('Instruction')

            else:
                messages.error(request, "Bad Credentials")
                return render(request, "myapp_RC/signin.html")
            
    except :
        return redirect ('SignIn')

    return render( request, "myapp_RC/signin.html")


################################################

def signin(request):
    # try:
        if request.method == 'POST':
            print("aaya")
            username = request.POST['username']
            pass1 = request.POST['pass1']
            isTeam = request.POST.get('flexRadioDefault')
            print(isTeam,username)
            if isTeam == "1":
                isTeam = True
            else:
                isTeam = False
            print(isTeam, "isteam", type(isTeam))
        
            user = authenticate(username = username, password = pass1)

            if user is not None:
                login(request, user)
                fname = user.first_name

                # =====================
                profile = Profile.objects.get(user = user)

                if profile.category == True:   # True for Junior
                    allQues = Question.objects.filter(is_junior = True)
                else:   #False for Senior
                    allQues = Question.objects.filter(is_junior = False)
                

                queIndex = [q.id for q in allQues]
                random.shuffle(queIndex)

                queIndex = queIndex[:11]

                profile.questionIndexList = str(queIndex)
                if profile.newlogin == False :
                    profile.newlogin = True
                else :
                    return render(request, 'myapp_RC/signin.html')
                profile.save()
                # =====================
                return redirect('Instruction')

            else:
                url = 'https://api.credenz.in/api/verify/user/'
                headers = {'Content-Type': 'application/json'}

                data = {
                    'username': username,
                    'password': pass1,
                    'event': 'rc',
                }
                
                if isTeam:
                    data['is_team'] = "true"
                    print("here")
                else:
                    data['is_team'] = None # empty string

                response = requests.post(url, headers=headers, json=data)
                print("json  ",json)
                
                if response.status_code == 200:
                    print("mai aagya")
                    response = response.json()
                    user = User.objects.create_user(username=username, password=pass1 )
                    if not isTeam:
                        try:
                            category = not response['user']['senior']
                            first_name = response['user']['first_name']
                            last_name = response['user']['last_name']
                        except:
                            messages.error(request, "Invalid Credentials")
                            return redirect('SignIn')
                    else: # if team
                        category = True
                        first_name = response['users'][0]['first_name']
                        last_name = response['users'][0]['last_name']

                        # display name
                        display_name = ""
                        for user1 in response['users']:
                            display_name += user1['username'] + " &"
                            if user1['senior']:
                                category = False
                        display_name = display_name[:-2]
                        print(display_name)
                    profile = Profile(user=user, category=category)
                    profile.save()
                    if profile.category == True:   # True for Junior
                        allQues = Question.objects.filter(is_junior = True)
                    else:   #False for Senior
                        allQues = Question.objects.filter(is_junior = False)
                

                    queIndex = [q.id for q in allQues]
                    random.shuffle(queIndex)

                    queIndex = queIndex[:11]

                    profile.questionIndexList = str(queIndex)
                    profile.save()      
                    
                    login(request, user)
                    messages.success(request, "Login Successful")
                    return redirect('Instruction')
                messages.error(request, "Bad Credentials")
                return redirect('SignIn')
    # except :
        # return redirect ('SignIn')        
    

        return render( request, "myapp_RC/signin.html")

###########################################


def signout(request):
    try :
        ruser = request.user
        profile = Profile.objects.get(user = ruser)
        profile.remainingTime = profile.remainingTime -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None)).seconds 
        profile.logoutTime = datetime.datetime.now()
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect('/home')
    except :
        return redirect('/home')

@login_required(login_url = 'SignIn')
def instruction(request):
    try :
        if request.method == 'POST':
            ruser = request.user
            profile = Profile.objects.get(user = ruser)
            profile.startTime = datetime.datetime.now()
            profile.save()
            print("profile.startTime :",profile.startTime)
            request.method = "GET"
            return QuestionView(request)
    except :
        print("ithe allo .....")
        return redirect('Instruction')
    return render(request,"myapp_RC/instruction.html")

@never_cache
@login_required(login_url = 'SignIn')
def QuestionView(request):
    
    context = { }
    ruser = request.user
    profile = Profile.objects.get(user = ruser)
    # print("dwer :",request.POST["submit"] )
    
    
    # if request.POST.get('submit') == int(profile.quesno):
    
    context['currquestNum'] = profile.quesno
    qList = eval(profile.questionIndexList)

    currQues = Question.objects.get(id=qList[0])
    
    context["currquest"] = currQues.question
    context['plusmrks'] = 4
    context['minusmrks'] = 0
    context["profile"] = profile
    context["users"] = list(Profile.objects.filter(category = bool(profile.category)).order_by('marks',"accuracy").reverse())
    print("lb :",context["users"])
    if profile.lifeline1_count == 3 and profile.lifeline1_using == False:
        print("In here qid generation")
        profile.lifeline1_status = True
        currQueslist = EasyQuestion.objects.all()
        profile.lifeline1_question_id = (random.randrange(len(currQueslist)))
        print("EASY QID: ", profile.lifeline1_question_id)
        profile.save()

    print(request.POST)
    print(request.GET)
    if request.method == 'GET':
        print("INSIDE GET RN")
        if profile.isFirstTry == 0:
            context["res1"] = profile.cache
        context["currquest"] = currQues.question
        context['plusmrks'] = profile.plusmrks
        context['minusmrks'] = profile.minusmrks
        context["profile"] = profile
        context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds
        return render(request, 'myapp_RC/question.html',context)
    
    print("POST->",str(request.POST.get("submit", False)))
    print("GET->",str(request.GET.get("submit", False)))
    if True:
        try:
            if profile.isFirstTry:
                print("if")
                profile.cache = request.POST["res1"]
                profile.save()
            else:
                print("else")
                print(profile.cache)
                # t = request.POST["res2"]
                t = request.POST.get("res2", False)
                if t == False:
                    raise Exception()
            print("Smooth slip")
        except:
            print("RELOAD except")
            print("SADNESS INTENSIFIES: ",profile.isFirstTry)
            
            context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds
            return render(request, 'myapp_RC/question.html',context)
        
    profile.accuracy = (profile.correctanswers/(profile.quesno))*100

    profile.save()

    context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds 
    
    
    if profile.accuracy > 50 and profile.quesno > 2 and profile.lifeline3_status == False and profile.lifeline3_used == False:
        profile.lifeline3_status = True
    
    
    if profile.isFirstTry == False :
        context["resp1"] = User_Response.objects.filter(user = ruser, user_profile = profile, quetionID = qList[0], isSimpleQuestion = False).first().response1
    
    if profile.lifeline1_using == True:
        print("In here , lifeline1_using true")
        givenAns = request.POST["res1"]
        profile.lifeline1_status = False  #to disable Simple Question button
        profile.simpleQuestionUsed = True 
        context["easyQuestion"] = False
        profile.lifeline1_using = False
        profile.plusmrks = 4
        profile.minusmrks = 0
        currQuest = EasyQuestion.objects.get(easyquestion_no = profile.lifeline1_question_id)

        if User_Response.objects.filter(user_profile = profile, quetionID = currQuest.easyquestion_no, response1 = givenAns, user = profile.user, isSimpleQuestion = True).exists():
            pass
        else:
            tempSol = User_Response(user_profile = profile, quetionID = currQuest.easyquestion_no, response1 = givenAns, user = profile.user, isSimpleQuestion = True)
            tempSol.save()
        print("Easy Given ans", givenAns)
        print("Easy Question", currQuest.easyquestion)
        print("Easy Answer", currQuest.easyanswer)

        if str(givenAns) == str(currQuest.easyanswer):
            profile.marks += 4
            profile.correctanswers+=1
        else:
            profile.marks -= 4
        
        # profile.save()
        profile.quesno += 1

        profile.questionIndexList = str(qList[1:])


        print(" now qlist = ", profile.questionIndexList)
        print("(In l1 in post)profile.simpleQuestionUsed = ", profile.simpleQuestionUsed)
        print("(In l1 in post)profile.lifeline1_status", profile.lifeline1_status)
            
        profile.isFirstTry = True
        print("In lifeline post profile.isFirstTry = ", profile.isFirstTry)
        print("question number before saving ",profile.quesno)
        print("Marks before save", profile.marks)
        profile.save()
        print("Marks after save", profile.marks)
        print("Question number after saving ",profile.quesno)
        request.method = "GET"
        # context['profile'] =  profile
        return QuestionView(request)

    if profile.quesno == 11 or profile.remainingTime == 0:
        profile.logoutTime = datetime.datetime.now()
        profile.save()
        return redirect('Result')
    print("====")

    context['plusmrks'] = profile.plusmrks
    context['minusmrks'] = profile.minusmrks
    
    if request.method == "POST" :
        # print("Checked Status: ",profile.lifeline2_status)
        print("Question: ",profile.quesno)
        print("In Post")
        print("profile.lifeline2_status:",profile.lifeline2_status)
        
        qList = eval(profile.questionIndexList)
        if profile.isFirstTry:
            print("First try true")
            profile.plusmrks = 4
            profile.minusmrks = 0
            givenAns = request.POST["res1"]

            if User_Response.objects.filter(user_profile = profile, quetionID = qList[0], response1 = givenAns, user = profile.user, isSimpleQuestion = False).exists() == False:
                tempSol = User_Response(user_profile = profile, quetionID = qList[0], response1 = givenAns, user = profile.user, isSimpleQuestion = False)
                tempSol.save()


            print("Planning to put if here!")
            if profile.cacheAnswer != int(givenAns):
                profile.cacheAnswer = int(givenAns)
                if str(givenAns) == str(currQues.answer):
                    print("correct answer")
                    if profile.lifeline2_status and profile.lifeline2_checked == False:
                        profile.lifeline2_checked = True
                        profile.lifeline2_status = False
                        print("Timer Up")
                        profile.remainingTime += 300
                        profile.lifeline2_secondattempt = False
                    profile.correctanswers += 1
                    
                    profile.marks += 4
                    profile.quesno += 1
                    profile.isFirstTry = True
                    
                    profile.questionIndexList = str(qList[1:])
                    print("first now qlist = ", profile.questionIndexList)
                    if profile.lifeline1_count < 3 :
                        profile.lifeline1_count += 1
                
                else:
                    print("answer Wrong")
                    if profile.lifeline2_status and profile.lifeline2_checked == False:                    
                        print("Timer Down")
                        profile.remainingTime -= 120 
                        profile.lifeline2_secondattempt = True

                    profile.plusmrks = 2
                    profile.minusmrks = -2   
                    print("toggle in first response")
                    profile.isFirstTry = False  
                    profile.save()

        elif profile.isFirstTry == False:

            givenAns = request.POST["res2"]
            tempSol = User_Response.objects.filter(user = ruser, user_profile = profile, quetionID = qList[0], isSimpleQuestion = False).first()
            tempSol.response2 = givenAns
            tempSol.save()
            profile.plusmrks = 4
            profile.minusmrks = 0
            
            if str(givenAns) == str(currQues.answer):
                if profile.lifeline2_status and profile.lifeline2_checked == False:
                    profile.lifeline2_checked = True
                    profile.lifeline2_status = False
                    print("Timer Up")
                    profile.remainingTime += 300
                    profile.lifeline2_secondattempt = False
                profile.marks += 2
                profile.correctanswers += 1

            else:
                if profile.lifeline2_status and profile.lifeline2_checked == False:
                    profile.lifeline2_checked = True
                    profile.lifeline2_status = False
                    print("Timer Down")
                    profile.remainingTime -= 180
                    profile.lifeline2_secondattempt = False
                profile.marks -= 2

            
            profile.quesno += 1
            profile.isFirstTry = True
            qList = eval(profile.questionIndexList)
            profile.questionIndexList = str(qList[1:])
            print("second now qlist = ", profile.questionIndexList)
        
        
        
        
        profile.save()
        # print("Profile Saved")
        request.method = "GET"
        return QuestionView(request)
        # return redirect(QuestionView)
    

    return render(request, 'myapp_RC/question.html', context)

def leaderboard(request) :
    context = {}
    context["usersjunior"] = list(Profile.objects.filter(category = True).order_by('marks',"remainingTime").reverse())

    context["userssenior"] = list(Profile.objects.filter(category = False).order_by('marks',"remainingTime").reverse())
    # context["users"] = list(Profile.objects.filter(category = True).order_by('marks',"remainingTime").reverse())
    return render(request, 'myapp_RC/leaderboard.html', context)

@login_required(login_url='SignIn')
def result(request):
    try:
        context = {}
        ruser = request.user
        profile = Profile.objects.get(user=ruser)
        context["profile"] = profile
        context["users"] = list(Profile.objects.all().order_by(
            'marks', 'remainingTime').reverse())
        context["rank"] = context["users"].index(profile) + 1
        profile.logoutTime = datetime.datetime.now()
        # context["q_correct"] = profile.accuracy
        # context["q_correct"] = round(
        #     ((profile.correctanswers)/(profile.quesno-1))*100, 2)
        # if profile.quesno == 1:
        profile.accuracy = round((profile.correctanswers/(profile.quesno))*100,2)
        # else:
        #     profile.accuracy = round((
        #         profile.correctanswers/(profile.quesno-1))*100)
        print("Accuracy: ", profile.accuracy, "%")
        context["q_correct"] = profile.accuracy
        if profile.remainingTime >= 2300:
            profile.remainingTime = 0
        context["timetaken"] = round(
            ((1800 - profile.remainingTime)/1800) * 100, 2)
        context["totalques"] = profile.quesno - 1
        profile.save()
        logout(request)
    except:
        return redirect('SignIn')

    return render(request, 'myapp_RC/result.html', context)


@login_required(login_url = 'SignIn')
def lifelineone(request):
    print("===")
    print("In Lifeline one")
    context = { }
    ruser = request.user
    profile = Profile.objects.get(user = ruser)
    profile.lifeline1_using = True
    profile.lifeline1_count = 0
    profile.lifeline1_status = False
    print("(In l1 before post)profile.simpleQuestionUsed = ", profile.simpleQuestionUsed)
    print("(In l1 before post)profile.lifeline1_status", profile.lifeline1_status)
    
    profile.plusmrks = 4
    profile.minusmrks = -4
    context['plusmrks'] = profile.plusmrks
    context['minusmrks'] = profile.minusmrks
    qList = eval(profile.questionIndexList)

    context["easyQuestion"] = True
    context["isSimpleQuestion"] = profile.simpleQuestionUsed

    context['currquestNum'] = profile.quesno

    # currQueslist = EasyQuestion.objects.all()

    # currQuest = EasyQuestion.objects.get(easyquestion_no = (random.randrange(len(currQueslist))))
    print("Iska value to ye hai ->", profile.lifeline1_question_id)
    currQuest = EasyQuestion.objects.get(easyquestion_no = profile.lifeline1_question_id)
    # currQuest = currQueslist[easyquestion_no=(random.randrange(len(currQueslist)).easyques)]
    # currQuest = EasyQuestion.objects.get(easyquestion_no=qList[0])

    context["currquest"] = currQuest.easyquestion
    context["profile"] = profile

    context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds 
    profile.startTime = datetime.datetime.now()
    profile.remainingTime = context["second1"]
       
    if profile.quesno == 11 or profile.remainingTime == 0 :
        profile.logoutTime = datetime.datetime.now()
        profile.save()
        return redirect('Result')
    
    print("(In l1 after post)profile.simpleQuestionUsed = ", profile.simpleQuestionUsed)
    print("(In l1 after post)profile.lifeline1_status", profile.lifeline1_status)
    print("===")
    profile.isFirstTry = True
    profile.save()
    return render(request, 'myapp_RC/question.html', context)


def lifeLine3(request):
    ruser = request.user
    profile = Profile.objects.get(user = ruser)
    profile.lifeline3_status = False
    profile.lifeline3_used = True
    profile.save()
    print("---")
    try :
        print("in L3")
        print("======================")
        profile.lifeline3_used = True
        profile.save()
        if request.method == "GET":
            userQuery = request.GET["question"]
            allKeys = chatGPTLifeLine.objects.all()
            allKeys2 = chatGPTLifeLine.objects.filter(isDepleted = False)

            if len(allKeys2) == 0:
                return JsonResponse({'question': {userQuery},'answer': "Somethingwentwrong"})
            
            isproblem = True

            #==== remove loop after testing=====
            for k in allKeys:
                print(k.key, k.numUsed, k.isDepleted)
            #===================================
            currentTime = time.time()

            for key in allKeys2:
                print(f"Key last used {currentTime - key.lastUsed} seconds ago")
                print(f"{currentTime} - {key.lastUsed} = {currentTime - key.lastUsed}")
                
                if True:
                    if key.numUsed < 3:
                        isproblem = False
                        key.numUsed += 1
                        key.lastUsed = time.time()
                        key.save()
                        break
                    else:
                        print("Key is depleted")
                        key.isDepleted = True
                        key.save()
                else:
                    print(f"is in use: {key}")

            if isproblem:
                return JsonResponse({'question': {userQuery},'answer': "Somethingwentwrong"})
            
            answerResp = GPT_Link(userQuery, key= key)

            return JsonResponse({'question': userQuery,'answer': answerResp})
    except :
        return JsonResponse({'question': {userQuery},'answer': "Somethingwentwrong"})


def GPT_Link(message, key):
    URL = "https://api.openai.com/v1/chat/completions"

    print(f"using key: {key}")

    payload = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": message}],
    "temperature" : 1.0,
    "top_p":1.0,
    "n" : 1,
    "stream": False,
    "presence_penalty":0,
    "frequency_penalty":0,
    }

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {key}"
    }

    response = requests.post(URL, headers=headers, json=payload, stream=False)
    print("Here==========",response.content)

    # if "choices" not in json.loads(response.content):
    #     return "Somethingwentwrong"
    
    return (json.loads(response.content)["choices"][0]['message']['content'])

@login_required(login_url = 'SignIn')
def lifeline2(request):
    print("Inside l2 function")

    ruser = request.user
    profile = Profile.objects.get(user = ruser)
    profile.lifeline2_status = True
    profile.lifeline2_superstatus = False
    profile.save()

    return JsonResponse({'success':'True'})
       
  
def webadmin(request) :
    
    if request.method == 'POST':
        superusername = request.POST['superusername']
        superpwd = request.POST['pass1']

        username = request.POST['username']
        password = request.POST['pass']

        superuser = authenticate(username = superusername, password = superpwd)
        user = authenticate(username = username, password = password)

        if superuser.is_superuser and user is not None:
            profile = Profile.objects.get(user = user)
            profile.remainingTime += int(request.POST['tabs'])
            profile.newlogin = False
            profile.save()

            messages.success(request, "Updated")
            return render(request, "myapp_RC/signin.html")

        else:
            messages.error(request, "Bad Credentials")
            return render(request, "myapp_RC/signin.html")
        
    return render (request, "myapp_RC/webadmin.html")

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def savetimer(request) :
    if request.method == 'POST':
        context = {}
        ruser = request.user
        profile = Profile.objects.get(user = ruser)
        context["second1"] = (datetime.timedelta(seconds = profile.remainingTime) -(datetime.datetime.now() - datetime.datetime.fromisoformat(str(profile.startTime)).replace(tzinfo=None))).seconds
        profile.startTime = datetime.datetime.now()
        profile.remainingTime = context["second1"]
        profile.save()
        return JsonResponse({'success':'True'})
    
def error_view(request, exception):
    return render(request, 'myapp_RC/error.html')

def error_500(request):
    return render(request, 'myapp_RC/error.html')