from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import authenticate
import jwt, time
from .config import JWT_SECRET, TIME_EXPIRE
from .models import UserInfo, Yacht, UserRole, RequestStatus
from django.contrib.auth.models import User
from .models import Request as YachtRequest


def check_token(params):
    if 'token' in params:
        try:
            data = jwt.decode(params['token'], JWT_SECRET, algorithms=["HS256"])

            if time.time() - data['time'] > TIME_EXPIRE:
                raise Exception("The token has expired")
            
            return data['username']
            
        except:
            raise Exception("Invalid credentials")

    else:
        raise Exception("Token required")


class CreateYachtRequest(APIView):
    def post(self, request: Request):
        try:
            username = check_token(request.query_params)

        except Exception as ex:
            return Response({'error': str(ex)}, 401)
        
        user = User.objects.filter(username=username)
        user_info = UserInfo.objects.filter(user=user[0])[0]

        params = ('yacht', 'from_time', 'to_time')
        no_params = []

        for param in params:
            if param not in request.data:
                no_params.append(param)

        if len(no_params) > 0:                
            return Response({'msg':'Missing parameters: ' + ', '.join(no_params)}, 400)
        
        if user_info.current_yacht is not None:
            return Response({'msg':'A yacht is already assigned to you'}, 400)
        
        yachts = Yacht.objects.filter(id=request.data['yacht'])

        if len(yachts) == 0:
            return Response({'msg':'Yacht not found'}, 400)
        
        yacht = yachts[0]

        if not yacht.available:
            return Response({'msg':'Yacht is busy'}, 400)

        try:
            from_time = int(request.data['from_time'])
            to_time = int(request.data['to_time'])

        except:
            return Response({'msg':'Wrong time format'}, 400)
        
        time_in_days = (to_time - from_time) / 60 / 60 / 24
        price_sum = yacht.rent_price * time_in_days

        if price_sum < 0 or price_sum > user_info.balance:
            return Response({'msg':'The balance is insufficient'}, 400)
        
        YachtRequest(
            yacht=yacht,
            user=user_info,
            time_req=time.time(),
            from_time=from_time,
            to_time=to_time,
            get=True
        ).save()

        return Response({'msg':'ok'})
    

class CreateBackRequest(APIView):
    def get(self, request: Request):
        try:
            username = check_token(request.query_params)

        except Exception as ex:
            return Response({'error': str(ex)}, 401)
        
        user = User.objects.filter(username=username)
        user_info = UserInfo.objects.filter(user=user[0])[0]

        if user_info.current_yacht is None:
            return Response({'msg':'No current yacht'}, 400)
        
        YachtRequest(
            yacht=user_info.current_yacht,
            user=user_info,
            time_req=time.time(),
            from_time=0,
            to_time=0,
            get=False
        ).save()

        return Response({'msg':'ok'})


def check_request_params(query_params, request_data):
    username = check_token(query_params)
    
    user = User.objects.filter(username=username)
    user_info = UserInfo.objects.filter(user=user[0])[0]

    user_role = UserRole(user_info.user_role)
    if user_role != UserRole.clerk:
        raise Exception("Access is denied")
    
    if 'request_id' not in request_data:
        raise Exception("Missing parameters: request_id")
    
    reqs = YachtRequest.objects.filter(id=request_data['request_id'])

    if len(reqs) == 0:
        raise Exception("Request not found")

    req = reqs[0]
    if RequestStatus(req.status) != RequestStatus.new:
        raise Exception('Request status not "new"')
    
    return req


class DenyRequest(APIView):
    def post(self, request: Request):
        try:
            req = check_request_params(request.query_params, request.data)

        except Exception as ex:
            return Response({'error': str(ex)}, 400)

        req.status = RequestStatus.deny.value

        if 'answer' in request.data:
            req.answer = request.data['answer']

        req.save()

        return Response({'msg':'ok'})
    

class GetUserRequest(APIView):
    def get(self, request: Request):
        try:
            username = check_token(request.query_params)

        except Exception as ex:
            return Response({'error': str(ex)}, 401)
        
        user = User.objects.filter(username=username)
        user_info = UserInfo.objects.filter(user=user[0])[0]

        if 'all' in request.query_params:
            if UserRole(user_info.user_role) != UserRole.clerk:
                return Response({'error': 'Access is denied'}, 400)
            
            reqs = YachtRequest.objects.all()

        else:
            reqs = YachtRequest.objects.filter(user=user_info)

        reqs_res = []

        for req in reqs:
            reqs_res.append({
                'id':req.id,
                'status':req.status,
                'yacht':{
                    'id':req.yacht.id,
                    'name':req.yacht.name,
                    'price':req.yacht.rent_price
                },
                'time_req':req.time_req,
                'get':req.get,
                'from_time':req.from_time,
                'to_time':req.to_time,
                'answer':req.answer,
                'user':req.user.user.username
            })

        return Response({'requests':reqs_res})
    

class AllowRequest(APIView):
    def post(self, request: Request):
        try:
            req = check_request_params(request.query_params, request.data)

        except Exception as ex:
            return Response({'error': str(ex)}, 400)
        
        yacht = req.yacht
        user_req = req.user
        
        if req.get:
            time_in_days = (req.to_time - req.from_time) / 60 / 60 / 24
            price_sum = req.yacht.rent_price * time_in_days

            if price_sum < 0 or price_sum > req.user.balance:
                return Response({'msg':'The balance is insufficient'}, 400)
            
            if not req.yacht.available:
                return Response({'msg':'Yacht is busy'}, 400)

            user_req.current_yacht = yacht
            user_req.balance -= price_sum
            user_req.save()

            yacht.available = False
            yacht.save()

        else:
            if user_req.current_yacht is None or user_req.current_yacht.id != yacht.id:
                return Response({'msg':'The current yacht differs from the one specified in the request'}, 400)

            user_req.current_yacht = None
            user_req.save()

            yacht.available = True
            yacht.save()

        req.status = RequestStatus.allow.value
        if 'answer' in request.data['answer']:
            req.answer = request.data['answer']

        req.save()

        return Response({'msg':'ok'})


class GetAvailableYachts(APIView):
    def get(self, request: Request):
        try:
            check_token(request.query_params)

        except Exception as ex:
            return Response({'error': str(ex)}, 401)
        
        yachts = Yacht.objects.filter(available=True)
        yachts_list = []

        for yacht in yachts:
            yachts_list.append({
                'id':yacht.id,
                'name':yacht.name,
                'price':yacht.rent_price
            })

        return Response({
            'yachts':yachts_list
        })
    

class AddBalance(APIView):
    def get(self, request: Request):
        try:
            username = check_token(request.query_params)

        except Exception as ex:
            return Response({'error': str(ex)}, 401)
        
        if 'balance' in request.query_params:
            try:
                balance = int(request.query_params['balance'])

            except:
                return Response({'msg':'Balance wrong format'})
            
            user = User.objects.filter(username=username)
            user_info = UserInfo.objects.filter(user=user[0])[0]

            user_info.balance += balance
            user_info.save()

            return Response({'msg':'ok'})

        else:
            return Response({'msg':'Missing parameters: balance'}, 400)
        

class GetUserInfo(APIView):
    def get(self, request: Request):
        try:
            username = check_token(request.query_params)

        except Exception as ex:
            return Response({'error': str(ex)}, 401)
        
        user = User.objects.filter(username=username)
        user_info = UserInfo.objects.filter(user=user[0])[0]

        current_yacht = None
        if user_info.current_yacht:
            current_yacht = user_info.current_yacht.id

        return Response({
            'username':username,
            'balance':user_info.balance,
            'current_yacht':current_yacht
        })
    

class Login(APIView):
    def post(self, request: Request):
        params = ('username','password')
        no_params = []

        for param in params:
            if param not in request.data:
                no_params.append(param)

        if len(no_params) > 0:                
            return Response({'msg':'Missing parameters: ' + ', '.join(no_params)}, 400)

        user = authenticate(username=request.data['username'], password=request.data['password'])

        if user is None:
            return Response({'msg':'Invalid credentials'}, 401)
        
        check_user_info = UserInfo.objects.filter(user=user)

        if len(check_user_info) == 0:
            UserInfo(user=user).save()

        json_data = {
            'username': request.data['username'],
            'time': int(time.time())
        }

        token = jwt.encode(payload=json_data, key=JWT_SECRET, algorithm="HS256")

        return Response({'access_token':token})
    

class Signup(APIView):
    def post(self, request: Request):
        params = ('username','password')
        no_params = []

        for param in params:
            if param not in request.data:
                no_params.append(param)

        if len(no_params) > 0:                
            return Response({'msg':'Missing parameters: ' + ', '.join(no_params)}, 400)
        
        usrs = User.objects.filter(username=request.data['username'])

        if len(usrs) > 0:
            return Response({'msg':'User already exists'}, 400)
        
        user_obj = User.objects.create_user(
            request.data['username'], 
            password=request.data['password']
        )

        UserInfo(user=user_obj).save()
        
        json_data = {
            'username': request.data['username'],
            'time': int(time.time())
        }

        token = jwt.encode(payload=json_data, key=JWT_SECRET, algorithm="HS256")
        return Response({'access_token':token})