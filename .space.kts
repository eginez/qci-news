job("Example shell script") {
    container(displayName = "Say Hello", image = "python") {
        shellScript {
            content = """
               ls -larth
               cd src
               python parse.py
            """
        }
    }
}