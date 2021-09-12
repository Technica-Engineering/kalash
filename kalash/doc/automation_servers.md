# Integration with CI vendors

Kalash is vendor-independent. That is, there is literally no difference whether you want to use Jenkins or GitLab CI, or anything else. Here's an example of usage with Jenkins:

```groovy
stage ("Call kalash runner"){
    steps{
        bat '''CALL conda.bat activate some_env
                kalash run -f ".kalash.yaml"
            '''
    }
}
```

What's happenning there? If you add this to your Jenkinsfile in tests repository and add a `".kalash.yaml"` file, `kalash` will use that file (`kalash run -f ".kalash.yaml"` command) and run specified tests with specified configuration. With Jenkins it's best to use Anaconda3 or Miniconda3 and you need to use a Python environment which has `kalash` installed.

In practice every `".kalash.yaml"` file will translate to a single specific job that will have a corresponding `Jenkinsfile`. The reason we split `kalash` away from Jenkins is to allow the QA engineers to specify test configuration themselves without meddling into CI server pipeline, where it's way easier to break stuff and the file looks way more daunting to even understand.

For example: `Jenkinsfile`s may be created in a `jenkinsfiles` folder in each test repository and `yamls` folder wilcouldl contain the YAMLs managed by QA engineers. In Jenkins, use SCM checkout and specify the path to correct `Jenkinsfile` that maps to a given job requested by QA engineers.
