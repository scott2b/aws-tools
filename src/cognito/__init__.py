import typer
import os
import boto3
from .awsclient import cognito_client
from .client import create_client as _create_client
from .pool import create_pool as _create_pool

app = typer.Typer()


## commands


@app.command()
def create_pool(name: str):
    _create_pool(pool_name=name)


@app.command()
def pools():
    pools = cognito_client.list_user_pools(MaxResults=100)
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
    print(response)


if __name__ == "__main__":
    app()
