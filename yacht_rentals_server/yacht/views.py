from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import authenticate
import jwt, time
from .config import JWT_SECRET, TIME_EXPIRE

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwidGltZSI6MTcxNDY0Njc0MX0.sUueaPC7iAN6DdI-mksNcTBy8lV0mRUP80a_1hAJdMo
def check_token(params):
    if 'token' in params:
        try:
            data = jwt.decode(params['token'], JWT_SECRET, algorithms=["HS256"])

            if time.time() - data['time'] > TIME_EXPIRE:
                raise Exception("The token has expired")
            
        except:
            raise Exception("Invalid credentials")

    else:
        raise Exception("Token required")


class GetTodo(APIView):

    def get(self, request: Request):
        try:
            check_token(request.query_params)

        except Exception as ex:
            return Response({'error': str(ex)}, 401)
        
        return Response({
            'title':'ok'
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

        json_data = {
            'username': request.data['username'],
            'time': int(time.time())
        }

        token = jwt.encode(payload=json_data, key=JWT_SECRET, algorithm="HS256")

        return Response({'access_token':token})