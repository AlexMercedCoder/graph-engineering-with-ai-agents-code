node: run-tests
brief: Run the project test suite from the sample-project directory. Report only
       failing tests, with the assertion that failed and the source file and line.
       Do not fix anything.
inputs: none
outputs: .agent-work/test-failures.md
success: the file exists and either lists failures or says "all passing"
