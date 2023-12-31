import typer
import os
import boto3
from .awsclient import cognito_client
from .client import create_client as _create_client
from .pool import create_pool as _create_pool
from .user import signup_user, confirm_user, login_user, list_users, get_user, authenticate_user
from .user import create_user as _create_user
from .user import update_user as _update_user
from .tables import CognitoPoolModel, CognitoClientModel


app = typer.Typer()


## commands


@app.command()
def create_pool(name: str):
    _create_pool(pool_name=name)


@app.command()
def pools():
    pools = cognito_client.list_user_pools(MaxResults=100)["UserPools"]
    for pool in pools:
        model = CognitoPoolModel(**pool)
        print(model)
    print(pools)

@app.command()
def create_client(name: str, pool_id: str):
    _create_client(client_name=name, pool_id=pool_id)


@app.command()
def clients(pool_id: str):
    response = cognito_client.list_user_pool_clients(
        UserPoolId=pool_id,
        MaxResults=100
    )
    for client in response["UserPoolClients"]:
        model = CognitoClientModel(**client)
        print(model)
    print(response)


@app.command()
def create_user(pool_id: str, email: str):
    response = _create_user(pool_id=pool_id, email=email)
    print(response)


@app.command()
def signup(client_id: str, email:str, password:str):
    response = signup_user(
        client_id=client_id,
        email=email,
        password=password
    )
    print(response)
    

@app.command()
def confirm(client_id: str, username: str, confirmation_code:str):
    response = confirm_user(
        client_id=client_id,
        username=username,
        confirmation_code=confirmation_code
    )
    print(response)


@app.command()
def login(client_id: str, username: str, password: str):
    response = login_user(
        client_id=client_id,
        username=username,
        password=password
    )
    print(response)


@app.command()
def authenticate(pool_id: str, client_id: str, username: str, password: str):
    response = authenticate_user(
        pool_id=pool_id,
        client_id=client_id,
        username=username,
        password=password
    )
    print(response)


@app.command()
def users(pool_id: str):
    response = list_users(pool_id=pool_id)
    print(response)


@app.command()
def user(pool_id: str, username: str):
    response = get_user(pool_id=pool_id, username=username)
    print(response)

from typing import List, Optional


@app.command()
def update_user(pool_id: str, username: str, attr: Optional[List[str]]=typer.Option(None)):
    if attr:
        attributes = { k:v for k,v in [a.split("=") for a in attr] }
    else:
        exit("At least one attr required.")
    response = _update_user(pool_id=pool_id, username=username, attributes=attributes)
    print(response)


if __name__ == "__main__":
    app()
