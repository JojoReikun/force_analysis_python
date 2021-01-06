import os

DEBUG = True and 'DEBUG' in os.environ and os.environ['DEBUG']
from forceAnalysis import DEBUG

from forceAnalysis.utils import auxiliaryfunctions
from forceAnalysis import operations
from forceAnalysis.operations.assemble_data import assemble
