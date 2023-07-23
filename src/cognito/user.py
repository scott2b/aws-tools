import os
from .awsclient import cognito_client


def signup_user(*, client_id: str, email:str, password:str):
    """When using Localstack, if SMTP is not configured, a successful signup will print
    the new user's confirmation code to the Localstack conole logs.
    """
    try:
        response = cognito_client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                }
            ]
        )
        return response
    except Exception as e:
        print("User sign-up failed:", e)
        print(dir(e))
        print(e.response)
        if e.response["message"] == "User already exists":
            response = cognito_client.admin_get_user(
                UserPoolId=POOL_ID,
                Username=username
            )
            if response['UserStatus'] == 'UNCONFIRMED':
                # Resend verification email
                r = cognito_client.resend_confirmation_code(
                    ClientId=client_id,
                    Username=username
                )
                print("Verification email resent.")
                print(r)



def confirm_user(*, client_id: str, username: str, confirmation_code:str):
    """If using Localstack without SMTP configured, get the confirmation code from
    the Localstack logs from the call to `signup_user`.
    """
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=confirmation_code
        )
        print("User confirmed successfully.")
        return response
    except cognito_client.exceptions.UserNotFoundException:
        print("User does not exist.")
    except cognito_client.exceptions.CodeMismatchException:
        print("Invalid verification code.")
    except Exception as e:
        print("Error:", e)


def login_user(*, client_id:str, username:str, password: str):
    try:
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        access_token = response['AuthenticationResult']['AccessToken']
        user = cognito_client.get_user(AccessToken=access_token)
        return {
            "auth": response,
            "user": user
        }
    except Exception as e:
        print("User login failed:", e)
