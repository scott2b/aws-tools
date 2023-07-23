import datetime
import os
from piccolo.table import Table
from piccolo.columns import Boolean, Email, ForeignKey, Varchar, Text, Timestamptz, JSON, UUID
from piccolo.utils.pydantic import create_pydantic_model
from pydantic import AnyUrl, BaseModel, Extra, Field
from pydantic import ValidationError, validator, root_validator #model_validator


def to_camel(string: str) -> str:
    init, *temp = string.split("_")
    return "".join([init.lower(), *map(str.title, temp)])


def to_pascal(string: str) -> str:
    init, *temp = string.split("_")
    r = "".join([init.lower(), *map(str.title, temp)])
    return r[0].upper() + r[1:]
    


def timestamp():
    tz = datetime.timezone.utc
    return datetime.datetime.now(tz=tz)


class Config:
    extra = Extra.ignore
    alias_generator = to_pascal
    allow_population_by_field_name = True


class CognitoPool(Table):

    id = Varchar(length=128, primary_key=True)
    name = Varchar(length=256)
    creation_date = Timestamptz()
    last_modified_date = Timestamptz()
    lambda_config = JSON()


class CognitoClient(Table):

    client_id = Varchar(length=128, primary_key=True)
    user_pool_id = ForeignKey(references=CognitoPool)
    client_name = Varchar(length=256)


class User(Table):

    sub = UUID()
    email = Email()

    @classmethod
    def from_response(cls, data):
        """Build a validated User model from an AWS Cognito API response for a Cognito
        User.
        """
        _ = {}
        for attr in data["UserAttributes"]:
            _[attr["Name"]] = attr["Value"]
        UserPoolModel = create_pydantic_model(cls,
            pydantic_config_class=Config
        )
        return UserPoolModel(**_) 



class UserAuth(Table):
    """The auth payload includes `ChallengeParameters` and `AuthenticationResult`,
    although, in my testing so far, ChallengeParameters is an empty dict. This class
    just implements the AuthenticationResult.

    It is not clear what the use case for this object is other than to get the user
    immediately from the auth response, which AWS mysteriously makes us fetch in a
    separate call. Perhaps these tokens can be passed to the client and used to access
    resources directly in AWS? If so, what resources and how?
    """
    access_token = Varchar(length=1024)
    expires_at = Timestamptz()
    token_type = Varchar(length=16)
    refresh_token = Varchar(length=16)
    id_token = Varchar(length=1024)



CognitoPoolModel = create_pydantic_model(CognitoPool,
    pydantic_config_class=Config
)

CognitoClientModel = create_pydantic_model(CognitoClient,
    pydantic_config_class=Config
)



class UserAuthModel(BaseModel):
    """It does not seem to work to subclass the model created by create_pydantic_model
    so we do this one from scratch so that ExpiresIn can be converted into ExpiresAt.
    """

    access_token: str
    expires_at: datetime.datetime
    token_type: str
    refresh_token: str
    id_token: str


    #@model_validator(mode='before') # pydantic >=2.0
    @root_validator(pre=True)
    def calculate_expiration(cls, data):
        """Besides `AuthenticationResult, there are `ChallengeParameters`, but we do not
        yet have a clear use for them.

        Pydantic >=2.0
        https://docs.pydantic.dev/latest/usage/validators/
        """
        if "AuthenticationResult" in data:
            data = data["AuthenticationResult"]
        expires_in = data.pop("ExpiresIn")
        dt = timestamp()
        expires_at = dt + datetime.timedelta(seconds=expires_in)
        data["ExpiresAt"] = expires_at 
        return data

    class Config:
        extra = Extra.ignore
        alias_generator = to_pascal
        allow_population_by_field_name = True
