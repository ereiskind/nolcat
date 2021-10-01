"""These classes represent all the relations used only in the `ingest` blueprint."""

from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from nolcat.models import Base