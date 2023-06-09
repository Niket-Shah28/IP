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

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

class IntervieweeRegisterAPI(GenericAPIView):
	permission_classes = [permissions.AllowAny]
	serializer_class = IntervieweeRegisterSerializer

	def post(self, request, *args, **kwargs):
		data = request.data
		serializer = self.serializer_class(data=data)
		serializer.is_valid(raise_exception=True)
		interviewee = serializer.save()
		user = User.objects.get(interviewee=interviewee)
		# try:
		# 	send_mail(user=user, html='',
		# 			text='Account Created Successfully',
		# 			subject='User Verification',
		# 			from_email='testsender1507@gmail.com',
		# 			to_emails=[user.email])
		# except:
		# 	pass
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
		print(request.user)
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
			# assign_pannels_to_intervieews()
			schedule_interviews()
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


# def getPanelInst(appl_stack):
# 	# panels = Panel.objects.all()
# 	panels = Panel.objects.filter(interviewers__stack__name = appl_stack)
# 	for panel_inst in panels:
# 		if panel_inst.interviewees.count() <= 5:
# # 			return panel_inst

# def assign_pannels_to_intervieews():
# 	application_stack = ApplicationStack.objects.all()
	
# 	for appl_stack_inst in application_stack:
		
# 		panel = getPanelInst(appl_stack_inst.name)
# 		print(panel)
# 		interviewee_inst = appl_stack_inst.application.interviewee
# 		print(appl_stack_inst.application)
# 		print(appl_stack_inst)
# 		#add interviewee to panel and save
# 		panel.interviewees.add(interviewee_inst)
	
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

@api_view(('GET',))
def NumberOfApplicationAPI(request, sapid):
	interviewee_user = Interviewee.objects.get(user = sapid)
	appl = Application.objects.filter(interviewee = interviewee_user)
	c=0
	for obj in appl:
		c=c+1
	return Response({"Number":c})


class IntervieweePanelAPI(GenericAPIView):
	serializer_class = PanelSerializer

	def get(self,request):
		interviewee = Interviewee.objects.get(user = request.user)
		panels = Panel.objects.filter(interviewees = interviewee)
		if not panels :
			return Response({"message":"No Panel has been assigned to you"}, status= status.HTTP_404_NOT_FOUND)
		serializer = PanelSerializer(panels, many = True)
		return Response(serializer.data)
	
def getPanelInst(user, user_appl_dict):

	#get relevant pannels
	interviewers=[]
	panels_stack_list=[]
	panels=[]
	min=999999
	#Through this we get the existing panels
	all_panels=Panel.objects.prefetch_related('interviewers')

	for panel in all_panels:
		interviewers.append(panel.interviewers.all())
		# We get interviewers as query set in a list format i.e [<QuerySet [<Interviewer: Name1>, <Interviewer: Name2>, <Interviewer: Name3>, <Interviewer: Name4>]>]
		panels.append(panel)
		stacks=[]
		for inter in interviewers[0]:
			stacks.append(inter.stack.name)
		# We append the stacks got from the interviewers list to another list for getting the list of stacks present in each panel
		panels_stack_list.append(stacks)
		interviewers=[]
	
	"""

	We now find the potential panels in which the user can be scheduled and if there is only one stack we 
	schedule in the panel which has least number of interviewees and if multiple stacks we find the Intersection
	of all the panels available in each stack and if intersection is NULL then just take UNION of all sets and 
	schedule in the one with least number of interviewees

	"""
	potential_panels=[]
	available_panel=[]
	count=0
	for stack in user_appl_dict[user]:
		for panel_stacks in panels_stack_list:
			if(stack!='Django'and stack!='Node'):
				if ''+str(stack) in panel_stacks:
					available_panel.append(panels[count])
					count+=1
			else:
				if(stack=='Django'):
					if 'Django' or 'FullstackDjango' in panel_stacks:
						available_panel.append(panels[count])
						count+=1
				elif(stack=='Node'):
					if 'Node' or 'FullstackNode' in panel_stacks:
						available_panel.append(panels[count])
						count+=1
		potential_panels.append(available_panel)
		available_panel=[]
		count=0
	print(potential_panels)


	if(len(potential_panels)==1):
		for panels in potential_panels[0]:
			panels_interviewees=Panel.objects.prefetch_related('interviewees').get(name=panels)
			# It will give same query set as those of Interviewers
			
			interviewees_existing=panels_interviewees.interviewees.all().count()
	
			if(interviewees_existing<min):
				final_panel=panels
				min=interviewees_existing

		print(final_panel)
		return final_panel
	else:
		final_set=set(potential_panels[0])
		for i in range(1,len(potential_panels)):
			final_set=final_set.intersection(set(potential_panels[i]))
		if(final_set):
			if(len(final_set)==1):
				final_panel=final_set[0]
				return final_panel
			else:
				for panels in final_set:
					panels_interviewees=Panel.objects.prefetch_related('interviewees').get(name=panels)

					interviewees_existing=panels_interviewees.interviewees.all().count()
					# if interviewees_existing:
					# 	interviewees=interviewees_existing[0]
					# else:
					# 	interviewees=interviewees_existing
					# print(interviewees)
					if(interviewees_existing<min):
						final_panel=panels
						min=interviewees_existing
				return final_panel
		else:
			for i in range(1,len(potential_panels)):
				final_set=final_set.union(set(potential_panels[i]))
			for panels in final_set:
				panels_interviewees=Panel.objects.prefetch_related('interviewees').get(name=panels)

				interviewees_existing=panels_interviewees.interviewees.all().count()
				# if interviewees_existing:
				# 	interviewees=interviewees_existing[0]
				# else:
				# 	interviewees=""
				if(interviewees_existing<min):
					final_panel=panels
					min=interviewees_existing
			return final_panel


	# potential_panel_list=[]
	# print(len(user_appl_dict[user]))
	# panel_dict={}
	# panels_data=Panel.objects.all()
	# for pan in panels_data:
	# 	panel_stacks=[]
	# 	print(Panel.objects.get(name='Alpha'))
	# 	for interviewers in pan.interviewers:
	# 		panel_stacks.append(interviewers)
	# 	panel_dict[pan]=panel_stacks

	# print("panel_dict="+panel_dict)
	# for appl in user_appl_dict[user]:
	# 	if(appl.name=='Django'):
	# 		panel_stack=Panel.objects.values_list('interviewers',flat=True)
	# 		print(panel_stack)
	# 		potential_panel_list.append(Panel.objects.filter(interviewers__stack__name = appl.name or 'FullstackDjango'))
	# 	elif(appl.name=='Node'):
	# 		potential_panel_list.append(Panel.objects.filter(interviewers__stack__name = appl.name or 'FullstackNode'))
	# 	else:
	# 		potential_panel_list.append(Panel.objects.filter(interviewers__stack__name = appl.name))
	# if(len(user_appl_dict[user])==1):
	# 	application_stack=user_appl_dict[user]
	# 	potential_panel_list.append(Panel.objects.filter(interviewers__stack__name = application_stack))
	# 	#min is to find the panel with minimum no. of applicants scheduled so we schedule him there
	# 	min=0
	# 	panel_selected=""
	# 	for panels in potential_panel_list:
	# 		scheduled_interviewers_count=Panel.objects.get(name=panels.name)
	# 		if(len(scheduled_interviewers_count)>=min):
	# 			min=len(scheduled_interviewers_count)
	# 			panel_selected=panels.name


	#print(potential_panel_list)
	# max=0
	# panel_name=""
	# for panels in potential_panel_list:
	# 	count=potential_panel_list.count(panels)
	# 	if(count>=max):
	# 		max=count
	# 		panel_name=panels


	# return panel_name
		

	
	# print(potential_panel_list)

	# #to select one pannel:	
	# potential_panel_name_list=[]
	# for panel_insts in potential_panel_list:
		
	# 	for inst in panel_insts:
	# 		potential_panel_name_list.append(inst.name)
	
	# #count number of pannel hits
	# potential_panel_name_score_dict = {i:potential_panel_name_list.count(i) for i in potential_panel_name_list}
	# # print(potential_panel_name_score_dict)

	# #find highest count pannel list
	# high=0
	# high_pannel=[]
	# for key in potential_panel_name_score_dict:
	# 	if high < potential_panel_name_score_dict[key]:
	# 		high = potential_panel_name_score_dict[key]
	# for key in potential_panel_name_score_dict:
	# 	if high == potential_panel_name_score_dict[key]:
	# 		high_pannel.append(key)
	# # print(high_pannel)

	# #check number of intervieews in pannel and assign one with less than fixed number
	# for panel_name in high_pannel:
	# 	panel_inst = Panel.objects.get(name=panel_name)
	# 	if panel_inst.interviewees.count() <= 5:
	# 		return panel_inst

	# #no pannel found within given conditions
	# return 0
	# panels = Panel.objects.all()
	# panels = Panel.objects.filter(interviewers__stack__name = appl_stack)
	# for panel_inst in panels:
	# 	if panel_inst.interviewees.count() <= 5:
	# 		return panel_inst

def schedule_interviews(self):
	application_stack = ApplicationStack.objects.all()
	
	appl_user_dict={}
	for appl_stack_inst in application_stack:
		appl_user_dict[appl_stack_inst]= appl_stack_inst.application.interviewee
		#print(appl_stack_inst, appl_stack_inst.application.interviewee)
		#print('\n')

	user_appl_dict = {}
	for key, value in appl_user_dict.items():	
		user_appl_dict.setdefault(value, []).append(key)

	#print(user_appl_dict)
	# print(user_appl_dict)
	
	#find the user with most applications
	reorder_dict = {}

	for itrnum, user in enumerate(user_appl_dict):
		reorder_dict[user]=len(user_appl_dict[user])
	#print(reorder_dict)

	#sort the above dict acc to number of applications
	sorted_reorder_dict = sorted(reorder_dict.items(), key=lambda x:x[1], reverse=True)
	converted_dict = dict(sorted_reorder_dict)
	#print(converted_dict)
	print(user_appl_dict)
	#find pannel for each user
	for user in converted_dict:
		
		#to visualize the dict with all data objects
		# print('\n')
		# print(user)
		# for appl in user_appl_dict[user]:
		# 	print(appl)
		# print('\n')
		panel = getPanelInst(user, user_appl_dict)
		print(user, panel)
		obj=Panel.objects.prefetch_related('interviewees').get(name=panel)
		interviewees=obj.interviewees
		name=User.objects.filter(name=user)
		interviewees.add(Interviewee.objects.get(user=name.name))
		obj.save()
	return Response("Successfully Scheduled")
		