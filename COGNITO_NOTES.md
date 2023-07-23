# Cognito notes


## The dumpster fire of AWS cognito User responses

### TL; DR

 - The thing that you specify as the `username` becomes an "attribute" (not a direct
   property) on the user, keyed by `cognito:username`
 - That username is not always available in user payloads. Specifically, it is not
   included in a `get_user` request when getting a user by authentication token
 - Cognito's de facto `Username` is in fact the `sub` (ie "subject") which is an
   assigned UUID and is usually provided both as the `Username` property and as the
   `sub` attribute.
 - `Attributes` appear maybe to be arbitrary key-value pairs, althought this is not
   entirely clear. In some cases it seems that that only `email` and `phone_number` are
   supported keys, and then the API adds in things (somewhat randomly) such as `sub`,
   and `cognito:username`. There is, however, indicationn in the docs that `custom:`
   namespaced attributes can be added. I am also seeing the ability to simply add
   arbitrary keys, although this could be a bug/oversight in Localstack.
 - A login request (ie. InitiateAuth and AdminInitiateAuth) does not return a User but
   an authentication object which can then be used to retrieve the user by token. This
   appears to be true for both endpoints, so it is not really clear why the so-called
   admin endpoint is even a thing -- presumably the difference as a "backend" oriented
   endpoint would be to retrieve the user rather than an auth token. From what I can see,
   these endpoints are identical for purposes that I can foresee.
 - The `AdminGetUser` endpoint can retrieve a user either by their UUID Username (aka
   `sub`), or by the initially provided username.
 - Not all User responses look the same. Be sure to account for such differences as:
     * Attributes being variously named "Attributes" and "UserAttributes"
     * Attributes sometimes there and sometimes not (e.g. `cognito:username`)

### Recommendations (so far)

Take this all with a grain of salt. I am just starting to get my head around this very
convoluted API. These are my best guesses based on what I know now and specifically for
use cases I have in mind.

 - Use cognito as the de facto copy of identifying information, including:

   * The AWS generate UUID (aka `Username`, aka `sub`)
   * The user's email address (aka attribute `email`)
   * The username (aka attribute `cognito:username`)
   * The user's phone number (aka attribute `phone_number`)

 - Also potentially use Cognito for arbitrary user info to minimize your app User model.
   However, be aware, I am still unsure as to how some of this info is handled. It seems
   recommended (required?) to prefix these attributes with `custom:`, and it is still
   unclear when these attributes may or may not show up in User responses.

 - In any case, use the UUID (aka `Username` aka `sub`) as the primary identifier for your
   users, rather than the username or email or phone number.

 - Don't pass auth tokens to your users until your application really needs it. I am
   still trying to understand the use cases for this. Maybe you can give your users
   direct access to AWS resources? But then ask yourself why, and if you understand this
   security model well enough to do so safely. As mentioned below, it is not yet clear
   to me that your users could not just start setting arbitrary attributes on their
   user object once you hand them a token.

 - Track your own app clients and access tokens (if you need them). I outline a (sort of
   gross) approach to overloading user pools as app client pools, but I don't really
   recommend it. This doesn't seem to be what Cognito was designed for. Alternatively,
   you could just use Cognito's auth tokens as access tokens and not have a concept of
   application clients. I really dislike this pattern however of passing in user
   credentials to get app client access. It is common enough, but strikes me as an
   anti-pattern.

 - Use groups for broad access controls. I have yet to explore groups (the need for a
   role ARN makes them unnecessarily complex) but it makes sense that you want your
   auth service to at least have a concept of groups, if not full ACL. Alternative,
   you might consider a simpler approach of having a "groups" attribute, but consider
   the caveats about how custom attributes are handled, and whether or not (?) users
   can set their own attributes when handed auth keys. (geez, I have to be wrong about
   this. I'm sure ... I must be just not seeing it yet)

 - Manage your own fine-grained access controls. I mean, I guess you could also do this
   in attributes, but again those caveats -- I need to dig into this attributes thing
   a bit more it seems.



### Things I have yet to explore

#### User groups

Groups are associated with user pools. Presumably, you can [create a group](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/create_group.html)
and then [AdminAddUserToGroup](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/admin_add_user_to_group.html)
Groups have a role ARN, which I suppose might open up access possibilities to AWS
resources, but also complicates setup -- presumably you would have to create a role
before creating a group (unless the ARN is not required?).

Apart from the complexity of the role requirement (?), groups may provide a reasonable
mechanism for broad authorization/access control.


#### ACL

Is this a thing in Cognito? I don't see it, despite claims of "fine grained access control."
My best guess is that this maybe is a reference to ability to set IAM policies on Cognito
users. I am not sure if this is possible, but it does seem in any case that user groups
and IAM roles are related.


### Usage patterns

While a fairly terrible mess, this API appears to have been designed for ultimate flexibility.
There is a lot here I have still not yet explored, and your use cases might be different
from mine. Here is my best guess at a couple of anticipated usage patterns:

1. Console (ie. user-facing UI) application Server-side auth

Your application serves the auth UI (an HTML form) and manages authorization access
after that -- I am presuming here via sessions (please
[don't use JWTs as sessions](http://cryto.net/~joepie91/blog/2016/06/13/stop-using-jwt-for-sessions/))

In this scenario I think your application user persistence would only have the UUID and
then any profile attributes you don't want to push to AWS. I recommend keeping at least
the email, username, and phone number in Cognito rather than your application database.

The pattern would look like this:

**Authentication:**

HTML Form (username+password) # username could, e.g., be an email address
    -> Controller
    -> InitiateAuth | AdminIniateAuth (there does not appear to be a practical difference)
    -> GetUser (by access token)
    -> (optionally) Controller looks up localized profile info # This might depend on the endpoint
    -> Controller sets a sesion for the user. I would recommend using server-side session
       data and utilizing the AWS UUID (aka `Username`, aka `sub`) as the user key.

**Authorization:**

Web Request:
    -> Controller gets the UUID of the user from the session
    -> 


2. Federated Identity Auth

Federated Identity with Cognito makes use of the CognitoIdentity client rather than the
CognitoIdentityProvider client investigated here. I have not yet dug into these patterns.
The federated auth flow is [documented here](https://docs.aws.amazon.com/cognito/latest/developerguide/authentication-flow.html)


3. OAuth (ie for client applications)

In theory, OAuth could be used by a web browser for UI access. I am hard pressed to make
sense of that approach, however. For UI, I recommend session-based authentication (see
#1 above).

This is for application-managed OAuth access for programmatic access to your application.
This does not cover 3rd party OAuth, which is also a possibility I have not yet explored.
Cognito does not actually seem to provide a mechanism for managing application clients
(as opposed to users). This is a bit of a convoluted attempt to coerce Cognito's model
into something appropriate for application clients. In the end, you might be better off
just managing tokens to your API on your own (ie. approach #1 below which is not covered
in detail).

**Caution:** I think there is some temptation here to create a user pool client to use
as the concept of an application client that would make requests on behalf of your user.
This strikes me as an anti-pattern for most use cases. It may be appropriate for a narrow
set of use cases where, for example, you have a user pool that is distinct for an entire
organization, and the client should have access to the users in that organzation. I think
more commonly however, for the standard use case of managing general application resources
(that likely cut across organizations and users) you will want to manage the concept of
"application clients" rather than "user clients". From what I can tell, Cognito does not
provide such a thing, and so I can imagine 2 approaches:

 1. Manage app clients and tokens in your application
 2. Set up a distinct user pool in which "users" will actually be application clients.

Approach #1 really just doesn't use Cognito for app clients, so this is approach #2.
Admittedly, it is a bit of a kludge. I am mostly leaning against recommending this
approach, but providing this for a sense of exploratory completeness.

1. Create a separate user pool for API keys. I just like the logical distinction of keys from users.
2. Create a general user-pool-client for the pool
3. Create the individual application clients:
  - username might be the "app name" (e.g. as used in Twitter API nomenclature)
  - password would be the app client secret (generated by your application)
  - the generated `Username` (aka `sub`) would be the app client ID
4. "authenticate" via the username and password, which we are now calling the app id and secret.
5. Return the auth token to the client user for subsequent requests.

In this approach, there is no real sense of ownership, so I am imagining you would have
to include a custom attribute such as a user ID or group ID to manage who the client
operates on behalf of.


The flow might look like this

Application API token request:
    -> Controller sends auth init to the "API clients" cognito user pool
    -> Controller retrieves the "user" (our app client concept) via the auth token
    -> Controller then retrieves the owner from the primary user pool using the owner
       attribute of the "client" (okay, it's getting kind of gross at this point)
    -> Controller caches the token and the associated user with a cache timeout based on
       the token timeout
    -> Controller returns the token to the client for subsequent requests



### User signup

This is what a registration request looks like

```
    response = cognito_client.sign_up(
        ClientId=client_id,
        Username=email,
        Password=password,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            }
        ]
    )
```

Take note of the fact that I have used the email address as the Username (presumably
some notion of identity given the structure, but we will see that it is not) as well
as added email as an attribute. While attributes here appear to be arbitrary key-value
pairs, it seems that only `email` and `phone_number` are the supported keys.


### User signup response:

Ignoring the ResponseMetadata, which is mostly useless header info that should maybe be
passed via the .... header?

```
{
    'UserConfirmed': False,
    'UserSub': '64d49acb-5316-418f-85ed-9d56741e2a04',
    'ResponseMetadata': ... # a bunch of stuff you mostly won't likely need
}
```

So here, the idea of a "UserSub" (which I believe means "subject") takes on the concept
of identity. Apart from that poorly named key, this is not a terrible start to the
user cycle. It is simple enough.


### Confirm and login

Do not actually return user objects. This is sort of bizarre to me, especially for login.
First, I really don't have a concept of what one would do with the tokens returned by
the login request, other than to fetch the user. Perhaps, a user can be given direct
access to AWS resources via this token? If that is the case, then okay maybe this makes
sense, but when using this primarily for identify and authentication it means every login
request will require an extra user request.


### Get User 

Get user by access token, e.g. after a successful login:

```
{
    'Username': '64d49acb-5316-418f-85ed-9d56741e2a04',
    'UserAttributes': [
        {
            'Name': 'email',
            'Value': 'scott@example.com'
        },
        {
            'Name': 'sub',
            'Value': '64d49acb-5316-418f-85ed-9d56741e2a04'
        }
    ],
    'ResponseMetadata': ...
}
```

So now, the concept of identity is apparently taken on by the `Username` which is just
a copy of the "subject" which is still considered an "attribute" to the user. This
arrangement is likely a side effect of the way I am makeing these requests, so it is
not entirely clear to me if `Username` is always the identity, and if so, is it always
the "subject" UUID? For now I am going with the assumption that both things will be
true at least for our use cases.

### List Users

Here is what a user looks like in a list response (listed by user pool)

```
{
    'Users': [
        {
            'Username': '64d49acb-5316-418f-85ed-9d56741e2a04',
            'Attributes': [
                {
                    'Name': 'cognito:username',
                    'Value': 'scott@example.com'
                },
                {
                    'Name': 'email',
                    'Value': 'scott@example.com'
                },
                {
                    'Name': 'sub',
                    'Value': '64d49acb-5316-418f-85ed-9d56741e2a04'
                }
            ],
            'UserCreateDate': datetime.datetime(2023, 7, 22, 20, 15, 24, 356803, tzinfo=tzlocal()),
            'UserLastModifiedDate': datetime.datetime(2023, 7, 22, 20, 15, 24, 356803, tzinfo=tzlocal()),
            'Enabled': True,
            'UserStatus': 'CONFIRMED'
        }
    ],
    'ResponseMetadata': ...
}
```
So, now there are 2 concepts of a username. One is actually an identity, the other is
the attribute that I have specified to be the (I guess) "official" username? which has
now been namespaced as a "cognito" username. This is a very strange pattern. The userame
is actually a required property when you create the user, but then it just becomes an
arbitrary attribute, albeit with this special namespace. Furthermore, the actual identity
of the user also becomes a (poorly named) arbitrary attribute that is **not** in the
special "cognito" namespace. It all feels kind of random. I'm not a fan. Honestly, I am
hard pressed to make clear decisions about best usage patterns here. Let's look at what
it is like to administratively create a user before deciding.

### Adminitratively create a user

This is a request to create a user

```
    response = cognito_client.admin_create_user(
        UserPoolId=pool_id,
        Username=email,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': email
            },
        ],
        DesiredDeliveryMediums=['EMAIL'], # 'EMAIL', 'SMS'
    )
```

The first thing to note is that when you create a user, they are associated directly
with a user pool. There is no client here. The idea appears to be that self-registered
users would be registered by a client application on behalf of the user. Clients thus
appear primarily responsible for the registration cycle, but then that's it. In the end
either process ends up with a user in a user pool.

Note that I have used the email address as the username to be consistent with the notes
above.

Secondly, I have not used it here, but you can pass in something called `ValidationData`
which are arbitrary key-value pairs that can be used by Lambda triggers for validation
actions. But there is also `ClientMetadata` which is more arbitrary pairs that can also
be used by Lambda triggers.

The `TemporaryPassword` can be set here, but I did not set it because I wanted to see
what the generate password looks like in the response.


The response

```
{
    'User': {
        'Username': '5bf4fb10-3b83-4406-9d2b-bc533d1df832',
        'Attributes': [
            {
                'Name': 'email',
                'Value': 'user@example.com'
            },
            {
                'Name': 'sub',
                'Value': '5bf4fb10-3b83-4406-9d2b-bc533d1df832'
            }
        ],
        'UserCreateDate': datetime.datetime(2023, 7, 23, 12, 26, 57, 195370, tzinfo=tzlocal()),
        'UserLastModifiedDate': datetime.datetime(2023, 7, 23, 12, 26, 57, 195370, tzinfo=tzlocal()),
        'Enabled': True,
        'UserStatus': 'FORCE_CHANGE_PASSWORD'
    },
    'ResponseMetadata': ...
}
```

Notably:

Even though we specified a username (the enpoint requires it) that does not show up here.
We see the `Username` that is actually the `sub` as we might expect, but based on the
above, we might have also expected a `cognito:username` attribute that is not here. In
that sense, this is more like a get-users request than a list-users request.

Attributes is called `Attributes` here and not `UserAttributes`. In that sense, this is
more like the list-users request than the get-users request 🙃


Finally, list the users to see that both processes end up with similar looking objects:

```
{
    'Users': [
        {
            'Username': '64d49acb-5316-418f-85ed-9d56741e2a04',
            'Attributes': [
                {
                    'Name': 'cognito:username',
                    'Value': 'scott@example.com'
                }, {
                    'Name': 'email',
                    'Value': 'scott@example.com'
                }, {
                    'Name': 'sub',
                    'Value': '64d49acb-5316-418f-85ed-9d56741e2a04'}
            ],
            'UserCreateDate': datetime.datetime(2023, 7, 22, 20, 15, 24, 356803, tzinfo=tzlocal()),
            'UserLastModifiedDate': datetime.datetime(2023, 7, 22, 20, 15, 24, 356803, tzinfo=tzlocal()),
            'Enabled': True,
            'UserStatus': 'CONFIRMED'
        }, {
            'Username': '5bf4fb10-3b83-4406-9d2b-bc533d1df832',
            'Attributes': [
                {
                    'Name': 'cognito:username',
                    'Value': 'user@example.com'
                }, {
                    'Name': 'email',
                    'Value': 'user@example.com'
                }, {
                    'Name': 'sub',
                    'Value': '5bf4fb10-3b83-4406-9d2b-bc533d1df832'
                }
            ],
            'UserCreateDate': datetime.datetime(2023, 7, 23, 12, 26, 57, 195370, tzinfo=tzlocal()),
            'UserLastModifiedDate': datetime.datetime(2023, 7, 23, 12, 26, 57, 195370, tzinfo=tzlocal()),
            'Enabled': True,
            'UserStatus': 'FORCE_CHANGE_PASSWORD'
        }
    ],
    'ResponseMetadata': ...
}
```

So, our `cognito` namespaced username that was previously missing is here now. (Although,
recall that it is not include in a get-user request)

Notably: there is no temporary password, so, like, how is this even supposed to work?


### A note about getting users

Interestingly enough, the `AdminGetUser` API endpoint, which gets a User by username,
will accept for the username either the `Username`, aka `sub`, which is the AWS-assigned
UUID for the distinct user in a pool, or the initially provided username which (sometimes)
shows up in responses as the `cognito:username` attribute.


### Updating users

There are 2 endpoint for updating users' attributes:

 - AdminUpdateUserAttributes (updates by pool ID + username)
 - UpdateUserAttributes (updates by access token) 

I am not sure there is a practical difference for server-side request. However,
presumably, a client could make direct update requests with an access token, but then
how do you control the attributes that clients are able to update? What keeps them from
pushing arbitrary data? What keeps one user from setting their email or phone number to
that of another existing user? etc. I fail to see this as a good pattern. User update
requests should be brokered by your application.
