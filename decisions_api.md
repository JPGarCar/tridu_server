# API Decisions Log Book
All decisions taken as to the design of this api will be
documented here with the relevant reasoning and evidence to support
the decision.

---

### API Schema Names
API schema names should follow this convention:
- If for a particular HTTP method, prepend the method ex: `PatchParticipantSchema`
- If for a particular logic action, prepend the action ex: `CreateBulkParticipantSchema`
- A generic view or "get" schema should just be the model name ex: `ParticipantSchema`
- Always append "Schema" at the end of all schemas

---
### Delete Methods Response

Delete methods respond either:
- 204 : Delete complete + Null -> When delete is successful
- 404 : Resource not found + str -> When the resource was not found (probably already deleted)

Reasoning is explained here: https://stackoverflow.com/a/60695301/14134362.

---
### POST Create Method Response

Any endpoints of type POST that create a resource will return:
- 201: Created + resource -> When the create is successful
- 409: Conflict + existing resource -> When the resource already exists

---
### Patch Update Method Response

To update a resource (able to partially edit), we use a Patch method with
the following return options:
- 200: Ok + resource -> When the resource was updated
- 404: Resource not found + str -> When the resource being updated was not found