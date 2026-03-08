My plan for my rewrite of my AI coding system:

define tasks using yaml. A task would be a prompt, specific steps to take, and pre-requesites before every step could be completed. The app would bounce back if a step is not completed.

Example:

task:
  - run_prompt: "Do XYZ and write it to log.log"
    - requires:
      - updated_file: log.log

this would ensure that log.log was updated. Commands could be things such as run a bash command and test the error code, ensure a file/directory exists, ensure a file is valid json/yaml and matches a schema, ensure an AI response contains something, write and validate tests, subtasks, etc...


Generic operations for tasks to perform would be things like search, write file, run sub-task. Workers would be able to define specific tasks with specific requirements as part of the workflow. Tasks can run other tasks as subtasks and block until the subtask is complete.

Workers would be loops that run through tasks and handle the state. Basically 1 worker = 1 codex session (excluding sub-sessions spawned in as part of research and verification tasks)

A worker definition would contain the yaml defining the tasks that it needs to go through, basically. It would be a prompt (or prompts for various states), some metadata, and a task/tasks to run through in the normal task format.

Epic -> Phase -> Plan -> Task/Plan. these are the layers of workers. Tasks can also start subtasks but they (generally) will execute in the same AI context as the task, unless it's a task for research to request a summary.

An epic worker would look at a project epic and break it into phases.

It would start with a epic-research task that builds general info and susses out requirements/overarching platform goals, and builds a list of phases to be developed, along with rationale and reasons. It would then run a review task that would ensure that all of the original criteria are matched. Once that is done it would start the phases. The phases would run a similar pipeline to develop plans to accomplish individual phase goals. Plans would define tasks using the above task yaml system. Tasks would be a collection of prompts and criteria as well as subtasks.

Example:

worker:
  - main_prompt: "You are an Epic Worker. Your task is to take the rough outline of a concept that was provided by the user and research it, turn it into actionable phases, and, when done, merge those phases back into your repo sanely."
    main_task: epic_task
    tier: 4

task:
  - name: epic_task
  - description: Processing loop for epic worker
  tasks:
    - research:
      - prompt: "Research all information required to gain a full image of the user's prompt. It is likely a vague concept that needs elaboration. Work out all reasonable methods of achieving it by researching the codebase and the internet and and settle on a coherent idea."
    - think_and_create_phases
    - review_phases_against_user_prompt
    - run_phases
    - review_phase_results_against_user_prompt
    - merge_phases

task:
  - name: think_and_create_phases
  - description: Think about the research and create phases following the phase schema.
  - tasks:
    - run_prompt
      - prompt: Think about the research provided and create phases following the <phase schema>. Phases are meant to be high-level tasks targeting the creation or linking of whole systems and major features. <elaborate> Write the plan to phase_layout.yaml. Respond with a JSON status: {"status": "OK"} or {"status": "FAIL", "message": <issue>}
      - on_fail: <restart epic_task with additional context>
      - requires:
        - updated_file: phase_layout.yaml
task:
  - name: review_phases_against_user_prompt
  - description: Reviews phases against the user prompt with the goal of ensuring the users' prompt is up to date.
  - tasks:
    - run_prompt:
      - prompt: Please review the phase layout in phase_layout.yaml and ensure that it matches the requirements specified in the users' prompt: {user prompt}. Respond with a JSON status: {"status": "OK"} or {"status": "FAIL", "message": <issue>}
      - on_fail: <restart epic_task with additional context>

run phases would set up the git clone/branch for the children and start their workers with the phase prompts in the phase layout.yaml

If review or phase generation fails and a layer can not accomplish it's task (asked to do something impossible by it's parent, for example) it should be able to trigger the parent to either: 1) provide additional context, or 2) discard it's children and re-enter it's planning phase with the additional info. This should be able to cascade up so when low-level implementation issues are found they can trigger re-generation at higher concept levels.

if regeneration attempts for a layer hits a threshold it should stop, provide a detailed summary of the scenario, and wait for user input.


the concept levels are all defined through yaml so somebody could totally redefine them if they wanted.
      

The user can create workers at any stage. If they need a simple plan they create a plan. If they need a many-part phase they can create phases. etc...

The system would be built using a git hierarchy. All epics would be multi-threaded, all phases, plans. There would be a child/sibling-based dependency graph. Any level can wait on any sibling or child to complete as a dependency before progressing. They can not depend on parents or cousins or niblings.

The summary of all dependencies and children should be passed to a level when it starts.

Every epic would be a git branch, every phase below it a git branch, every plan below it a git branch, every task a git branch. When all siblings on a layer are complete the parent layer would run a merge task to merge them all into the parent sanely/intelligently. The top node in a chain would merge back to base when it is complete.

At any point a node should be able to be modified. Modifying a node's generation by modifying it's prompts/input/plan would trigger a rebuild of that node as well as it's entire parent chain back to the epic. This would be done by git reverting the applicable parent commits from epic down, resetting the lowest level parent, and remerging all siblings. This method of reconciliation would hopefully allow modifying specific small components and "recompiling" the prompts to code sanely as a whole.

At every stage a database of relations for every block of code and variable and change would be created/updated. It would show all places where code interlinked and dependencies and rationale for the linking. It would be updated/reconciled along with the git merges.

it should be possible to manually create an epic->task tree instead of automating it. Doing this it should be possible to deterministically define _every single prompt_ that goes into a task and completely rebuild it from prompts to fix issues.

It should be possible to optionally spawn worker children in their own isolated docker or systemd+ip namespace containers so multiple workers can work on things like tests that require network ports and such.

Every action the user can perform in the interface should be automatable, but the user should also be able to turn off things like auto-merge to parent and 

A command line interface would exist that would allow AIs to query the rationale/prompt/summary/results/changes of any other stage to see why things are like they are. It would also allow them to navigate the database.

There should be project-based hooks for tasks that would be added at various points. Example if a project wants testing done it could add a hook to the end of the task phase to ensure that tests are written and verified before the tasks would be considered complete and returned to the plan parent node.

The AI sessions themselves are ran in tmux. They will be given CLI commands to execute to interface with and notify the database when their state changes. Basically after every sub-task stage they will run a command like 'ai-tool mark stage complete {uuid}`. Every task will be started and told to run a command to retrieve it's prompt. If they quit processing (terminal goes idle) then they should be nudged to complete the task by having the last stage repeated and the information on how to register a summary with the CLI in event of an error/getting stuck repeated.

Session IDs need to be tracked so the sessions can be resumed (codex resume {id}) in the event tmux crashes or the host reboots or whatever. See if this can be done provider agnostically (like by abusing codex resume --last being per folder or something)

there should be a documentation generator. this would use a combination of static analysis and the relational database of rationale/function/variable/etc... links to create a thoroughly documented <doxygen/sphinx/...?> code. There should be a search option to list a function and see all tasks/plans/etc... that modified it along with the rationale.


