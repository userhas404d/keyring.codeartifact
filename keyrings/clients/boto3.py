import boto3
import boto3.session

import os
from datetime import datetime

import logging

logging.getLogger("keyrings.codeartifact")


class Boto3CAClient:
    def __init__(
        self,
        region: str,
        domain: str = None,
        account: str = None,
        profile_name: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        token_duration: int = 3600,
    ):
        """
        Initialize the Boto3CodeArtifact keyring.

        :param region: AWS region to use.
        :param domain: CodeArtifact domain name.
        :param account: AWS account ID.
        :param profile_name: AWS profile name (optional).
        """
        self.region = region
        self.domain = domain
        self.account = account
        self.profile_name = profile_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.token_duration = token_duration

    def _get_codeartifact_client(self):
        session = boto3.session.Session()

        # CodeArtifact requires a region.
        kwargs = {"region_name": self.region}

        # If a profile name was provided, use it.
        if self.profile_name:
            kwargs.update({"profile_name": self.profile_name})

        # If static access/secret keys were provided, use them.
        if self.aws_access_key_id and self.aws_secret_access_key:
            kwargs.update(
                {
                    "aws_access_key_id": self.aws_access_key_id,
                    "aws_secret_access_key": self.aws_secret_access_key,
                }
            )

        # Build a CodeArtifact client from the session.
        return session.client("codeartifact", **kwargs)

    def get_authorization_token(self):
        """
        Get the CodeArtifact authorization token.

        :return: Authorization token as a string.
        """
        client = self._get_codeartifact_client()
        response = client.get_authorization_token(
            domain=self.domain, domainOwner=self.account
        )

        # Figure out our local timezone from the current time.
        tzinfo = datetime.now().astimezone().tzinfo
        now = datetime.now(tz=tzinfo)

        # Give up if the token has already expired.
        if response.get("expiration", now) <= now:
            logging.warning("Received an expired CodeArtifact token!")
            return

        return response.get("authorizationToken")
