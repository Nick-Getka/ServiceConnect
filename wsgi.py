from serviceconnect import prep_app;
import os

app = prep_app(os.environ['ENV'])

if __name__ == '__main__':
    app.run()
