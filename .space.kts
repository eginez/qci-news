job("Example shell script") {
    container(displayName = "juju", image = "python") {
        shellScript {
            content = """
               ls -larth
               pip install requests
               cd src
               python parse.py
            """
        }
    }
}