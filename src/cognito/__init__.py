import typer
import os
import boto3
from .client import cognito_client
from .pool import create_pool as _create_pool

app = typer.Typer()


## commands

@app.command()
def pools():
    pools = cognito_client.list_user_pools(MaxResults=100)
    print(pools)


@app.command()
def create_pool(name: str):
    _create_pool(pool_name=name)


@app.command()
def clients(poolid: str):
    response = cognito_client.list_user_pool_clients(
        UserPoolId=poolid,
        MaxResults=100
    )
    print(response)


if __name__ == "__main__":
    app()
