from flask import jsonify

def api_response(data=None, message="Success", code=200, status="success", error=None):
   
    response_body = {
        "status": status,
        "code": code,
        "message": message,
        "data": data
    }

    if error:
        response_body["error"] = error
 

    return jsonify(response_body), code