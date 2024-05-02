from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import authenticate
import jwt, time
from .config import JWT_SECRET, TIME_EXPIRE
from .models import UserInfo, Yacht
from django.contrib.auth.models import User

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwidGltZSI6MTcxNDY0Njc0MX0.sUueaPC7iAN6DdI-mksNcTBy8lV0mRUP80a_1hAJdMo
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