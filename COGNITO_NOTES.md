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
 - `Attributes` appear at first glance to be arbitrary key-value pairs, but it seems
   that only `email` and `phone_number` are supported, and then the API adds in things
   (somewhat randomly) such as `sub`, and `cognito:username`
 - A login request does not return a User but an authentication object which can then
   be used to retrieve the user by token
 - The `AdminGetUser` endpoint can retrieve a user either by their UUID Username (aka
   `sub`), or by the initially provided username.
 - Not all User responses look the same. Be sure to account for such differences as:
     * Attributes being variously named "Attributes" and "UserAttributes"
     * Attributes sometimes there and sometimes not (e.g. `cognito:username`)


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


### A note about getting users

Interestingly enough, the `AdminGetUser` API endpoint, which gets a User by username,
will accept for the username either the `Username`, aka `sub`, which is the AWS-assigned
UUID for the distinct user in a pool, or the initially provided username which (sometimes)
shows up in responses as the `cognito:username` attribute.

