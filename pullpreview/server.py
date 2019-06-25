def run():
    from pullpreview.web import application
    application.run(port=8765, threaded=True, debug=True)


if __name__ == '__main__':
    run()
