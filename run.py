from serviceconnect import db, prep_app

app = prep_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
