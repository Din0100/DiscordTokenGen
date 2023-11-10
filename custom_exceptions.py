class mail_error(Exception):
    ''' Exception for when unexpected response from email '''
    
class sms_timeout(Exception):
    '''' message took longer than set timeout '''

class sms_error(Exception):
    ''' generic error with getting sms code '''

#Captcha Exceptions 
class captcha_error(Exception):
    ''' custom captcha exception '''
    
class no_useragent(Exception):
    ''' error for when useragent is true but the session does not have a useragent set '''
    
class missing_params(Exception):
    ''' generic error for when there are missing params based on method passed in '''
    
class captcha_unsolvable(Exception):
    ''' exception for when captcha service cannot solve the captcha '''
    
    
#Generator Exceptions
class no_session(Exception):
    ''' No sesion to configure, return immediately '''
    
class token_gen_failure(Exception):
    ''' exception for when token generation has failed '''
    
class locked_token(Exception):
    ''' Token has been locked '''
    
class no_email(Exception):
    ''' email has not arrived yet '''
    
class cookie_or_fingerprint_exception(Exception):
    ''' Could not get cookies or fingerprint '''
    
class consent_error(Exception):
    pass
    