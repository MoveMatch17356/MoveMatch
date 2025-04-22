# Code Review Checklist

### General
- [ ] Is the purpose of the PR clearly described?
- [ ] Is the code easy to understand?
- [ ] Are variable and function names meaningful?
- [ ] Is the code style consistent with the rest of the codebase?

### Functionality
- [ ] Does the feature work as expected?
- [ ] Are edge cases handled appropriately?
- [ ] Are there any obvious bugs?

### Security
- [ ] No secrets, tokens, or credentials are exposed
- [ ] User input is validated/sanitized
- [ ] API responses don’t leak sensitive data

### Django-Specific
- [ ] Database migrations are included if needed
- [ ] Views/controllers follow DRY principles
- [ ] Admin views are protected or limited if necessary

### Testing
- [ ] Are new features covered by tests?
- [ ] Do all tests pass?
- [ ] Are there tests for failure conditions?

### Cleanup
- [ ] No commented-out or debug code
- [ ] No unused variables or imports