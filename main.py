from __init__ import create_app


if __name__=="__main__":
    app,api=create_app()
    app.run(host="localhost", port="8001")