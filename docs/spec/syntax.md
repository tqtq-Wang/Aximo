# Syntax

## Goal

This document captures the initial syntax surface for Axiom v0.1 as reflected by the repository bootstrap. It is intentionally conservative and stays close to the RFC.

## Core Style

Axiom uses a block-oriented syntax with:

- braces for blocks
- `fn` for functions
- `struct`, `enum`, and `newtype` for data declarations
- `trait` and `impl` for abstraction and implementation
- `match` for pattern matching
- `let` for immutable bindings
- `var` for mutable bindings
- `pub` and `internal` for explicit visibility
- `async fn` and `await` for async operations
- `effects [...]` for effect declarations

## File Structure

A file begins with a module declaration followed by zero or more imports and declarations.

```axiom
module domain.user.service

use domain.user.model.{User, Email, CreateUserInput}
use domain.user.errors.CreateUserError
use domain.user.repo.{UserRepo, RepoError}
```

## Imports

Imports are explicit. Wildcard imports are not allowed.

```axiom
use domain.user.model.{User, UserId}
use domain.user.errors.CreateUserError
```

## Visibility

Supported forms:

```axiom
pub fn create_user(...) -> ...
internal fn normalize_email(...) -> ...
fn helper(...) -> ...
```

## Data Declarations

### Struct

```axiom
pub struct User {
    pub id: UserId
    pub name: String
    pub email: Email
}
```

### Enum

```axiom
pub enum CreateUserError {
    InvalidName
    InvalidEmail
    AlreadyExists
    StorageUnavailable
}
```

### Newtype

```axiom
pub newtype UserId = String
pub newtype Email = String
```

## Function Declarations

### Basic Function

```axiom
pub fn parse_email(input: String) -> Result<Email, CreateUserError> {
    if input.contains("@") {
        Ok(Email(input))
    } else {
        Err(CreateUserError::InvalidEmail)
    }
}
```

### Function with Effects

```axiom
pub fn save_user(user: User) -> Result<Unit, RepoError>
    effects [db.write, log.write]
{
    ...
}
```

### Async Function

```axiom
pub async fn fetch_user(id: UserId) -> Result<User, FetchUserError>
    effects [net.call]
{
    let response = await http.get("/users/" + id)?
    decode_user(response.body)
}
```

## Trait and Impl

```axiom
pub trait UserRepo {
    fn exists_by_email(email: Email) -> Result<Bool, RepoError>
        effects [db.read]

    fn insert(user: User) -> Result<Unit, RepoError>
        effects [db.write]
}
```

```axiom
impl UserRepo for SqlUserRepo {
    fn exists_by_email(email: Email) -> Result<Bool, RepoError>
        effects [db.read]
    {
        ...
    }
}
```

## Generics

The RFC uses generic parameters with trait constraints in function declarations:

```axiom
pub fn create_user<R: UserRepo>(
    repo: R,
    input: CreateUserInput
) -> Result<User, CreateUserError>
    effects [db.read, db.write]
{
    ...
}
```

This repository treats that form as part of the initial syntax surface.

## Match

```axiom
match err {
    RepoError::Conflict => CreateUserError::AlreadyExists,
    RepoError::ConnectionFailed => CreateUserError::StorageUnavailable,
    RepoError::Unknown => CreateUserError::StorageUnavailable
}
```

## Tests

```axiom
test "parse valid email" {
    let result = parse_email("a@test.com")
    assert_eq(result, Ok(Email("a@test.com")))
}
```

## Simplified EBNF

```ebnf
module_decl     = "module" ident_path ;
use_decl        = "use" ident_path [ "." "{" ident_list "}" ] ;
visibility      = "pub" | "internal" ;
mutability      = "let" | "var" ;
struct_decl     = [visibility] "struct" IDENT "{" field_list "}" ;
enum_decl       = [visibility] "enum" IDENT "{" variant_list "}" ;
newtype_decl    = [visibility] "newtype" IDENT "=" type_expr ;
fn_decl         = [visibility] ["async"] "fn" IDENT generic_params?
                  "(" param_list? ")" "->" type_expr effects_clause? block ;
effects_clause  = "effects" "[" effect_list? "]" ;
trait_decl      = [visibility] "trait" IDENT generic_params?
                  "{" trait_member_list "}" ;
test_decl       = "test" STRING block ;
match_expr      = "match" expr "{" match_arm_list "}" ;
```

## Explicitly Out of Scope

The bootstrap does not define:

- macro syntax
- implicit conversions
- implicit imports
- annotation-driven hidden behavior
