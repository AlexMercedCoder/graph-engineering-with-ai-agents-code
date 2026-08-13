node: verify
brief: Run the whole suite and confirm nothing outside the migrated module changed
       behaviour. Report any test that passed before and fails now.
inputs: none
outputs: a one-paragraph verdict
success: npm test exits zero
