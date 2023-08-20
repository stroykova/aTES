Migrate tasks description to title + jira_id
1. add TaskCreatedV2 with title + jira_id in the registry
2. add migration to databases with fields addition (do not remove an old field)
3. modify consumers to consume both version
4. modify producer
5. migrate a database and remove support from the code only if necessary and after meaningful amount of time (when we are sure we do not need old data)