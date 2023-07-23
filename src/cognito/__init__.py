import typer
import os
import boto3
from .awsclient import cognito_client
from .client import create_client as _create_client
from .pool import create_pool as _create_pool
from .user import signup_user, confirm_user, login_user
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


if __name__ == "__main__":
    app()
