job("Example") {
    // check-out repo-2 to /mnt/space/work/repo-2
    git("repo-2")
    // check-out repo-3 to /mnt/space/work/thirdRepo
    git("repo-3") {
        cloneDir = "thirdRepo"
    }
    container(displayName = "Show dir", image = "openjdk:latest") {
        shellScript {
            content = """
                echo Directory structure
                ls -R /mnt
                echo Working dir is
                pwd
            """
        }
    }
    // If the main repository is 'main-repo', then
    // working dir is /mnt/space/work/main-repo
}