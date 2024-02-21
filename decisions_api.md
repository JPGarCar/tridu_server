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
### Error Object Response
As per [RFC 7807](https://www.rfc-editor.org/rfc/rfc7807), whenever we have an error, either 4xx or 5xx
we will return the correct error code with this Error Object. We have decided this because:
- we are building a REST JSON api, all responses should be JSON objects for consistency
- the object below is well known and referenced in an RFC
- provides a way to add more information to errors in the future for clients to use without braking changes

The error object will be as follows:

```json
{
  "title": "A short, human readable summary of the problem. Should not change between different occurrences.",
  "status": 500, // the status code
  "detail": "a human readable explanation specific to this occurrence of the problem."
}
```

If we ever want to add more information to the Error Object, we can!
The Error Object can be found in `tridu_server/schemas.py`.

---
### Delete Methods Response

Delete methods respond either:
- 204 : Delete complete + Null -> When delete is successful
- 404 : Resource not found + ErrorObjectSchema -> When the resource was not found (probably already deleted)

Reasoning is explained here: https://stackoverflow.com/a/60695301/14134362.

---
### POST Create Method Response

Any endpoints of type POST that create a resource will return:
- 201: Created + resource -> When the create is successful
- 200: Not Created but found + existing resource -> When the resource already exists

---
### Patch Update Method Response

To update a resource (able to partially edit), we use a Patch method with
the following return options:
- 200: Ok + resource -> When the resource was updated
- 404: Resource not found + ErrorObjectSchema -> When the resource being updated was not found