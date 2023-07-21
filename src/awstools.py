import typer
import cognito


app = typer.Typer()
app.add_typer(cognito.app, name="cognito")


if __name__ == "__main__":
    app()
