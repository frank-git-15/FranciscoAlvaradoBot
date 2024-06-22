# Template: Python - Minimal

This template leverages the new [Python framework](https://github.com/robocorp/robocorp), the [libraries](https://github.com/robocorp/robocorp/blob/master/docs/README.md#python-libraries) from to same project as well.

The template provides you with the basic structure of a Python project: logging out of the box and controlling your tasks without fiddling with the base Python stuff. The environment contains the most used libraries, so you do not have to start thinking about those right away. 

👉 Other templates are available as well via our tooling and on our [Portal](https://robocorp.com/portal/tag/template)

## Running

#### VS Code
1. Get [Robocorp Code](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features) -extension for VS Code.
1. You'll get an easy-to-use side panel and powerful command-palette commands for running, debugging, code completion, docs, etc.

#### Command line

1. [Get RCC](https://github.com/robocorp/rcc?tab=readme-ov-file#getting-started)
1. Use the command: `rcc run`

## Results
    After running the bot, check out the `articles_webScraping xxxxxx.xlsx` under the `output` -folder.

#### RUN BOTH IN CONTROL ROOM
### Control room work items
    Create a work item using the next structure
      {
        "payload": {
          "search_criteria": "phrase to seach within web page",
          "months_before": How many months ago are the articles needed as integer
        }
      }
### Results in control room
    Artifacts:
      articles_webScraping xxxxx.xlsx
      consolidated_images.zip
      execution_logs.log
      info_logs.log





