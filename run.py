from onlineexam import app, socketio  # instances
from onlineexam import webapp, testing  # python files


if __name__ == "__main__":
    socketio.run(app, debug=True)