import os
import boto3
from .awsclient import cognito_client



def create_client(*, client_name: str, pool_id: str):
    """
    Compare to the AWS CLI:
    [aws cognito-idp create-user-pool-client](https://docs.aws.amazon.com/cli/latest/reference/cognito-idp/create-user-pool-client.html)
    """
    response = cognito_client.create_user_pool_client(
        UserPoolId=pool_id,
        ClientName=client_name,
        #GenerateSecret=True,
        #RefreshTokenValidity=3600,
        #AccessTokenValidity=60,
        #IdTokenValidity=60,
        #TokenValidityUnits={
        #    'AccessToken': 'seconds', #|'minutes'|'hours'|'days',
        #    'IdToken': 'seconds', #|'minutes'|'hours'|'days',
        #    'RefreshToken': 'seconds' #|'minutes'|'hours'|'days'
        #},
        #ReadAttributes=[
        #    'string',
        #],
        #WriteAttributes=[
        #    'string',
        #],
        ExplicitAuthFlows=[
            #'ADMIN_NO_SRP_AUTH',
            #'CUSTOM_AUTH_FLOW_ONLY',
            'USER_PASSWORD_AUTH',
            #'ALLOW_ADMIN_USER_PASSWORD_AUTH',
            #'ALLOW_CUSTOM_AUTH',
            #'ALLOW_USER_PASSWORD_AUTH',
            #'ALLOW_USER_SRP_AUTH',
            #'ALLOW_REFRESH_TOKEN_AUTH',
        ],
        #SupportedIdentityProviders=[
        #    'string',
        #],
        #CallbackURLs=[
        #    'string',
        #],
        #LogoutURLs=[
        #    'string',
        #],
        #DefaultRedirectURI='string',
        #AllowedOAuthFlows=[
        #    'code'|'implicit'|'client_credentials',
        #],
        #AllowedOAuthScopes=[
        #    'string',
        #],
        #AllowedOAuthFlowsUserPoolClient=True|False,
        #AnalyticsConfiguration={
        #    'ApplicationId': 'string',
        #    'ApplicationArn': 'string',
        #    'RoleArn': 'string',
        #    'ExternalId': 'string',
        #    'UserDataShared': True|False
        #},
        #PreventUserExistenceErrors='ENABLED', # 'LEGACY'
        #EnableTokenRevocation=True,
        #EnablePropagateAdditionalUserContextData=False,
        #AuthSessionValidity=3600
    )
    return response
