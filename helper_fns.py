def JSONResponse(value,error_code):
    response=make_response(jsonify(value),error_code)
    response.headers["Content-Type"] = "application/json"
    return response

def validateUserData(username,password):
        errors={}
        if username=="" or type(username)!=str or (not username[0].isalpha()) or (not username.isalnum()):
            errors["USERS001"]="Username is required and must begin with an english alphabet and mustn't contain special characters"

        if password=="" or type(password)!=str or (not password.isalnum()):
            errors["USERS002"]="Password is required and should be a string. Cannot contain special characters"

        return errors

def validateDeckData(username,deckname):
        errors={}
        if username=="" or type(username)!=str or (not username[0].isalpha()) or (not username.isalnum()):
            errors["USERS001"]="Username is required and must begin with an english alphabet and mustn't contain special characters"
        if deckname=="" or type(deckname)!=str:
            errors["DECKS001"]="Deckname is required and should be a string."
        return errors

def validateCardData(question,answer):
        errors={}
        if question=="" or type(question)!=str:
            errors["CARDS001"]="Question is required and should be string."

        if answer=="":
            errors["CARDS002"]="Answer is required."

        return errors