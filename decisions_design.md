# Design Decisions Log Book
All decisions taken as to the design of this project will be
documented here with the relevant reasoning and evidence to support
the decision.

---
### Use of Managers and QuerySets
We will create custom querysets for any model that has filtering actions 
done to it. 

[See here](https://docs.djangoproject.com/en/5.0/topics/db/managers/#creating-a-manager-with-queryset-methods)


This will localise any ORM logic into querysets for re-usability and easier testability.

If you also need to create methods for the manager, that is, methods 
involve ORM operations but do not return a queryset, instead a instance, 
boolean, etc, then a manager is created and the queryset is added to it.

[See Here](https://docs.djangoproject.com/en/5.0/topics/db/managers/#from-queryset)

This logic is consistent with multiple websites:
- https://stackoverflow.com/a/53972793/14134362
- https://stackoverflow.com/a/18129747/14134362
- https://sunscrapers.com/blog/where-to-put-business-logic-django/#idea-3-services

---
### Use of Service Layer and Model Methods
We will discourage the use of model methods as we want to keep Models thin, 
focusing on fields, relationships, and properties.

Any logic involving the models should be in the Model's Service file.
This logic is logic that only involves that model. When importing 
this file, you should do:
```python
import race.service_race as RaceService
```
This will keep all service functions within `RaceService`.

Any logic that involves multiple models should be found in a generic 
services file for the app in question called `service.py`.
```python
import race.service as RaceAppService
```
In this case we prepend the app name and then "App" to the import name.

---
