import os
from .awsclient import cognito_client
from .tables import User, UserAuthModel


def create_user(*, pool_id: str, email: str):
    response = cognito_client.admin_create_user(
        UserPoolId=pool_id,
        Username=email,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            },
        ],
        #ValidationData=[
        #    {
        #        'Name': 'string',
        #        'Value': 'string'
        #    },
        #],
        #TemporaryPassword='string',
        #ForceAliasCreation=True|False,
        #MessageAction='RESEND'|'SUPPRESS',
        DesiredDeliveryMediums=['EMAIL'], # 'EMAIL', 'SMS'
        #ClientMetadata={
        #    'string': 'string'
        #}
    )
    return response


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
        user = User.from_response(user)
        auth = UserAuthModel(**response)
        return {
            "auth": auth,
            "user": user
        }
    except Exception as e:
        print("User login failed:", e)



def authenticate_user(*, pool_id:str, client_id: str, username:str, password: str):
    """This is like login but uses the AdminInitiateAuth. Which strangely requires
    both a pool and a client.
    """
    try:
        response = cognito_client.admin_initiate_auth(
            UserPoolId=pool_id,
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response
    except Exception as e:
        print("User login failed:", e)



def list_users(*, pool_id: str, attributes: list[str]=None, page_token:str=None, filter:str=None):
    """
    boto docs:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/list_users.html
    """
    kwargs = {
        "UserPoolId": pool_id,
        "AttributesToGet": attributes or []
    }
    if page_token is not None:
        kwargs["PaginationToken"] = page_token
    if filter is not None:
        kwargs["Filter"] = filter
    response = cognito_client.list_users(**kwargs)
    print(response)
    return [User.from_response(user) for user in response["Users"]]


def get_user(*, pool_id: str, username: str):
    """username can be either the `Username` (aka `sub`) which is the AWS-assigned UUID,
    or can be the username that was provided when the user was created or registered.
    """
    response = cognito_client.admin_get_user(
        UserPoolId=pool_id,
        Username=username
    )
    return response


def update_user(*, pool_id: str, username: str, attributes: dict[str:str]):
    attributes = [ { "Name":k, "Value": v } for k,v in attributes.items() ]
    response = cognito_client.admin_update_user_attributes(
        UserPoolId=pool_id,
        Username=username,
        UserAttributes=attributes
    )  
    return response
