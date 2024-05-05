import requests


class VARS:
    token = None


def api_method(method, query_params=None, data_json=None):
    if VARS.token:
        if query_params:
            query_params['token'] = VARS.token

        else:
            query_params = {'token':VARS.token}

    if data_json is None:
        resp = requests.get(f"http://127.0.0.1:8000/yacht/{method}", query_params)
    
    else:
        resp = requests.post(f"http://127.0.0.1:8000/yacht/{method}", params=query_params, json=data_json)
    
    return resp.status_code, resp.json()
