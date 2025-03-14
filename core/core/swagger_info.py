from drf_spectacular.utils import OpenApiResponse, OpenApiExample

response_for_registration = {
    201: OpenApiResponse(
        response={
            'refresh': 'string',
            'access': 'string'
        },
        description='User registration successful',
        examples=[
            OpenApiExample(
                name="Successful Registration",
                value={
                    'refresh': 'string',
                    'access': 'string'
                },
                description="A successful registration returns both refresh and access tokens.",
                response_only=True,
                status_codes=["201"]
            )
        ],
    ),
    400: OpenApiResponse(
        response={
            'error': 'string'
        },
        description='User registration failed',
        examples=[
            OpenApiExample(
                name="Registration Failed - Password Mismatch",
                value={
                    "error": "Passwords do not match."
                },
                description="Occurs when the provided passwords do not match.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Registration Failed - Duplicate Email",
                value={
                    "error": "User with this email already exists"
                },
                description="Occurs when a user tries to register with an email that is already in use.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Registration Failed - Last name is required",
                value={
                    'error': 'First name is required.'
                },
                description="Occurs when the user provides data that does not pass validation.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Registration Failed - First name is required",
                value={
                    'error': 'Last name is required.'
                },
                description="Occurs when the user provides data that does not pass validation.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Registration Failed - Invalid Data",
                value={
                    "error": "Invalid email format"
                },
                description="Occurs when the user provides data that does not pass validation.",
                response_only=True,
                status_codes=["400"]
            )
        ],
    )
}

response_for_login = {
    200: OpenApiResponse(
        response={
            'refresh': 'string',
            'access': 'string',
        },
        examples=[
            OpenApiExample(
                name="Successful Login",
                value={},
                description="A successful login returns both refresh and access tokens.",
                response_only=True,
                status_codes=["200"]
            )
        ],
        description="User login successful"
    ),
    400: OpenApiResponse(
        response={
            'error': 'string',
        },
        examples=[
            OpenApiExample(
                name="Missing Credentials",
                value={"error": "Email and password are required"},
                description="Occurs when the email or password is not provided.",
                response_only=True,
                status_codes=["400"]
            )
        ],
        description="User login failed due to missing credentials"
    ),
    401: OpenApiResponse(
        response={
            'error': 'string',
        },
        examples=[
            OpenApiExample(
                name="Authentication Failed",
                value={"error": "Incorrect email or password"},
                description="Occurs when the provided email or password is incorrect.",
                response_only=True,
                status_codes=["401"]
            )
        ],
        description="User login failed due to incorrect credentials"
    )
}

response_for_important_data = {
    200: OpenApiResponse(
        response={
            'refresh': 'string',
            'access': 'string'
        },
        description="User data updated successfully",
        examples=[
            OpenApiExample(
                name="Successful Update",
                value={},
                description="Returned when user data is updated successfully.",
                response_only=True,
                status_codes=["200"]
            )
        ]
    ),
    400: OpenApiResponse(
        response={'error': 'string'},
        description="User data update failed due to validation errors",
        examples=[
            OpenApiExample(
                name="Validation Error - data_to_update is required",
                value={'error': 'data_to_update is required'},
                description="Occurs when required fields are missing or invalid.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Validation Error - token is required",
                value={'error': 'Refresh token is required'},
                description="Occurs when required fields are missing or invalid.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Validation Error - password is required",
                value={'error': 'Current password is required'},
                description="Occurs when required fields are missing or invalid.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Validation Error - password is incorrect",
                value={'error': 'Current password is incorrect'},
                response_only=True,
                status_codes=["400"]
            )
        ]
    ),
    401: OpenApiResponse(
        response={'error': 'string'},
        description="Authentication failed due to incorrect current password",
        examples=[
            OpenApiExample(
                name="Authentication Failed",
                value={'error': 'Current password is incorrect'},
                description="Occurs when the provided current password does not match.",
                response_only=True,
                status_codes=["401"]
            )
        ]
    )
}

response_for_refresh_token = {
    200: OpenApiResponse(
        response={'ok': 'ok'},
        description="User data updated successfully",
        examples=[
            OpenApiExample(
                name="Successful Refresh",
                value={},
                response_only=True,
                status_codes=["200"]
            )
        ]
    ),
    401: OpenApiResponse(
        response={'error': 'string'},
        description="Invalid refresh token",
        examples=[
            OpenApiExample(
                name="Authentication Failed",
                value={'error': 'Invalid refresh token'},
                description="Occurs when the provided current password does not match.",
                response_only=True,
                status_codes=["401"]
            )
        ]
    )
}

response_for_validate_token = {
    200: OpenApiResponse(
        response={'detail': 'Token is valid'},
        description="Token is valid",
        examples=[
            OpenApiExample(
                name="Token is valid",
                value={'detail': 'Token is valid'},
                response_only=True,
                status_codes=["200"]
            )
        ]
    ),
    401: OpenApiResponse(
        response={'error': 'string'},
        description="Invalid refresh token",
        examples=[
            OpenApiExample(
                name="Authentication Failed",
                value={'error': 'Invalid refresh token'},
                description="Occurs when the provided current password does not match.",
                response_only=True,
                status_codes=["401"]
            )
        ]
    )
}

request_for_logout = {
    'application/json': {
        'type': 'object',
        'properties': {
            'refresh_token': {
                'type': 'string',
            },
        },
    }
}

response_for_logout = {
    205: OpenApiResponse(
        response={
            'detail': 'string'
        },
        description='Successfully logged out',
        examples=[
            OpenApiExample(
                name="Successful Logout",
                value={},
                description="Returned when the user has been successfully logged out.",
                response_only=True,
                status_codes=["205"]
            )
        ]
    ),
    400: OpenApiResponse(
        response={
            'error': 'string'
        },
        description='Invalid request',
        examples=[
            OpenApiExample(
                name="Logout Failed - Missing Refresh Token",
                value={"error": "Refresh token is required"},
                description="Occurs when the refresh token is not provided in the request.",
                response_only=True,
                status_codes=["400"]
            )
        ]
    )
}

response_for_upload_image = {
    200: OpenApiResponse(
        response={
            'response': 'string'
        },
        description='Image successfully uploaded',
        examples=[
            OpenApiExample(
                name="Image Upload Success",
                value={"response": "ok"},
                description="Returned when the image is successfully uploaded.",
                response_only=True,
                status_codes=["200"]
            )
        ]
    ),
    400: OpenApiResponse(
        response={
            'error': 'string'
        },
        description='Image upload failed',
        examples=[
            OpenApiExample(
                name="Image Upload Failed - No Image Provided",
                value={"error": "image is required"},
                description="Occurs when no image is provided in the request.",
                response_only=True,
                status_codes=["400"]
            ),
            OpenApiExample(
                name="Image Upload Failed - No Header multipart/form-data",
                value={"error": "header multipart/form-data is required"},
                response_only=True,
                status_codes=["400"]
            )
        ]
    )
}

request_for_important_info = {
    'application/json': {
        'type': 'object',
        'properties': {
            'data_to_update': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'password2': {'type': 'string'}
                },
                'required': ['email'],
            },
            'password': {'type': 'string'},
            'refresh_token': {
                'type': 'string',
            },
        },
        'required': ['data_to_update', 'refresh_token', 'password'],
    }
}

request_for_login = {
    'application/json': {
        'type': 'object',
        'properties': {
            'email': {'type': 'string'},
            'password': {'type': 'string'},
        },
        'required': ['email', 'password'],
    }
}

request_for_upload_image = {
    'multipart/form-data': {
        'type': 'object',
        'properties': {
            'image': {
                'type': 'string',
                'format': 'binary',  # Указываем, что это бинарные данные (файл)
                'description': 'The image file to upload'
            }
        },
        'required': ['image']
    }
}
