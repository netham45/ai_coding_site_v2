there needs to be a command/dashboard to review all blocked on user input elements
there should be a general dashboard to show stats and what's running or not
web frontend
option to launch vscode in a session/container/whatever?
containers for v2
website for v2?
need firm featureset for v1 - what to do to lock down featureset
  simulate everything and iterate and simulate and iterate and patch any holes in logic
  review cli to make sure everything is sensible. cli needs to like match db for constraints and queries and such. program state needs queriable too. how shall the cli tool query the program to get the running state of variables? ipc? http interface? there's no real need to make it crazy hard. things that can be handled over db can just be done over db (db locking is critical)
  review database, decide on single database or per-project database that can be made portable? import/export > storing the db in git? need to make sure projects aren't locked to one computer.
  create pseudocode to cover all code routes, create pseudotests the AI can logic it's way through to verify the pseudocode. build list of all code routes. look at list as partial and extrapolate based on obvious related conditions to fill out all possibilities in pseudocode.

add helper cli commands to jump to task folders

proposed featureset for v1:
cli available that works with running worker daemon, all functions available over cli
functional templates for epics that create phases that create plans that create tasks. individual prompts for every stage.
worker loop that tracks the state of every node, tmux session, and keeps AIs on track.
a thorough list of and prompts for messages like "You are failing this criteria to advance to the next stage: need file XYZ or command failed: test ...., or idle detected. here's your last task. here's how you file an error state. etc..."
ability to track and manage codex sessions throughout the entire lifecycle of a task
ability for one task to create children
dependencies work
all CLI commands available
storyboards of sample user interactions
git management per node, git restore and rollback when a node is regenerated
final list of base subtasks that perform operations (like verify and run command)
what phases?
testing contract?
what else?
