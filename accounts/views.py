from .permissions import IntervieweePermission, InterviewerPermission

from django.http import HttpResponse
from rest_framework.generics import GenericAPIView, ListAPIView

from django.http.response import JsonResponse
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from accounts.utils import send_mail
from .serializers import *

from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status, permissions


class IntervieweeRegisterAPI(GenericAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = IntervieweeRegisterSerializer

	def post(self, request, *args, **kwargs):
		data = request.data
		serializer = self.serializer_class(data=data)
		serializer.is_valid(raise_exception=True)
		interviewee = serializer.save()
		user = User.objects.get(interviewee=interviewee)
		try:
			send_mail(user=user, html='',
					text='Account Created Successfully',
					subject='User Verification',
					from_email='testsender1507@gmail.com',
					to_emails=[user.email])
		except:
			pass
		return Response({'Success': 'Your account is successfully created'}, status=status.HTTP_201_CREATED)


class IntervieweeAPI(APIView):
	serializer_class = IntervieweeRegisterSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		serializer = self.serializer_class(request)
		print(serializer.data)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def put(self, request):
		interviewee=Interviewee.objects.get(user=request.user)
		# print(request.user)
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid()
		print("Here")
		serializer.update(interviewee, request.data)
		return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class IntervieweeSapAPI(APIView):
	serializer_class = Interviewee_GET_Serializer
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request, sapid):
		try:
			user = User.objects.get(sapid =sapid)
			interviewee = Interviewee.objects.get(user = user)
			token = Token.objects.get(user=user)
		except:
			JsonResponse("interviewee not found", status= status.HTTP_404_NOT_FOUND)
		serializer = self.serializer_class(interviewee)
		final_value = serializer.data
		final_value['token'] = token.key
		print(final_value)
		return JsonResponse(final_value , safe=False)


class LoginAPI(GenericAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = LoginSerializer
	
	def post(self,request,*args,**kwargs ):
		sapid = request.data.get('sapid',None)
		password = request.data.get('password',None)
		user = authenticate(username = sapid, password = password)
		if user:
			login(request,user)
			token = Token.objects.get(user=user)
			if Interviewer.objects.filter(user = user):
				is_interviewer = True
			else:
				is_interviewer = False
			return Response({'token' : token.key,'sapid' : user.sapid,'is_interviewer' : is_interviewer},status = status.HTTP_200_OK)
			
		return Response('Invalid Credentials',status = status.HTTP_404_NOT_FOUND)


class ApplicationView(GenericAPIView):
	permission_classes = [IntervieweePermission]
	serializer_class = ApplicationSerializer

	def get(self,request):
		try:
			interviewee = Interviewee.objects.get(user = request.user)
			try:
				application = Application.objects.get(interviewee = interviewee)
				serializer = ApplicationSerializer(application)
				return Response(serializer.data)
			except:
				return Response({"message":"Application not found"}, status= status.HTTP_404_NOT_FOUND)
		except:
			return Response({"message":"interviewee not found"}, status= status.HTTP_404_NOT_FOUND)


	def post(self,request,*args,**kwargs):
		serializer = self.serializer_class(data=request.data, context={'request': request})
		serializer.is_valid(raise_exception = True)
		response = serializer.create(request.data)
		return response

	def put(self,request,*args,**kwargs):
		interviewee = Interviewee.objects.get(user = request.user)
		application = Application.objects.get(interviewee = interviewee)
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		response = serializer.update(request.data,application)

		return response
		
class TaskAPI(ListAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = TasksSerializer
	model = serializer_class.Meta.model

	def get_queryset(self):
		queryset = Task.objects.all()
		return queryset

class ResourcesAPI(ListAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = StackSerializer

	def get_queryset(self):
		queryset = Stack.objects.all()
		return queryset


class PanelAPI(GenericAPIView):
	permission_classes = [InterviewerPermission]
	serializer_class = PanelSerializer

	def get(self,request):
		interviewer = Interviewer.objects.get(user = request.user)
		panels = Panel.objects.filter(interviewers = interviewer)
		if not panels :
			return Response({"message":"No Panel has been assigned to you"}, status= status.HTTP_404_NOT_FOUND)
		serializer = PanelSerializer(panels, many = True)
		return Response(serializer.data)

class CandidateAPI(GenericAPIView):
	permission_classes = [InterviewerPermission]
	serializer_class = ApplicationSerializer

	def get(self,request,sapid):
		
		interviewee = Interviewee.objects.get(user = sapid)
		application = Application.objects.get(interviewee = interviewee)
		serializer = ApplicationSerializer(application)
		return Response(serializer.data)


class RemarksAPI(GenericAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = RemarksSerializer

	def post(self, request):

		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception = True)
		response = serializer.create(request.data)

		return Response(response, status=status.HTTP_202_ACCEPTED)

	
class ScoreAPI(GenericAPIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = ScoreSerializer

	def post(self, request):

		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception = True)
		response = serializer.create(request.data)

		return Response(response, status=status.HTTP_202_ACCEPTED)

class ScorecardGetAPI(GenericAPIView):
	permission_classes = [InterviewerPermission]
	serializer_class = ScoreSerializer

	def get(self,request,sapid, stack):
		
		interviewee = Interviewee.objects.get(user=sapid)
		app = Application.objects.get(interviewee=interviewee)
		app_stack = ApplicationStack.objects.filter(application=app).get(name=stack)
		scorecard = Score.objects.get(stack = app_stack)
		serializer = GetScoreSerializer(scorecard)
		return Response(serializer.data)


class QuestionAPI(ListAPIView):
	permission_classes = [InterviewerPermission]
	serializer_class = QuestionSerializer

	def get_queryset(self):
		
		stack = self.kwargs['stack']
		stack_obj = Stack.objects.get(name= stack)
		queryset = Question.objects.filter(stack = stack_obj)
		return queryset


class InterviewAPI(GenericAPIView):
	permission_classes = [IntervieweePermission]
	serializer_class = Interviewee_Panel_Serializer
	
	def get(self,request):
		interviewee = Interviewee.objects.get(user = request.user)
		panels = Panel.objects.filter(interviewees = interviewee)
		if not panels:
			assign_pannels_to_intervieews()
			# return Response({"message" : "Interviews have not been scheduled yet"})
		# else:
		serializer = Interviewee_Panel_Serializer(panels, many = True)
		return Response(serializer.data)


# pending
class Scheduler(GenericAPIView):

	permission_classes = [InterviewerPermission]
	serializer_class = PanelSerializer

	def get(self,request):
		dict_of_stacks = {"django_list": ApplicationStack.objects.filter(name = 'Django'),
		"frontend_list" : ApplicationStack.objects.filter(name = 'Frontend'),
		"node_list" : ApplicationStack.objects.filter(name = 'Node'),
		"native_list" : ApplicationStack.objects.filter(name = 'ReactNative'),
		"flutter_list" : ApplicationStack.objects.filter(name = 'Flutter'),
		"fdjango_list" : ApplicationStack.objects.filter(name = 'FullstackDjango'),
		"fnode_list" : ApplicationStack.objects.filter(name = 'FullstackNode'),
		}

		panels = Panel.objects.all()
		no_of_panels = panels.count()
		count = [0]*no_of_panels
		print(count)
		panel_dict = {}
		for panel in panels:
			interviewers = panel.interviewers.all()
			stack_list =[]
			for interviewer in interviewers:
				#Assuming every interviewer has only one stack
				stack = interviewer.stack
				stack_list.append(stack.name)

			panel_dict[panel] = stack_list

		# stack_list.clear()

		print(panel_dict)
				
			
		# for stack in dict_of_stacks:
		# 	print(stack)
		# 	for i in dict_of_stacks[stack]:
		# 		application = i.application
		# 		interviewee = application.interviewee
		# 		print(interviewee)
		# 		if interviewers.filter(stack = "Django"):
		# 			if 
		interviewee_dict = {}
		applications = Application.objects.all()
		interviewees = []
		for application in applications:
			interviewee_stacks = []
			interviewee = application.interviewee
			interviewees.append(interviewee)
			application_stacks = ApplicationStack.objects.filter(application = application)
			for app_stack in application_stacks:
				interviewee_stacks.append(app_stack.name)
				interviewee_dict[interviewee] = interviewee_stacks
		
		print(interviewee_dict)
		
		print(interviewees)

# Allot where all stacks are present in a single panel
		for interviewee in interviewee_dict:
			# list_of_stacks = []
			list_of_app_stacks = interviewee_dict[interviewee]
			index = 0
			for panel in panel_dict:
				index +=1
				list_of_pan_stacks = panel_dict[panel]
				result =  all(elem in list_of_pan_stacks  for elem in list_of_app_stacks)
				if result:
					panel.interviewees.add(interviewee)
					# interviewee_dict.pop(interviewee)
					interviewees.remove(interviewee)
					count[index]+=1

		print(interviewees)
		interviewees2 = interviewees

# Allocation for the rest where multiple interviews are required(DIvide this into, single allocation and at least 2 are common)
		for interviewee in interviewees:
			list_of_app_stacks = interviewee_dict[interviewee]
			for panel in panel_dict:
				list_of_pan_stacks = panel_dict[panel]
				# result =  any(elem in list_of_pan_stacks  for elem in list_of_app_stacks)
				# common = [i for i in list_of_pan_stacks if i in list_of_app_stacks]
				# if result:
				# 	panel.interviewees.add(interviewee)
				# 	list_of_app_stacks.remove(common)
				# 	if not list_of_app_stacks:
				# 		interviewees2.remove(interviewee)

				for app_stack in list_of_pan_stacks:
					for pan_stack in list_of_app_stacks:
						if pan_stack == app_stack:
							panel.interviewees.add(interviewee)
							common = app_stack
					try:
						list_of_app_stacks.remove(common)
						if not list_of_app_stacks:
							interviewees2.remove(interviewee)
					except:
						pass

		print(interviewees2)

		return HttpResponse("None")


# def create_pannels(Interviewers):
# 	list_int_obj = [] 
# 	for intview_obj in Interviewers:
# 		list_int_obj.append(intview_obj)
	
# def get_stack(stack_code):
# 	if stack_code==1:
# 		return 'Fr'
# 	elif stack_code==2:
# 		return 'D'
# 	elif stack_code==3:
# 		return 'N'
# 	elif stack_code==4:
# 			return 'R'
# 	elif stack_code==5:
# 			return 'Fn'
# 	elif stack_code==6:
# 			return 'Fl'
# 	elif stack_code==7:
# 			return 'Fd'
	
# def get_application_stack(obj_id):
# 	appl_stack = ApplicationStack.objects.filter(application=obj_id).name
# 	return appl_stack

# def assign_pannels_to_intervieews(Interviewers, applications):

# 	dict_of_stacks = {
# 		"django_list": ApplicationStack.objects.filter(name = 'Django'),
# 		"frontend_list" : ApplicationStack.objects.filter(name = 'Frontend'),
# 		"node_list" : ApplicationStack.objects.filter(name = 'Node'),
# 		"native_list" : ApplicationStack.objects.filter(name = 'ReactNative'),
# 		"flutter_list" : ApplicationStack.objects.filter(name = 'Flutter'),
# 		"fdjango_list" : ApplicationStack.objects.filter(name = 'FullstackDjango'),
# 		"fnode_list" : ApplicationStack.objects.filter(name = 'FullstackNode'),
# 		}
	
# 	panels = Panel.objects.all()
# 	panel_num = panels.count()
# 	panel_stack_str_list = []

	# for i in range(0, panel_num):
	# 	panel_stack_str =''
	# 	for j in panels[i].interviewers:
	# 		stack_code = j.stack
	# 		stack_name = get_stack(stack_code)
	# 		panel_stack_str+=stack_name
	# 	panel_stack_str_list.append(panel_stack_str)

# 	applications = Application.objects.all()
# 	application_num = applications.count()
# 	application_stack_str_list = []

# 	for i in range(0, application_num):
# 		application_stack_str =''
# 		for obj_id in applications[i].id:
# 			stack_code = get_application_stack(obj_id)
# 			stack_name = get_stack(stack_code)
# 			panel_stack_str+=stack_name
# 		application_stack_str_list.append(panel_stack_str)
	

# def get_info(self, request):

# 	applications = Application.objects.all()
# 	Interviewers = Interviewer.objects.all()

# 	# create_pannels(Interviewers)
# 	assign_pannels_to_intervieews(Interviewers, applications)


def getPanelInst(appl_stack):
	# panels = Panel.objects.all()
	panels = Panel.objects.filter(interviewers__stack__name = appl_stack)
	for panel_inst in panels:
		if panel_inst.interviewees.count() <= 5:
			return panel_inst

def assign_pannels_to_intervieews():
	application_stack = ApplicationStack.objects.all()
	
	for appl_stack_inst in application_stack:
		
		panel = getPanelInst(appl_stack_inst.name)
		print(panel)
		interviewee_inst = appl_stack_inst.application.interviewee
		print(appl_stack_inst.application)
		print(appl_stack_inst)
		#add interviewee to panel and save
		panel.interviewees.add(interviewee_inst)
	
class Candidate_test_API(GenericAPIView):
	permission_classes = [InterviewerPermission]
	serializer_class = ViewCandidateSerializer

	def get(self,request,sapid):
		
		interviewee = Interviewee.objects.get(user = sapid)
		application = Application.objects.get(interviewee = interviewee)
		serializer = ViewCandidateSerializer(application)
		
		return Response(serializer.data)

class All_Panel_data(GenericAPIView):
	permission_classes = [InterviewerPermission]
	serializer_class = PanelSerializer

	def get(self,request):
		panel_details=Panel.objects.all()
		serializer = PanelSerializer(panel_details, many = True)
		return Response(serializer.data)