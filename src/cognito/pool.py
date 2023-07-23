import os
import boto3
from .awsclient import cognito_client


def create_pool(*, pool_name):
    """
    Compare to the AWS CLI:
    [aws cognito-idp create-user-pool](https://docs.aws.amazon.com/cli/latest/reference/cognito-idp/create-user-pool.html)
    """
    password_policy = {
        'MinimumLength': 6,
        'RequireUppercase': False,
        'RequireLowercase': False,
        'RequireNumbers': False,
        'RequireSymbols': False,
        'TemporaryPasswordValidityDays': 10
    }


    response = cognito_client.create_user_pool(
        PoolName=pool_name,
        Policies={
            'PasswordPolicy': password_policy
        },
        DeletionProtection='ACTIVE',
        AutoVerifiedAttributes=[
            #'phone_number',
            'email',
        ],
        AliasAttributes=[ # alternate usernames which apparently not include the name attributes as UsernameAttributes
            'phone_number',
            #'email',
            'preferred_username',
        ],
        UsernameAttributes=[ # this seems to be the primary username
            #'phone_number',
            'email',
        ],
        SmsVerificationMessage='Verify your phone number',
        EmailVerificationMessage='Verify your email',
        EmailVerificationSubject='Verification required',
        #VerificationMessageTemplate={
        #    'SmsMessage': 'string',
        #    'EmailMessage': 'string',
        #    'EmailSubject': 'string',
        #    'EmailMessageByLink': 'string',
        #    'EmailSubjectByLink': 'string',
        #    'DefaultEmailOption': 'CONFIRM_WITH_LINK'|'CONFIRM_WITH_CODE'
        #},
        SmsAuthenticationMessage='Authenticated',
        MfaConfiguration='OFF', # |'ON'|'OPTIONAL',
        UserAttributeUpdateSettings={
            'AttributesRequireVerificationBeforeUpdate': [
                'phone_number',
                'email',
            ]
        },
        DeviceConfiguration={
            'ChallengeRequiredOnNewDevice': True,
            'DeviceOnlyRememberedOnUserPrompt': True
        },
        #EmailConfiguration={
        #    'SourceArn': 'string',
        #    'ReplyToEmailAddress': 'string',
        #    'EmailSendingAccount': 'COGNITO_DEFAULT'|'DEVELOPER',
        #    'From': 'string',
        #    'ConfigurationSet': 'string'
        #},
        #SmsConfiguration={
        #    'SnsCallerArn': 'string',
        #    'ExternalId': 'string',
        #    'SnsRegion': 'string'
        #},
        #UserPoolTags={
        #    'string': 'string'
        #},
        #AdminCreateUserConfig={
        #    'AllowAdminCreateUserOnly': True|False,
        #    'UnusedAccountValidityDays': 123,
        #    'InviteMessageTemplate': {
        #        'SMSMessage': 'string',
        #        'EmailMessage': 'string',
        #        'EmailSubject': 'string'
        #    }
        #},
        #Schema=[
        #    {
        #        'Name': 'string',
        #        'AttributeDataType': 'String'|'Number'|'DateTime'|'Boolean',
        #        'DeveloperOnlyAttribute': True|False,
        #        'Mutable': True|False,
        #        'Required': True|False,
        #        'NumberAttributeConstraints': {
        #            'MinValue': 'string',
        #            'MaxValue': 'string'
        #        },
        #        'StringAttributeConstraints': {
        #            'MinLength': 'string',
        #            'MaxLength': 'string'
        #        }
        #    },
        #],
        #UserPoolAddOns={
        #    'AdvancedSecurityMode': 'OFF'|'AUDIT'|'ENFORCED'
        #},
        UsernameConfiguration={
            'CaseSensitive': False
        },
        AccountRecoverySetting={
            'RecoveryMechanisms': [
                {
                    'Priority': 1,
                    'Name': 'verified_email' # |'verified_phone_number'|'admin_only'
                },
            ]
        }
    )
    return response
